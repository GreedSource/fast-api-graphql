import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from fastapi import BackgroundTasks

from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


@singleton
class MailHelper:
    def __init__(self):
        self._initialized = False

    def init_app(self):
        if self._initialized:
            return

        self.mail_server = os.environ.get("MAIL_SERVER", "smtp.mailgun.org")
        self.mail_port = int(os.environ.get("MAIL_PORT", 587))
        self.mail_username = os.environ.get("MAIL_USERNAME")
        self.mail_password = os.environ.get("MAIL_PASSWORD")
        self.default_sender = os.environ.get("MAIL_DEFAULT_SENDER")

        self._initialized = True
        LoggerHelper.info("MailHelper initialized (FastAPI)")

    def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: Optional[str] = None,
        html: Optional[str] = None,
        sender: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> bool:
        if not self._initialized:
            raise CustomGraphQLExceptionHelper("MailHelper no está inicializado")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender or self.default_sender
        msg["To"] = ", ".join(recipients)
        msg.set_content(body or "")

        if html:
            msg.add_alternative(html, subtype="html")

        if background_tasks:
            background_tasks.add_task(self._send, msg)
            return True

        return self._send(msg)

    def _send(self, msg: EmailMessage) -> bool:
        try:
            with smtplib.SMTP(self.mail_server, self.mail_port) as server:
                server.starttls()
                server.login(self.mail_username, self.mail_password)
                server.send_message(msg)

            LoggerHelper.info(f"Correo enviado a {msg['To']} - {msg['Subject']}")
            return True

        except Exception as e:
            LoggerHelper.error(f"Error enviando correo: {e}")
            return False
