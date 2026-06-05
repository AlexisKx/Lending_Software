# Loan Management System — Handover for Claude Code

This document carries the design decisions and context from earlier conversations so you can start building immediately. Pair it with `Mini_Loan_Management_System_SRS.md` for the full requirements.

---

## 1. Project goal

Build a **single-user Loan Management System** for a small lender (operating in the Philippines, peso amounts). The lender records borrowers, loans, and payments, and views analytics on a dashboard.

**There is no application or approval workflow.** The lender records a loan at the moment of the agreement; saving the record is the lending decision.

---

## 2. Stack (already decided — don't re-litigate)

| Layer | Choice | Reason |
|------|--------|--------|
| Language / framework | **Django 5.x** (Python) | Free admin = 60–70% of CRUD screens; LTS stability; user already knows Python |
| Interactivity | **HTMX** | Live form updates (net proceeds calc, dashboard filters) without an SPA |
| Database | **SQLite** | Single-user; one file; trivial backup; switch to Postgres later if needed |
| Styling | **Tailwind CSS** (standalone CLI binary) | Maps directly to the mockup; no Node build pipeline |
| Charts | **Chart.js** from CDN | Already used in the mockup; no install |
| Auth | Django's built-in auth | One superuser account |
| Hosting | **Railway** (~$5/mo) | One-command GitHub deploys; doesn't sleep |

**Avoid:** React/Next.js, separate API + frontend, microservices, Node build tooling. Wrong scale.

---

## 3. The single user

One user — the lender. No roles, no multi-tenancy. Create the account with `python manage.py createsuperuser`. Use the standard Django login view at `/accounts/login/` and require login on every view via `LoginRequiredMixin` or `@login_required`.

---

## 4. Data model

```python
# borrowers/models.py
class Borrower(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    contact = models.CharField(max_length=50, blank=True)
    valid_id = models.CharField(max_length=100, blank=True)
    source_of_income = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

# loans/models.py
class Loan(models.Model):
    STATUS = [("ACTIVE", "Active"), ("PAID", "Paid"), ("OVERDUE", "Overdue")]
    borrower = models.ForeignKey(Borrower, on_delete=models.PROTECT, related_name="loans")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # % per month
    term_months = models.PositiveIntegerField()
    advance_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_proceeds = models.DecimalField(max_digits=12, decimal_places=2)  # computed on save
    release_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

class Comaker(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name="comaker")
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=50, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    source_of_income = models.CharField(max_length=200, blank=True)

class ComakerWaiver(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name="waiver")
    reason = models.CharField(max_length=300)
    waived_at = models.DateTimeField(auto_now_add=True)

# payments/models.py
class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="payments")
    date_paid = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class LoanAudit(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField()
```

Each loan has *either* a `Comaker` *or* a `ComakerWaiver`, never both. A loan with neither shouldn't normally exist — the form requires one or the other before saving.

---

## 5. The Record Loan screen (most distinctive feature — build this first)

A single screen that captures borrower + loan + co-maker + advance interest. On save, the loan becomes `ACTIVE` immediately.

Sections on the page (vertical):
1. **Borrower** — select an existing borrower (autocomplete) OR create a new one in the same form
2. **Loan details** — amount, monthly rate, term, release date
3. **Co-maker** — name/contact/relationship/income, OR a "Skip with waiver reason" toggle that swaps in a reason field. Show an advisory chip ("Recommended" / "May be waived") based on the borrower's payment history rating, but never block submission
4. **Advance interest + Net proceeds** — as the lender types the advance interest amount, an HTMX endpoint recomputes and re-renders the net proceeds panel (`amount − advance_interest − fees`)
5. **Save & release** button

HTMX endpoint for live net proceeds:
```
POST /loans/_compute_proceeds/  →  returns the proceeds panel partial
```

---

## 6. Dashboard (centerpiece)

Default landing page after login. Single view, single SQL aggregation pass per panel, all panels filterable by date range via a top-right `<select>` driving an HTMX swap.

Panels:
- **KPI cards** — Total Borrowers, Active Loans (count + outstanding), Collection Rate (collected / expected for period), Overdue (count + amount)
- **Monthly Revenue & Interest** — Chart.js bar chart, last 6 months
- **Paid vs Unpaid** — Chart.js doughnut (Paid / Active / Overdue)
- **Overdue aging** — horizontal bars for 1–30 / 31–60 / 61–90 / 90+ days past due (server-computed, no chart library needed)
- **Recent activity** — last 5–10 events (new loans, payments, overdue flags)

Each KPI card and chart segment links to a filtered list view (drill-down).

A mockup of this layout exists; replicate it in Tailwind.

---

## 7. Business rules (enforce in model `save()` or signals)

1. On `Loan.save()`, compute `net_proceeds = amount − advance_interest − fees`. Never accept it from the form.
2. On `Payment.save()`, recompute `balance_after`, update the loan's outstanding balance, and set `status = PAID` if balance reaches zero.
3. A nightly management command (`manage.py flag_overdue`) sets `status = OVERDUE` for any loan with an installment past its due date. Run via a Railway cron job.
4. Any edit to a saved `Loan` writes a `LoanAudit` row with the previous values.
5. Co-maker advisory: rate the borrower's history as good / fair / poor based on their prior loans' payment timeliness. Surface as a UI hint only — never block.

---

## 8. Suggested project layout

```
loandesk/
├── manage.py
├── requirements.txt
├── loandesk/              # project package (settings, urls, wsgi)
├── borrowers/             # Borrower model + views
├── loans/                 # Loan, Comaker, Waiver, LoanAudit + Record Loan flow
├── payments/              # Payment model + views
├── dashboard/             # Dashboard view + HTMX partials
├── templates/
│   ├── base.html
│   ├── dashboard/
│   ├── borrowers/
│   ├── loans/
│   └── payments/
├── static/
│   ├── css/output.css     # Tailwind CLI output
│   └── js/                # small HTMX/Chart.js glue
└── tailwind.config.js
```

---

## 9. Starting tasks (in order)

1. **Bootstrap** — `django-admin startproject`, create the four apps, install `django`, `whitenoise`, `htmx` (just include the script tag), and download the Tailwind standalone CLI.
2. **Models + migrations** — paste from section 4, run migrations.
3. **Auth** — `createsuperuser`, restrict all views with `@login_required`.
4. **Base template + Tailwind** — layout shell matching the mockup (top bar with brand + horizontal nav + avatar).
5. **Record Loan screen** — build this *before* the dashboard. It exercises every model and proves the live-compute HTMX pattern.
6. **Payment recording** — simple form on the loan detail page.
7. **Dashboard** — KPIs, then charts, then aging + activity.
8. **Reports** — list views with date filters and a CSV/PDF export action.
9. **Backup script** — see section 11.
10. **Deploy to Railway** — connect the GitHub repo, add `DATABASE_URL` if/when moving to Postgres, set `DJANGO_SETTINGS_MODULE` and `SECRET_KEY`.

---

## 10. UI mockup reference

A two-screen mockup was produced in the previous conversation:

- **Dashboard:** top bar (brand "LoanDesk" + nav: Dashboard / Borrowers / Loans / Payments / Reports + avatar). Page header with date filter. 4 KPI cards (Total Borrowers, Active Loans, Collection Rate, Overdue). Two-chart row (Monthly Revenue & Interest bar chart 1.55fr, Paid vs Unpaid donut 1fr). Bottom row: Overdue Aging horizontal bars + Recent Activity feed.
- **Record Loan:** sectioned form — Borrower / Loan details / Co-maker (with amber "Recommended" advisory chip) / Advance Interest + auto-computed Net Proceeds panel in blue / Save & Release button.

Colors used: blue `#378ADD` for revenue/active, green `#1D9E75` for interest/paid, red `#E24B4A` for overdue, amber `#FAC775` for warnings. Tailwind has near-equivalents — use `blue-500`, `emerald-600`, `red-500`, `amber-400` or configure exact hex values in `tailwind.config.js`.

---

## 11. CRITICAL: backup from day one

A lending system's worst failure mode is losing the database. Before anything goes into production:

```bash
# Nightly cron on Railway or a separate scheduled job
sqlite3 /app/db.sqlite3 ".backup '/tmp/backup-$(date +%F).sqlite3'"
# then upload to S3 / Google Drive / Backblaze B2
```

Use `litestream` if you want continuous replication to S3 — it's the gold standard for SQLite in production and runs as a sidecar process.

---

## 12. Non-goals (do not build these)

- Multi-user / role-based access
- Loan application / approval / pending states
- Borrower-facing portal or login
- SMS / email notifications (can be added later)
- Mobile app (responsive web is enough)
- A REST API (server-rendered + HTMX only)

---

## 13. Open decisions left to make during build

- Exact interest computation method (simple flat per-month vs. amortized). Confirm with the lender — the field convention in Philippine small lending is usually flat monthly interest on the original principal.
- Whether payments are scheduled (fixed installments with due dates) or open (lender records whatever comes in). This determines how "overdue" is computed.
- Currency formatting and number locale (default to `en-PH`).
