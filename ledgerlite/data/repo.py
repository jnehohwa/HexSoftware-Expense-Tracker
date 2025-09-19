"""Repository pattern implementation for database operations."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from .models import Account, Attachment, Budget, Category, Transaction


class BaseRepository:
    """Base repository class with common database operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        self.session = session


class AccountRepository(BaseRepository):
    """Repository for account operations."""
    
    def create(self, name: str, account_type: str, currency: str = "USD") -> Account:
        """Create a new account.
        
        Args:
            name: Account name.
            account_type: Type of account (cash, bank, card).
            currency: Currency code (default: USD).
            
        Returns:
            Created account instance.
        """
        account = Account(name=name, type=account_type, currency=currency)
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account
    
    def get_all(self) -> List[Account]:
        """Get all accounts.
        
        Returns:
            List of all accounts.
        """
        return self.session.query(Account).order_by(Account.name).all()
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID.
        
        Args:
            account_id: Account ID.
            
        Returns:
            Account instance or None if not found.
        """
        return self.session.query(Account).filter(Account.id == account_id).first()
    
    def update(self, account: Account) -> Account:
        """Update an account.
        
        Args:
            account: Account instance to update.
            
        Returns:
            Updated account instance.
        """
        self.session.commit()
        self.session.refresh(account)
        return account
    
    def delete(self, account_id: int) -> bool:
        """Delete an account.
        
        Args:
            account_id: Account ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        account = self.get_by_id(account_id)
        if account:
            self.session.delete(account)
            self.session.commit()
            return True
        return False


class CategoryRepository(BaseRepository):
    """Repository for category operations."""
    
    def create(
        self, 
        name: str, 
        category_type: str, 
        color_hex: str = "#3498db",
        parent_id: Optional[int] = None
    ) -> Category:
        """Create a new category.
        
        Args:
            name: Category name.
            category_type: Type of category (expense, income).
            color_hex: Hex color code.
            parent_id: Parent category ID for subcategories.
            
        Returns:
            Created category instance.
        """
        category = Category(
            name=name, 
            type=category_type, 
            color_hex=color_hex,
            parent_id=parent_id
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def get_all(self) -> List[Category]:
        """Get all categories.
        
        Returns:
            List of all categories.
        """
        return self.session.query(Category).order_by(Category.name).all()
    
    def get_by_type(self, category_type: str) -> List[Category]:
        """Get categories by type.
        
        Args:
            category_type: Type of category (expense, income).
            
        Returns:
            List of categories of specified type.
        """
        return (
            self.session.query(Category)
            .filter(Category.type == category_type)
            .order_by(Category.name)
            .all()
        )
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID.
        
        Args:
            category_id: Category ID.
            
        Returns:
            Category instance or None if not found.
        """
        return self.session.query(Category).filter(Category.id == category_id).first()
    
    def update(self, category: Category) -> Category:
        """Update a category.
        
        Args:
            category: Category instance to update.
            
        Returns:
            Updated category instance.
        """
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def delete(self, category_id: int) -> bool:
        """Delete a category.
        
        Args:
            category_id: Category ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        category = self.get_by_id(category_id)
        if category:
            self.session.delete(category)
            self.session.commit()
            return True
        return False


class TransactionRepository(BaseRepository):
    """Repository for transaction operations."""
    
    def create(
        self,
        account_id: int,
        category_id: int,
        date: datetime,
        amount: Decimal,
        transaction_type: str,
        note: Optional[str] = None
    ) -> Transaction:
        """Create a new transaction.
        
        Args:
            account_id: Account ID.
            category_id: Category ID.
            date: Transaction date.
            amount: Transaction amount.
            transaction_type: Type of transaction (expense, income).
            note: Optional transaction note.
            
        Returns:
            Created transaction instance.
        """
        transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            date=date,
            amount=amount,
            type=transaction_type,
            note=note
        )
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction
    
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Transaction]:
        """Get all transactions with pagination.
        
        Args:
            limit: Maximum number of transactions to return.
            offset: Number of transactions to skip.
            
        Returns:
            List of transactions.
        """
        query = (
            self.session.query(Transaction)
            .order_by(desc(Transaction.date))
        )
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID.
            
        Returns:
            Transaction instance or None if not found.
        """
        return (
            self.session.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get transactions within date range.
        
        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            limit: Maximum number of transactions to return.
            
        Returns:
            List of transactions in date range.
        """
        query = (
            self.session.query(Transaction)
            .filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
            .order_by(desc(Transaction.date))
        )
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_by_category(
        self,
        category_id: int,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get transactions by category.
        
        Args:
            category_id: Category ID.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of transactions for the category.
        """
        query = (
            self.session.query(Transaction)
            .filter(Transaction.category_id == category_id)
            .order_by(desc(Transaction.date))
        )
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def search(
        self,
        search_term: str,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Search transactions by note content.
        
        Args:
            search_term: Search term to look for in notes.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of matching transactions.
        """
        query = (
            self.session.query(Transaction)
            .filter(Transaction.note.ilike(f"%{search_term}%"))
            .order_by(desc(Transaction.date))
        )
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_totals_by_type(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[Decimal, Decimal]:
        """Get total income and expense amounts.
        
        Args:
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            
        Returns:
            Tuple of (total_income, total_expense).
        """
        query = self.session.query(Transaction)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        income = (
            query.filter(Transaction.type == "income")
            .with_entities(func.sum(Transaction.amount))
            .scalar() or Decimal("0")
        )
        
        expense = (
            query.filter(Transaction.type == "expense")
            .with_entities(func.sum(Transaction.amount))
            .scalar() or Decimal("0")
        )
        
        return income, expense
    
    def get_count_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Get count of transactions within date range.
        
        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            
        Returns:
            Count of transactions in date range.
        """
        return (
            self.session.query(Transaction)
            .filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
            .count()
        )
    
    def update(self, transaction: Transaction) -> Transaction:
        """Update a transaction.
        
        Args:
            transaction: Transaction instance to update.
            
        Returns:
            Updated transaction instance.
        """
        self.session.commit()
        self.session.refresh(transaction)
        return transaction
    
    def delete(self, transaction_id: int) -> bool:
        """Delete a transaction.
        
        Args:
            transaction_id: Transaction ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        transaction = self.get_by_id(transaction_id)
        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        return False


class BudgetRepository(BaseRepository):
    """Repository for budget operations."""
    
    def create(
        self,
        category_id: int,
        month: str,
        amount_cap: Decimal
    ) -> Budget:
        """Create a new budget.
        
        Args:
            category_id: Category ID.
            month: Month in YYYY-MM format.
            amount_cap: Budget amount cap.
            
        Returns:
            Created budget instance.
        """
        budget = Budget(
            category_id=category_id,
            month=month,
            amount_cap=amount_cap
        )
        self.session.add(budget)
        self.session.commit()
        self.session.refresh(budget)
        return budget
    
    def get_all(self) -> List[Budget]:
        """Get all budgets.
        
        Returns:
            List of all budgets.
        """
        return (
            self.session.query(Budget)
            .order_by(desc(Budget.month), Budget.category_id)
            .all()
        )
    
    def get_by_month(self, month: str) -> List[Budget]:
        """Get budgets for a specific month.
        
        Args:
            month: Month in YYYY-MM format.
            
        Returns:
            List of budgets for the month.
        """
        return (
            self.session.query(Budget)
            .filter(Budget.month == month)
            .order_by(Budget.category_id)
            .all()
        )
    
    def get_by_category_and_month(
        self,
        category_id: int,
        month: str
    ) -> Optional[Budget]:
        """Get budget for specific category and month.
        
        Args:
            category_id: Category ID.
            month: Month in YYYY-MM format.
            
        Returns:
            Budget instance or None if not found.
        """
        return (
            self.session.query(Budget)
            .filter(
                and_(
                    Budget.category_id == category_id,
                    Budget.month == month
                )
            )
            .first()
        )
    
    def update(self, budget: Budget) -> Budget:
        """Update a budget.
        
        Args:
            budget: Budget instance to update.
            
        Returns:
            Updated budget instance.
        """
        self.session.commit()
        self.session.refresh(budget)
        return budget
    
    def delete(self, budget_id: int) -> bool:
        """Delete a budget.
        
        Args:
            budget_id: Budget ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        budget = (
            self.session.query(Budget)
            .filter(Budget.id == budget_id)
            .first()
        )
        if budget:
            self.session.delete(budget)
            self.session.commit()
            return True
        return False

