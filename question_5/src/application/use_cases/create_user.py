from src.application.exceptions import EmailAlreadyExistsError, RoleNotFoundError
from src.application.schemas import UserCreateInput, UserOutput
from src.application.security import generate_password, hash_password
from src.domain import UnitOfWorkPort
from src.domain.repositories import RoleRepositoryPort, UserRepositoryPort


class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        role_repository: RoleRepositoryPort,
        unit_of_work: UnitOfWorkPort,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.unit_of_work = unit_of_work

    async def create_user(self, payload: UserCreateInput) -> UserOutput:
        role = await self.role_repository.get_by_id(payload.role_id)
        if role is None:
            raise RoleNotFoundError(payload.role_id)

        if await self.user_repository.exists_by_email(payload.email):
            raise EmailAlreadyExistsError(payload.email)

        async with self.unit_of_work.transaction():
            user = await self.user_repository.create(
                name=payload.name,
                email=payload.email,
                password=hash_password(payload.password or generate_password()),
                role_id=role.id,
            )
            await self.user_repository.refresh(user)

        return UserOutput.model_validate(user)
