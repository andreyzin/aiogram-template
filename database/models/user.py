from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserORM(Base):
    __tablename__ = "users"  # type: ignore

    tg_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    join_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    from_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=True)
