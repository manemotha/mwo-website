from pydantic import BaseModel

class PasswordAuthModel(BaseModel):
    password: str

class UpdatePasswordModel(BaseModel):
    old_password: str
    new_password: str
