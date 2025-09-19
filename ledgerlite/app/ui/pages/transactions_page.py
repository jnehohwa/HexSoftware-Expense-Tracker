"""Transactions page for managing financial transactions."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QHeaderView,
    QMessageBox,
    QFrame,
    QSplitter,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QScrollArea,
)

from ledgerlite.data.repo import AccountRepository, CategoryRepository, TransactionRepository
from ledgerlite.app.ui.pages.base_page import BasePage
from ledgerlite.app.ui.widgets.transaction_form import TransactionForm
from ledgerlite.app.ui.widgets.category_badge import CategoryBadge
from ledgerlite.utils.currency import format_amount_with_sign, get_amount_color
from ledgerlite.utils.validators import validate_amount


class TransactionsPage(BasePage):
    """Page for managing transactions with filtering and CRUD operations."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the transactions page.
        
        Args:
            parent: Parent widget.
        """
        self.current_month = datetime.now().strftime("%Y-%m")
        self.current_page = 1
        self.page_size = 50
        self.total_transactions = 0
        super().__init__(parent)
    
    def setup_ui(self) -> None:
        """Set up the transactions UI."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title and add button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Transactions")
        title_label.setObjectName("page-title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_button = QPushButton("Add Transaction")
        self.add_button.setObjectName("primary-button")
        header_layout.addWidget(self.add_button)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for filters and table
        splitter = QSplitter(Qt.Horizontal)
        
        # Filters panel
        filters_panel = self.create_filters_panel()
        splitter.addWidget(filters_panel)
        
        # Transactions table
        table_panel = self.create_table_panel()
        splitter.addWidget(table_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def create_filters_panel(self) -> QWidget:
        """Create the filters panel.
        
        Returns:
            Widget containing filter controls.
        """
        panel = QFrame()
        panel.setObjectName("filters-panel")
        panel.setFixedWidth(300)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Panel title
        title_label = QLabel("Filters")
        title_label.setObjectName("panel-title")
        layout.addWidget(title_label)
        
        # Date range filters
        date_frame = QFrame()
        date_layout = QVBoxLayout(date_frame)
        date_layout.setSpacing(5)
        
        date_label = QLabel("Date Range:")
        date_layout.addWidget(date_label)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_edit)
        
        layout.addWidget(date_frame)
        
        # Category filter
        category_frame = QFrame()
        category_layout = QVBoxLayout(category_frame)
        category_layout.setSpacing(5)
        
        category_label = QLabel("Category:")
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories", None)
        category_layout.addWidget(self.category_combo)
        
        layout.addWidget(category_frame)
        
        # Account filter
        account_frame = QFrame()
        account_layout = QVBoxLayout(account_frame)
        account_layout.setSpacing(5)
        
        account_label = QLabel("Account:")
        account_layout.addWidget(account_label)
        
        self.account_combo = QComboBox()
        self.account_combo.addItem("All Accounts", None)
        account_layout.addWidget(self.account_combo)
        
        layout.addWidget(account_frame)
        
        # Type filter
        type_frame = QFrame()
        type_layout = QVBoxLayout(type_frame)
        type_layout.setSpacing(5)
        
        type_label = QLabel("Type:")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types", None)
        self.type_combo.addItem("Income", "income")
        self.type_combo.addItem("Expense", "expense")
        type_layout.addWidget(self.type_combo)
        
        layout.addWidget(type_frame)
        
        # Search filter
        search_frame = QFrame()
        search_layout = QVBoxLayout(search_frame)
        search_layout.setSpacing(5)
        
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in notes...")
        search_layout.addWidget(self.search_edit)
        
        layout.addWidget(search_frame)
        
        # Filter buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.setObjectName("secondary-button")
        button_layout.addWidget(self.apply_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondary-button")
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def create_table_panel(self) -> QWidget:
        """Create the transactions table panel.
        
        Returns:
            Widget containing the transactions table.
        """
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Table title
        title_label = QLabel("Transactions")
        title_label.setObjectName("panel-title")
        layout.addWidget(title_label)
        
        # Create transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setObjectName("transactions-table")
        
        # Set table properties
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.transactions_table.setSortingEnabled(True)
        
        # Set table headers
        headers = ["Date", "Account", "Category", "Type", "Amount", "Note", "Actions"]
        self.transactions_table.setColumnCount(len(headers))
        self.transactions_table.setHorizontalHeaderLabels(headers)
        
        # Configure header
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Account
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Note
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.transactions_table)
        
        return panel
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        # Filter buttons
        self.apply_button.clicked.connect(self.apply_filters)
        self.clear_button.clicked.connect(self.clear_filters)
        
        # Add transaction button
        self.add_button.clicked.connect(self.add_transaction)
        
        # Table double-click
        self.transactions_table.itemDoubleClicked.connect(self.edit_transaction)
        
        # Search field
        self.search_edit.textChanged.connect(self.apply_filters)
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Cmd+N for new transaction
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.add_transaction)
        
        # Cmd+F for focus search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)
        
        # Delete key for delete selected
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected_transaction)
    
    def focus_search(self) -> None:
        """Focus the search field."""
        self.search_edit.setFocus()
        self.search_edit.selectAll()
    
    def delete_selected_transaction(self) -> None:
        """Delete the selected transaction."""
        current_row = self.transactions_table.currentRow()
        if current_row >= 0:
            date_item = self.transactions_table.item(current_row, 0)
            if date_item:
                transaction_id = date_item.data(Qt.UserRole)
                session = self.get_database_session()
                try:
                    transaction_repo = TransactionRepository(session)
                    transaction = transaction_repo.get_by_id(transaction_id)
                    if transaction:
                        self.delete_transaction(transaction)
                finally:
                    session.close()
    
    def load_data(self) -> None:
        """Load transactions data."""
        self.load_filter_options()
        self.apply_filters()
    
    def load_filter_options(self) -> None:
        """Load options for filter dropdowns."""
        session = self.get_database_session()
        try:
            # Load categories
            category_repo = CategoryRepository(session)
            categories = category_repo.get_all()
            
            self.category_combo.clear()
            self.category_combo.addItem("All Categories", None)
            for category in categories:
                self.category_combo.addItem(f"{category.name} ({category.type})", category.id)
            
            # Load accounts
            account_repo = AccountRepository(session)
            accounts = account_repo.get_all()
            
            self.account_combo.clear()
            self.account_combo.addItem("All Accounts", None)
            for account in accounts:
                self.account_combo.addItem(f"{account.name} ({account.type})", account.id)
        finally:
            session.close()
    
    def apply_filters(self) -> None:
        """Apply current filters and refresh the table."""
        # Get filter values
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        category_id = self.category_combo.currentData()
        account_id = self.account_combo.currentData()
        transaction_type = self.type_combo.currentData()
        search_term = self.search_edit.text().strip()
        
        # Load filtered transactions
        session = self.get_database_session()
        try:
            transaction_repo = TransactionRepository(session)
            
            # Get all transactions in date range
            transactions = transaction_repo.get_by_date_range(start_date, end_date)
            
            # Apply additional filters
            filtered_transactions = []
            for transaction in transactions:
                # Category filter
                if category_id and transaction.category_id != category_id:
                    continue
                
                # Account filter
                if account_id and transaction.account_id != account_id:
                    continue
                
                # Type filter
                if transaction_type and transaction.type != transaction_type:
                    continue
                
                # Search filter
                if search_term and (not transaction.note or search_term.lower() not in transaction.note.lower()):
                    continue
                
                filtered_transactions.append(transaction)
            
            self.populate_table(filtered_transactions)
        finally:
            session.close()
    
    def populate_table(self, transactions: List) -> None:
        """Populate the transactions table.
        
        Args:
            transactions: List of transaction objects.
        """
        self.transactions_table.setRowCount(len(transactions))
        
        session = self.get_database_session()
        try:
            account_repo = AccountRepository(session)
            category_repo = CategoryRepository(session)
            
            # Create lookup dictionaries
            accounts = {acc.id: acc for acc in account_repo.get_all()}
            categories = {cat.id: cat for cat in category_repo.get_all()}
            
            for row, transaction in enumerate(transactions):
                # Date
                date_item = QTableWidgetItem(transaction.date.strftime("%Y-%m-%d"))
                date_item.setData(Qt.UserRole, transaction.id)
                self.transactions_table.setItem(row, 0, date_item)
                
                # Account
                account = accounts.get(transaction.account_id)
                account_name = account.name if account else "Unknown"
                self.transactions_table.setItem(row, 1, QTableWidgetItem(account_name))
                
                # Category (with badge)
                category = categories.get(transaction.category_id)
                if category:
                    category_badge = CategoryBadge(category.name, category.color_hex)
                    self.transactions_table.setCellWidget(row, 2, category_badge)
                else:
                    self.transactions_table.setItem(row, 2, QTableWidgetItem("Unknown"))
                
                # Type
                type_item = QTableWidgetItem(transaction.type.title())
                type_item.setData(Qt.UserRole, transaction.type)
                self.transactions_table.setItem(row, 3, type_item)
                
                # Amount (with color and sign)
                amount_text = format_amount_with_sign(transaction.amount, transaction.type)
                amount_item = QTableWidgetItem(amount_text)
                amount_item.setData(Qt.UserRole, float(transaction.amount))
                amount_color = get_amount_color(transaction.amount, transaction.type)
                amount_item.setForeground(QColor(amount_color))
                self.transactions_table.setItem(row, 4, amount_item)
                
                # Note
                note_text = transaction.note or ""
                self.transactions_table.setItem(row, 5, QTableWidgetItem(note_text))
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                edit_button = QPushButton("Edit")
                edit_button.setObjectName("small-button")
                edit_button.clicked.connect(lambda checked, t=transaction: self.edit_transaction(t))
                actions_layout.addWidget(edit_button)
                
                delete_button = QPushButton("Delete")
                delete_button.setObjectName("small-button")
                delete_button.clicked.connect(lambda checked, t=transaction: self.delete_transaction(t))
                actions_layout.addWidget(delete_button)
                
                self.transactions_table.setCellWidget(row, 6, actions_widget)
        finally:
            session.close()
    
    def clear_filters(self) -> None:
        """Clear all filters."""
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.category_combo.setCurrentIndex(0)
        self.account_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.search_edit.clear()
        self.apply_filters()
    
    def add_transaction(self) -> None:
        """Open dialog to add a new transaction."""
        form = TransactionForm(self)
        if form.exec() == TransactionForm.Accepted:
            self.apply_filters()  # Refresh table
            self.data_changed.emit()  # Notify other pages
    
    def edit_transaction(self, transaction=None) -> None:
        """Open dialog to edit a transaction.
        
        Args:
            transaction: Transaction object to edit, or None to get from table selection.
        """
        if transaction is None:
            # Get transaction from table selection
            current_row = self.transactions_table.currentRow()
            if current_row < 0:
                return
            
            # Get transaction ID from the date item
            date_item = self.transactions_table.item(current_row, 0)
            if not date_item:
                return
            
            transaction_id = date_item.data(Qt.UserRole)
            
            # Load transaction from database
            session = self.get_database_session()
            try:
                transaction_repo = TransactionRepository(session)
                transaction = transaction_repo.get_by_id(transaction_id)
                
                if not transaction:
                    QMessageBox.warning(self, "Error", "Transaction not found.")
                    return
            finally:
                session.close()
        
        form = TransactionForm(self, transaction)
        if form.exec() == TransactionForm.Accepted:
            self.apply_filters()  # Refresh table
            self.data_changed.emit()  # Notify other pages
    
    def delete_transaction(self, transaction) -> None:
        """Delete a transaction.
        
        Args:
            transaction: Transaction object to delete.
        """
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this transaction?\n\n"
            f"Amount: ${transaction.amount:,.2f}\n"
            f"Date: {transaction.date.strftime('%Y-%m-%d')}\n"
            f"Note: {transaction.note or 'No note'}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = self.get_database_session()
            try:
                transaction_repo = TransactionRepository(session)
                if transaction_repo.delete(transaction.id):
                    self.apply_filters()  # Refresh table
                    self.data_changed.emit()  # Notify other pages
                    QMessageBox.information(self, "Success", "Transaction deleted successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete transaction.")
            finally:
                session.close()
    
    def on_month_changed(self, month: str) -> None:
        """Handle month change event.
        
        Args:
            month: New month in YYYY-MM format.
        """
        self.current_month = month
        
        # Update date filters to show the selected month
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        
        self.start_date_edit.setDate(start_date.date())
        self.end_date_edit.setDate(end_date.date())
        
        self.apply_filters()
    
    def get_database_session(self):
        """Get a database session.
        
        Returns:
            Database session context manager.
        """
        from ledgerlite.data.db import db_manager
        return db_manager.get_session_sync()
