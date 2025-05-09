from sqlalchemy import Column, ForeignKey, DateTime, Integer, String, Float, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import uuid

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CurrencyConversionTransaction(Base):
    __tablename__ = 'currency_conversion_transactions'

    transaction_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_from: Mapped[float] = mapped_column(Float, nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_to: Mapped[float] = mapped_column(Float, nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __repr__(self):
        return (f"<CurrencyConversionTransaction("
                f"transaction_id={self.transaction_id}, "
                f"user_id={self.user_id}, "
                f"from_currency={self.from_currency}, "
                f"amount_from={self.amount_from}, "
                f"to_currency={self.to_currency}, "
                f"amount_to={self.amount_to}, "
                f"exchange_rate={self.exchange_rate}, "
                f"timestamp={self.timestamp})>")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[list["CurrencyConversionTransaction"]] = relationship(
        "CurrencyConversionTransaction",
        back_populates="user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, is_active={self.is_active})>"


class UserSession(Base):
    __tablename__ = 'user_sessions'

    session_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, user_id={self.user_id}, created_at={self.created_at})>"

    @property
    def is_expired(self):
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False

    @staticmethod
    def create_session(user_id: int, db: AsyncSession):
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        session = UserSession(
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(session)
        return session
