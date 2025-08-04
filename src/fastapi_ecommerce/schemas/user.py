from pydantic import BaseModel, EmailStr



class NewUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
