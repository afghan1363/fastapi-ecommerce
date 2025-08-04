from backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Product(Base):
    __tablename__ = 'products'
    # id = Column(Integer, primary_key=True, index=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # name = Column(String)
    name: Mapped[str] = mapped_column(String(100))
    # slug = Column(String, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    # description = Column(String)
    description: Mapped[str] = mapped_column(String)
    # price = Column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    # image_url = Column(String)
    image_url: Mapped[str] = mapped_column(String)
    # stock = Column(Integer)
    stock: Mapped[int] = mapped_column(Integer)
    # rating = Column(Float)
    rating: Mapped[float] = mapped_column(Float)
    # is_active = Column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)

    # category_id = Column(Integer, ForeignKey('categories.id'))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))
    category: Mapped["Category"] = relationship(back_populates='products', uselist=False)

    reviews: Mapped[list['Review']] = relationship(back_populates='product', uselist=True)
