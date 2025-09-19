"""Main window for LedgerLite application."""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QFrame,
    QToolBar,
    QSpacerItem,
    QSizePolicy,
)

from ledgerlite.data.db import db_manager
from ledgerlite.app.ui.pages.dashboard_page import DashboardPage
from ledgerlite.app.ui.pages.transactions_page import TransactionsPage
from ledgerlite.app.ui.pages.categories_page import CategoriesPage
from ledgerlite.app.ui.pages.budgets_page import BudgetsPage
from ledgerlite.app.ui.pages.import_export_page import ImportExportPage
from ledgerlite.utils.config import config


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""
    
    # Signals
    month_changed = Signal(str)  # Emitted when month selection changes
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        # Load last selected month from config
        self.current_month = config.get_last_month() or datetime.now().strftime("%Y-%m")
        self.setup_ui()
        self.setup_connections()
        self.load_styles()
        
        # Set window properties
        self.setWindowTitle("LedgerLite - Expense Tracker")
        self.setMinimumSize(1200, 800)
        
        # Load window geometry from config
        geometry = config.get_window_geometry()
        if geometry:
            self.resize(geometry.get("width", 1400), geometry.get("height", 900))
            self.move(geometry.get("x", 100), geometry.get("y", 100))
        else:
            self.resize(1400, 900)
            self.center_window()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        # Create top toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 0)
        
        # Create main content area
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area, 1)
    
    def create_toolbar(self) -> None:
        """Create the top toolbar with month selector and add transaction button."""
        toolbar = QToolBar()
        toolbar.setObjectName("main-toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Month navigation
        prev_button = QPushButton("←")
        prev_button.setObjectName("nav-button")
        prev_button.setFixedSize(32, 32)
        prev_button.clicked.connect(self.previous_month)
        
        self.month_label = QLabel()
        self.month_label.setObjectName("month-label")
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setMinimumWidth(120)
        
        next_button = QPushButton("→")
        next_button.setObjectName("nav-button")
        next_button.setFixedSize(32, 32)
        next_button.clicked.connect(self.next_month)
        
        # Add transaction button (secondary style)
        self.add_transaction_button = QPushButton("+ Transaction")
        self.add_transaction_button.setProperty("class", "secondary")
        
        # Add widgets to toolbar with proper spacing
        toolbar.addWidget(prev_button)
        toolbar.addWidget(self.month_label)
        toolbar.addWidget(next_button)
        toolbar.addSeparator()
        
        # Add spacer to push the button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        toolbar.addWidget(self.add_transaction_button)
        
        # Add toolbar to main window
        self.addToolBar(toolbar)
        
        # Update month display
        self.update_month_display()
    
    def create_sidebar(self) -> QWidget:
        """Create the sidebar navigation."""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title
        title_label = QLabel("LedgerLite")
        title_label.setObjectName("app-title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(60)
        layout.addWidget(title_label)
        
        # Month selector
        month_frame = QFrame()
        month_frame.setObjectName("month-selector")
        month_layout = QVBoxLayout(month_frame)
        month_layout.setContentsMargins(15, 10, 15, 10)
        
        month_label = QLabel("Current Month:")
        month_label.setObjectName("month-label")
        month_layout.addWidget(month_label)
        
        self.month_combo = QComboBox()
        self.month_combo.setObjectName("month-combo")
        self.populate_month_combo()
        month_layout.addWidget(self.month_combo)
        
        layout.addWidget(month_frame)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("nav-list")
        self.nav_list.setSpacing(2)
        
        # Add navigation items
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Transactions", "transactions"),
            ("Categories", "categories"),
            ("Budgets", "budgets"),
            ("Import/Export", "import_export"),
        ]
        
        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.nav_list.addItem(item)
        
        # Select first item by default
        if self.nav_list.count() > 0:
            self.nav_list.item(0).setCheckState(Qt.Checked)
        
        layout.addWidget(self.nav_list)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Theme toggle button
        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.setObjectName("theme-button")
        self.theme_button.setFixedHeight(40)
        layout.addWidget(self.theme_button)
        
        return sidebar
    
    def create_content_area(self) -> QWidget:
        """Create the main content area."""
        content_widget = QWidget()
        content_widget.setObjectName("content-area")
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked-widget")
        
        # Create pages
        self.dashboard_page = DashboardPage()
        self.transactions_page = TransactionsPage()
        self.categories_page = CategoriesPage()
        self.budgets_page = BudgetsPage()
        self.import_export_page = ImportExportPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.transactions_page)
        self.stacked_widget.addWidget(self.categories_page)
        self.stacked_widget.addWidget(self.budgets_page)
        self.stacked_widget.addWidget(self.import_export_page)
        
        layout.addWidget(self.stacked_widget)
        
        return content_widget
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        # Navigation list selection
        self.nav_list.currentRowChanged.connect(self.on_navigation_changed)
        
        # Month combo selection
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        
        # Add transaction button
        self.add_transaction_button.clicked.connect(self.add_transaction)
        
        # Theme button
        self.theme_button.clicked.connect(self.toggle_theme)
        
        # Connect month changed signal to pages
        self.month_changed.connect(self.dashboard_page.on_month_changed)
        self.month_changed.connect(self.transactions_page.on_month_changed)
        self.month_changed.connect(self.budgets_page.on_month_changed)
        
        # Connect data changed signals between pages for synchronization
        self.dashboard_page.data_changed.connect(self.transactions_page.refresh_data)
        self.dashboard_page.data_changed.connect(self.categories_page.refresh_data)
        self.dashboard_page.data_changed.connect(self.budgets_page.refresh_data)
        
        self.transactions_page.data_changed.connect(self.dashboard_page.refresh_data)
        self.transactions_page.data_changed.connect(self.categories_page.refresh_data)
        self.transactions_page.data_changed.connect(self.budgets_page.refresh_data)
        
        self.categories_page.data_changed.connect(self.dashboard_page.refresh_data)
        self.categories_page.data_changed.connect(self.transactions_page.refresh_data)
        self.categories_page.data_changed.connect(self.budgets_page.refresh_data)
        
        self.budgets_page.data_changed.connect(self.dashboard_page.refresh_data)
        self.budgets_page.data_changed.connect(self.transactions_page.refresh_data)
        self.budgets_page.data_changed.connect(self.categories_page.refresh_data)
    
    def previous_month(self) -> None:
        """Navigate to previous month."""
        current_date = datetime.strptime(self.current_month, "%Y-%m")
        if current_date.month == 1:
            new_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            new_date = current_date.replace(month=current_date.month - 1)
        
        new_month = new_date.strftime("%Y-%m")
        self.current_month = new_month
        self.update_month_display()
        self.month_changed.emit(new_month)
    
    def next_month(self) -> None:
        """Navigate to next month."""
        current_date = datetime.strptime(self.current_month, "%Y-%m")
        if current_date.month == 12:
            new_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            new_date = current_date.replace(month=current_date.month + 1)
        
        new_month = new_date.strftime("%Y-%m")
        self.current_month = new_month
        self.update_month_display()
        self.month_changed.emit(new_month)
    
    def update_month_display(self) -> None:
        """Update the month display in the toolbar."""
        current_date = datetime.strptime(self.current_month, "%Y-%m")
        display_text = current_date.strftime("%B %Y")
        self.month_label.setText(display_text)
    
    def add_transaction(self) -> None:
        """Open the add transaction dialog."""
        # This will be implemented when we create the transaction form
        from ledgerlite.app.ui.widgets.transaction_form import TransactionForm
        form = TransactionForm(self)
        if form.exec() == TransactionForm.Accepted:
            # Refresh current page data
            current_page = self.stacked_widget.currentWidget()
            if hasattr(current_page, 'refresh_data'):
                current_page.refresh_data()
    
    def populate_month_combo(self) -> None:
        """Populate the month combo box with recent months."""
        current_date = datetime.now()
        
        # Add current month and previous 11 months
        for i in range(12):
            month_date = current_date.replace(day=1)
            if i > 0:
                # Subtract months
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            
            month_str = month_date.strftime("%Y-%m")
            display_str = month_date.strftime("%B %Y")
            
            self.month_combo.addItem(display_str, month_str)
            
            # Set current month as selected
            if month_str == self.current_month:
                self.month_combo.setCurrentIndex(i)
    
    def on_navigation_changed(self, row: int) -> None:
        """Handle navigation list selection change.
        
        Args:
            row: Selected row index.
        """
        # Update check states
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            item.setCheckState(Qt.Checked if i == row else Qt.Unchecked)
        
        # Switch to corresponding page
        self.stacked_widget.setCurrentIndex(row)
    
    def on_month_changed(self, display_text: str) -> None:
        """Handle month selection change.
        
        Args:
            display_text: Display text of selected month.
        """
        # Get the month string from the combo box data
        index = self.month_combo.findText(display_text)
        if index >= 0:
            month_str = self.month_combo.itemData(index)
            if month_str != self.current_month:
                self.current_month = month_str
                self.month_changed.emit(month_str)
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        # This will be implemented when we add styling
        pass
    
    def center_window(self) -> None:
        """Center the window on the screen."""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def load_styles(self) -> None:
        """Load application styles."""
        from pathlib import Path
        
        # Load stylesheet
        stylesheet_path = Path(__file__).parent.parent.parent / "assets" / "styles.qss"
        if stylesheet_path.exists():
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
    
    def get_current_month(self) -> str:
        """Get the currently selected month.
        
        Returns:
            Current month in YYYY-MM format.
        """
        return self.current_month
    
    def get_database_session(self):
        """Get a database session.
        
        Returns:
            Database session context manager.
        """
        return db_manager.get_session()
