from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select #, update
from slugify import slugify
from typing import Annotated

from backend.db_depends import get_db
from schemas.category import NewCategory
from models.category import Category
from routers.user import get_current_user


category_router = APIRouter(prefix="/category", tags=['category'])


@category_router.get('/')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active==True))
    return categories.all()

@category_router.get('/{slug}')
async def get_category(db: Annotated[AsyncSession, Depends(get_db)], slug: str):
    category = await db.scalar(select(Category).where(Category.slug==slug, Category.is_active==True))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@category_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(get_user: Annotated[dict, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db)], create_category: NewCategory):
    
    if get_user.get("is_admin"):
        await db.execute(insert(Category).values(name=create_category.name,
                                        parent_id=create_category.parent_id,
                                        slug=slugify(create_category.name)))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permissions to do it, mazafaka"
        )


@category_router.put('/{slug}')
async def update_category(get_user: Annotated[dict, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db)], slug: str, category_updates: NewCategory):
    if not get_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permissions to do it, mazafaka"
        ) 
    category = await db.scalar(select(Category).where(Category.slug == slug, Category.is_active == True))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Категорію не знайдено")
    
    category.name = category_updates.name
    category.slug = slugify(category_updates.name)
    category.parent_id = category_updates.parent_id
    
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category updated.'
    }


@category_router.delete('/{slug}')
async def delete_category(get_user: Annotated[dict, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db)], slug: str):
    if not get_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Чухай ногу об дорогу")
    category = await db.scalar(select(Category).where(Category.slug==slug, Category.is_active==True))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no \"{slug}\" category found.")
    category.is_active = False
    # db.delete(category)
    await db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Category deactivated.'}
