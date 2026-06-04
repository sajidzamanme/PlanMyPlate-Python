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
            phone=obj_in.phone,
            date_of_birth=obj_in.dateOfBirth
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "firstName" in update_data:
            db_obj.first_name = update_data["firstName"]
        if "lastName" in update_data:
            db_obj.last_name = update_data["lastName"]
        if "phone" in update_data:
            db_obj.phone = update_data["phone"]
        if "dateOfBirth" in update_data:
            db_obj.date_of_birth = update_data["dateOfBirth"]
        if "age" in update_data:
            db_obj.age = update_data["age"]
        if "weight" in update_data:
            db_obj.weight = update_data["weight"]
        if "budget" in update_data:
            db_obj.budget = update_data["budget"]
            
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
