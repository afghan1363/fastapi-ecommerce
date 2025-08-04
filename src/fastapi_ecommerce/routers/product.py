from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update
from slugify import slugify
from typing import Annotated

from backend.db_depends import get_db
from routers.user import get_current_user
from models.product import Product
from models.category import Category
from schemas.product import NewProduct


product_router = APIRouter(prefix='/products', tags=['products'])


@product_router.get('/')
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no one products")
    return products.all()


@product_router.get('/detail/{product_slug}')
async def get_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug,
                                              Product.is_active == True, Product.stock > 0))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There is no product "{product_slug}"')
    return product


@product_router.get('/{category_slug}')
async def get_products_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Категорія {category_slug} не знайдена')
    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))
    categories_and_subcategories = [category.id] + [c.id for c in subcategories.all()]
    products_category = await db.scalars(
        select(Product).where(Product.category_id.in_(categories_and_subcategories),
                                                      Product.is_active == True,
                                                      Product.stock > 0)
    )
    return products_category.all()


@product_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(get_user: Annotated[dict, Depends(get_current_user)],
                         db: Annotated[AsyncSession, Depends(get_db)], new_product: NewProduct):
    if not get_user.get("is_admin") and not get_user.get("is_supplier"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to use this method.")
    category = await db.scalar(select(Category).where(Category.id == new_product.category))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    await db.execute(insert(Product).values(
        name = new_product.name,
        description = new_product.description,
        price = new_product.price,
        image_url = new_product.image_url,
        stock = new_product.stock,
        category_id = new_product.category,
        rating = 0.0,
        slug = slugify(new_product.name),
        supplier_id = get_user.get("id")
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@product_router.put('/{product_slug}')
async def update_product(get_user: Annotated[dict, Depends(get_current_user)],
                         db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         product_updates: NewProduct):
    
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There is no product "{product_slug}"')
    elif not get_user.get("is_admin") and not get_user.get("id") == product.supplier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are don't have a permission to edit this product.")
    
    category = await db.scalar(select(Category).where(Category.id == product_updates.category))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    product.name = product_updates.name
    product.description = product_updates.description
    product.price = product_updates.price
    product.image_url = product_updates.image_url
    product.stock = product_updates.stock
    product.category = product_updates.category
    product.slug = slugify(product_updates.name)
    
    await db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Produt updated'}


@product_router.delete('/del/{product_slug}')
async def delete_product(get_user: Annotated[dict, Depends(get_current_user)],
                         db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Product "{product_slug}" not found')
    elif not get_user.get("is_admin") and not get_user.get("id") == product.supplier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are don't have a permission to edit this product.")
    product.is_active = False
    await db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Product deactivated.'}
