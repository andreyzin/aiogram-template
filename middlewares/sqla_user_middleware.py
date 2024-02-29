from typing import Any, Awaitable, Callable, Dict, Type, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import UserORM


class SqlAlchemyUserMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user is None:
            return await handler(event, data)

        async with self._sessionmaker() as session:
            user = await session.get(UserORM, event.from_user.id)

            if (
                user is None
                and isinstance(event, Message)
                and event.chat.type == "private"
            ):
                user = UserORM(tg_id=event.from_user.id)  # type: ignore
                user = await session.merge(user)
                await session.commit()

            data["user"] = user

            return await handler(event, data)
