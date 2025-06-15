from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from core.dependencies import get_current_user
from core.models import Employee, Customer, Supplier
from core.database import get_db
from core.security import verify_password, create_access_token
from schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenData(BaseModel):
    sub: str
    role: str

class UserOut(BaseModel):
    username: str
    role: str

class UserMeResponse(BaseModel):
    username: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = None
    role = None
    customer_id = None
    supplier_id = None  # Добавляем переменную для supplier_id

    # Поиск в employees
    result = await db.execute(select(Employee).where(Employee.username == form_data.username))
    employee = result.scalar_one_or_none()
    if employee and verify_password(form_data.password, employee.password_hash):
        user = employee
        role = "admin"
    else:
        # Поиск в customers
        result = await db.execute(select(Customer).where(Customer.username == form_data.username))
        customer = result.scalar_one_or_none()
        if customer and verify_password(form_data.password, customer.password_hash):
            user = customer
            role = "customer"
            customer_id = customer.id
        else:
            # Поиск в suppliers
            result = await db.execute(select(Supplier).where(Supplier.username == form_data.username))
            supplier = result.scalar_one_or_none()
            if supplier and verify_password(form_data.password, supplier.password_hash):
                user = supplier
                role = "supplier"
                supplier_id = supplier.id  # Сохраняем supplier_id

    if not user or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаем данные для токена
    token_data = {"sub": form_data.username, "role": role}

    # Добавляем ID в зависимости от роли
    if role == "admin":
        token_data["employee_id"] = user.id
    elif role == "customer":
        token_data["customer_id"] = customer_id
    elif role == "supplier":
        token_data["supplier_id"] = supplier_id

    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserMeResponse)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("username"):
        raise HTTPException(status_code=400, detail="Username not found in token")

    return {
        "username": current_user["username"],
        "role": current_user["role"],
        # Другие поля, если нужно
    }