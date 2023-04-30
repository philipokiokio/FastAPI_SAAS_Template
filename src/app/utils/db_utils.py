from passlib.context import CryptContext
from src.app.database import SessionFactory
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Verify Password

    Args:
        hashed_password (str): Stored passwoed in the DB compared with the raw string
        plain_password (str): Raw string  to be compared.

    Returns:
        _type_: Bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hashes Password string

    Args:
        password (str): String

    Returns:
        str: Hashed string
    """
    return pwd_context.hash(password)



def get_db():
    db = SessionFactory()

    try:
        yield db
    except: 
        db.rollback()
        
    finally:
        db.close()