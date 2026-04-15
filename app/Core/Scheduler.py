from contextlib import contextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.Console.Commands.FinancialRecurringGenerator import (
    generate_recurring_financial_entries,
)

scheduler = AsyncIOScheduler()


def __register_schedulers():
    scheduler.add_job(
        generate_recurring_financial_entries, CronTrigger(hour=0, minute=0)
    )


@contextmanager
def setupScheduler():
    __register_schedulers()
    scheduler.start()
    yield
    scheduler.shutdown()
