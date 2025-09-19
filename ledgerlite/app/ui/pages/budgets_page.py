"""Budgets page for managing monthly spending limits."""

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ledgerlite.app.ui.pages.base_page import BasePage


class BudgetsPage(BasePage):
    """Page for managing budgets with monthly caps and progress indicators."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the budgets page.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
    
    def setup_ui(self) -> None:
        """Set up the budgets UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Budgets")
        title_label.setObjectName("page-title")
        layout.addWidget(title_label)
        
        # TODO: Implement budgets management UI
        placeholder_label = QLabel("Budgets management will be implemented here")
        layout.addWidget(placeholder_label)
