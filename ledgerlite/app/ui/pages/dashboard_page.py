"""Dashboard page with KPIs and charts."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFrame,
    QScrollArea,
)

from ledgerlite.data.repo import TransactionRepository, BudgetRepository
from ledgerlite.app.ui.pages.base_page import BasePage
from ledgerlite.app.ui.widgets.kpi_card import KpiCard
from ledgerlite.app.charts.category_bar import CategoryBarChart
from ledgerlite.app.charts.monthly_trend import MonthlyTrendChart
from ledgerlite.utils.formatters import format_currency, format_number, format_month_display, format_delta


# KPICard is now imported from widgets


class DashboardPage(BasePage):
    """Dashboard page displaying key metrics and charts."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the dashboard page.
        
        Args:
            parent: Parent widget.
        """
        self.current_month = datetime.now().strftime("%Y-%m")
        super().__init__(parent)
    
    def setup_ui(self) -> None:
        """Set up the dashboard UI."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("Dashboard")
        title_label.setObjectName("page-title")
        main_layout.addWidget(title_label)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # KPI Cards section
        kpi_section = self.create_kpi_section()
        content_layout.addWidget(kpi_section)
        
        # Charts section
        charts_section = self.create_charts_section()
        content_layout.addWidget(charts_section)
        
        # Add stretch to push everything to top
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_kpi_section(self) -> QWidget:
        """Create the KPI cards section.
        
        Returns:
            Widget containing KPI cards.
        """
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setSpacing(10)
        
        # Section title
        title_label = QLabel("Key Metrics")
        title_label.setObjectName("section-title")
        layout.addWidget(title_label)
        
        # KPI cards grid
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(15)
        
        # Create KPI cards (will be populated with data)
        self.income_card = KpiCard("Total Income", "R 0", "positive")
        self.expense_card = KpiCard("Total Expenses", "R 0", "negative")
        self.net_card = KpiCard("Net Amount", "R 0", "neutral")
        self.transaction_card = KpiCard("Transactions", "0", "warning")
        
        kpi_grid.addWidget(self.income_card, 0, 0)
        kpi_grid.addWidget(self.expense_card, 0, 1)
        kpi_grid.addWidget(self.net_card, 1, 0)
        kpi_grid.addWidget(self.transaction_card, 1, 1)
        
        layout.addLayout(kpi_grid)
        
        return section_widget
    
    def create_charts_section(self) -> QWidget:
        """Create the charts section.
        
        Returns:
            Widget containing charts.
        """
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setSpacing(10)
        
        # Section title
        title_label = QLabel("Analytics")
        title_label.setObjectName("section-title")
        layout.addWidget(title_label)
        
        # Charts grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)
        
        # Create chart widgets with titles
        self.category_chart = CategoryBarChart()
        self.trend_chart = MonthlyTrendChart()
        
        # Add chart titles
        category_title = QLabel(f"Expenses by Category — {format_month_display(self.current_month)}")
        category_title.setObjectName("chart-title")
        trend_title = QLabel(f"Daily Net — {format_month_display(self.current_month)}")
        trend_title.setObjectName("chart-title")
        
        charts_grid.addWidget(category_title, 0, 0)
        charts_grid.addWidget(trend_title, 0, 1)
        charts_grid.addWidget(self.category_chart, 1, 0)
        charts_grid.addWidget(self.trend_chart, 1, 1)
        
        layout.addLayout(charts_grid)
        
        return section_widget
    
    def load_data(self) -> None:
        """Load dashboard data."""
        self.update_kpi_cards()
        self.update_charts()
    
    def update_kpi_cards(self) -> None:
        """Update KPI cards with current data."""
        # Get date range for current month
        start_date, end_date = self.get_month_date_range(self.current_month)
        
        # Get transaction totals
        session = self.get_database_session()
        try:
            transaction_repo = TransactionRepository(session)
            income, expense = transaction_repo.get_totals_by_type(start_date, end_date)
            
            # Calculate net amount
            net = income - expense
            
            # Update income card
            self.income_card.update_value(format_currency(income))
            
            # Update expense card
            self.expense_card.update_value(format_currency(expense))
            
            # Update net card with appropriate color
            net_color_role = "positive" if net >= 0 else "negative"
            self.net_card.update_color_role(net_color_role)
            self.net_card.update_value(format_currency(net))
            
            # Update transaction count card
            transaction_count = transaction_repo.get_count_by_date_range(start_date, end_date)
            self.transaction_card.update_value(format_number(transaction_count))
        finally:
            session.close()
    
    def update_charts(self) -> None:
        """Update charts with current data."""
        # Update category chart
        self.category_chart.update_data(self.current_month)
        
        # Update trend chart
        self.trend_chart.update_data(self.current_month)
    
    def get_month_date_range(self, month: str) -> tuple[datetime, datetime]:
        """Get start and end dates for a given month.
        
        Args:
            month: Month in YYYY-MM format.
            
        Returns:
            Tuple of (start_date, end_date).
        """
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        
        # Calculate end date (last day of month)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    def on_month_changed(self, month: str) -> None:
        """Handle month change event.
        
        Args:
            month: New month in YYYY-MM format.
        """
        self.current_month = month
        self.load_data()
    
    def get_database_session(self):
        """Get a database session.
        
        Returns:
            Database session context manager.
        """
        # This will be connected to the main window's database session
        # For now, we'll import and use the global db_manager
        from ledgerlite.data.db import db_manager
        return db_manager.get_session_sync()
