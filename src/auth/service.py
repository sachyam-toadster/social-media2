from src.db.models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.utils import generate_password_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()
        return user

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_password_hash(user_data_dict["password"])

        session.add(new_user)

        await session.commit()

        return new_user
    
    async def verify_user_email(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        if user:
            user.is_verified = True
            session.add(user)
            await session.commit()
            return True

        return False
    
    async def update_user(self, user: User, update_data: dict, session: AsyncSession):
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        await session.commit()

        return user