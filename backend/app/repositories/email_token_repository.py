from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import utcnow
from app.models.email_token import EmailToken


class EmailTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def revoke_open(self, person_id: int, purpose: str) -> None:
        rows = (
            self.db.query(EmailToken)
            .filter(
                EmailToken.person_id == person_id,
                EmailToken.purpose == purpose,
                EmailToken.consumed.is_(False),
            )
            .all()
        )
        for row in rows:
            row.consumed = True
            self.db.add(row)
        self.db.flush()

    def create(
        self,
        *,
        person_id: int,
        purpose: str,
        token_hash: str,
        expires_at: datetime,
    ) -> EmailToken:
        self.revoke_open(person_id, purpose)
        row = EmailToken(
            person_id=person_id,
            purpose=purpose,
            token_hash=token_hash,
            expires_at=expires_at,
            consumed=False,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_valid(self, token_hash: str, purpose: str) -> EmailToken | None:
        row = (
            self.db.query(EmailToken)
            .filter(EmailToken.token_hash == token_hash, EmailToken.purpose == purpose)
            .one_or_none()
        )
        if row is None or row.consumed or row.expires_at <= utcnow():
            return None
        return row

    def consume(self, row: EmailToken) -> None:
        row.consumed = True
        self.db.add(row)
        self.db.flush()
