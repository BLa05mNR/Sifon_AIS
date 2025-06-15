import uvicorn
from fastapi import FastAPI
from routers import auth, routers

app = FastAPI()
app.include_router(auth.router)
app.include_router(routers.customer_router)
app.include_router(routers.employee_router)
app.include_router(routers.supplier_router)
app.include_router(routers.product_category_router)
app.include_router(routers.product_router)
app.include_router(routers.order_router)
app.include_router(routers.order_detail_router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000)