from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            first_name=obj_in.firstName,
            last_name=obj_in.lastName,
            user_name=obj_in.userName or f"{obj_in.firstName}_{obj_in.lastName}".lower(),
            phone=obj_in.phone,
            date_of_birth=obj_in.dateOfBirth
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by email or phone number."""
        # Try email first
        user = self.get_by_email(db, email=identifier)
        if not user:
            # Try phone
            user = self.get_by_phone(db, phone=identifier)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

user = CRUDUser(User)
