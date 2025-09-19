"""Database initialization and session management for LedgerLite."""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


# Database configuration
DATABASE_DIR = Path.home() / ".ledgerlite"
DATABASE_PATH = DATABASE_DIR / "ledgerlite.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine.
    
    Returns:
        SQLAlchemy engine instance.
    """
    global _engine
    if _engine is None:
        # Ensure database directory exists
        DATABASE_DIR.mkdir(exist_ok=True)
        
        # Create engine with SQLite-specific optimizations
        _engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 30,  # Connection timeout
            }
        )
    return _engine


def get_session_factory():
    """Get or create the session factory.
    
    Returns:
        SQLAlchemy sessionmaker instance.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal


def get_session() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        SQLAlchemy session instance.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    """Initialize the database by creating all tables.
    
    This function should be called once at application startup.
    """
    db_manager.init_database()


def _create_default_data() -> None:
    """Create default data for the application.
    
    This includes default accounts and categories.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    try:
        from .models import Account, Category
        
        # Check if we already have data
        if session.query(Account).count() > 0:
            return  # Data already exists
        
        # Create default accounts
        default_accounts = [
            Account(name="Cash", type="cash", currency="USD"),
            Account(name="Checking Account", type="bank", currency="USD"),
            Account(name="Savings Account", type="bank", currency="USD"),
            Account(name="Credit Card", type="card", currency="USD"),
        ]
        
        for account in default_accounts:
            session.add(account)
        
        # Create default expense categories
        expense_categories = [
            Category(name="Food & Dining", type="expense", color_hex="#e74c3c"),
            Category(name="Transportation", type="expense", color_hex="#f39c12"),
            Category(name="Shopping", type="expense", color_hex="#9b59b6"),
            Category(name="Entertainment", type="expense", color_hex="#1abc9c"),
            Category(name="Bills & Utilities", type="expense", color_hex="#34495e"),
            Category(name="Healthcare", type="expense", color_hex="#e67e22"),
            Category(name="Education", type="expense", color_hex="#3498db"),
            Category(name="Travel", type="expense", color_hex="#2ecc71"),
            Category(name="Other", type="expense", color_hex="#95a5a6"),
        ]
        
        for category in expense_categories:
            session.add(category)
        
        # Create default income categories
        income_categories = [
            Category(name="Salary", type="income", color_hex="#27ae60"),
            Category(name="Freelance", type="income", color_hex="#16a085"),
            Category(name="Investment", type="income", color_hex="#2980b9"),
            Category(name="Gift", type="income", color_hex="#8e44ad"),
            Category(name="Other", type="income", color_hex="#7f8c8d"),
        ]
        
        for category in income_categories:
            session.add(category)
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    """
    engine = get_engine()
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default data
    _create_default_data()


def get_database_path() -> Path:
    """Get the path to the database file.
    
    Returns:
        Path to the database file.
    """
    return DATABASE_PATH


def database_exists() -> bool:
    """Check if the database file exists.
    
    Returns:
        True if database file exists, False otherwise.
    """
    return DATABASE_PATH.exists()


class DatabaseManager:
    """Database manager class for handling database operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self._engine = None
        self._session_factory = None
    
    def get_engine(self):
        """Get or create the database engine.
        
        Returns:
            SQLAlchemy engine instance.
        """
        if self._engine is None:
            # Ensure database directory exists
            DATABASE_DIR.mkdir(exist_ok=True)
            
            # Create engine with SQLite-specific optimizations
            self._engine = create_engine(
                DATABASE_URL,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                connect_args={
                    "check_same_thread": False,  # Allow multi-threading
                    "timeout": 30,  # Connection timeout
                }
            )
        return self._engine
    
    def get_session_factory(self):
        """Get or create the session factory.
        
        Returns:
            SQLAlchemy sessionmaker instance.
        """
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.get_engine()
            )
        return self._session_factory
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.
        
        Yields:
            SQLAlchemy session instance.
        """
        SessionLocal = self.get_session_factory()
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get a database session synchronously.
        
        Returns:
            SQLAlchemy session instance.
        """
        SessionLocal = self.get_session_factory()
        return SessionLocal()
    
    def init_database(self) -> None:
        """Initialize the database by creating all tables.
        
        This function should be called once at application startup.
        """
        engine = self.get_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize default data if needed
        self._create_default_data()
    
    def _create_default_data(self) -> None:
        """Create default data for the application.
        
        This includes default accounts and categories.
        """
        session = self.get_session_sync()
        
        try:
            from .models import Account, Category
            
            # Check if we already have data
            if session.query(Account).count() > 0:
                return  # Data already exists
            
            # Create default accounts
            default_accounts = [
                Account(name="Cash", type="cash", currency="USD"),
                Account(name="Checking Account", type="bank", currency="USD"),
                Account(name="Savings Account", type="bank", currency="USD"),
                Account(name="Credit Card", type="card", currency="USD"),
            ]
            
            for account in default_accounts:
                session.add(account)
            
            # Create default expense categories
            expense_categories = [
                Category(name="Food & Dining", type="expense", color_hex="#e74c3c"),
                Category(name="Transportation", type="expense", color_hex="#f39c12"),
                Category(name="Shopping", type="expense", color_hex="#9b59b6"),
                Category(name="Entertainment", type="expense", color_hex="#1abc9c"),
                Category(name="Bills & Utilities", type="expense", color_hex="#34495e"),
                Category(name="Healthcare", type="expense", color_hex="#e67e22"),
                Category(name="Education", type="expense", color_hex="#3498db"),
                Category(name="Travel", type="expense", color_hex="#2ecc71"),
                Category(name="Other", type="expense", color_hex="#95a5a6"),
            ]
            
            for category in expense_categories:
                session.add(category)
            
            # Create default income categories
            income_categories = [
                Category(name="Salary", type="income", color_hex="#27ae60"),
                Category(name="Freelance", type="income", color_hex="#16a085"),
                Category(name="Investment", type="income", color_hex="#2980b9"),
                Category(name="Gift", type="income", color_hex="#8e44ad"),
                Category(name="Other", type="income", color_hex="#7f8c8d"),
            ]
            
            for category in income_categories:
                session.add(category)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def reset_database(self) -> None:
        """Reset the database by dropping and recreating all tables.
        
        WARNING: This will delete all data!
        """
        engine = self.get_engine()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        
        # Create default data
        self._create_default_data()


# Global database manager instance
db_manager = DatabaseManager()
