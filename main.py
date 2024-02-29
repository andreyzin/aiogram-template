import asyncio
import logging
import platform

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import Settings
from database.models import *
from handlers import all_routers
from middlewares.sqla_user_middleware import SqlAlchemyUserMiddleware
from misc.sqlalchemy_storage import SqlAlchemyStorage
from tools.yaml_repository import YamlRepo

settings = Settings()

async def on_startup(bot: Bot):
    pass


async def on_shutdown(bot: Bot):
    pass


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore


async def main() -> None:
    engine = create_async_engine(
        f"postgresql+psycopg://{settings.db.user}:{settings.db.password}@{settings.db.host}/{settings.db.name}",
    )
    # engine = create_async_engine(
    #     f"sqlite+aiosqlite:///db.db",
    # )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine)

    if settings.bot.local_server_url:
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(
                f"{settings.bot.local_server_url}:{settings.bot.local_server_port}",
                is_local=True,
            )
        )
    else:
        session = None

    bot = Bot(token=settings.bot.token, parse_mode="HTML", session=session)
    tg_user_middleware = SqlAlchemyUserMiddleware(sessionmaker=sessionmaker)

    dp = Dispatcher(storage=SqlAlchemyStorage(sessionmaker))
    dp["sessionmaker"] = sessionmaker

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # INCLUDE ROUTERS
    dp.include_routers(*all_routers)

    # MIDDLEWARES
    dp.message.middleware(tg_user_middleware)
    dp.callback_query.middleware(tg_user_middleware)

    # await dp.start_polling(bot)
    # return

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    webhook_requests_handler.register(app, path=settings.bot.webhook_path)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)

    await runner.setup()
    site = web.TCPSite(runner, host="localhost", port=settings.app.base_port)

    webhook_url = (
        f"{settings.app.base_url}:{settings.app.base_port}{settings.bot.webhook_path}"
    )
    await bot.set_webhook(webhook_url, drop_pending_updates=True)

    await site.start()

    names = sorted(str(s.name) for s in runner.sites)
    print(
        "======== Running on {} ========\n"
        "(Press CTRL+C to quit)".format(", ".join(names))
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
