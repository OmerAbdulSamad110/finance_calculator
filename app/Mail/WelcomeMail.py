from .BaseMail import BaseMail


class WelcomeMail(BaseMail):
    def build(self) -> "WelcomeMail":
        return (
            self.with_subject("Welcome to our app")
            .with_body("Welcome to our app")
            .as_html()
        )
