"""Transaction form dialog for adding/editing transactions."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ledgerlite.data.models import Transaction
from ledgerlite.data.repo import AccountRepository, CategoryRepository, TransactionRepository


class TransactionForm(QDialog):
    """Dialog for adding or editing transactions."""
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        transaction: Optional[Transaction] = None
    ) -> None:
        """Initialize the transaction form.
        
        Args:
            parent: Parent widget.
            transaction: Transaction to edit, or None for new transaction.
        """
        super().__init__(parent)
        self.transaction = transaction
        self.is_edit_mode = transaction is not None
        
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
        # Set dialog properties
        self.setWindowTitle("Edit Transaction" if self.is_edit_mode else "Add Transaction")
        self.setModal(True)
        self.resize(400, 300)
    
    def setup_ui(self) -> None:
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setDate(datetime.now().date())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Account field
        self.account_combo = QComboBox()
        form_layout.addRow("Account:", self.account_combo)
        
        # Category field
        self.category_combo = QComboBox()
        form_layout.addRow("Category:", self.category_combo)
        
        # Type field
        self.type_combo = QComboBox()
        self.type_combo.addItems(["expense", "income"])
        form_layout.addRow("Type:", self.type_combo)
        
        # Amount field
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        form_layout.addRow("Amount:", self.amount_edit)
        
        # Note field
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        self.note_edit.setPlaceholderText("Optional note...")
        form_layout.addRow("Note:", self.note_edit)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_form)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        # Update category options when type changes
        self.type_combo.currentTextChanged.connect(self.update_category_options)
    
    def load_data(self) -> None:
        """Load form data."""
        # Load accounts and categories
        self.load_accounts()
        self.load_categories()
        
        # If editing, populate form with transaction data
        if self.is_edit_mode and self.transaction:
            self.date_edit.setDate(self.transaction.date.date())
            self.amount_edit.setText(str(self.transaction.amount))
            self.type_combo.setCurrentText(self.transaction.type)
            self.note_edit.setPlainText(self.transaction.note or "")
            
            # Set account
            account_index = self.account_combo.findData(self.transaction.account_id)
            if account_index >= 0:
                self.account_combo.setCurrentIndex(account_index)
            
            # Set category (will be updated by type change)
            self.update_category_options(self.transaction.type)
            category_index = self.category_combo.findData(self.transaction.category_id)
            if category_index >= 0:
                self.category_combo.setCurrentIndex(category_index)
    
    def load_accounts(self) -> None:
        """Load accounts into the combo box."""
        from ledgerlite.data.db import db_manager
        
        session = db_manager.get_session_sync()
        try:
            account_repo = AccountRepository(session)
            accounts = account_repo.get_all()
            
            self.account_combo.clear()
            for account in accounts:
                self.account_combo.addItem(f"{account.name} ({account.type})", account.id)
        finally:
            session.close()
    
    def load_categories(self) -> None:
        """Load categories into the combo box."""
        from ledgerlite.data.db import db_manager
        
        session = db_manager.get_session_sync()
        try:
            category_repo = CategoryRepository(session)
            categories = category_repo.get_all()
            
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(f"{category.name} ({category.type})", category.id)
        finally:
            session.close()
    
    def update_category_options(self, transaction_type: str) -> None:
        """Update category options based on transaction type.
        
        Args:
            transaction_type: Type of transaction (expense or income).
        """
        from ledgerlite.data.db import db_manager
        
        session = db_manager.get_session_sync()
        try:
            category_repo = CategoryRepository(session)
            categories = category_repo.get_by_type(transaction_type)
            
            # Store current selection
            current_category_id = self.category_combo.currentData()
            
            # Clear and repopulate
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
            
            # Restore selection if it's still valid
            if current_category_id:
                index = self.category_combo.findData(current_category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
        finally:
            session.close()
    
    def accept_form(self) -> None:
        """Accept the form and save the transaction."""
        if not self.validate_form():
            return
        
        try:
            if self.is_edit_mode:
                self.update_transaction()
            else:
                self.create_transaction()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save transaction: {str(e)}"
            )
    
    def validate_form(self) -> bool:
        """Validate the form data.
        
        Returns:
            True if form is valid, False otherwise.
        """
        # Check required fields
        if not self.account_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select an account.")
            return False
        
        if not self.category_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a category.")
            return False
        
        # Validate amount
        amount_text = self.amount_edit.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Validation Error", "Please enter an amount.")
            return False
        
        try:
            amount = Decimal(amount_text)
            if amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
                return False
        except InvalidOperation:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount.")
            return False
        
        return True
    
    def create_transaction(self) -> None:
        """Create a new transaction."""
        from ledgerlite.data.db import db_manager
        
        session = db_manager.get_session_sync()
        try:
            transaction_repo = TransactionRepository(session)
            
            transaction_repo.create(
                account_id=self.account_combo.currentData(),
                category_id=self.category_combo.currentData(),
                date=datetime.combine(self.date_edit.date().toPython(), datetime.min.time()),
                amount=Decimal(self.amount_edit.text().strip()),
                transaction_type=self.type_combo.currentText(),
                note=self.note_edit.toPlainText().strip() or None
            )
        finally:
            session.close()
    
    def update_transaction(self) -> None:
        """Update an existing transaction."""
        from ledgerlite.data.db import db_manager
        
        session = db_manager.get_session_sync()
        try:
            transaction_repo = TransactionRepository(session)
            
            # Update transaction fields
            self.transaction.account_id = self.account_combo.currentData()
            self.transaction.category_id = self.category_combo.currentData()
            self.transaction.date = datetime.combine(self.date_edit.date().toPython(), datetime.min.time())
            self.transaction.amount = Decimal(self.amount_edit.text().strip())
            self.transaction.type = self.type_combo.currentText()
            self.transaction.note = self.note_edit.toPlainText().strip() or None
            
            transaction_repo.update(self.transaction)
        finally:
            session.close()
