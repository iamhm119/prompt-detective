"""SQLAlchemy model for contact messages submitted via support form."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class ContactMessage(Base):
    """Represents a customer contact/support request."""

    __tablename__ = "contact_messages"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(255), nullable=False)
    email: str = Column(String(255), nullable=False, index=True)
    subject: str = Column(String(500), nullable=False)
    message: str = Column(Text, nullable=False)
    category: str | None = Column(String(50), nullable=True)
    status: str = Column(String(50), nullable=False, default="new")
    priority: str = Column(String(20), nullable=False, default="normal")
    auto_response_sent: bool = Column(Boolean, nullable=False, default=False)
    admin_response: str | None = Column(Text, nullable=True)
    responded_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    responded_by: int | None = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime | None = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ContactMessage id={self.id} email={self.email!r} status={self.status!r}>"
