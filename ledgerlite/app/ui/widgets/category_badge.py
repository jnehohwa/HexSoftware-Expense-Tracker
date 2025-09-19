"""Category badge widget for displaying categories with colors."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel, QWidget


class CategoryBadge(QLabel):
    """A colored badge widget for displaying categories."""
    
    def __init__(
        self,
        text: str,
        color: str = "#3498db",
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the category badge.
        
        Args:
            text: Text to display in the badge.
            color: Hex color code for the badge.
            parent: Parent widget.
        """
        super().__init__(text, parent)
        self.color = color
        self.setObjectName("category-badge")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(24)
        self.setMinimumWidth(60)
        
        # Set up styling
        self.setStyleSheet(f"""
            QLabel#category-badge {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                border: none;
            }}
        """)
    
    def set_color(self, color: str) -> None:
        """Update the badge color.
        
        Args:
            color: New hex color code.
        """
        self.color = color
        self.setStyleSheet(f"""
            QLabel#category-badge {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                border: none;
            }}
        """)
    
    def set_text(self, text: str) -> None:
        """Update the badge text.
        
        Args:
            text: New text to display.
        """
        self.setText(text)
    
    def get_color(self) -> str:
        """Get the current badge color.
        
        Returns:
            Current hex color code.
        """
        return self.color


