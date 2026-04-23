from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Table, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Association tables
user_allergies = Table(
    "user_allergies",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("allergy_id", Integer, ForeignKey("allergies.allergy_id"), primary_key=True)
)

user_dislikes = Table(
    "user_dislikes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("ing_id", Integer, ForeignKey("ingredients.ing_id"), primary_key=True)
)

user_prefs_allergies = Table(
    "user_preferences_allergies",
    Base.metadata,
    Column("pref_id", Integer, ForeignKey("user_preferences.pref_id"), primary_key=True),
    Column("allergy_id", Integer, ForeignKey("allergies.allergy_id"), primary_key=True)
)

user_prefs_dislikes = Table(
    "user_preferences_dislikes",
    Base.metadata,
    Column("pref_id", Integer, ForeignKey("user_preferences.pref_id"), primary_key=True),
    Column("ing_id", Integer, ForeignKey("ingredients.ing_id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    age = Column(Integer)
    weight = Column(Numeric(5, 2))
    budget = Column(Numeric(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    reset_token = Column(String(100), nullable=True)
    reset_token_expiry = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    allergies = relationship("Allergy", secondary=user_allergies, backref="users")
    dislikes = relationship("Ingredient", secondary=user_dislikes, backref="users_who_dislike")
    preferences = relationship("UserPreferences", uselist=False, back_populates="user", cascade="all, delete-orphan")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    pref_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    diet_id = Column(Integer, ForeignKey("diets.diet_id"))
    servings = Column(Integer, nullable=False, default=1)
    budget = Column(Numeric(10, 2))
    
    user = relationship("User", back_populates="preferences")
    diet = relationship("Diet")
    allergies = relationship("Allergy", secondary=user_prefs_allergies, backref="preferences")
    dislikes = relationship("Ingredient", secondary=user_prefs_dislikes, backref="preferences_who_dislike")
