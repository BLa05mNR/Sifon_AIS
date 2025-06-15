from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    ForeignKey,
    DECIMAL,
    TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ---------------------- Сотрудники ----------------------
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    position = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    hire_date = Column(Date, nullable=False)

    username = Column(String(50), unique=True, nullable=True)
    password_hash = Column(String, nullable=True)


# ---------------------- Покупатели ----------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(50))
    address = Column(Text)

    username = Column(String(50), unique=True, nullable=True)
    password_hash = Column(String, nullable=True)


# ---------------------- Поставщики ----------------------
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20), nullable=False)
    email = Column(String(50))
    address = Column(Text)

    username = Column(String(50), unique=True, nullable=True)
    password_hash = Column(String, nullable=True)


# ---------------------- Категории товаров ----------------------
class ProductCategory(Base):
    __tablename__ = "product_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey("product_category.id"), nullable=True)

    parent = relationship("ProductCategory", remote_side=[id])


# ---------------------- Товары ---------------------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("product_category.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    stock_quantity = Column(Integer, nullable=False)

    category = relationship("ProductCategory")
    supplier = relationship("Supplier")


# ---------------------- Заказы ----------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    customer = relationship("Customer")


# ---------------------- Детали заказа ----------------------
class OrderDetail(Base):
    __tablename__ = "order_detail"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order")
    product = relationship("Product")


# ---------------------- Продажи ----------------------
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sale_date = Column(TIMESTAMP(timezone=True), nullable=False)
    payment_method = Column(String(20), nullable=False)

    order = relationship("Order")


# ---------------------- Операции на складе ----------------------
class StockOperation(Base):
    __tablename__ = "stock_operations"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    operation_type = Column(String(20), nullable=False)  # приход или расход
    quantity = Column(Integer, nullable=False)
    operation_date = Column(TIMESTAMP(timezone=True), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    product = relationship("Product")
    employee = relationship("Employee")


# ---------------------- Финансовые отчёты ----------------------
class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=False)
    total_revenue = Column(DECIMAL(12, 2), nullable=False)
    total_expenses = Column(DECIMAL(12, 2), nullable=False)
    profit = Column(DECIMAL(12, 2), nullable=False)
