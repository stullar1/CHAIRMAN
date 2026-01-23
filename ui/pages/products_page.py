"""
CHAIRMAN - Products & Inventory Management
Professional grade inventory tracking
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QDoubleSpinBox, QComboBox,
    QDialog, QGridLayout
)

from ui.dialogs import StyledMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter

from data.db import get_connection
from core.logging_config import get_logger

logger = get_logger(__name__)


class ProductDialog(QDialog):
    """Dialog for adding/editing products with overlay background."""

    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._setup_ui()

    def showEvent(self, event):
        """Position dialog to cover entire parent window."""
        super().showEvent(event)
        if self.parent():
            main_window = self.parent().window()
            self.setGeometry(main_window.geometry())

    def paintEvent(self, event):
        """Draw semi-transparent dark overlay background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    def mousePressEvent(self, event):
        """Close dialog when clicking outside the form."""
        if hasattr(self, 'container'):
            container_geo = self.container.geometry()
            if not container_geo.contains(event.pos()):
                self.reject()
        super().mousePressEvent(event)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        self.container = QFrame()
        self.container.setObjectName("dialog_container")
        self.container.setFixedSize(480, 580)
        self.container.setStyleSheet("""
            QFrame#dialog_container {
                background-color: #1A1A1A;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            QFrame#dialog_container QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("Edit Product" if self.product else "Add Product")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("x")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Form styling
        input_style = """
            QLineEdit, QComboBox {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                background-color: #282828;
            }
            QDoubleSpinBox {
                background-color: #252525;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                background-color: #282828;
            }
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 30px;
                border: none;
                background-color: #333333;
                border-top-right-radius: 8px;
            }
            QDoubleSpinBox::up-button:hover {
                background-color: #5865F2;
            }
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 30px;
                border: none;
                background-color: #333333;
                border-bottom-right-radius: 8px;
            }
            QDoubleSpinBox::down-button:hover {
                background-color: #5865F2;
            }
            QDoubleSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #AAAAAA;
            }
            QDoubleSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #AAAAAA;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                background-color: #333333;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #AAAAAA;
            }
        """
        label_style = "font-size: 12px; font-weight: bold; color: #888888;"

        # Name
        name_label = QLabel("PRODUCT NAME")
        name_label.setStyleSheet(label_style)
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Premium Hair Gel")
        self.name_input.setMinimumHeight(44)
        self.name_input.setStyleSheet(input_style)
        if self.product:
            self.name_input.setText(self.product.get('name', ''))
        layout.addWidget(self.name_input)

        # Brand
        brand_label = QLabel("BRAND")
        brand_label.setStyleSheet(label_style)
        layout.addWidget(brand_label)

        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("e.g., Professional Co.")
        self.brand_input.setMinimumHeight(44)
        self.brand_input.setStyleSheet(input_style)
        if self.product:
            self.brand_input.setText(self.product.get('brand', ''))
        layout.addWidget(self.brand_input)

        # Category
        category_label = QLabel("CATEGORY")
        category_label.setStyleSheet(label_style)
        layout.addWidget(category_label)

        self.category_input = QComboBox()
        self.category_input.addItems([
            "Hair Gel/Styling", "Shampoo", "Conditioner", "Hair Color/Dye",
            "Bleach", "Toner", "Developer", "Treatment/Mask",
            "Spray/Finishing", "Pomade/Wax", "Oil/Serum", "Tools/Equipment", "Other"
        ])
        self.category_input.setMinimumHeight(44)
        self.category_input.setStyleSheet(input_style)
        if self.product:
            idx = self.category_input.findText(self.product.get('category', ''))
            if idx >= 0:
                self.category_input.setCurrentIndex(idx)
        layout.addWidget(self.category_input)

        # Quantity
        qty_label = QLabel("QUANTITY/WEIGHT (g or ml)")
        qty_label.setStyleSheet(label_style)
        layout.addWidget(qty_label)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 100000)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setSuffix(" g/ml")
        self.quantity_input.setMinimumHeight(44)
        self.quantity_input.setStyleSheet(input_style)
        if self.product:
            self.quantity_input.setValue(self.product.get('quantity', 0))
        layout.addWidget(self.quantity_input)

        # Cost
        cost_label = QLabel("COST ($)")
        cost_label.setStyleSheet(label_style)
        layout.addWidget(cost_label)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 10000)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("$ ")
        self.cost_input.setMinimumHeight(44)
        self.cost_input.setStyleSheet(input_style)
        if self.product:
            self.cost_input.setValue(self.product.get('cost', 0))
        layout.addWidget(self.cost_input)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: bold;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Product" if self.product else "Add Product")
        save_btn.setMinimumHeight(44)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: bold;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
        """)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        outer.addWidget(self.container)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'brand': self.brand_input.text().strip(),
            'category': self.category_input.currentText(),
            'quantity': self.quantity_input.value(),
            'cost': self.cost_input.value()
        }


class ProductCard(QFrame):
    """Professional product card."""

    def __init__(self, product, on_edit, on_delete, on_use, parent=None):
        super().__init__(parent)
        self.product = product
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_use = on_use
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
            QFrame:hover {
                border-color: #5865F2;
                background-color: #222222;
            }
        """)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Top row: Name and actions
        top_row = QHBoxLayout()

        name = QLabel(self.product['name'])
        name.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; border: none;")
        top_row.addWidget(name)

        if self.product.get('brand'):
            brand = QLabel(f"by {self.product['brand']}")
            brand.setStyleSheet("font-size: 13px; color: #666666; border: none;")
            top_row.addWidget(brand)

        top_row.addStretch()

        # Action buttons with press animations
        use_btn = QPushButton("Use")
        use_btn.setFixedSize(50, 30)
        use_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton:pressed {
                background-color: #15803D;
                padding-top: 2px;
            }
        """)
        use_btn.setCursor(Qt.PointingHandCursor)
        use_btn.clicked.connect(lambda: self.on_use(self.product))
        top_row.addWidget(use_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(50, 30)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5865F2;
            }
            QPushButton:pressed {
                background-color: #4752C4;
                padding-top: 2px;
            }
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.on_edit(self.product))
        top_row.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedSize(56, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
            QPushButton:pressed {
                background-color: #DC2626;
                padding-top: 2px;
            }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.on_delete(self.product))
        top_row.addWidget(delete_btn)

        layout.addLayout(top_row)

        # Info row
        info_row = QHBoxLayout()
        info_row.setSpacing(32)

        # Category
        cat = QLabel(f"Category: {self.product.get('category', 'N/A')}")
        cat.setStyleSheet("font-size: 13px; color: #888888; border: none;")
        info_row.addWidget(cat)

        # Quantity - highlight if low
        qty = self.product.get('quantity', 0)
        qty_color = "#22C55E" if qty > 100 else "#F59E0B" if qty > 0 else "#EF4444"
        qty_label = QLabel(f"Stock: {qty:.1f} g/ml")
        qty_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {qty_color}; border: none;")
        info_row.addWidget(qty_label)

        # Cost
        cost = self.product.get('cost', 0)
        cost_label = QLabel(f"${cost:.2f}")
        cost_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #5865F2; border: none;")
        info_row.addWidget(cost_label)

        # Cost per gram
        if qty > 0:
            cpg = cost / qty
            cpg_label = QLabel(f"(${cpg:.4f}/g)")
            cpg_label.setStyleSheet("font-size: 12px; color: #666666; border: none;")
            info_row.addWidget(cpg_label)

        info_row.addStretch()
        layout.addLayout(info_row)


class ProductsPage(QWidget):
    """Professional products management page."""

    def __init__(self):
        super().__init__()
        self._init_database()
        self._setup_ui()
        self._load_products()

    def _init_database(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT,
                    category TEXT,
                    quantity REAL DEFAULT 0,
                    cost REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Products table initialized")
        except Exception as e:
            logger.error(f"Error initializing products table: {e}")

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)

        # Header
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel("Products")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        title_col.addWidget(title)

        subtitle = QLabel("Track inventory and product costs")
        subtitle.setStyleSheet("font-size: 14px; color: #666666;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Product count
        self.count_label = QLabel("0 products")
        self.count_label.setFixedHeight(44)
        self.count_label.setStyleSheet("""
            background-color: #252525;
            border: none;
            border-radius: 8px;
            padding: 0 20px;
            font-size: 14px;
            color: #888888;
        """)
        header.addWidget(self.count_label)

        # Add button
        add_btn = QPushButton("+ Add Product")
        add_btn.setFixedHeight(44)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-weight: bold;
                padding: 0 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
                padding-top: 2px;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_product)
        header.addWidget(add_btn)

        content_layout.addLayout(header)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setMinimumHeight(48)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border-color: #5865F2;
            }
        """)
        self.search_input.textChanged.connect(self._on_search)
        content_layout.addWidget(self.search_input)

        # Products grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.grid_container)
        content_layout.addWidget(scroll, 1)

        layout.addWidget(content)

    def _load_products(self, search_text=""):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if search_text:
                cursor.execute("""
                    SELECT id, name, brand, category, quantity, cost
                    FROM products
                    WHERE name LIKE ? OR brand LIKE ? OR category LIKE ?
                    ORDER BY name
                """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
            else:
                cursor.execute("""
                    SELECT id, name, brand, category, quantity, cost
                    FROM products ORDER BY name
                """)

            products = cursor.fetchall()
            self.count_label.setText(f"{len(products)} product{'s' if len(products) != 1 else ''}")

            if not products:
                empty = QLabel("No products found" if search_text else "No products yet. Click '+ Add Product' to get started.")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet("color: #666666; font-size: 16px; padding: 60px;")
                self.grid_layout.addWidget(empty, 0, 0, 1, 2)
            else:
                for idx, p in enumerate(products):
                    product = {
                        'id': p[0], 'name': p[1], 'brand': p[2],
                        'category': p[3], 'quantity': p[4], 'cost': p[5]
                    }
                    card = ProductCard(product, self._edit_product, self._delete_product, self._use_product)
                    row = idx // 2
                    col = idx % 2
                    self.grid_layout.addWidget(card, row, col)

        except Exception as e:
            logger.error(f"Error loading products: {e}")

    def _on_search(self, text):
        self._load_products(text)

    def _add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                StyledMessageBox.warning(self, "Error", "Please enter a product name")
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, brand, category, quantity, cost)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['name'], data['brand'], data['category'], data['quantity'], data['cost']))
                conn.commit()
                self._load_products(self.search_input.text())
            except Exception as e:
                logger.error(f"Error adding product: {e}")
                StyledMessageBox.error(self, "Error", str(e))

    def _edit_product(self, product):
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                StyledMessageBox.warning(self, "Error", "Please enter a product name")
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE products SET name=?, brand=?, category=?, quantity=?, cost=?
                    WHERE id=?
                """, (data['name'], data['brand'], data['category'], data['quantity'], data['cost'], product['id']))
                conn.commit()
                self._load_products(self.search_input.text())
            except Exception as e:
                logger.error(f"Error updating product: {e}")
                StyledMessageBox.error(self, "Error", str(e))

    def _delete_product(self, product):
        confirmed = StyledMessageBox.question(
            self, "Delete Product",
            f"Are you sure you want to delete '{product['name']}'?"
        )
        if confirmed:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id=?", (product['id'],))
                conn.commit()
                self._load_products(self.search_input.text())
            except Exception as e:
                logger.error(f"Error deleting product: {e}")
                StyledMessageBox.error(self, "Error", str(e))

    def _use_product(self, product):
        """Record product usage."""
        from PySide6.QtWidgets import QInputDialog

        amount, ok = QInputDialog.getDouble(
            self, "Use Product",
            f"How much of '{product['name']}' did you use? (g/ml)",
            0, 0, product.get('quantity', 0), 2
        )
        if ok and amount > 0:
            try:
                new_qty = max(0, product.get('quantity', 0) - amount)
                cost_used = (product.get('cost', 0) / product.get('quantity', 1)) * amount if product.get('quantity', 0) > 0 else 0

                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_qty, product['id']))
                conn.commit()

                StyledMessageBox.success(
                    self, "Usage Recorded",
                    f"Used: {amount:.2f} g/ml\nCost: ${cost_used:.2f}\nRemaining: {new_qty:.2f} g/ml"
                )
                self._load_products(self.search_input.text())
            except Exception as e:
                logger.error(f"Error recording usage: {e}")
                StyledMessageBox.error(self, "Error", str(e))
