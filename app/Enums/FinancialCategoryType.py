from enum import Enum


class FinancialCategoryType(Enum):
    # ── Core Flow ──────────────────────────────
    INCOME = "income"  # salary, freelance, rental income
    EXPENSE = "expense"  # groceries, rent, subscriptions
    REFUND = "refund"  # any expense refund

    # ── Investment & Returns ───────────────────
    INVESTMENT = "investment"  # stocks, crypto, property bought
    RETURNS = "returns"  # gains from investments, business

    # ── Tax  ───────────────────────
    TAX = "tax"  # income tax, sales tax, VAT

    # ── Losses ─────────────────────────────────
    LOSS = "loss"  # stock dip, business loss
    LOSS_RECOVERY = "loss_recovery"  # money added to cover losses

    # ── Debt You OWE (Liabilities) ─────────────
    LOAN_RECEIVED = "loan_received"  # borrowed money (inflow, not income)
    LOAN_REPAYMENT = "loan_repayment"  # paying back borrowed money

    # ── Money OWED to You (Assets) ─────────────
    LOAN_GIVEN = "loan_given"  # money you lent out (outflow, not expense)
    LOAN_RECOVERY = "loan_recovery"  # money coming back to you

    # ── Transfers & Adjustments ────────────────
    # TRANSFER = "transfer"  # moving money between your own accounts ← NEW
    # SAVING = "saving"  # money set aside (not spent, not invested)

    # ── Miscellaneous ──────────────────────────
    OTHER = "other"
