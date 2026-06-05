from datetime import date
from decimal import Decimal


def payment_history_rating(borrower):
    """
    Rate the borrower's past loans as 'good', 'fair', or 'poor' based on
    how many loans they've completed and whether any are currently overdue.
    Returns ('good'|'fair'|'poor'|'new', summary_text).
    """
    loans = list(borrower.loans.all())
    if not loans:
        return "new", "No prior loans on file."

    paid = sum(1 for l in loans if l.status == "PAID")
    overdue = sum(1 for l in loans if l.status == "OVERDUE")

    if overdue:
        return "poor", f"{overdue} loan(s) currently overdue."
    if paid >= 2:
        return "good", f"{paid} loan(s) fully repaid, no overdue."
    if paid == 1:
        return "fair", "One prior loan repaid."
    return "fair", "Has active loan(s) but no completed history yet."


def waiver_recommendation(borrower):
    rating, _ = payment_history_rating(borrower)
    if rating == "good":
        return "may_waive", "Good payment history — co-maker may be waived."
    if rating == "new":
        return "recommend", "New borrower — co-maker recommended."
    if rating == "poor":
        return "strongly_recommend", "Poor history — co-maker strongly recommended."
    return "recommend", "Co-maker recommended."
