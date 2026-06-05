from typing import Optional, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get(self, db: Session, id: Any) -> Optional[User]:
        user = db.get(self.model, id)
        if user and user.is_deleted:
            return None
        return user

    def remove(self, db: Session, *, id: int) -> Optional[User]:
        user = db.get(self.model, id)
        if user:
            user.is_deleted = True
            
            # Prevent VARCHAR(150) overflow for email
            email_suffix = f"_deleted_{user.user_id}"
            max_email_len = 150 - len(email_suffix)
            user.email = f"{user.email[:max_email_len]}{email_suffix}"
            
            # Prevent VARCHAR(20) overflow for phone
            phone_suffix = f"_deleted_{user.user_id}"
            max_phone_len = 20 - len(phone_suffix)
            user.phone = f"{user.phone[:max_phone_len]}{phone_suffix}"
            
            db.add(user)
            db.commit()
        return user

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.is_deleted == False).first()

    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone, User.is_deleted == False).first()

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
        
        # Auto-create inventory for the user
        from app.models.inventory import Inventory
        from datetime import date
        inventory = Inventory(user_id=db_obj.user_id, last_update=date.today())
        db.add(inventory)
        db.commit()
        
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
