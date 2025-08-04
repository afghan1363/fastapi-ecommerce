from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy import Integer, Float, String, Boolean, ForeignKey, DateTime, CheckConstraint
from datetime import datetime
from typing import List

from backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'
    # __table_args__ = (CheckConstraint("grade > 0 and grade <= 5"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(String)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    grade: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="reviews", uselist=False)

    @validates('grade')
    def validate_grade(self, key, value):
        if not 0 < value <= 5:
            raise ValueError(f'Invalid grade {value}. Must be between 1 and 5')
        return value
