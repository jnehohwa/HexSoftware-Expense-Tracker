"""KPI Card widget for displaying key metrics on the dashboard."""

from typing import Literal, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class KpiCard(QWidget):
    """A card widget for displaying key performance indicators.
    
    Args:
        title: The title/label for the metric
        value: The main value to display
        color_role: Semantic color role for the card
        subtitle: Optional subtitle (e.g., delta from previous period)
    """
    
    def __init__(
        self, 
        title: str, 
        value: str, 
        color_role: Literal["positive", "negative", "warning", "neutral"] = "neutral",
        subtitle: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color_role = color_role
        self.subtitle = subtitle
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the card UI."""
        self.setObjectName("KpiCard")
        self.setProperty("role", self.color_role)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("KpiTitle")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.title_label)
        
        # Value label
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("KpiValue")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.value_label)
        
        # Subtitle label (optional)
        if self.subtitle:
            self.subtitle_label = QLabel(self.subtitle)
            self.subtitle_label.setObjectName("KpiSubtitle")
            self.subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            layout.addWidget(self.subtitle_label)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def update_value(self, value: str, subtitle: Optional[str] = None) -> None:
        """Update the card value and optional subtitle.
        
        Args:
            value: New value to display
            subtitle: Optional new subtitle
        """
        self.value = value
        self.value_label.setText(value)
        
        if subtitle is not None:
            self.subtitle = subtitle
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setText(subtitle)
            elif subtitle:
                # Create subtitle label if it doesn't exist
                self.subtitle_label = QLabel(subtitle)
                self.subtitle_label.setObjectName("KpiSubtitle")
                self.subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                self.layout().insertWidget(2, self.subtitle_label)
    
    def update_color_role(self, color_role: Literal["positive", "negative", "warning", "neutral"]) -> None:
        """Update the color role of the card.
        
        Args:
            color_role: New color role
        """
        self.color_role = color_role
        self.setProperty("role", color_role)
        self.style().unpolish(self)
        self.style().polish(self)


