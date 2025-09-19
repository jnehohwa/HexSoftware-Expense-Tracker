"""Categories page for managing transaction categories."""

from typing import Optional, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QColorDialog,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QGridLayout,
    QFrame,
    QScrollArea,
)

from ledgerlite.app.ui.pages.base_page import BasePage
from ledgerlite.app.ui.widgets.category_badge import CategoryBadge
from ledgerlite.data.repo import CategoryRepository, TransactionRepository
from ledgerlite.utils.validators import validate_category_name, validate_color_hex


class CategoryForm(QWidget):
    """Form widget for adding/editing categories."""
    
    def __init__(self, parent: Optional[QWidget] = None, category=None):
        """Initialize the category form.
        
        Args:
            parent: Parent widget.
            category: Category to edit, or None for new category.
        """
        super().__init__(parent)
        self.category = category
        self.setup_ui()
        
        if category:
            self.populate_form()
    
    def setup_ui(self) -> None:
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Category name")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Type field
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["expense", "income"])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Color field
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.current_color = "#3498db"
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        # Parent category field
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("Parent:"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None", None)
        parent_layout.addWidget(self.parent_combo)
        layout.addLayout(parent_layout)
    
    def populate_form(self) -> None:
        """Populate form with category data."""
        if self.category:
            self.name_edit.setText(self.category.name)
            self.type_combo.setCurrentText(self.category.type)
            self.current_color = self.category.color_hex
            self.color_button.setText(f"Color: {self.current_color}")
            self.color_button.setStyleSheet(f"background-color: {self.current_color}; color: white;")
    
    def choose_color(self) -> None:
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self.current_color), self, "Choose Category Color")
        if color.isValid():
            self.current_color = color.name()
            self.color_button.setText(f"Color: {self.current_color}")
            self.color_button.setStyleSheet(f"background-color: {self.current_color}; color: white;")
    
    def get_data(self) -> dict:
        """Get form data.
        
        Returns:
            Dictionary with form data.
        """
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "color_hex": self.current_color,
            "parent_id": self.parent_combo.currentData()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate form data.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        name = self.name_edit.text().strip()
        is_valid, error = validate_category_name(name)
        if not is_valid:
            return False, error
        
        is_valid, error = validate_color_hex(self.current_color)
        if not is_valid:
            return False, error
        
        return True, ""


class CategoriesPage(BasePage):
    """Page for managing categories with color picker and CRUD operations."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the categories page.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
    
    def setup_ui(self) -> None:
        """Set up the categories UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Categories")
        title_label.setObjectName("page-title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_button = QPushButton("Add Category")
        self.add_button.setObjectName("primary-button")
        self.add_button.clicked.connect(self.add_category)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setObjectName("categories-table")
        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.categories_table.setSelectionMode(QTableWidget.SingleSelection)
        self.categories_table.setSortingEnabled(True)
        
        # Set table headers
        headers = ["Name", "Type", "Color", "Usage Count", "Actions"]
        self.categories_table.setColumnCount(len(headers))
        self.categories_table.setHorizontalHeaderLabels(headers)
        
        # Configure header
        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Color
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Usage Count
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.categories_table)
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        # Table double-click
        self.categories_table.itemDoubleClicked.connect(self.edit_category)
    
    def load_data(self) -> None:
        """Load categories data."""
        self.populate_table()
    
    def populate_table(self) -> None:
        """Populate the categories table."""
        session = self.get_database_session()
        try:
            category_repo = CategoryRepository(session)
            transaction_repo = TransactionRepository(session)
            
            categories = category_repo.get_all()
            self.categories_table.setRowCount(len(categories))
            
            for row, category in enumerate(categories):
                # Name
                name_item = QTableWidgetItem(category.name)
                name_item.setData(Qt.UserRole, category.id)
                self.categories_table.setItem(row, 0, name_item)
                
                # Type
                type_item = QTableWidgetItem(category.type.title())
                self.categories_table.setItem(row, 1, type_item)
                
                # Color (badge)
                color_badge = CategoryBadge("", category.color_hex)
                color_badge.setFixedSize(60, 24)
                self.categories_table.setCellWidget(row, 2, color_badge)
                
                # Usage count
                transactions = transaction_repo.get_by_category(category.id)
                usage_count = len(transactions)
                usage_item = QTableWidgetItem(str(usage_count))
                self.categories_table.setItem(row, 3, usage_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                edit_button = QPushButton("Edit")
                edit_button.setObjectName("small-button")
                edit_button.clicked.connect(lambda checked, c=category: self.edit_category(c))
                actions_layout.addWidget(edit_button)
                
                delete_button = QPushButton("Delete")
                delete_button.setObjectName("small-button")
                delete_button.clicked.connect(lambda checked, c=category: self.delete_category(c))
                actions_layout.addWidget(delete_button)
                
                self.categories_table.setCellWidget(row, 4, actions_widget)
        finally:
            session.close()
    
    def add_category(self) -> None:
        """Add a new category."""
        form = CategoryForm(self)
        if self.show_category_dialog(form, "Add Category"):
            self.populate_table()
            self.data_changed.emit()
    
    def edit_category(self, category=None) -> None:
        """Edit a category.
        
        Args:
            category: Category to edit, or None to get from table selection.
        """
        if category is None:
            current_row = self.categories_table.currentRow()
            if current_row < 0:
                return
            
            name_item = self.categories_table.item(current_row, 0)
            if not name_item:
                return
            
            category_id = name_item.data(Qt.UserRole)
            
            session = self.get_database_session()
            try:
                category_repo = CategoryRepository(session)
                category = category_repo.get_by_id(category_id)
                
                if not category:
                    QMessageBox.warning(self, "Error", "Category not found.")
                    return
            finally:
                session.close()
        
        form = CategoryForm(self, category)
        if self.show_category_dialog(form, "Edit Category"):
            self.populate_table()
            self.data_changed.emit()
    
    def show_category_dialog(self, form: CategoryForm, title: str) -> bool:
        """Show category dialog.
        
        Args:
            form: Category form widget.
            title: Dialog title.
            
        Returns:
            True if dialog was accepted.
        """
        from PySide6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(form)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            is_valid, error = form.validate()
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error)
                return False
            
            data = form.get_data()
            self.save_category(data, form.category)
            return True
        
        return False
    
    def save_category(self, data: dict, category=None) -> None:
        """Save category data.
        
        Args:
            data: Category data dictionary.
            category: Category to update, or None for new category.
        """
        session = self.get_database_session()
        try:
            category_repo = CategoryRepository(session)
            
            if category:
                category.name = data["name"]
                category.type = data["type"]
                category.color_hex = data["color_hex"]
                category.parent_id = data["parent_id"]
                category_repo.update(category)
            else:
                category_repo.create(
                    name=data["name"],
                    category_type=data["type"],
                    color_hex=data["color_hex"],
                    parent_id=data["parent_id"]
                )
        finally:
            session.close()
    
    def delete_category(self, category) -> None:
        """Delete a category.
        
        Args:
            category: Category to delete.
        """
        session = self.get_database_session()
        try:
            transaction_repo = TransactionRepository(session)
            transactions = transaction_repo.get_by_category(category.id)
            
            if transactions:
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Category '{category.name}' has {len(transactions)} transactions. "
                    "Are you sure you want to delete it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            category_repo = CategoryRepository(session)
            if category_repo.delete(category.id):
                self.populate_table()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Category deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete category.")
        finally:
            session.close()
    
    def get_database_session(self):
        """Get a database session.
        
        Returns:
            Database session context manager.
        """
        from ledgerlite.data.db import db_manager
        return db_manager.get_session_sync()
