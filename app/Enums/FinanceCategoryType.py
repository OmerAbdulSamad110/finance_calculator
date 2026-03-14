from enum import Enum


class FinanceCategoryType(Enum):
    # ── Core Flow ──────────────────────────────
    INCOME = "income"  # salary, freelance, rental income
    EXPENSE = "expense"  # groceries, rent, subscriptions

    # ── Investment & Returns ───────────────────
    INVESTMENT = "investment"  # stocks, crypto, property bought
    PROFIT = "profit"  # gains from investments, business
    LOSS = "loss"  # stock dip, business loss
    DIVIDEND = "dividend"  # periodic return on investment ← NEW

    # ── Tax & Government ───────────────────────
    TAX = "tax"  # income tax, sales tax, VAT
    FINE = "fine"  # traffic fines, penalties ← NEW

    # ── Debt You OWE (Liabilities) ─────────────
    LIABILITY = "liability"  # new debt created (installment plan, loan taken)
    INSTALLMENT = "installment"  # recurring payment toward a liability ← NEW
    LOAN_RECEIVED = "loan_received"  # borrowed money (inflow, not income) ← NEW
    LOAN_REPAYMENT = "loan_repayment"  # paying back borrowed money ← NEW
    INTEREST_EXPENSE = "interest_expense"  # interest you pay on loans ← NEW

    # ── Money OWED to You (Assets) ─────────────
    LOAN_GIVEN = "loan_given"  # money you lent out (outflow, not expense) ← NEW
    LOAN_RECOVERY = "loan_recovery"  # money coming back to you ← NEW
    INTEREST_INCOME = "interest_income"  # interest you earn from loans ← NEW

    # ── Fees ───────────────────────────────────
    FEE = "fee"  # bank fees, service charges, late fees ← NEW
    SUBSCRIPTION = (
        "subscription"  # recurring service fees (could be EXPENSE subtype) ← NEW
    )

    # ── Transfers & Adjustments ────────────────
    TRANSFER = "transfer"  # moving money between your own accounts ← NEW
    REFUND = "refund"  # money returned to you ← NEW
    SAVING = "saving"  # money set aside (not spent, not invested)

    # ── Miscellaneous ──────────────────────────
    OTHER = "other"
