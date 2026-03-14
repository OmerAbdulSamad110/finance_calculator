from .BaseMail import BaseMail
from bootstrap.config import config


class ForgetPasswordMail(BaseMail):
    def __init__(self, token: str):
        super().__init__()
        self.link = config("frontend_url") + "/reset-password?token=" + token

    def build(self) -> "ForgetPasswordMail":
        return (
            self.with_subject("Forget Password Reset Link")
            .with_body(
                f"<p>Press the link below to reset your password:</p><p><a href='{self.link}'>Reset Password</a></p>"
            )
            .as_html()
        )
