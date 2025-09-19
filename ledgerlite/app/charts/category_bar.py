"""Category bar chart widget for displaying expense/income by category."""

from decimal import Decimal
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ledgerlite.data.repo import CategoryRepository, TransactionRepository
from ledgerlite.utils.formatters import currency_formatter


class CategoryBarChart(QWidget):
    """Bar chart widget showing expenses/income by category."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the category bar chart.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setup_ui()
        self.setup_chart()
    
    def setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def setup_chart(self) -> None:
        """Set up the chart configuration."""
        # Configure matplotlib style
        plt.style.use('default')
        
        # Create subplot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Category", fontsize=12)
        self.ax.set_ylabel("Amount", fontsize=12)
        
        # Set background color
        self.ax.set_facecolor('#f8f9fa')
        self.figure.patch.set_facecolor('white')
        
        # Configure grid
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
        self.ax.set_axisbelow(True)
        
        # Configure y-axis formatting
        self.ax.yaxis.set_major_formatter(currency_formatter())
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    
    def update_data(self, month: str) -> None:
        """Update chart with data for the specified month.
        
        Args:
            month: Month in YYYY-MM format.
        """
        # Clear previous data
        self.ax.clear()
        self.setup_chart()
        
        # Get data
        category_data = self.get_category_data(month)
        
        if not category_data:
            self.ax.text(0.5, 0.5, 'No data available', 
                        transform=self.ax.transAxes, 
                        ha='center', va='center', 
                        fontsize=12, color='gray')
            self.canvas.draw()
            return
        
        # Sort data by amount (descending) and limit to top 8
        sorted_data = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_data) > 8:
            # Keep top 7 and aggregate the rest as "Other"
            top_categories = sorted_data[:7]
            other_amount = sum(amount for _, amount in sorted_data[7:])
            if other_amount > 0:
                top_categories.append(("Other", other_amount))
            sorted_data = top_categories
        
        categories = [name for name, _ in sorted_data]
        amounts = [float(amount) for _, amount in sorted_data]
        colors = self.get_category_colors(categories)
        
        # Truncate long category names
        display_categories = []
        for cat in categories:
            if len(cat) > 12:
                display_categories.append(cat[:9] + "...")
            else:
                display_categories.append(cat)
        
        # Create bar chart
        bars = self.ax.bar(display_categories, amounts, color=colors, alpha=0.8, 
                          edgecolor='white', linewidth=1, width=0.6)
        
        # Rotate x-axis labels
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels on bars using bar_label
        self.ax.bar_label(bars, padding=3, fontsize=9, fmt='R %.0f')
        
        # Adjust layout with margins
        self.figure.tight_layout()
        self.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.2)
        
        # Refresh canvas
        self.canvas.draw()
    
    def get_category_data(self, month: str) -> Dict[str, Decimal]:
        """Get category expense data for the specified month.
        
        Args:
            month: Month in YYYY-MM format.
            
        Returns:
            Dictionary mapping category names to total amounts.
        """
        from datetime import datetime, timedelta
        from ledgerlite.data.db import db_manager
        
        # Calculate date range
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        
        category_data = {}
        
        session = db_manager.get_session_sync()
        try:
            category_repo = CategoryRepository(session)
            transaction_repo = TransactionRepository(session)
            
            # Get expense categories
            expense_categories = category_repo.get_by_type("expense")
            
            for category in expense_categories:
                # Get transactions for this category in the date range
                transactions = transaction_repo.get_by_date_range(start_date, end_date)
                category_transactions = [t for t in transactions if t.category_id == category.id and t.type == "expense"]
                
                total_amount = sum(t.amount for t in category_transactions)
                if total_amount > 0:
                    category_data[category.name] = total_amount
        finally:
            session.close()
        
        return category_data
    
    def get_category_colors(self, categories: List[str]) -> List[str]:
        """Get colors for categories.
        
        Args:
            categories: List of category names.
            
        Returns:
            List of hex color codes.
        """
        # Default color palette
        colors = [
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#e67e22', '#34495e', '#f1c40f', '#e91e63'
        ]
        
        # Cycle through colors if we have more categories than colors
        return [colors[i % len(colors)] for i in range(len(categories))]
