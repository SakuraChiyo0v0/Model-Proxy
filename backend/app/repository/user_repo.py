from sqlalchemy.orm import Session

from app.models.user import UserModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def create(self, username: str, password: str) -> UserModel:
        obj = UserModel(
            username=username,
            password_hash=pwd_context.hash(password),
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
