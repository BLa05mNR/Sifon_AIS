from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


# -------------------- AUTH --------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------- CUSTOMER --------------------
class CustomerBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    username: str
    password: str

class CustomerOut(CustomerBase):
    id: int
    class Config:
        from_attributes = True


# -------------------- EMPLOYEE --------------------
class EmployeeBase(BaseModel):
    full_name: str
    position: str
    phone: str
    hire_date: date

class EmployeeCreate(EmployeeBase):
    username: str
    password: str

class EmployeeOut(EmployeeBase):
    id: int
    class Config:
        from_attributes = True


# -------------------- SUPPLIER --------------------
class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    username: str
    password: str

class SupplierOut(SupplierBase):
    id: int
    class Config:
        from_attributes = True

# -------------------- PRODUCT CATEGORY --------------------
class ProductCategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(ProductCategoryBase):
    pass

class ProductCategoryOut(ProductCategoryBase):
    id: int
    class Config:
        from_attributes = True

# -------------------- PRODUCT --------------------
class ProductBase(BaseModel):
    name: str
    category_id: int
    supplier_id: int
    price: float
    description: Optional[str] = None
    stock_quantity: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    price: float | None = None
    description: str | None = None
    stock_quantity: int | None = None

class ProductOut(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductStockUpdate(BaseModel):
    quantity_change: int

# -------------------- ORDER --------------------
class OrderBase(BaseModel):
    customer_id: int
    order_date: datetime
    status: str
    total_amount: float

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    class Config:
        from_attributes = True


# -------------------- ORDER DETAIL --------------------
class OrderDetailBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price_per_unit: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetailOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str  # Добавлено поле с названием товара
    quantity: int
    price_per_unit: float
    order_date: datetime

    class Config:
        from_attributes = True

class OrderDetailSupplierOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    price_per_unit: float
    order_date: datetime

    class Config:
        from_attributes = True