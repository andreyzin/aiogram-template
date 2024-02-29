from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from inspect import iscoroutinefunction


class DependanciesMiddleware(BaseMiddleware):
    def __init__(self, **dependencies: Callable[[], Any]):
        self._dependencies = dependencies

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ):
        for i, dep in self._dependencies.items():
            if iscoroutinefunction(dep):
                data[i] = await dep()
            else:
                data[i] = dep()
        return await handler(event, data)
