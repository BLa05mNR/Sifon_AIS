import datetime
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.dependencies import require_role
from core.models import Product, Order, OrderDetail, StockOperation, Sale, FinancialReport, ProductCategory, Supplier, \
    Employee, Customer
from schemas import (
    ProductCreate, ProductOut,
    OrderCreate, OrderOut,
    OrderDetailCreate, OrderDetailOut,
    ProductCategoryOut, ProductCategoryCreate, ProductCategoryUpdate, SupplierCreate, SupplierOut, EmployeeCreate,
    EmployeeOut, CustomerCreate, CustomerOut, SupplierBase, OrderDetailSupplierOut
)
from core.database import get_db
from core.security import TokenData, hash_password

# -------------------- CUSTOMERS --------------------
customer_router = APIRouter(prefix="/customers", tags=["Customers"])

@customer_router.get("/", response_model=list[CustomerOut])
async def get_customers(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Customer))
    return result.scalars().all()

@customer_router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Покупатель не найден")
    return customer

@customer_router.post("/", response_model=CustomerOut, status_code=201)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    new_customer = Customer(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

@customer_router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: int,
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Покупатель не найден")

    for key, value in data.dict().items():
        if key == "password":
            setattr(customer, "password_hash", hash_password(value))
        elif key != "username":
            setattr(customer, key, value)

    await db.commit()
    await db.refresh(customer)
    return customer

@customer_router.patch("/{customer_id}/password")
async def change_customer_password(
    customer_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Покупатель не найден")
    customer.password_hash = hash_password(new_password)
    await db.commit()
    return {"detail": "Пароль обновлен"}

@customer_router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Покупатель не найден")
    await db.delete(customer)
    await db.commit()
    return {"detail": "Покупатель удален"}

# -------------------- EMPLOYEES --------------------
employee_router = APIRouter(prefix="/employees", tags=["Employees"])

@employee_router.get("/", response_model=list[EmployeeOut])
async def get_employees(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Employee))
    return result.scalars().all()

@employee_router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee

@employee_router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    new_employee = Employee(
        full_name=data.full_name,
        phone=data.phone,
        position=data.position,
        hire_date=data.hire_date,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)
    return new_employee

@employee_router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee(
    employee_id: int,
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    for key, value in data.dict().items():
        if key == "password":
            setattr(employee, "password_hash", hash_password(value))
        elif key != "username":
            setattr(employee, key, value)

    await db.commit()
    await db.refresh(employee)
    return employee

@employee_router.patch("/{employee_id}/password")
async def change_employee_password(
    employee_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    employee.password_hash = hash_password(new_password)
    await db.commit()
    return {"detail": "Пароль обновлен"}

@employee_router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    await db.delete(employee)
    await db.commit()
    return {"detail": "Сотрудник удален"}

# -------------------- SUPPLIERS --------------------
supplier_router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@supplier_router.get("/", response_model=list[SupplierOut])
async def get_suppliers(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Supplier))
    return result.scalars().all()

@supplier_router.get("/{supplier_id}", response_model=SupplierOut)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return supplier

@supplier_router.post("/", response_model=SupplierOut, status_code=201)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    new_supplier = Supplier(
        name=data.name,
        contact_person=data.contact_person,
        phone=data.phone,
        email=data.email,
        address=data.address,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(new_supplier)
    await db.commit()
    await db.refresh(new_supplier)
    return new_supplier

@supplier_router.put("/{supplier_id}", response_model=SupplierOut)
async def update_supplier(
    supplier_id: int,
    data: SupplierBase,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    # Обновляем все поля, кроме пароля и username
    for key, value in data.dict().items():
        if key not in ["password", "username"]:
            setattr(supplier, key, value)

    await db.commit()
    await db.refresh(supplier)
    return supplier

@supplier_router.patch("/{supplier_id}/password")
async def change_supplier_password(
    supplier_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    supplier.password_hash = hash_password(new_password)
    await db.commit()
    return {"detail": "Пароль обновлен"}

@supplier_router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    await db.delete(supplier)
    await db.commit()
    return {"detail": "Поставщик удален"}

# -------------------- PRODUCT CATEGORY --------------------
product_category_router = APIRouter(prefix="/product-categories", tags=["Product Categories"])

@product_category_router.get("/", response_model=list[ProductCategoryOut])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["admin"]))
):
    result = await db.execute(select(ProductCategory))
    return result.scalars().all()

@product_category_router.get("/{category_id}", response_model=ProductCategoryOut)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category

@product_category_router.get("/{category_id}/children", response_model=list[ProductCategoryOut])
async def get_child_categories(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.parent_id == category_id))
    return result.scalars().all()

@product_category_router.post("/", response_model=ProductCategoryOut, status_code=201)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    if data.parent_id:
        parent_result = await db.execute(select(ProductCategory).where(ProductCategory.id == data.parent_id))
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Родительская категория не существует")

    new_category = ProductCategory(**data.dict())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

@product_category_router.put("/{category_id}", response_model=ProductCategoryOut)
async def update_category(
    category_id: int,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if data.parent_id == category_id:
        raise HTTPException(status_code=400, detail="Категория не может быть родителем самой себя")

    if data.parent_id:
        parent_result = await db.execute(select(ProductCategory).where(ProductCategory.id == data.parent_id))
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Родительская категория не существует")

    for key, value in data.dict().items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)
    return category

@product_category_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    children_result = await db.execute(select(ProductCategory).where(ProductCategory.parent_id == category_id))
    if children_result.scalars().first():
        raise HTTPException(status_code=400, detail="Нельзя удалить категорию с дочерними элементами")

    products_result = await db.execute(select(Product).where(Product.category_id == category_id))
    if products_result.scalars().first():
        raise HTTPException(status_code=400, detail="Нельзя удалить категорию с привязанными товарами")

    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    await db.delete(category)
    await db.commit()
    return {"detail": "Категория удалена"}

# -------------------- PRODUCT --------------------
product_router = APIRouter(prefix="/products", tags=["Products"])

@product_router.get("/", response_model=list[ProductOut])
async def get_products(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["admin", "supplier", "customer"]))
    ):
    result = await db.execute(select(Product))
    return result.scalars().all()

@product_router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product

@product_router.get("/supplier/{supplier_id}", response_model=list[ProductOut])
async def get_products_by_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["admin", "supplier", "customer"]))
):
    # Проверяем, существует ли поставщик
    supplier_result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = supplier_result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    # Получаем все товары, связанные с данным поставщиком
    result = await db.execute(select(Product).where(Product.supplier_id == supplier_id))
    products = result.scalars().all()

    if not products:
        raise HTTPException(status_code=404, detail="Товары для поставщика не найдены")

    return products


@product_router.post("/", response_model=ProductOut, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    new_product = Product(**data.dict())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@product_router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    for key, value in data.dict().items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

@product_router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    await db.delete(product)
    await db.commit()
    return {"detail": "Продукт удален"}

# -------------------- ORDER --------------------
order_router = APIRouter(prefix="/orders", tags=["Orders"])

@order_router.get("/", response_model=list[OrderOut])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["customer", "admin"]))
):
    result = await db.execute(select(Order))
    return result.scalars().all()

@order_router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("customer"))
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order

@order_router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["admin", "supplier", "customer"]))
):
    new_order = Order(**data.dict())
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

@order_router.put("/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: int,
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    for key, value in data.dict().items():
        setattr(order, key, value)

    await db.commit()
    await db.refresh(order)
    return order

@order_router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    await db.delete(order)
    await db.commit()
    return {"detail": "Заказ удален"}

@order_router.get("/customer/{customer_id}", response_model=list[OrderOut])
async def get_orders_by_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("customer"))
):
    result = await db.execute(select(Order).where(Order.customer_id == customer_id))
    orders = result.scalars().all()
    if not orders:
        raise HTTPException(status_code=404, detail="Заказы для покупателя не найдены")
    return orders

@order_router.get("/recent", response_model=list[OrderOut])
async def get_recent_orders(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role(["admin"]))
):
    # Вычисляем дату 3 дня назад
    three_days_ago = datetime.now() - timedelta(days=3)

    # Запрашиваем заказы, которые были созданы за последние 3 дня
    result = await db.execute(
        select(Order).where(Order.order_date >= three_days_ago)
    )
    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=404, detail="Заказы за последние 3 дня не найдены")

    return orders

# -------------------- ORDER DETAIL --------------------
order_detail_router = APIRouter(prefix="/order-details", tags=["Order Details"])

@order_detail_router.get("/", response_model=list[OrderDetailOut])
async def get_order_details(
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    try:
        # Запрос с join для получения информации о товаре
        result = await db.execute(
            select(
                OrderDetail,
                Order.order_date,
                Product.name.label("product_name")
            )
            .join(Order, OrderDetail.order_id == Order.id)
            .join(Product, OrderDetail.product_id == Product.id)
        )
        order_details = result.all()

        # Формируем ответ с включением названия товара
        return [
            {
                "id": detail.OrderDetail.id,
                "order_id": detail.OrderDetail.order_id,
                "product_id": detail.OrderDetail.product_id,
                "product_name": detail.product_name,
                "quantity": detail.OrderDetail.quantity,
                "price_per_unit": detail.OrderDetail.price_per_unit,
                "order_date": detail.order_date
            }
            for detail in order_details
        ]
    except Exception as e:
        print(f"Error fetching order details: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@order_detail_router.get("/{order_detail_id}", response_model=OrderDetailOut)
async def get_order_detail(
        order_detail_id: int,
        db: AsyncSession = Depends(get_db),
        _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(
        select(
            OrderDetail,
            Product.name.label("product_name"),
            Order.order_date
        )
        .join(Product, OrderDetail.product_id == Product.id)
        .join(Order, OrderDetail.order_id == Order.id)
        .where(OrderDetail.id == order_detail_id)
    )

    detail = result.first()
    if not detail:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")

    return OrderDetailOut(
        id=detail.OrderDetail.id,
        order_id=detail.OrderDetail.order_id,
        product_id=detail.OrderDetail.product_id,
        product_name=detail.product_name,
        quantity=detail.OrderDetail.quantity,
        price_per_unit=detail.OrderDetail.price_per_unit,
        order_date=detail.order_date
    )


@order_detail_router.get("/supplier/{supplier_id}", response_model=list[OrderDetailSupplierOut])
async def get_order_details_by_supplier(
        supplier_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        db: AsyncSession = Depends(get_db),
        _: TokenData = Depends(require_role("supplier"))
):
    # 1. First verify the supplier exists
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # 2. Build the base query
    query = (
        select(
            OrderDetail,
            Product.name.label("product_name"),
            Order.order_date
        )
        .join(Product, OrderDetail.product_id == Product.id)
        .join(Order, OrderDetail.order_id == Order.id)
        .where(Product.supplier_id == supplier_id)
    )

    # 3. Apply date filters if provided
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        # Include the entire end date by using <= end_date + 1 day
        query = query.where(Order.order_date <= end_date + timedelta(days=1))

    # 4. Execute the query
    result = await db.execute(query)
    details = result.all()

    # 5. Return results or empty list instead of 404 if no results found
    return [
        OrderDetailSupplierOut(
            id=detail.OrderDetail.id,
            order_id=detail.OrderDetail.order_id,
            product_id=detail.OrderDetail.product_id,
            product_name=detail.product_name,
            quantity=detail.OrderDetail.quantity,
            price_per_unit=detail.OrderDetail.price_per_unit,
            order_date=detail.order_date
        )
        for detail in details
    ]


@order_detail_router.post("/", response_model=OrderDetailOut, status_code=201)
async def create_order_detail(
        data: OrderDetailCreate,
        db: AsyncSession = Depends(get_db),
        _: TokenData = Depends(require_role(["admin", "supplier", "customer"]))
):
    new_order_detail = OrderDetail(**data.dict())
    db.add(new_order_detail)
    await db.commit()
    await db.refresh(new_order_detail)

    # Get the related product to include product_name
    product_result = await db.execute(
        select(Product).where(Product.id == new_order_detail.product_id))
    product = product_result.scalar_one()

    # Get the related order to include order_date
    order_result = await db.execute(
        select(Order).where(Order.id == new_order_detail.order_id))
    order = order_result.scalar_one()

    # Return with all required fields
    return OrderDetailOut(
        id=new_order_detail.id,
        order_id=new_order_detail.order_id,
        product_id=new_order_detail.product_id,
        product_name=product.name,  # Include product name
        quantity=new_order_detail.quantity,
        price_per_unit=new_order_detail.price_per_unit,
        order_date=order.order_date
    )

@order_detail_router.put("/{order_detail_id}", response_model=OrderDetailOut)
async def update_order_detail(
    order_detail_id: int,
    data: OrderDetailCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(OrderDetail).where(OrderDetail.id == order_detail_id))
    order_detail = result.scalar_one_or_none()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")

    for key, value in data.dict().items():
        setattr(order_detail, key, value)

    await db.commit()
    await db.refresh(order_detail)
    return order_detail

@order_detail_router.delete("/{order_detail_id}")
async def delete_order_detail(
    order_detail_id: int,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_role("admin"))
):
    result = await db.execute(select(OrderDetail).where(OrderDetail.id == order_detail_id))
    order_detail = result.scalar_one_or_none()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")
    await db.delete(order_detail)
    await db.commit()
    return {"detail": "Деталь заказа удалена"}


@order_detail_router.get("/customer/{customer_id}", response_model=list[OrderDetailOut])
async def get_order_details_by_customer(
        customer_id: int,
        db: AsyncSession = Depends(get_db),
        _: TokenData = Depends(require_role(["admin", "customer"]))
):
    result = await db.execute(
        select(
            OrderDetail,
            Product.name.label("product_name"),
            Order.order_date
        )
        .join(Order, OrderDetail.order_id == Order.id)
        .join(Product, OrderDetail.product_id == Product.id)
        .where(Order.customer_id == customer_id)
    )

    details = result.all()

    if not details:
        raise HTTPException(status_code=404, detail="Детали заказов не найдены")

    return [
        OrderDetailOut(
            id=detail.OrderDetail.id,
            order_id=detail.OrderDetail.order_id,
            product_id=detail.OrderDetail.product_id,
            product_name=detail.product_name,
            quantity=detail.OrderDetail.quantity,
            price_per_unit=detail.OrderDetail.price_per_unit,
            order_date=detail.order_date
        )
        for detail in details
    ]

# Пример для get_order_details_by_order_id
@order_detail_router.get("/order/{order_id}", response_model=list[OrderDetailOut])
async def get_order_details_by_order_id(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        _: TokenData = Depends(require_role(["admin", "customer"]))
):
    # Получаем данные с join
    result = await db.execute(
        select(
            OrderDetail,
            Product.name.label("product_name"),
            Order.order_date
        )
        .join(Product, OrderDetail.product_id == Product.id)
        .join(Order, OrderDetail.order_id == Order.id)
        .where(OrderDetail.order_id == order_id)
    )

    items = result.all()

    # Преобразуем в Pydantic модель
    return [
        OrderDetailOut(
            id=item.OrderDetail.id,
            order_id=item.OrderDetail.order_id,
            product_id=item.OrderDetail.product_id,
            product_name=item.product_name,  # берём из join
            quantity=item.OrderDetail.quantity,
            price_per_unit=item.OrderDetail.price_per_unit,
            order_date=item.order_date
        )
        for item in items
    ]