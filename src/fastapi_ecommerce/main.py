from fastapi import FastAPI

from routers.category import category_router
from routers.product import product_router
from routers.user import user_router
from routers.permission import permission_router
from routers.reviews import review_router


app = FastAPI()

@app.get('/')
async def welcome():
    return {'message': 'E-Commers application'}


app.include_router(router=permission_router)
app.include_router(router=user_router)
app.include_router(router=category_router)
app.include_router(router=product_router)
app.include_router(router=review_router)
