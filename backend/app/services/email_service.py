import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger("auther.email")


class EmailService:
    def send_invite(self, to_email: str, link: str) -> None:
        self._send(
            to_email,
            "Defina sua senha no Auther",
            f"Use o link para definir sua senha:\n\n{link}\n",
        )

    def send_reset(self, to_email: str, link: str) -> None:
        self._send(
            to_email,
            "Redefina sua senha no Auther",
            f"Use o link para definir uma nova senha:\n\n{link}\n",
        )

    def send_verification(self, to_email: str, link: str) -> None:
        self._send(
            to_email,
            "Confirme seu e-mail no Auther",
            f"Use o link para confirmar seu e-mail:\n\n{link}\n",
        )

    def _send(self, to_email: str, subject: str, body: str) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_FROM:
            logger.error("SMTP não configurado")
            raise AppError(503, "Envio de e-mail não configurado")
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message.set_content(body)
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                smtp.starttls()
                if settings.SMTP_USER:
                    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.send_message(message)
        except AppError:
            raise
        except Exception:
            logger.exception("falha no envio de e-mail")
            raise AppError(503, "Não foi possível enviar o e-mail") from None
        logger.info("e-mail enviado")
