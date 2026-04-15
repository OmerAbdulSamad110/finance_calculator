from app.Core.Database import getAysncDbContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, case, extract
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.Models.RecurringFinancialEntry import RecurringFinancialEntry
from app.Models.FinancialEntry import FinancialEntry
from app.Enums.FinancialFrequency import FinancialRecurringFrequency
from app.Core.Logger import logger


async def generate_recurring_financial_entries():
    async with getAysncDbContext() as db:
        db: AsyncSession
        coursor_id = None
        today: datetime = datetime.now()
        while True:
            try:
                # Fetch all active recurring entries
                query = (
                    select(RecurringFinancialEntry)
                    .where(RecurringFinancialEntry.is_active == True)
                    .where(
                        extract("month", RecurringFinancialEntry.generate_at)
                        == today.month,
                        extract("year", RecurringFinancialEntry.generate_at)
                        == today.year,
                    )
                )
                if coursor_id is not None:
                    query = query.where(RecurringFinancialEntry.id > coursor_id)
                result = await db.execute(
                    query.order_by(RecurringFinancialEntry.id).limit(501)
                )
                entries = list(result.scalars().all())

                last_entry = entries.pop() if len(entries) == 501 else None
                if last_entry is not None:
                    coursor_id = last_entry.id

                financial_entries = []
                recurring_financial_enteries = {}
                for entry in entries:
                    # ✅ current_generate_at is what this entry is FOR
                    current_generate_at: datetime = entry.generate_at.replace(
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )
                    frequency = (
                        entry.frequency.value
                        if isinstance(entry.frequency, FinancialRecurringFrequency)
                        else entry.frequency
                    )
                    # Update the next generate_at based on frequency
                    if frequency == "daily":
                        next_generate_at = current_generate_at + timedelta(days=1)
                    elif frequency == "weekly":
                        next_generate_at = current_generate_at + timedelta(weeks=1)
                    elif frequency == "monthly":
                        next_generate_at = current_generate_at + relativedelta(months=1)
                    elif frequency == "quarterly":
                        next_generate_at = current_generate_at + relativedelta(months=3)
                    elif frequency == "annually":
                        next_generate_at = current_generate_at + relativedelta(years=1)
                    else:
                        next_generate_at = entry.generate_at

                    title = __format_template(entry.title, current_generate_at)
                    description = __format_template(
                        entry.description, current_generate_at
                    )
                    financial_entries.append(
                        {
                            "title": title,
                            "amount": entry.amount,
                            "description": description,
                            "entered_at": current_generate_at,
                            "frequency": frequency,
                            "client_id": entry.client_id,
                            "financial_category_id": entry.financial_category_id,
                            "recurring_financial_entry_id": entry.id,
                        }
                    )
                    recurring_financial_enteries[entry.id] = next_generate_at
                if len(financial_entries) > 0:
                    await db.execute(
                        insert(FinancialEntry.__table__), financial_entries
                    )
                    stmt = (
                        update(RecurringFinancialEntry)
                        .where(
                            RecurringFinancialEntry.id.in_(
                                recurring_financial_enteries.keys()
                            )
                        )
                        .values(
                            generate_at=case(
                                recurring_financial_enteries,
                                value=RecurringFinancialEntry.id,
                            )
                        )
                    )
                    await db.execute(stmt)
                    await db.commit()
            except Exception as e:
                logger.error(e.__str__())
                await db.rollback()
                raise e
            if last_entry is None:
                break


def __format_template(template: str, dt: datetime) -> str:
    previous_dt = dt - timedelta(days=1)
    replacements = {
        "{month}": dt.strftime("%B"),
        "{previous_month}": (dt - relativedelta(months=1)).strftime("%B"),
        "{year}": str(dt.year),
        "{previous_year}": str(dt.year - 1),
        "{day}": str(dt.day),
        "{previous_day}": str(previous_dt.day),
        "{date}": dt.strftime("%d-%m-%Y"),
        "{previous_date}": previous_dt.strftime("%d-%m-%Y"),
        "{time}": dt.strftime("%I:%M %p"),
        "{datetime}": dt.strftime("%d-%m-%Y %I:%M %p"),
        "{previous_datetime}": previous_dt.strftime("%d-%m-%Y %I:%M %p"),
        "{dateMonth}": dt.strftime("%d %B"),
        "{previous_dateMonth}": previous_dt.strftime("%d %B"),
        "{daymonth}": dt.strftime("%A %B"),
        "{previous_daymonth}": previous_dt.strftime("%A %B"),
        "{monthyear}": dt.strftime("%B %Y"),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return template
