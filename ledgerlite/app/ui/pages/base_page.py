"""Base page class for all application pages."""

from abc import ABC, abstractmethod
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    """Base class for all application pages."""
    
    # Signals
    data_changed = Signal()  # Emitted when page data changes
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the base page.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.load_data()
    
    @abstractmethod
    def setup_ui(self) -> None:
        """Set up the user interface. Must be implemented by subclasses."""
        pass
    
    def setup_connections(self) -> None:
        """Set up signal connections. Can be overridden by subclasses."""
        pass
    
    def load_data(self) -> None:
        """Load page data. Can be overridden by subclasses."""
        pass
    
    def refresh_data(self) -> None:
        """Refresh page data. Can be overridden by subclasses."""
        self.load_data()
    
    def on_month_changed(self, month: str) -> None:
        """Handle month change event.
        
        Args:
            month: New month in YYYY-MM format.
        """
        # Default implementation does nothing
        # Subclasses can override this method
        pass

