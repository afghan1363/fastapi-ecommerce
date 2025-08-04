from pydantic import BaseModel



class NewProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int
