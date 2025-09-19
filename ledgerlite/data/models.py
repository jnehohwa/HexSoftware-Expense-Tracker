"""SQLAlchemy models for LedgerLite application."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Account(Base):
    """Account model representing different financial accounts."""
    
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # cash, bank, card
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name='{self.name}', type='{self.type}')>"


class Category(Base):
    """Category model for organizing transactions."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # expense, income
    color_hex = Column(String(7), nullable=False, default="#3498db")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"


class Transaction(Base):
    """Transaction model representing financial transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(20), nullable=False)  # expense, income
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    attachments = relationship("Attachment", back_populates="transaction")
    
    # Indexes
    __table_args__ = (
        Index("idx_transactions_date", "date"),
        Index("idx_transactions_category_id", "category_id"),
        Index("idx_transactions_account_id", "account_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, amount={self.amount}, type='{self.type}')>"


class Budget(Base):
    """Budget model for monthly spending limits per category."""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    month = Column(String(7), nullable=False)  # YYYY-MM format
    amount_cap = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="budgets")
    
    # Indexes
    __table_args__ = (
        Index("idx_budgets_category_month", "category_id", "month"),
    )
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, category_id={self.category_id}, month='{self.month}')>"


class Attachment(Base):
    """Attachment model for transaction receipts and documents."""
    
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    added_at = Column(DateTime, default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="attachments")
    
    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, transaction_id={self.transaction_id})>"

