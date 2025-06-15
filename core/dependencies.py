from typing import Union, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from core.models import Employee, Customer, Supplier
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    sub: str
    role: str
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    employee_id: Optional[int] = None  # Добавляем необязательное поле для employee_id

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded token payload:", payload)  # Отладочное сообщение
        username: str = payload.get("sub")
        role: str = payload.get("role")
        customer_id: Optional[int] = payload.get("customer_id")
        supplier_id: Optional[int] = payload.get("supplier_id")
        employee_id: Optional[int] = payload.get("employee_id")  # Получаем employee_id из токена

        if username is None or role is None:
            raise credentials_exception

        user = None
        user_model = None

        if role == "admin":
            result = await db.execute(select(Employee).where(Employee.username == username))
            user_model = Employee
        elif role == "customer":
            result = await db.execute(select(Customer).where(Customer.username == username))
            user_model = Customer
        elif role == "supplier":
            result = await db.execute(select(Supplier).where(Supplier.username == username))
            user_model = Supplier

        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return {
            "username": username,
            "role": role,
            "customer_id": customer_id if role == "customer" else None,
            "supplier_id": supplier_id if role == "supplier" else None,
            "employee_id": employee_id if role == "admin" else None,  # Добавляем employee_id
            "user": user
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен или срок действия истёк")

def require_role(required_roles: Union[str, List[str]]):
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    async def role_dependency(current_user: dict = Depends(get_current_user)):
        print(f"User role: {current_user['role']}, Required roles: {required_roles}")
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return current_user

    return role_dependency

def require_owner_or_role(model: str, required_role: str):
    async def dependency(current_user: dict = Depends(get_current_user)):
        if current_user["role"] == required_role:
            return current_user
        if model == "customer" and current_user["role"] == "customer":
            return current_user
        if model == "supplier" and current_user["role"] == "supplier":
            return current_user
        if model == "admin" and current_user["role"] == "admin":
            return current_user
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    return dependency
