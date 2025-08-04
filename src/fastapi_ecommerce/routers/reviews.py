from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from typing import Annotated

from backend.db_depends import get_db
from routers.user import get_current_user
from models.review import Review
from models.product import Product
from schemas.reviews import NewReview, UpdateReview



review_router = APIRouter(prefix="/reviews", tags=["reviews"])


@review_router.get("/")
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    # print(f'reviews = {reviews}')
    # if not list(reviews):
    #     return {
    #         "message": "No one has left a review yet"
    #     }
    return reviews.all()



@review_router.get("/{product_slug}")
async def get_product_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The is no product {product_slug}.")
    reviews = await db.scalars(select(Review).where(Review.product_id == product.id, Review.is_active == True))
    # if len(reviews._allrows()) == 0:
    #     return {
    #         "message": "No one has left a review yet"
    #     }
    # print(len(reviews._allrows()))
    return reviews.all()



@review_router.get("/{product_slug}/{review_id}")
async def retrieve_review(db: Annotated[AsyncSession, Depends(get_db)],
                          product_slug: str,
                          review_id: int):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no product {product_slug}.")
    review = await db.scalar(select(Review).where(Review.id == review_id, Review.is_active == True))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The product have no this review")
    return review



@review_router.post("/{product_slug}")
async def post_review(get_user: Annotated[dict, Depends(get_current_user)],
                      db: Annotated[AsyncSession, Depends(get_db)],
                      product_slug: str,
                      new_review: NewReview):
    # if not get_user:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only authorized users!")
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no product {product_slug}.")
    if get_user.get("id") == product.supplier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="The supplier can't leave a review for the product")
    # grades = ...
    await db.execute(insert(Review).values(
        product_id = product.id,
        comment = new_review.comment,
        grade = new_review.grade,
        user_id = get_user.get("id")        
    ))

    if product.rating:
        grades = await db.scalars(select(Review.grade).where(Review.product_id == product.id,
                                                             Review.is_active == True))
        grades_list = tuple(grades)
        round_avg = round(sum(grades_list) / len(grades_list), 2)
        product.rating = round_avg
    else:
        product.rating = new_review.grade
    await db.commit()
    return {
        "status": status.HTTP_201_CREATED,
        "trasaction": "Successful"
    }



@review_router.put("/{product_slug}/{review_id}")
async def update_review(get_user: Annotated[dict, Depends(get_current_user)],
                        db: Annotated[AsyncSession, Depends(get_db)],
                        upd_review: UpdateReview,
                        product_slug: str,
                        review_id: int):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no product {product_slug}.")
    if get_user.get("id") == product.supplier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="The supplier can't edit a review for the his product")
    review = await db.scalar(select(Review).where(Review.id == review_id, Review.product_id == product.id))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The product {product_slug} no have this review.")
    if not get_user.get("is_admin") and get_user.get("id") != review.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not author of it review.")
    if upd_review.comment is not None:
        review.comment = upd_review.comment
    if upd_review.grade:
        review.grade = upd_review.grade
    get_grades = await db.scalars(select(Review.grade).where(Review.product_id == product.id,
                                                         Review.is_active == True))
    grades = tuple(get_grades)
    round_avg = round(sum(grades) / len(grades), 2)
    product.rating = round_avg
    await db.commit()
    return review




@review_router.delete("/{product_slug}/{review_id}")
async def delete_review(get_user: Annotated[dict, Depends(get_current_user)],
                        db: Annotated[AsyncSession, Depends(get_db)],
                        product_slug: str,
                        review_id: int):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no product {product_slug}.")
    review = await db.scalar(select(Review).where(Review.id == review_id, Review.is_active == True))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The product {product_slug} no have this review.")
    if not get_user.get("is_admin") and review.user_id != get_user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not author of it review.")
    review.is_active = False
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Deactivated"
    }
