from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases import CreateUserUseCase
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import SqlRoleRepository, SqlUserRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


async def get_db() -> AsyncIterator[AsyncSession]:
    async with get_session() as session:
        yield session


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> SqlRoleRepository:
    return SqlRoleRepository(db)


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(db)


async def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(db)


async def get_create_user_use_case(
    user_repository: SqlUserRepository = Depends(get_user_repository),
    role_repository: SqlRoleRepository = Depends(get_role_repository),
    unit_of_work: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
) -> CreateUserUseCase:
    return CreateUserUseCase(
        user_repository=user_repository,
        role_repository=role_repository,
        unit_of_work=unit_of_work,
    )


async def get_user_service(
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> CreateUserUseCase:
    return use_case
