# import sys 
# sys.path.append('fastapi_ecommerce')  # Добавляем родительский каталог в путь поиска модулей
from typing import List 
 
from backend.db import Base
from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
# from models.product import Product
# from src.fastapi_ecommerce.backend.db import Base



class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}

    # id = Column(Integer, primary_key=True, index=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # name = Column(String)
    name: Mapped[str] = mapped_column(String(100))
    # slug = Column(String, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    # is_active = Column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    products: Mapped[List['Product']] = relationship(back_populates='category', uselist=True)
