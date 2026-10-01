from sqlalchemy.orm import Session

from app.models.person import Person


class PersonRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, person_id: int) -> Person | None:
        return self.db.query(Person).filter(Person.id == person_id).one_or_none()

    def get_by_cpf(self, cpf: str) -> Person | None:
        return self.db.query(Person).filter(Person.cpf == cpf).one_or_none()

    def get_by_email(self, email: str) -> Person | None:
        return self.db.query(Person).filter(Person.email == email).one_or_none()

    def count_platform_admins(self) -> int:
        return self.db.query(Person).filter(Person.is_platform_admin.is_(True)).count()

    def list_people(
        self,
        *,
        cpf: str | None,
        email: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[Person], int]:
        query = self.db.query(Person)
        if cpf:
            query = query.filter(Person.cpf == cpf)
        if email:
            query = query.filter(Person.email == email)
        total = query.count()
        items = (
            query.order_by(Person.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return items, total

    def save(self, person: Person) -> Person:
        self.db.add(person)
        self.db.flush()
        return person

    def delete(self, person: Person) -> None:
        self.db.delete(person)
        self.db.flush()
