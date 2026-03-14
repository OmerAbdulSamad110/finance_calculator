from fastapi import FastAPI
from bootstrap.config import config
from fastapi_mail import FastMail, ConnectionConfig
from functools import lru_cache
from starlette.background import BackgroundTasks
from app.Mail.BaseMail import BaseMail


class Mailer:
    def __init__(self):
        self._fm: FastMail = None  # lazy init

    @lru_cache()
    def getMailConfig(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=config("mail_username"),
            MAIL_PASSWORD=config("mail_password"),
            MAIL_FROM=config("mail_from"),
            MAIL_FROM_NAME=config("app_name"),
            MAIL_PORT=int(config("mail_port")),
            MAIL_SERVER=config("mail_host"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )

    def initMailer(self, app: FastAPI) -> FastAPI:
        self._fm = FastMail(self.getMailConfig())
        app.state.mailer = self
        return app

    async def send(self, mailable: BaseMail):
        message, template = mailable.to_message()
        await self._fm.send_message(message, template_name=template)

    def queue(self, mailable: BaseMail, background_tasks: BackgroundTasks):
        message, template = mailable.to_message()
        background_tasks.add_task(
            self._fm.send_message, message, template_name=template
        )


mailer = Mailer()


def setupMailer(app: FastAPI):
    mailer.initMailer(app)
