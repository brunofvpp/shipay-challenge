from fastapi import APIRouter, Depends, status

from src.application.schemas import UserCreateInput, UserOutput
from src.application.use_cases import CreateUserUseCase
from src.presentation import deps

users_router = APIRouter(prefix="/users", tags=["🧑🏽 Users"])


@users_router.post("", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateInput,
    use_case: CreateUserUseCase = Depends(deps.get_user_service),
):
    return await use_case.create_user(payload)
