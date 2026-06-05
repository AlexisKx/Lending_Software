# Mini Loan Management System (MLMS)
## System Requirements Specification — *Single-User Lender Edition*

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for a **Mini Loan Management System (MLMS)** operated by **a single user — the lender**. The system gives the lender a centralized platform to **record, track, and visualize** borrowers, loans, and payments. It deliberately omits any application or approval workflow: the lender records a loan at the moment the lending agreement takes place, and that record itself represents the granted loan.

### 1.2 Scope
The MLMS supports the lender in:
- Recording a borrower and their loan in a **single combined flow**
- Capturing optional co-maker details or a waiver
- Computing **net proceeds** when interest is deducted in advance
- Recording repayments and tracking collections
- Monitoring overdue accounts and aging
- Viewing visual analytics through a **dashboard**
- Generating operational and financial reports

There is **no application status, no pending state, and no formal approval step**. The lender's act of saving the loan record is the lending decision.

### 1.3 Definitions
| Term | Meaning |
|------|---------|
| Borrower | The person receiving the loan. Not a system user. |
| Lender | The sole system user. |
| Co-maker | A third party who guarantees the loan. Not a system user. |
| Advance Interest | Interest deducted from the loan amount before the borrower receives the proceeds. |
| Net Proceeds | Cash the borrower actually receives = loan amount − advance interest − fees. |
| Payment History | Record of a borrower's past and current loan repayments. |
| Collection | Money actually received by the lender. |
| Aging | Classification of overdue accounts by days past due (1–30, 31–60, 61–90, 90+). |

---

## 2. Overall Description

### 2.1 User
The system has **one user: the lender**, who performs every operation — recording borrowers and loans, recording payments, reviewing the dashboard, and generating reports.

Borrowers and co-makers are **data subjects**, not users.

### 2.2 Mapping of the Field Workflow to System Functions
| # | Field Workflow Step | System Function |
|---|--------------------|-----------------|
| 1 | Customer approaches the lender for a loan. | The lender opens the **Record Loan** screen. |
| 2 | Lender decides whether to require a co-maker, or waive it for borrowers with good payment history and financial capability. | The system captures co-maker details OR a waiver reason; it shows an advisory recommendation but does not block the lender. |
| 3 | Lender grants the loan and releases the funds. | Saving the record creates the loan as *Active* with the release date. |
| 4 | Interest may be deducted in advance. | The system computes **net proceeds** when an advance interest amount is entered. |

### 2.3 Assumptions and Constraints
- Designed for a small lending operation run by one person.
- One borrower may have multiple loans over time; the borrower record persists across loans.
- Interest rates, terms, and waiver thresholds are configurable.
- The system records and informs; it does not enforce policy on the lender.

---

## 3. Functional Requirements

### FR-1 Borrower Management
- **FR-1.1** Register a borrower with personal details (name, address, contact number, valid ID, source of income).
- **FR-1.2** Persist each borrower across multiple loans so payment history accumulates over time.
- **FR-1.3** Search, filter, view, edit, and archive borrower records.

### FR-2 Loan Recording (Combined Create Flow)
The lender records a borrower and their loan **in one screen**, without any separate application or approval step.

- **FR-2.1** Provide a single **Record Loan** screen that captures:
  - Borrower information (select existing or create new on the same screen)
  - Loan amount, interest rate, term
  - Co-maker information *or* a waiver reason (see FR-3)
  - Advance interest and any fees (if applicable)
  - Release date (defaults to today)
- **FR-2.2** Automatically compute and display the amortization schedule, total interest, and total repayable amount as the lender enters values.
- **FR-2.3** Compute **net proceeds** = loan amount − advance interest − fees, and display it clearly before saving.
- **FR-2.4** On save, create the loan record with status *Active* and store the release date.
- **FR-2.5** Allow the lender to edit a recorded loan's details (with an audit trail) and to void a loan recorded in error.

### FR-3 Co-maker Handling
- **FR-3.1** Prompt for co-maker details by default on the Record Loan screen.
- **FR-3.2** Capture co-maker fields (name, contact, relationship to borrower, source of income).
- **FR-3.3** Allow the lender to skip a co-maker by entering a **waiver reason**.
- **FR-3.4** Show an **advisory recommendation** indicating whether the borrower qualifies for a waiver based on BR-1. This is informational only — it does not prevent the lender from proceeding.

### FR-4 Credit Evaluation (Advisory)
- **FR-4.1** Rate the borrower's payment history as good / fair / poor based on past loans recorded in the system.
- **FR-4.2** Record an assessment of the borrower's financial capability as part of the loan record.
- **FR-4.3** Use FR-4.1 and FR-4.2 to produce the waiver recommendation in FR-3.4.

### FR-5 Repayment & Collection Tracking
- **FR-5.1** Record borrower payments with date, amount, and the updated balance.
- **FR-5.2** Update the outstanding balance and mark the loan *Paid* when fully settled.
- **FR-5.3** Track due dates and automatically flag overdue accounts.
- **FR-5.4** Classify overdue accounts into aging buckets (1–30, 31–60, 61–90, 90+ days).
- **FR-5.5** Update each borrower's payment history (used by FR-4.1).

### FR-6 Dashboard & Analytics  *(centerpiece of the system)*
The dashboard shall be the **default landing screen** after login and present a real-time visual snapshot of operations.

- **FR-6.1 Total Borrowers** — Total count of registered borrowers, with active-vs-inactive breakdown.
- **FR-6.2 Active Loans** — Number of active loans and aggregate outstanding principal.
- **FR-6.3 Paid vs Unpaid Loans** — Counts and proportions of paid versus unpaid loans (chart).
- **FR-6.4 Loan Collection Status** — Expected vs actual collections for the selected period, with a collection-rate percentage.
- **FR-6.5 Monthly Revenue & Interest Earnings** — Time-series chart of collected revenue and interest earned per month.
- **FR-6.6 Overdue Payments** — Total overdue count, total overdue amount, and aging breakdown.
- **FR-6.7 Borrower Payment History (Quick Access)** — Search any borrower from the dashboard and drill into their full payment history.
- **FR-6.8 Date Range Filter** — Global filter on time-based metrics (This Month, Last 3 Months, Year-to-Date, Custom).
- **FR-6.9 Drill-Down** — Clicking any card or chart segment opens the underlying list of loans, payments, or borrowers.
- **FR-6.10 Real-Time Refresh** — Dashboard values update whenever a new loan or payment is recorded.

### FR-7 Reports
- **FR-7.1** Lists of active, overdue, and fully paid loans.
- **FR-7.2** Per-borrower payment history report.
- **FR-7.3** Loan release report showing loan amount, advance interest, and net proceeds.
- **FR-7.4** Monthly revenue and interest earnings report.
- **FR-7.5** Export reports to printable or downloadable format (PDF or spreadsheet).

### FR-8 Authentication
- **FR-8.1** Single lender account secured by username and password.
- **FR-8.2** Allow the lender to change the password.
- **FR-8.3** Automatic session timeout after a period of inactivity.

---

## 4. Business Rules
| ID | Rule |
|----|------|
| **BR-1** | A co-maker is recommended for every loan, but may be **waived** when the borrower has both a **good payment history AND demonstrated financial capability**. The waiver is the lender's decision; the system does not block it. |
| **BR-2** | When advance interest is entered, the borrower receives the **net proceeds** (loan amount − advance interest − fees). |
| **BR-3** | A loan is automatically flagged **Overdue** when any installment is past its due date. |
| **BR-4** | A loan is automatically marked **Paid** once the outstanding balance reaches zero. |
| **BR-5** | Edits to a saved loan must be recorded with an audit trail (date and previous values). |

---

## 5. Data Requirements
| Entity | Key Fields |
|--------|-----------|
| Borrower | borrower_id, name, address, contact, valid_id, source_of_income, status |
| Co-maker | comaker_id, loan_id, name, contact, relationship, source_of_income |
| Loan | loan_id, borrower_id, comaker_id (nullable), waiver_reason (nullable), amount, interest_rate, term, advance_interest, fees, net_proceeds, release_date, status (*Active* / *Paid* / *Overdue*) |
| Payment | payment_id, loan_id, date_paid, amount_paid, balance, days_past_due |
| Evaluation Snapshot | loan_id, payment_history_rating, financial_capability, waiver_recommended |
| Collection Summary (view) | period, expected_amount, collected_amount, collection_rate, interest_earned |
| User | user_id, username, password_hash |

---

## 6. Non-Functional Requirements
- **NFR-1 Security** — Password stored hashed; session protected against unauthorized access.
- **NFR-2 Data Integrity** — Balances, net proceeds, aging, and status flags are system-computed and not manually editable.
- **NFR-3 Usability** — The lender should complete a full **Record Loan** action in a single screen with minimal navigation.
- **NFR-4 Reliability** — Data is preserved on unexpected shutdown; no duplicate records can be created in a single save.
- **NFR-5 Auditability** — Loan edits and voids record date and previous values.
- **NFR-6 Performance** — Dashboard loads within a few seconds for typical small-office data volumes.
- **NFR-7 Privacy** — Borrower and co-maker personal data is accessible only after authentication.
- **NFR-8 Visual Clarity** — Dashboard uses clear, distinguishable charts and color coding (e.g., overdue in red, paid in green) for at-a-glance comprehension.

---

## 7. Use Case Summary (Lender's View)
1. **Log In** — Lender authenticates and lands on the dashboard (FR-6, FR-8).
2. **Review Dashboard** — Lender reviews KPIs and overdue alerts at a glance (FR-6).
3. **Record Loan** — Lender enters borrower details, loan terms, co-maker (or waiver reason), and advance interest on a single screen; the system saves it as *Active* (FR-1, FR-2, FR-3, FR-4).
4. **Record Payment** — Lender logs each repayment; balance, status, and history update automatically (FR-5).
5. **View Borrower Payment History** — Lender opens a borrower's full payment record (FR-1, FR-5).
6. **Generate Report** — Lender exports operational or financial reports (FR-7).
