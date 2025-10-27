import bcrypt
import secrets
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from tinydb import TinyDB, Query
import base64


# Authentication decorator
def token_authenticator():
    def wrapper(func):
        def inner(request: Request, *args, **kwargs):
            # Authentication logic can be implemented here
            return func(*args, **kwargs)
        return inner
    return wrapper

def generate_auth_token() -> str:
    """
    Generate authentication token with an expiration date.

    :returns: A string containing the token.
    """
    token = secrets.token_urlsafe(64)
    return token

def hash_password(password: str) -> str:
    """
    Generate hashed password.

    :param password: The string to hash.
    :returns: The hashed password as bytes.
    """
    return base64.b64encode(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())).decode('utf-8')

def compare_hashed_password(password: str, hashed_password: str) -> bool:
    """
    Compare a password with a hashed password.

    :param password: The string password to compare.
    :param hashed_password: The hashed password to compare against.
    :returns: True if the password matches the hashed password, otherwise False.
    """
    return bcrypt.checkpw(password.encode("utf-8"), base64.b64decode(hashed_password))

def authenticate(password: str) -> bool:
    """
    Authenticate the user by comparing the provided password with the stored hash.

    :param password: The password to authenticate.
    :return: True if authentication is successful, False otherwise.
    """
    db = TinyDB('db.json')
    auth_table = db.table('auth')
    query = Query()

    # Retrieve the stored hashed password
    hashed_password = auth_table.get(query.hashed_password.exists())
    db.close()

    # Check if the stored password hash is found and is a Document
    if isinstance(hashed_password, dict) and not None:
        hashed_password = hashed_password['hashed_password']
        return compare_hashed_password(password, hashed_password)
    else:
        return False
