import datetime
import requests
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QListWidget, QListWidgetItem,
                               QFrame, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QMessageBox,
                               QFormLayout, QDialog, QLineEdit, QDialogButtonBox, QScrollArea,
                               QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QTabWidget, QSpinBox, QComboBox,
                               QDateEdit)
from PySide6.QtGui import QIcon, QPixmap, QColor, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QSize
from pathlib import Path


class SupplierWindow(QMainWindow):
    def __init__(self, token_data):
        super().__init__()
        self.token_data = token_data
        self.supplier_id = token_data.get('supplier_id')
        self.access_token = token_data.get('access_token')
        self.sales_data = []  # <-- Добавлено инициализацию атрибута

        if "supplier_id" not in token_data:
            QMessageBox.warning(self, "Предупреждение",
                                "ID поставщика не найден. Некоторые функции могут быть недоступны.")
        self.token_data = token_data
        self.setWindowTitle("АИС 'Сифон' - Поставщик")
        self.setFixedSize(1280, 768)

        # Базовый URL API
        self.api_url = "http://localhost:8000"

        # Пути к иконкам
        self.icon_dir = Path(__file__).parent / "icons"

        # Основной стек виджетов
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Создаем виджеты для разных разделов
        self.products_widget = self.create_products_widget()
        self.profile_widget = self.create_profile_widget()
        self.stats_widget = self.create_stats_widget()

        self.stack.addWidget(self.products_widget)
        self.stack.addWidget(self.profile_widget)
        self.stack.addWidget(self.stats_widget)

        # Создаем навигационное меню
        self.create_navigation()

        # Загружаем товары поставщика
        self.load_supplier_products()

        # Стилизация
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QFrame.section-frame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 15px;
            }
            .title-label {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
            .product-title {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            .product-price {
                font-size: 18px;
                color: #e74c3c;
                font-weight: bold;
            }
            .success-button {
                background-color: #2ecc71;
            }
                .success-button:hover {
                background-color: #27ae60;
            }
            .danger-button {
                background-color: #e74c3c;
            }
            .danger-button:hover {
                background-color: #c0392b;
            }
            .warning-button {
                background-color: #f39c12;
            }
            .warning-button:hover {
                background-color: #d35400;
            }
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: none;
            }
            QMenuBar {
                background-color: transparent;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 8px 15px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #2980b9;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

    def get_auth_headers(self):
        """Возвращает заголовки с токеном авторизации"""
        return {
            "Authorization": f"Bearer {self.token_data['access_token']}",
            "Content-Type": "application/json"
        }

    def create_navigation(self):
        """Создает навигационную панель"""
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        menubar.setCornerWidget(spacer)

        menu = menubar.addMenu("Меню")

        products_action = menu.addAction("Мои товары")
        products_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.products_widget))

        stats_action = menu.addAction("Статистика")
        stats_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.stats_widget))

        profile_action = menu.addAction("Профиль")
        profile_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.profile_widget))

    def load_supplier_products(self):
        """Загружает товары поставщика"""
        try:
            supplier_id = self.token_data.get("supplier_id")
            if not supplier_id:
                QMessageBox.warning(self, "Ошибка", "ID поставщика не найден")
                return

            response = requests.get(
                f"{self.api_url}/products/supplier/{supplier_id}",
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                self.supplier_products = response.json()
                self.update_products_list()
            else:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось загрузить товары. Код ошибки: {response.status_code}")
                self.supplier_products = []
                self.update_products_list()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")
            self.supplier_products = []
            self.update_products_list()

    def update_products_list(self):
        """Обновляет список товаров"""
        if hasattr(self, 'products_list_widget'):
            self.products_list_widget.clear()

            if not self.supplier_products:
                item = QListWidgetItem()
                widget = QLabel("Нет товаров")
                widget.setAlignment(Qt.AlignCenter)
                widget.setStyleSheet("color: #7f8c8d; font-size: 14px;")
                self.products_list_widget.addItem(item)
                self.products_list_widget.setItemWidget(item, widget)
                return

            for product in self.supplier_products:
                item = QListWidgetItem()
                card = self.create_product_card(product)
                item.setSizeHint(card.sizeHint())
                self.products_list_widget.addItem(item)
                self.products_list_widget.setItemWidget(item, card)

    def create_product_card(self, product):
        """Создает карточку товара"""
        card = QFrame()
        card.setObjectName("product-card")
        card.setStyleSheet("""
            QFrame#product-card {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 8px;
            }
        """)
        card.setFixedHeight(150)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Блок с изображением
        icon_frame = QFrame()
        icon_frame.setFixedSize(80, 80)
        icon_frame.setStyleSheet("""
            background-color: #f9f9f9;
            border-radius: 8px;
            border: 1px solid #eee;
        """)

        icon_layout = QVBoxLayout(icon_frame)
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(str(self.icon_dir / "products.png")).scaled(60, 60, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)

        # Информация о товаре
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)

        name_label = QLabel(product.get("name", "Без названия"))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        name_label.setWordWrap(True)

        desc_label = QLabel(product.get("description", "Описание отсутствует"))
        desc_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        desc_label.setWordWrap(True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        info_layout.addStretch()

        # Статистика товара
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(5)

        price_label = QLabel(f"Цена: {float(product.get('price', 0)):,.2f} ₽".replace(",", " "))
        price_label.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: bold;")

        stock_label = QLabel(f"Остаток: {product.get('stock_quantity', 0)} шт.")
        stock_label.setStyleSheet("font-size: 14px; color: #3498db;")

        sold_label = QLabel(f"Продано: {product.get('sold_quantity', 0)} шт.")
        sold_label.setStyleSheet("font-size: 14px; color: #2ecc71;")

        stats_layout.addWidget(price_label)
        stats_layout.addWidget(stock_label)
        stats_layout.addWidget(sold_label)
        stats_layout.addStretch()

        # Удалены кнопки "Изменить" и "Обновить склад"

        # Собираем все вместе
        layout.addWidget(icon_frame)
        layout.addWidget(info_widget, stretch=1)
        layout.addWidget(stats_widget)

        return card

    def edit_product(self, product):
        """Редактирование товара"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование товара")
        dialog.setFixedSize(400, 450)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Название
        name_edit = QLineEdit(product.get("name", ""))
        name_edit.setPlaceholderText("Название товара")
        form_layout.addRow("Название:", name_edit)

        # Описание
        desc_edit = QTextEdit()
        desc_edit.setPlainText(product.get("description", ""))
        desc_edit.setPlaceholderText("Описание товара")
        desc_edit.setFixedHeight(100)
        form_layout.addRow("Описание:", desc_edit)

        # Цена
        price_edit = QLineEdit(str(product.get("price", 0)))
        price_edit.setPlaceholderText("Цена")
        price_edit.setValidator(QDoubleValidator(0, 999999, 2))
        form_layout.addRow("Цена:", price_edit)

        # Категория
        category_edit = QLineEdit(str(product.get("category_id", 0)))
        category_edit.setPlaceholderText("Категория")
        form_layout.addRow("Категория:", category_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted:
            updated_data = {
                "name": name_edit.text(),
                "description": desc_edit.toPlainText(),
                "price": float(price_edit.text()),
                "category_id": int(category_edit.text()),
                "supplier_id": product.get("supplier_id", 0),
                "stock_quantity": product.get("stock_quantity", 0)
            }

            try:
                response = requests.put(
                    f"{self.api_url}/products/{product['id']}",
                    json=updated_data,
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Товар успешно обновлен")
                    self.load_supplier_products()
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось обновить товар. Код ошибки: {response.status_code}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")

    def update_product_stock(self, product):
        """Обновление количества товара на складе"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Обновление остатка")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout(dialog)

        current_label = QLabel(f"Текущий остаток: {product.get('stock_quantity', 0)} шт.")
        current_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(current_label, alignment=Qt.AlignCenter)

        form_layout = QFormLayout()
        quantity_edit = QLineEdit()
        quantity_edit.setPlaceholderText("Новое количество")
        quantity_edit.setValidator(QIntValidator(0, 999999))
        form_layout.addRow("Количество:", quantity_edit)

        layout.addLayout(form_layout)

        note_label = QLabel("Укажите абсолютное количество, а не изменение")
        note_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        note_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(note_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted and quantity_edit.text():
            try:
                response = requests.patch(
                    f"{self.api_url}/products/{product['id']}/stock",
                    json={"stock_quantity": int(quantity_edit.text())},
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Остаток товара обновлен")
                    self.load_supplier_products()
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось обновить остаток. Код ошибки: {response.status_code}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")

    def create_products_widget(self):
        """Создает виджет списка товаров"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Заголовок и кнопки
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Мои товары")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setIcon(QIcon(str(self.icon_dir / "refresh.png")))
        refresh_btn.clicked.connect(self.load_supplier_products)
        header_layout.addWidget(refresh_btn)

        layout.addWidget(header_widget)

        # Список товаров
        self.products_list_widget = QListWidget()
        self.products_list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.products_list_widget.setSpacing(10)
        self.products_list_widget.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(self.products_list_widget)

        return widget

    def add_new_product(self):
        """Добавление нового товара"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление товара")
        dialog.setFixedSize(400, 500)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Название
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название товара")
        form_layout.addRow("Название:", name_edit)

        # Описание
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("Описание товара")
        desc_edit.setFixedHeight(100)
        form_layout.addRow("Описание:", desc_edit)

        # Цена
        price_edit = QLineEdit()
        price_edit.setPlaceholderText("Цена")
        price_edit.setValidator(QDoubleValidator(0, 999999, 2))
        form_layout.addRow("Цена:", price_edit)

        # Категория
        category_edit = QLineEdit()
        category_edit.setPlaceholderText("Категория")
        form_layout.addRow("Категория:", category_edit)

        # Количество на складе
        stock_edit = QLineEdit("0")
        stock_edit.setPlaceholderText("Количество")
        stock_edit.setValidator(QIntValidator(0, 999999))
        form_layout.addRow("Количество на складе:", stock_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted:
            new_product = {
                "name": name_edit.text(),
                "description": desc_edit.toPlainText(),
                "price": float(price_edit.text()),
                "category_id": int(category_edit.text()),
                "supplier_id": self.token_data.get("supplier_id"),
                "stock_quantity": int(stock_edit.text())
            }

            try:
                response = requests.post(
                    f"{self.api_url}/products/",
                    json=new_product,
                    headers=self.get_auth_headers()
                )

                if response.status_code == 201:
                    QMessageBox.information(self, "Успех", "Товар успешно добавлен")
                    self.load_supplier_products()
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось добавить товар. Код ошибки: {response.status_code}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")

    def create_profile_widget(self):
        """Создает виджет профиля поставщика, который занимает все окно"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Стиль для виджета
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                padding: 5px 0;
            }
            QFrame#profile-frame {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                border: none;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            QLabel[fieldName="true"] {
                font-size: 14px;
                color: #7f8c8d;
                font-weight: bold;
                padding: 6px 0;
            }
            QLabel[fieldValue="true"] {
                font-size: 15px;
                color: #2c3e50;
                padding: 6px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            QPushButton#edit-btn {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-width: 200px;
            }
            QPushButton#edit-btn:hover {
                background-color: #2980b9;
            }
            QPushButton#edit-btn:pressed {
                background-color: #1d6fa5;
            }
        """)

        # Заголовок профиля
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Профиль поставщика")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title.setObjectName("title")
        title_layout.addWidget(title, alignment=Qt.AlignLeft)
        title_layout.addStretch()

        layout.addWidget(title_container)

        # Основной контейнер для профиля
        profile_frame = QFrame()
        profile_frame.setObjectName("profile-frame")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setSpacing(15)

        supplier_id = self.token_data.get("supplier_id")
        if not supplier_id:
            error_label = QLabel("ID поставщика не найден. Невозможно загрузить данные профиля.")
            error_label.setStyleSheet("""
                color: #e74c3c;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 0;
            """)
            profile_layout.addWidget(error_label)
        else:
            try:
                # Загружаем данные пользователя с сервера
                response = requests.get(
                    f"{self.api_url}/suppliers/{supplier_id}",
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    supplier_data = response.json()

                    # Создаем форму для отображения данных
                    form_layout = QFormLayout()
                    form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
                    form_layout.setHorizontalSpacing(25)
                    form_layout.setVerticalSpacing(10)

                    # Функция для создания строк формы с иконками
                    def add_form_row(label_text, value_text, icon_name):
                        row_widget = QWidget()
                        row_layout = QHBoxLayout(row_widget)
                        row_layout.setContentsMargins(0, 0, 0, 0)
                        row_layout.setSpacing(10)

                        # Иконка
                        icon_label = QLabel()
                        icon_label.setPixmap(QPixmap(str(self.icon_dir / icon_name)).scaled(20, 20, Qt.KeepAspectRatio))
                        row_layout.addWidget(icon_label)

                        # Название поля
                        label = QLabel(label_text)
                        label.setProperty("fieldName", "true")
                        label.setFixedWidth(120)
                        row_layout.addWidget(label)

                        # Значение
                        value = QLabel(value_text or "Не указано")
                        value.setProperty("fieldValue", "true")
                        value.setWordWrap(True)
                        row_layout.addWidget(value, stretch=1)

                        form_layout.addRow(row_widget)

                    # Добавляем строки с иконками
                    add_form_row("Компания:", supplier_data.get("name"), "company.png")
                    add_form_row("Контакт:", supplier_data.get("contact_person"), "person.png")
                    add_form_row("Телефон:", supplier_data.get("phone"), "phone.png")
                    add_form_row("Email:", supplier_data.get("email"), "email.png")
                    add_form_row("Адрес:", supplier_data.get("address"), "address.png")

                    profile_layout.addLayout(form_layout)

                    # Кнопка редактирования
                    edit_btn = QPushButton("Редактировать профиль")
                    edit_btn.setObjectName("edit-btn")
                    edit_btn.setIcon(QIcon(str(self.icon_dir / "edit.png")))
                    edit_btn.setIconSize(QSize(16, 16))
                    edit_btn.clicked.connect(lambda: self.edit_supplier_profile(supplier_data))
                    profile_layout.addWidget(edit_btn, alignment=Qt.AlignRight)

                elif response.status_code == 404:
                    error_label = QLabel("Профиль поставщика не найден на сервере.")
                    error_label.setStyleSheet("""
                        color: #e74c3c;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 10px 0;
                    """)
                    profile_layout.addWidget(error_label)
                else:
                    error_label = QLabel(f"Ошибка загрузки профиля (код {response.status_code})")
                    error_label.setStyleSheet("""
                        color: #e74c3c;
                        font-weight: bold;
                        font-size: 14px;
                        padding: 10px 0;
                    """)
                    profile_layout.addWidget(error_label)

            except requests.exceptions.RequestException as e:
                error_label = QLabel(f"Ошибка подключения к серверу: {str(e)}")
                error_label.setStyleSheet("""
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 0;
                """)
                profile_layout.addWidget(error_label)

        layout.addWidget(profile_frame, stretch=1)
        return widget

    def edit_supplier_profile(self, supplier_data):
        """Редактирование профиля поставщика"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование профиля")
        dialog.setFixedSize(400, 500)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Название компании
        company_edit = QLineEdit(supplier_data.get("name", ""))
        company_edit.setPlaceholderText("Название компании")
        form_layout.addRow("Название компании:", company_edit)

        # Контактное лицо
        contact_edit = QLineEdit(supplier_data.get("contact_person", ""))
        contact_edit.setPlaceholderText("Контактное лицо")
        form_layout.addRow("Контактное лицо:", contact_edit)

        # Телефон
        phone_edit = QLineEdit(supplier_data.get("phone", ""))
        phone_edit.setPlaceholderText("Телефон")
        form_layout.addRow("Телефон:", phone_edit)

        # Email
        email_edit = QLineEdit(supplier_data.get("email", ""))
        email_edit.setPlaceholderText("Email")
        form_layout.addRow("Email:", email_edit)

        # Адрес
        address_edit = QTextEdit()
        address_edit.setPlainText(supplier_data.get("address", ""))
        address_edit.setPlaceholderText("Адрес")
        address_edit.setFixedHeight(80)
        form_layout.addRow("Адрес:", address_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted:
            updated_data = {
                "name": company_edit.text(),
                "contact_person": contact_edit.text(),
                "phone": phone_edit.text(),
                "email": email_edit.text(),
                "address": address_edit.toPlainText(),
                "username": supplier_data.get("username", ""),
                "password": supplier_data.get("password", "")
            }

            try:
                response = requests.put(
                    f"{self.api_url}/suppliers/{supplier_data['id']}",
                    json=updated_data,
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Профиль успешно обновлен")
                    # Обновляем данные в текущем виджете профиля
                    self.update_profile_data(updated_data)
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось обновить профиль. Код ошибки: {response.status_code}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")

    def update_profile_data(self, new_data):
        """Обновляет данные профиля без пересоздания виджета"""
        # Находим все QLabel в виджете профиля и обновляем их
        for widget in self.profile_widget.findChildren(QLabel):
            if widget.property("fieldValue"):
                field_name = widget.text().replace(":", "").strip().lower()
                if field_name == "название компании":
                    widget.setText(new_data.get("name", "Не указано"))
                elif field_name == "контактное лицо":
                    widget.setText(new_data.get("contact_person", "Не указано"))
                elif field_name == "телефон":
                    widget.setText(new_data.get("phone", "Не указано"))
                elif field_name == "email":
                    widget.setText(new_data.get("email", "Не указано"))
                elif field_name == "адрес":
                    widget.setText(new_data.get("address", "Не указано"))

        # Принудительно обновляем виджет профиля
        self.profile_widget.update()

    def create_stats_widget(self):
        """Создает виджет статистики продаж"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Статистика продаж")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title, alignment=Qt.AlignLeft)

        # Фильтры по дате
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(15)

        # Период
        period_label = QLabel("Период:")
        filter_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "За последнюю неделю",
            "За последний месяц",
            "За последний квартал",
            "За последний год",
            "За все время",
            "Произвольный период"
        ])
        self.period_combo.currentIndexChanged.connect(self.update_date_inputs)
        filter_layout.addWidget(self.period_combo)

        # Даты начала и конца
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(datetime.date.today() - datetime.timedelta(days=30))
        self.start_date_edit.setEnabled(False)
        filter_layout.addWidget(QLabel("с:"))
        filter_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(datetime.date.today())
        self.end_date_edit.setEnabled(False)
        filter_layout.addWidget(QLabel("по:"))
        filter_layout.addWidget(self.end_date_edit)

        # Кнопка применения
        apply_btn = QPushButton("Применить")
        apply_btn.setIcon(QIcon(str(self.icon_dir / "refresh.png")))
        apply_btn.clicked.connect(self.load_sales_data)
        filter_layout.addWidget(apply_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_widget)

        # Вкладки для разных видов статистики
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 1. Сводная статистика
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_tab)
        self.tab_widget.addTab(self.summary_tab, "Сводка")

        # 2. Детализация по товарам
        self.products_tab = QWidget()
        self.products_layout = QVBoxLayout(self.products_tab)
        self.tab_widget.addTab(self.products_tab, "По товарам")

        # 3. Графики
        self.charts_tab = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_tab)
        self.tab_widget.addTab(self.charts_tab, "Графики")

        # Загружаем данные
        self.load_sales_data()

        return widget

    def load_sales_data(self):
        """Загружает данные о продажах"""
        supplier_id = self.token_data.get("supplier_id")
        if not supplier_id:
            QMessageBox.warning(self, "Ошибка", "ID поставщика не найден")
            return

        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        # Проверка, что начальная дата не позже конечной
        if start_date > end_date:
            QMessageBox.warning(self, "Ошибка", "Начальная дата не может быть позже конечной")
            return

        try:
            # Получаем даты из интерфейса
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            # Добавляем параметры в URL
            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            print(f"Requesting data for period: {start_date} to {end_date}")  # Для отладки

            response = requests.get(
                f"{self.api_url}/order-details/supplier/{supplier_id}",
                params=params,
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                sales_data = response.json()
                self.process_sales_data(sales_data)
            else:
                error_msg = f"Не удалось загрузить статистику продаж. Код ошибки: {response.status_code}"
                if response.status_code == 404:
                    error_msg += "\nВозможно, нет данных за выбранный период"
                QMessageBox.warning(self, "Ошибка", error_msg)
                self.clear_stats()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")
            self.clear_stats()

    def process_sales_data(self, sales_data):
        """Обрабатывает данные о продажах и обновляет интерфейс"""
        # Сохраняем данные о продажах в атрибуте класса
        self.sales_data = sales_data  # <-- Добавлено сохранение данных

        if not sales_data:
            self.clear_stats()
            QMessageBox.information(self, "Информация", "Нет данных о продажах за выбранный период")
            return

        # Агрегируем данные
        total_sales = len(sales_data)
        total_quantity = sum(item['quantity'] for item in sales_data)
        total_revenue = sum(item['quantity'] * item['price_per_unit'] for item in sales_data)
        unique_products = len({item['product_id'] for item in sales_data})
        unique_orders = len({item['order_id'] for item in sales_data})

        # Обновляем сводную статистику
        self.update_summary_stats(total_sales, total_quantity, total_revenue, unique_products, unique_orders)

        # Обновляем статистику по товарам
        self.update_products_stats(sales_data)

        # Обновляем графики
        self.update_charts(sales_data)

    def clear_stats(self):
        """Очищает все статистические данные"""
        # Очищаем сводную статистику
        for i in reversed(range(self.summary_layout.count())):
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Очищаем статистику по товарам
        for i in reversed(range(self.products_layout.count())):
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Очищаем графики
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Добавляем сообщение об отсутствии данных
        no_data_label = QLabel("Нет данных для отображения")
        no_data_label.setAlignment(Qt.AlignCenter)
        no_data_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        self.summary_layout.addWidget(no_data_label)

    def update_summary_stats(self, total_sales, total_quantity, total_revenue, unique_products, unique_orders):
        """Обновляет вкладку сводной статистики с упрощенными карточками"""
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.summary_layout.count())):
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Создаем карточки статистики
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(15)

        # Карточка количества продаж
        sales_card = self.create_stat_card(
            "Всего продаж",
            str(total_sales),
            "#3498db"
        )
        cards_layout.addWidget(sales_card)

        # Карточка количества товаров
        products_card = self.create_stat_card(
            "Уникальных товаров",
            str(unique_products),
            "#9b59b6"
        )
        cards_layout.addWidget(products_card)

        # Карточка количества заказов
        orders_card = self.create_stat_card(
            "Уникальных заказов",
            str(unique_orders),
            "#f39c12"
        )
        cards_layout.addWidget(orders_card)

        # Карточка выручки
        revenue_card = self.create_stat_card(
            "Общая выручка",
            f"{total_revenue:,.2f} ₽".replace(",", " "),
            "#2ecc71"
        )
        cards_layout.addWidget(revenue_card)

        # Карточка количества проданных единиц
        quantity_card = self.create_stat_card(
            "Проданные единицы",
            str(total_quantity),
            "#e74c3c"
        )
        cards_layout.addWidget(quantity_card)

        self.summary_layout.addWidget(cards_container)

        # Таблица с последними продажами (остается без изменений)
        recent_label = QLabel("Последние продажи:")
        recent_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        self.summary_layout.addWidget(recent_label)

        recent_table = QTableWidget()
        recent_table.setColumnCount(5)
        recent_table.setHorizontalHeaderLabels(["Дата", "Товар", "Количество", "Цена", "Сумма"])
        recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_table.verticalHeader().setVisible(False)
        recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        recent_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Заполняем таблицу (первые 10 записей)
        recent_table.setRowCount(min(10, len(self.sales_data)))
        for row, item in enumerate(self.sales_data[:10]):
            # Универсальная обработка даты
            date_str = item.get("order_date", "")
            formatted_date = self.format_date(date_str)
            date_item = QTableWidgetItem(formatted_date)
            recent_table.setItem(row, 0, date_item)

            # Остальные колонки без изменений
            product_item = QTableWidgetItem(item.get("product_name", "Неизвестно"))
            recent_table.setItem(row, 1, product_item)

            quantity_item = QTableWidgetItem(str(item.get("quantity", 0)))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            recent_table.setItem(row, 2, quantity_item)

            price_item = QTableWidgetItem(f"{item.get('price_per_unit', 0):,.2f} ₽".replace(",", " "))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            recent_table.setItem(row, 3, price_item)

            total = item.get("quantity", 0) * item.get("price_per_unit", 0)
            total_item = QTableWidgetItem(f"{total:,.2f} ₽".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            recent_table.setItem(row, 4, total_item)

        self.summary_layout.addWidget(recent_table)

    def format_date(self, date_str):
        """Форматирует дату из строки в единый формат"""
        if not date_str:
            return "Нет данных"

        # Удаляем 'Z' в конце, если есть (UTC обозначение)
        clean_date = date_str.rstrip('Z')

        # Список возможных форматов даты
        date_formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO с миллисекундами
            "%Y-%m-%dT%H:%M:%S",  # ISO без миллисекунд
            "%Y-%m-%d %H:%M:%S",  # Альтернативный формат
            "%Y-%m-%d",  # Только дата
            "%d.%m.%Y %H:%M",  # Русский формат
            "%m/%d/%Y %H:%M:%S",  # Американский формат
        ]

        for fmt in date_formats:
            try:
                dt = datetime.datetime.strptime(clean_date, fmt)
                return dt.strftime("%d.%m.%Y %H:%M")  # Единый выходной формат
            except ValueError:
                continue

        # Если ни один формат не подошел, возвращаем исходную строку
        return date_str

    def update_products_stats(self, sales_data):
        """Обновляет статистику по товарам"""
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.products_layout.count())):
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Группируем данные по товарам
        products_stats = {}
        for item in sales_data:
            product_id = item['product_id']
            if product_id not in products_stats:
                products_stats[product_id] = {
                    'name': item['product_name'],
                    'quantity': 0,
                    'revenue': 0.0,
                    'orders': set()
                }

            products_stats[product_id]['quantity'] += item['quantity']
            products_stats[product_id]['revenue'] += item['quantity'] * item['price_per_unit']
            products_stats[product_id]['orders'].add(item['order_id'])

        # Преобразуем в список и сортируем по выручке
        products_list = []
        for product_id, stats in products_stats.items():
            products_list.append({
                'id': product_id,
                'name': stats['name'],
                'quantity': stats['quantity'],
                'revenue': stats['revenue'],
                'orders_count': len(stats['orders']),
                'avg_price': stats['revenue'] / stats['quantity'] if stats['quantity'] > 0 else 0
            })

        products_list.sort(key=lambda x: x['revenue'], reverse=True)

        # Создаем таблицу
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Товар", "Продажи", "Заказы", "Выручка", "Ср. цена", "Доля выручки"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        # Рассчитываем общую выручку для вычисления долей
        total_revenue = sum(p['revenue'] for p in products_list)

        # Заполняем таблицу
        table.setRowCount(len(products_list))
        for row, product in enumerate(products_list):
            # Товар
            name_item = QTableWidgetItem(product['name'])
            table.setItem(row, 0, name_item)

            # Количество
            quantity_item = QTableWidgetItem(str(product['quantity']))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, quantity_item)

            # Заказы
            orders_item = QTableWidgetItem(str(product['orders_count']))
            orders_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, orders_item)

            # Выручка
            revenue_item = QTableWidgetItem(f"{product['revenue']:,.2f} ₽".replace(",", " "))
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, revenue_item)

            # Средняя цена
            avg_price_item = QTableWidgetItem(f"{product['avg_price']:,.2f} ₽".replace(",", " "))
            avg_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 4, avg_price_item)

            # Доля выручки
            share = product['revenue'] / total_revenue if total_revenue > 0 else 0
            share_item = QTableWidgetItem(f"{share:.1%}")
            share_item.setTextAlignment(Qt.AlignCenter)

            # Цвет в зависимости от доли
            if share >= 0.3:
                share_item.setForeground(QColor("#2ecc71"))  # зеленый
            elif share >= 0.1:
                share_item.setForeground(QColor("#f39c12"))  # оранжевый
            else:
                share_item.setForeground(QColor("#e74c3c"))  # красный

            table.setItem(row, 5, share_item)

        self.products_layout.addWidget(table)

    def update_charts(self, sales_data):
        """Обновляет вкладку с графиками"""
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not sales_data:
            no_data_label = QLabel("Нет данных для построения графиков")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
            self.charts_layout.addWidget(no_data_label)
            return

        # Группируем данные по дням
        daily_stats = {}
        for item in sales_data:
            date_str = item.get("order_date", "")
            try:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            except ValueError:
                continue

            if date not in daily_stats:
                daily_stats[date] = {
                    'quantity': 0,
                    'revenue': 0.0,
                    'orders': set()
                }

            daily_stats[date]['quantity'] += item['quantity']
            daily_stats[date]['revenue'] += item['quantity'] * item['price_per_unit']
            daily_stats[date]['orders'].add(item['order_id'])

        # Сортируем по дате
        sorted_dates = sorted(daily_stats.keys())

        # Подготавливаем данные для графиков
        dates = [date.strftime("%d.%m") for date in sorted_dates]
        quantities = [daily_stats[date]['quantity'] for date in sorted_dates]
        revenues = [daily_stats[date]['revenue'] for date in sorted_dates]
        orders = [len(daily_stats[date]['orders']) for date in sorted_dates]

        # Создаем виджеты с графиками
        charts_container = QWidget()
        charts_container_layout = QVBoxLayout(charts_container)

        # 1. График выручки
        revenue_chart = QLabel("График выручки по дням")
        revenue_chart.setAlignment(Qt.AlignCenter)
        revenue_chart.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 50px;
            color: #7f8c8d;
            font-size: 16px;
        """)
        # Здесь должна быть реальная реализация графика с использованием QChart или matplotlib
        charts_container_layout.addWidget(revenue_chart)

        # 2. График количества продаж
        quantity_chart = QLabel("График количества продаж по дням")
        quantity_chart.setAlignment(Qt.AlignCenter)
        quantity_chart.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 50px;
            color: #7f8c8d;
            font-size: 16px;
            margin-top: 15px;
        """)
        charts_container_layout.addWidget(quantity_chart)

        self.charts_layout.addWidget(charts_container)

    def update_date_inputs(self):
        """Обновляет даты в зависимости от выбранного периода"""
        period_index = self.period_combo.currentIndex()
        today = datetime.date.today()

        if period_index == 5:  # Произвольный период
            self.start_date_edit.setEnabled(True)
            self.end_date_edit.setEnabled(True)
            return

        self.start_date_edit.setEnabled(False)
        self.end_date_edit.setEnabled(False)

        if period_index == 0:  # неделя
            start_date = today - datetime.timedelta(days=7)
        elif period_index == 1:  # месяц
            start_date = today - datetime.timedelta(days=30)
        elif period_index == 2:  # квартал
            start_date = today - datetime.timedelta(days=90)
        elif period_index == 3:  # год
            start_date = today - datetime.timedelta(days=365)
        else:  # все время
            start_date = datetime.date(2000, 1, 1)  # Начальная дата

        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(today)

    def update_sales_stats(self):
        """Обновляет статистику продаж"""
        supplier_id = self.token_data.get("supplier_id")
        if not supplier_id:
            QMessageBox.warning(self, "Ошибка", "ID поставщика не найден")
            return

        # Определяем период
        period_index = self.period_combo.currentIndex()
        if period_index == 0:  # неделя
            start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        elif period_index == 1:  # месяц
            start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        elif period_index == 2:  # год
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        else:  # все время
            start_date = "2000-01-01"  # Условная дата

        try:
            # Загружаем данные о продажах
            response = requests.get(
                f"{self.api_url}/order-details/supplier/{supplier_id}?start_date={start_date}",
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                sales_data = response.json()
                self.update_sales_table(sales_data)
            else:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось загрузить статистику продаж. Код ошибки: {response.status_code}")
                self.sales_table.setRowCount(0)
                self.update_summary_labels(0, 0, 0, 0)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")
            self.sales_table.setRowCount(0)
            self.update_summary_labels(0, 0, 0, 0)

    def update_sales_table(self, sales_data):
        """Обновляет таблицу продаж"""
        # Сначала собираем информацию о товарах поставщика для отображения названий
        product_names = {}
        for product in getattr(self, 'supplier_products', []):
            product_names[product['id']] = product['name']

        # Подсчитываем статистику
        unique_orders = set()
        unique_products = set()
        total_quantity = 0
        total_revenue = 0.0

        # Устанавливаем количество строк
        self.sales_table.setRowCount(len(sales_data))

        for row, sale in enumerate(sales_data):
            order_id = sale.get('order_id', 0)
            product_id = sale.get('product_id', 0)
            quantity = sale.get('quantity', 0)
            price = sale.get('price_per_unit', 0)
            total = quantity * price

            # Обновляем статистику
            unique_orders.add(order_id)
            unique_products.add(product_id)
            total_quantity += quantity
            total_revenue += total

            # Название товара
            product_name = product_names.get(product_id, "Неизвестный товар")
            product_item = QTableWidgetItem(product_name)
            self.sales_table.setItem(row, 0, product_item)

            # Количество
            quantity_item = QTableWidgetItem(str(quantity))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(row, 1, quantity_item)

            # Цена за единицу
            price_item = QTableWidgetItem(f"{price:,.2f} ₽".replace(",", " "))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 2, price_item)

            # Сумма
            total_item = QTableWidgetItem(f"{total:,.2f} ₽".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 3, total_item)

        # Обновляем итоговые данные
        self.update_summary_labels(len(unique_orders), len(unique_products), total_quantity, total_revenue)

    def update_summary_labels(self, orders_count, products_count, total_quantity, total_revenue):
        """Обновляет итоговые метки статистики"""
        self.total_orders_label.setText(f"Всего заказов: {orders_count}")
        self.total_products_label.setText(f"Всего товаров: {products_count}")
        self.total_quantity_label.setText(f"Всего продано: {total_quantity} шт.")
        self.total_revenue_label.setText(f"Общая выручка: {total_revenue:,.2f} ₽".replace(",", " "))


    def update_summary_tab(self, summary_data):
        """Обновляет вкладку сводной статистики"""
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.summary_layout.count())):
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Создаем карточки статистики
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(15)

        # Карточка общего количества продаж
        sales_card = self.create_stat_card(
            "Всего продаж",
            str(summary_data.get("total_sales", 0)),
            "#3498db",
            "sales.png"
        )
        cards_layout.addWidget(sales_card)

        # Карточка общей выручки
        revenue_card = self.create_stat_card(
            "Общая выручка",
            f"{summary_data.get('total_revenue', 0):,.2f} ₽".replace(",", " "),
            "#2ecc71",
            "revenue.png"
        )
        cards_layout.addWidget(revenue_card)

        # Карточка среднего чека
        avg_card = self.create_stat_card(
            "Средний чек",
            f"{summary_data.get('average_order', 0):,.2f} ₽".replace(",", " "),
            "#9b59b6",
            "average.png"
        )
        cards_layout.addWidget(avg_card)

        # Карточка популярного товара
        popular_card = self.create_stat_card(
            "Самый популярный товар",
            summary_data.get("popular_product", "Нет данных"),
            "#e74c3c",
            "popular.png"
        )
        cards_layout.addWidget(popular_card)

        self.summary_layout.addWidget(cards_container)

        # График продаж (заглушка)
        chart_label = QLabel("График продаж будет здесь")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 50px;
            color: #7f8c8d;
            font-size: 16px;
        """)
        self.summary_layout.addWidget(chart_label)

    def create_stat_card(self, title, value, color):
        """Создает упрощенную карточку статистики без иконок и без рамок у текста"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 15px;
                min-width: 180px;
            }}
            QLabel {{
                border: none;
                padding: 0;
                margin: 0;
            }}
            QLabel#title {{
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 5px;
            }}
            QLabel#value {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
                margin-top: 5px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Заголовок
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Значение
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)

        return card

    def update_products_tab(self, products_stats):
        """Обновляет вкладку статистики по товарам"""
        # Очищаем предыдущие виджеты
        for i in reversed(range(self.products_layout.count())):
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not products_stats:
            no_data_label = QLabel("Нет данных о продажах товаров")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
            self.products_layout.addWidget(no_data_label)
            return

        # Создаем таблицу
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Товар", "Продано", "Выручка", "Рейтинг"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        # Заполняем таблицу данными
        table.setRowCount(len(products_stats))
        for row, product in enumerate(products_stats):
            # Товар
            name_item = QTableWidgetItem(product.get("name", "Без названия"))
            table.setItem(row, 0, name_item)

            # Продано
            sold_item = QTableWidgetItem(str(product.get("sold_quantity", 0)))
            sold_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, sold_item)

            # Выручка
            revenue_item = QTableWidgetItem(f"{product.get('revenue', 0):,.2f} ₽".replace(",", " "))
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 2, revenue_item)

            # Средняя цена
            avg_price_item = QTableWidgetItem(f"{product.get('average_price', 0):,.2f} ₽".replace(",", " "))
            avg_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, avg_price_item)

            # Доля
            share_item = QTableWidgetItem(f"{product.get('share', 0):.1%}")
            share_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 4, share_item)

            # Рейтинг (визуализация звездами)
            rating = product.get("rating", 0)
            rating_item = QTableWidgetItem("★" * int(round(rating)) + "☆" * (5 - int(round(rating))))
            rating_item.setTextAlignment(Qt.AlignCenter)

            # Цвет в зависимости от рейтинга
            if rating >= 4:
                rating_item.setForeground(QColor("#2ecc71"))  # зеленый
            elif rating >= 3:
                rating_item.setForeground(QColor("#f39c12"))  # оранжевый
            else:
                rating_item.setForeground(QColor("#e74c3c"))  # красный

            table.setItem(row, 5, rating_item)

        self.products_layout.addWidget(table)