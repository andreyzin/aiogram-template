from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

SessionMakerType = async_sessionmaker[AsyncSession]
