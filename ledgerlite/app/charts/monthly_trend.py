"""Monthly trend chart widget for displaying daily net amounts."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ledgerlite.data.repo import TransactionRepository
from ledgerlite.utils.formatters import currency_formatter


class MonthlyTrendChart(QWidget):
    """Line chart widget showing daily net amounts over time."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the monthly trend chart.
        
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
        self.ax.set_xlabel("Date", fontsize=12)
        self.ax.set_ylabel("Net Amount", fontsize=12)
        
        # Set background color
        self.ax.set_facecolor('#f8f9fa')
        self.figure.patch.set_facecolor('white')
        
        # Configure grid
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        self.ax.set_axisbelow(True)
        
        # Add horizontal line at zero
        self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
        
        # Configure date formatting
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
        
        # Configure y-axis formatting
        self.ax.yaxis.set_major_formatter(currency_formatter())
    
    def update_data(self, month: str) -> None:
        """Update chart with data for the specified month.
        
        Args:
            month: Month in YYYY-MM format.
        """
        # Clear previous data
        self.ax.clear()
        self.setup_chart()
        
        # Get data
        daily_data = self.get_daily_data(month)
        
        if not daily_data:
            self.ax.text(0.5, 0.5, 'No data available', 
                        transform=self.ax.transAxes, 
                        ha='center', va='center', 
                        fontsize=12, color='gray')
            self.canvas.draw()
            return
        
        # Prepare data for plotting
        dates = list(daily_data.keys())
        net_amounts = [float(amount) for amount in daily_data.values()]
        
        # Handle outliers using p95 threshold
        if net_amounts:
            p95 = np.percentile(np.abs(net_amounts), 95)
            ylim_max = 1.2 * p95
            
            # Set y-axis limits to show most data clearly
            self.ax.set_ylim(-ylim_max, ylim_max)
            
            # Annotate outliers that exceed the p95 threshold
            for date, amount in zip(dates, net_amounts):
                if abs(amount) > p95:
                    # Position annotation at the top edge of the plot
                    y_pos = ylim_max if amount > 0 else -ylim_max
                    self.ax.annotate(f'R {amount:.0f}', 
                                   (date, y_pos),
                                   textcoords="offset points", 
                                   xytext=(0, 10 if amount > 0 else -10), 
                                   ha='center', 
                                   fontsize=8,
                                   arrowprops=dict(arrowstyle='->', color='red', lw=1),
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9))
        
        # Create line chart
        self.ax.plot(dates, net_amounts, marker='o', linewidth=1.6, markersize=3, 
                    color='#3498db', alpha=0.8)
        
        # Fill area under the curve
        self.ax.fill_between(dates, net_amounts, alpha=0.3, color='#3498db')
        
        # Format x-axis dates
        self.ax.tick_params(axis='x', rotation=45)
        
        # Adjust layout
        self.figure.tight_layout()
        self.figure.subplots_adjust(bottom=0.2)
        
        # Refresh canvas
        self.canvas.draw()
    
    def get_daily_data(self, month: str) -> Dict[datetime, Decimal]:
        """Get daily net amount data for the specified month.
        
        Args:
            month: Month in YYYY-MM format.
            
        Returns:
            Dictionary mapping dates to net amounts.
        """
        from ledgerlite.data.db import db_manager
        
        # Calculate date range
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        
        daily_data = {}
        
        session = db_manager.get_session_sync()
        try:
            transaction_repo = TransactionRepository(session)
            
            # Get all transactions in the date range
            transactions = transaction_repo.get_by_date_range(start_date, end_date)
            
            # Group transactions by date
            daily_transactions = {}
            for transaction in transactions:
                date = transaction.date.date()
                if date not in daily_transactions:
                    daily_transactions[date] = []
                daily_transactions[date].append(transaction)
            
            # Calculate daily net amounts
            current_date = start_date.date()
            while current_date <= end_date.date():
                if current_date in daily_transactions:
                    day_transactions = daily_transactions[current_date]
                    daily_income = sum(t.amount for t in day_transactions if t.type == "income")
                    daily_expense = sum(t.amount for t in day_transactions if t.type == "expense")
                    daily_net = daily_income - daily_expense
                else:
                    daily_net = Decimal("0")
                
                daily_data[datetime.combine(current_date, datetime.min.time())] = daily_net
                current_date += timedelta(days=1)
        finally:
            session.close()
        
        return daily_data
