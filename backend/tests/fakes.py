from types import SimpleNamespace

from app.core.security import utcnow
from app.models.person import Person


class MemoryPeople:
    def __init__(self) -> None:
        self.rows: dict[int, Person] = {}
        self.seq = 1

    def save(self, person: Person) -> Person:
        if person.id is None:
            person.id = self.seq
            self.seq += 1
        self.rows[int(person.id)] = person
        return person

    def get_by_id(self, person_id: int) -> Person | None:
        return self.rows.get(person_id)

    def get_by_cpf(self, cpf: str) -> Person | None:
        return next((person for person in self.rows.values() if person.cpf == cpf), None)

    def get_by_email(self, email: str) -> Person | None:
        return next((person for person in self.rows.values() if person.email == email), None)

    def count_platform_admins(self) -> int:
        return sum(1 for person in self.rows.values() if person.is_platform_admin)

    def delete(self, person: Person) -> None:
        self.rows.pop(int(person.id), None)

    def list_people(self, *, cpf, email, page, limit):
        rows = list(self.rows.values())
        if cpf:
            rows = [person for person in rows if person.cpf == cpf]
        if email:
            rows = [person for person in rows if person.email == email]
        rows.sort(key=lambda person: person.id, reverse=True)
        total = len(rows)
        start = (page - 1) * limit
        return rows[start : start + limit], total


class MemoryRefresh:
    def __init__(self) -> None:
        self.rows: list[SimpleNamespace] = []

    def save(self, *, person_id, token_hash, expires_at, auth_version):
        row = SimpleNamespace(
            person_id=person_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
            auth_version=auth_version,
        )
        self.rows.append(row)
        return row

    def get_by_hash(self, token_hash: str):
        return next((row for row in self.rows if row.token_hash == token_hash), None)

    def revoke(self, row) -> None:
        row.revoked = True

    def revoke_all(self, person_id: int) -> None:
        for row in self.rows:
            if row.person_id == person_id:
                row.revoked = True


class MemoryTokens:
    def __init__(self) -> None:
        self.rows: list[SimpleNamespace] = []

    def revoke_open(self, person_id: int, purpose: str) -> None:
        for row in self.rows:
            if row.person_id == person_id and row.purpose == purpose and not row.consumed:
                row.consumed = True

    def create(self, *, person_id, purpose, token_hash, expires_at):
        self.revoke_open(person_id, purpose)
        row = SimpleNamespace(
            person_id=person_id,
            purpose=purpose,
            token_hash=token_hash,
            expires_at=expires_at,
            consumed=False,
        )
        self.rows.append(row)
        return row

    def get_valid(self, token_hash: str, purpose: str):
        now = utcnow()
        for row in self.rows:
            if row.token_hash == token_hash and row.purpose == purpose and not row.consumed and row.expires_at > now:
                return row
        return None

    def consume(self, row) -> None:
        row.consumed = True


class MemoryEmail:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send_invite(self, to_email: str, link: str) -> None:
        self.sent.append(("invite", to_email, link))

    def send_reset(self, to_email: str, link: str) -> None:
        self.sent.append(("reset", to_email, link))

    def send_verification(self, to_email: str, link: str) -> None:
        self.sent.append(("verify", to_email, link))
