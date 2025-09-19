"""Budget progress widget for displaying budget usage with progress bars."""

from decimal import Decimal
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class BudgetProgressWidget(QWidget):
    """Widget displaying budget progress with color-coded progress bar."""
    
    def __init__(
        self,
        category_name: str,
        spent: Decimal,
        budget: Decimal,
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the budget progress widget.
        
        Args:
            category_name: Name of the category.
            spent: Amount spent.
            budget: Budget amount.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.category_name = category_name
        self.spent = spent
        self.budget = budget
        
        self.setup_ui()
        self.update_progress()
    
    def setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Category name and amounts
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.category_label = QLabel(self.category_name)
        self.category_label.setObjectName("budget-category")
        header_layout.addWidget(self.category_label)
        
        header_layout.addStretch()
        
        self.amount_label = QLabel()
        self.amount_label.setObjectName("budget-amount")
        header_layout.addWidget(self.amount_label)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("budget-progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
    
    def update_progress(self) -> None:
        """Update the progress display."""
        if self.budget <= 0:
            percentage = 0
        else:
            percentage = min(100, float(self.spent / self.budget * 100))
        
        # Update amount label
        self.amount_label.setText(f"${self.spent:,.2f} / ${self.budget:,.2f}")
        
        # Update progress bar
        self.progress_bar.setValue(int(percentage))
        
        # Set color based on percentage
        if percentage >= 100:
            color = "#ff3b30"  # Red
        elif percentage >= 85:
            color = "#ff9500"  # Orange/Amber
        else:
            color = "#34c759"  # Green
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar#budget-progress {{
                border: none;
                border-radius: 4px;
                background-color: #e5e5e7;
                text-align: center;
            }}
            QProgressBar#budget-progress::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
    
    def update_amounts(self, spent: Decimal, budget: Decimal) -> None:
        """Update the spent and budget amounts.
        
        Args:
            spent: New spent amount.
            budget: New budget amount.
        """
        self.spent = spent
        self.budget = budget
        self.update_progress()
    
    def get_percentage(self) -> float:
        """Get the current budget usage percentage.
        
        Returns:
            Budget usage percentage (0-100).
        """
        if self.budget <= 0:
            return 0.0
        return min(100.0, float(self.spent / self.budget * 100))
    
    def is_over_budget(self) -> bool:
        """Check if spending is over budget.
        
        Returns:
            True if spending exceeds budget.
        """
        return self.spent > self.budget
    
    def is_warning_threshold(self) -> bool:
        """Check if spending is at warning threshold (85%).
        
        Returns:
            True if spending is at or above 85% of budget.
        """
        return self.get_percentage() >= 85.0


