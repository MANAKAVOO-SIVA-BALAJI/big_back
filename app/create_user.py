from .models import User
from sqlalchemy.orm import Session

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_or_update_user(db: Session, username: str, hashed_password: str):
    user = get_user_by_username(db, username)
    if user:
        user.password = hashed_password  # update password
    else:
        user = User(username=username, password=hashed_password)
        db.add(user)
    db.commit()
    db.refresh(user)
    return user

