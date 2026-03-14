from abc import ABC, abstractmethod
from fastapi_mail import MessageSchema
from pathlib import Path

TEMPLATE_DIR = Path("views/mail/templates")


class BaseMail(ABC):

    def __init__(self):
        self.recipients = []
        self.cc = []
        self.bcc = []
        self._body = ""
        self._template_body = {}
        self.subject = ""
        self.template = None  # 👈 must be here
        self.subtype = "html"  # 👈 must be here

    def to(self, recipients: str | list[str]) -> "BaseMail":
        # also handle single string vs list
        self.recipients = [recipients] if isinstance(recipients, str) else recipients
        return self

    def cc_to(self, cc: list[str]) -> "BaseMail":
        self.cc = cc
        return self

    def bcc_to(self, bcc: list[str]) -> "BaseMail":
        self.bcc = bcc
        return self

    def with_subject(self, subject: str) -> "BaseMail":
        self.subject = subject
        return self

    def with_body(self, body: str) -> "BaseMail":
        self._body = body
        return self

    def with_template(self, template: str, data: dict = {}) -> "BaseMail":
        self.template = template
        self._template_body = data
        return self

    def as_html(self) -> "BaseMail":
        self.subtype = "html"
        return self

    def as_text(self) -> "BaseMail":
        self.subtype = "plain"
        return self

    @abstractmethod
    def build(self) -> "BaseMail":
        pass

    def to_message(self) -> tuple[MessageSchema, str | None]:
        self.build()

        use_template = self.template and TEMPLATE_DIR.exists()

        message = MessageSchema(
            subject=self.subject,
            recipients=self.recipients,
            cc=self.cc,
            bcc=self.bcc,
            body=self._body if not use_template else None,
            template_body=self._template_body if use_template else None,
            subtype=self.subtype,
        )
        return message, self.template if use_template else None
