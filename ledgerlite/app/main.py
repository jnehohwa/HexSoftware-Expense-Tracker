"""Main application entry point for LedgerLite."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ledgerlite.data.db import init_database
from ledgerlite.app.ui.main_window import MainWindow


def main() -> int:
    """Main application entry point.
    
    Returns:
        Exit code.
    """
    # Initialize database
    init_database()
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("LedgerLite")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("HexSoftware")
    
    # Set application icon (if available)
    icon_path = project_root / "assets" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Enable high DPI scaling (deprecated in Qt6, handled automatically)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
