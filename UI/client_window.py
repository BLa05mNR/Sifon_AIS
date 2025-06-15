import datetime

import requests
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QListWidget, QListWidgetItem,
                               QFrame, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QMessageBox, QFormLayout, QDialog,
                               QLineEdit, QDialogButtonBox, QScrollArea)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from pathlib import Path


class ClientWindow(QMainWindow):
    def __init__(self, token_data):
        super().__init__()
        if "customer_id" not in token_data:
            QMessageBox.warning(self, "Предупреждение",
                                "ID пользователя не найден. Некоторые функции могут быть недоступны.")
        self.token_data = token_data
        self.setWindowTitle("АИС 'Сифон' - Клиент")
        self.setFixedSize(1280, 768)

        # Базовый URL API
        self.api_url = "http://localhost:8000"

        # Пути к иконкам
        self.icon_dir = Path(__file__).parent / "icons"

        # Основной стек виджетов
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Корзина (словарь: ключ - ID товара, значение - словарь с товаром и количеством)
        self.cart = {}

        # Создаем виджеты для разных разделов
        self.catalog_widget = self.create_catalog_widget()
        self.cart_widget = self.create_cart_widget()
        self.profile_widget = self.create_profile_widget()

        self.stack.addWidget(self.catalog_widget)
        self.stack.addWidget(self.cart_widget)
        self.stack.addWidget(self.profile_widget)

        # Создаем навигационное меню
        self.create_navigation()

        # Загружаем товары с сервера
        self.load_products()

        # Стилизация
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
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
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                border: none;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: transparent;
            }
            .product-card {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 15px;
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
            .product-button {
                background-color: #2ecc71;
                padding: 8px 15px;
            }
            .product-button:hover {
                background-color: #27ae60;
            }
            .refresh-button {
                background-color: #3498db;
            }
            .refresh-button:hover {
                background-color: #2980b9;
            }
            .remove-button {
                background-color: #e74c3c;
                padding: 5px 10px;
                font-size: 12px;
            }
            .remove-button:hover {
                background-color: #c0392b;
            }
            .cart-item {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 15px;
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
        """)

    def get_auth_headers(self):
        """Возвращает заголовки с токеном авторизации"""
        return {
            "Authorization": f"Bearer {self.token_data['access_token']}",
            "Content-Type": "application/json"
        }

    def load_products(self):
        """Загружает товары с сервера"""
        try:
            response = requests.get(
                f"{self.api_url}/products/",
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                self.products = response.json()
                self.update_product_list()
            elif response.status_code == 401:
                self.show_error("Ошибка авторизации", "Не удалось авторизоваться. Пожалуйста, войдите снова.")
            else:
                self.show_error("Ошибка сервера", f"Не удалось загрузить товары. Код ошибки: {response.status_code}")
                self.products = []
                self.update_product_list()

        except requests.exceptions.RequestException as e:
            self.show_error("Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")
            self.products = []
            self.update_product_list()

    def show_error(self, title, message):
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, title, message)

    def update_product_list(self):
        """Обновляет список товаров в каталоге"""
        if hasattr(self, 'product_list_widget'):
            self.product_list_widget.clear()

            if not self.products:
                item = QListWidgetItem()
                widget = QLabel("Нет доступных товаров или ошибка загрузки")
                widget.setAlignment(Qt.AlignCenter)
                widget.setStyleSheet("color: #7f8c8d; font-size: 14px;")
                self.product_list_widget.addItem(item)
                self.product_list_widget.setItemWidget(item, widget)
                return

            for product in self.products:
                item = QListWidgetItem()
                card = self.create_product_card(product)
                item.setSizeHint(card.sizeHint())
                self.product_list_widget.addItem(item)
                self.product_list_widget.setItemWidget(item, card)

    def create_navigation(self):
        """Создает навигационную панель в верхнем правом углу"""
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        menubar.setCornerWidget(spacer)

        menu = menubar.addMenu("Меню")

        catalog_action = menu.addAction("Каталог")
        catalog_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.catalog_widget))

        cart_action = menu.addAction("Корзина")
        cart_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.cart_widget))

        # Добавляем значок с количеством товаров в корзине
        self.cart_items_count = QLabel("0")
        self.cart_items_count.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 12px;
        """)
        cart_action.setIcon(QIcon(str(self.icon_dir / "cart.png")))
        cart_action.setIconText(self.cart_items_count.text())

        profile_action = menu.addAction("Профиль")
        profile_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.profile_widget))

    def create_product_card(self, product):
        """Создает просторную карточку товара с гарантированно видимой кнопкой"""
        card = QFrame()
        card.setObjectName("product-card")
        card.setFixedHeight(180)

        card.setStyleSheet("""
            QFrame#product-card {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 8px;
            }
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(20)

        # Блок с изображением
        icon_frame = QFrame()
        icon_frame.setFixedSize(120, 120)
        icon_frame.setStyleSheet("""
            background-color: #f9f9f9;
            border-radius: 8px;
            border: 1px solid #eee;
        """)

        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(str(self.icon_dir / "products.png")).scaled(100, 100, Qt.KeepAspectRatio))
        icon_label.mousePressEvent = lambda event: self.show_product_image(product)
        icon_label.setCursor(Qt.PointingHandCursor)
        icon_layout.addWidget(icon_label)

        # Основная информация
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        name_label = QLabel(product.get("name", "Без названия"))
        name_label.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        """)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(300)

        desc_label = QLabel(product.get("description", "Описание отсутствует"))
        desc_label.setStyleSheet("""
            color: #666;
            font-size: 13px;
        """)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(300)

        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        info_layout.addStretch()

        # Правый блок (цена + кнопка)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        right_layout.setSpacing(12)

        # Блок цены и наличия
        price_widget = QWidget()
        price_layout = QVBoxLayout(price_widget)
        price_layout.setContentsMargins(0, 0, 0, 0)
        price_layout.setSpacing(5)

        price_label = QLabel(f"{float(product.get('price', 0)):,.2f} ₽".replace(",", " "))
        price_label.setStyleSheet("""
            font-size: 20px;
            color: #e74c3c;
            font-weight: bold;
        """)

        stock_label = QLabel(f"В наличии: {product.get('stock_quantity', 0)} шт.")
        stock_label.setStyleSheet("""
            color: #3498db;
            font-size: 14px;
        """)

        price_layout.addWidget(price_label, 0, Qt.AlignRight)
        price_layout.addWidget(stock_label, 0, Qt.AlignRight)

        # Кнопка добавления в корзину
        add_btn = QPushButton("Добавить в корзину")
        add_btn.setFixedSize(180, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.add_to_cart(product))

        right_layout.addWidget(price_widget)
        right_layout.addStretch()
        right_layout.addWidget(add_btn, 0, Qt.AlignRight)

        # Собираем все вместе
        layout.addWidget(icon_frame)
        layout.addWidget(info_widget)
        layout.addWidget(right_widget)

        return card

    def show_product_image(self, product):
        """Отображает увеличенное изображение товара"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(product.get("name", "Изображение товара"))

        image_label = QLabel()
        pixmap = QPixmap(str(self.icon_dir / "products.png")).scaled(400, 400, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)

        dialog.layout().addWidget(image_label, 0, 0, 1, dialog.layout().columnCount())
        dialog.addButton(QMessageBox.Close)
        dialog.resize(500, 500)
        dialog.exec()

    def add_to_cart(self, product):
        """Добавляет товар в корзину с проверкой доступного количества"""
        product_id = product.get("id")
        stock_quantity = product.get("stock_quantity", 0)

        if stock_quantity <= 0:
            QMessageBox.warning(
                self,
                "Нет в наличии",
                f"Товар '{product.get('name', 'Без названия')}' отсутствует в наличии."
            )
            return

        if product_id not in self.cart:
            # Если товара нет в корзине, добавляем его с количеством 1
            self.cart[product_id] = {
                "product": product,
                "quantity": 1
            }
        else:
            # Если товар уже есть в корзине, проверяем доступное количество
            current_quantity = self.cart[product_id]["quantity"]
            if current_quantity >= stock_quantity:
                QMessageBox.warning(
                    self,
                    "Достигнут лимит",
                    f"Невозможно добавить больше товара '{product.get('name', 'Без названия')}'. "
                    f"В наличии только {stock_quantity} шт."
                )
                return
            # Увеличиваем количество только если есть в наличии
            self.cart[product_id]["quantity"] += 1

        # Обновляем счетчик товаров в корзине
        self.update_cart_count()

        # Обновляем виджет корзины
        self.update_cart_widget()

        # Показываем уведомление
        QMessageBox.information(
            self,
            "Товар добавлен",
            f"Товар '{product.get('name', 'Без названия')}' добавлен в корзину!\n"
            f"Количество: {self.cart[product_id]['quantity']} шт."
        )

    def update_cart_count(self):
        """Обновляет счетчик товаров в корзине"""
        total_items = sum(item["quantity"] for item in self.cart.values())
        self.cart_items_count.setText(str(total_items))

        # Обновляем значок в меню
        menu = self.menuBar().findChild(QMenu, "Меню")
        if menu:
            actions = menu.actions()
            if len(actions) > 1:  # Второй элемент - это корзина
                actions[1].setIconText(self.cart_items_count.text())

    def update_cart_widget(self):
        """Обновляет виджет корзины с современным дизайном"""
        self.cart_list_widget.clear()

        if not self.cart:
            # Красивое сообщение о пустой корзине
            empty_item = QListWidgetItem()
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)

            empty_icon = QLabel()
            empty_icon.setPixmap(QPixmap(str(self.icon_dir / "empty_cart.png")).scaled(100, 100, Qt.KeepAspectRatio))
            empty_icon.setAlignment(Qt.AlignCenter)

            empty_text = QLabel("Ваша корзина пуста")
            empty_text.setAlignment(Qt.AlignCenter)
            empty_text.setStyleSheet("font-size: 18px; color: #7f8c8d; margin-top: 15px;")

            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_text)
            empty_layout.addStretch()

            self.cart_list_widget.addItem(empty_item)
            self.cart_list_widget.setItemWidget(empty_item, empty_widget)
            return

        total_price = 0

        for product_id, item in self.cart.items():
            product = item["product"]
            quantity = item["quantity"]
            item_price = float(product.get("price", 0)) * quantity
            total_price += item_price

            # Создаем карточку товара
            cart_item = QListWidgetItem()
            cart_item.setSizeHint(QSize(0, 120))  # Оптимальная высота

            cart_widget = QFrame()
            cart_widget.setObjectName("cart-item")
            cart_widget.setStyleSheet("""
                    QFrame#cart-item {
                        background-color: white;
                        border-radius: 12px;
                        border: 1px solid #e0e0e0;
                        padding: 12px;
                    }
                """)

            layout = QHBoxLayout(cart_widget)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(12)

            # Блок с изображением (компактный)
            icon_frame = QFrame()
            icon_frame.setFixedSize(50, 50)
            icon_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 6px;")

            icon_layout = QVBoxLayout(icon_frame)
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(str(self.icon_dir / "products.png")).scaled(40, 40, Qt.KeepAspectRatio))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)

            layout.addWidget(icon_frame)

            # Блок с информацией
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(4)

            title_label = QLabel(product.get("name", "Без названия"))
            title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")
            title_label.setWordWrap(True)
            title_label.setMaximumWidth(250)

            price_label = QLabel(f"{float(product.get('price', 0)):,.2f} ₽".replace(",", " "))
            price_label.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: bold;")

            info_layout.addWidget(title_label)
            info_layout.addWidget(price_label)
            info_layout.addStretch()

            layout.addWidget(info_widget, stretch=1)

            # Блок управления количеством (горизонтальный)
            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout(quantity_widget)
            quantity_layout.setContentsMargins(0, 0, 0, 0)
            quantity_layout.setSpacing(5)

            # Кнопка уменьшения
            decrease_btn = QPushButton("-")
            decrease_btn.setFixedSize(30, 30)
            decrease_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                    QPushButton:pressed {
                        background-color: #a5281b;
                    }
                """)
            decrease_btn.clicked.connect(lambda _, pid=product_id: self.change_quantity(pid, -1))

            # Отображение количества
            quantity_display = QLabel(str(quantity))
            quantity_display.setAlignment(Qt.AlignCenter)
            quantity_display.setFixedWidth(30)
            quantity_display.setStyleSheet("""
                    font-size: 14px;
                    font-weight: bold;
                    color: #333;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 2px;
                """)

            # Кнопка увеличения
            increase_btn = QPushButton("+")
            increase_btn.setFixedSize(30, 30)
            increase_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #1e8449;
                    }
                """)
            increase_btn.clicked.connect(lambda _, pid=product_id: self.change_quantity(pid, 1))

            quantity_layout.addWidget(decrease_btn)
            quantity_layout.addWidget(quantity_display)
            quantity_layout.addWidget(increase_btn)

            # Кнопка удаления (четкая и понятная)
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(30, 30)
            remove_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #95a5a6;
                        color: white;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #7f8c8d;
                    }
                    QPushButton:pressed {
                        background-color: #6c7a7d;
                    }
                """)
            remove_btn.setToolTip("Удалить товар")
            remove_btn.clicked.connect(lambda _, pid=product_id: self.remove_from_cart(pid))

            # Общий layout для управления
            control_widget = QWidget()
            control_layout = QHBoxLayout(control_widget)
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_layout.setSpacing(10)
            control_layout.addWidget(quantity_widget)
            control_layout.addWidget(remove_btn)

            layout.addWidget(control_widget)

            self.cart_list_widget.addItem(cart_item)
            self.cart_list_widget.setItemWidget(cart_item, cart_widget)

        # Блок итогов
        total_item = QListWidgetItem()
        total_item.setSizeHint(QSize(0, 80))  # Увеличили высоту для кнопки
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.setContentsMargins(10, 10, 10, 10)

        total_label = QLabel(f"Итого: {total_price:,.2f} ₽".replace(",", " "))
        total_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #2c3e50;
            margin-right: 20px;
        """)

        checkout_btn = QPushButton("Оформить заказ")
        checkout_btn.setIcon(QIcon(str(self.icon_dir / "checkout.png")))
        checkout_btn.setIconSize(QSize(24, 24))
        checkout_btn.setFixedSize(200, 50)  # Увеличили размер кнопки
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 18px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)

        total_layout.addWidget(total_label, stretch=1)
        total_layout.addWidget(checkout_btn)

        self.cart_list_widget.addItem(total_item)
        self.cart_list_widget.setItemWidget(total_item, total_widget)

    def update_cart_quantity(self, product_id, new_quantity):
        """Обновляет количество товара в корзине"""
        if product_id in self.cart:
            self.cart[product_id]["quantity"] = new_quantity
            self.update_cart_count()
            # Не обновляем весь виджет, чтобы не терять фокус

    def change_quantity(self, product_id, delta):
        """Изменяет количество товара в корзине с проверкой доступного количества"""
        if product_id in self.cart:
            product = self.cart[product_id]["product"]
            stock_quantity = product.get("stock_quantity", 0)
            current_quantity = self.cart[product_id]["quantity"]
            new_quantity = current_quantity + delta

            # Проверяем, чтобы количество было не меньше 1
            if new_quantity < 1:
                self.remove_from_cart(product_id)
                return

            # Проверяем, чтобы не превышало доступное количество
            if delta > 0 and new_quantity > stock_quantity:
                QMessageBox.warning(
                    self,
                    "Достигнут лимит",
                    f"Невозможно добавить больше товара '{product.get('name', 'Без названия')}'. "
                    f"В наличии только {stock_quantity} шт."
                )
                return

            # Обновляем количество
            self.cart[product_id]["quantity"] = new_quantity

            # Обновляем интерфейс
            self.update_cart_count()
            self.update_cart_widget()  # Полностью обновляем виджет корзины

    def remove_from_cart(self, product_id):
        """Удаляет товар из корзины"""
        if product_id in self.cart:
            product_name = self.cart[product_id]["product"].get("name", "Без названия")
            del self.cart[product_id]

            # Обновляем интерфейс
            self.update_cart_count()
            self.update_cart_widget()

            # Показываем уведомление
            QMessageBox.information(
                self,
                "Товар удален",
                f"Товар '{product_name}' удален из корзины!"
            )

    def checkout(self):
        """Оформление заказа с отправкой данных на сервер"""
        if not self.cart:
            QMessageBox.warning(self, "Корзина пуста", "Ваша корзина пуста. Добавьте товары перед оформлением заказа.")
            return

        # Получаем customer_id из токена
        customer_id = self.token_data.get("customer_id")
        if not customer_id:
            QMessageBox.critical(
                self,
                "Ошибка оформления",
                "Не удалось определить ID пользователя. Пожалуйста, войдите снова."
            )
            return

        # Подготовка данных для заказа
        total_price = sum(
            float(item["product"].get("price", 0)) * item["quantity"]
            for item in self.cart.values()
        )

        # 1. Создаем основной заказ
        order_data = {
            "customer_id": customer_id,
            "order_date": datetime.datetime.now().isoformat(),
            "status": "Оплачен",
            "total_amount": total_price
        }

        try:
            # Отправляем POST запрос для создания заказа
            response = requests.post(
                f"{self.api_url}/orders/",
                json=order_data,
                headers=self.get_auth_headers()
            )

            if response.status_code != 201:
                raise Exception(f"Ошибка создания заказа: {response.status_code} - {response.text}")

            order_response = response.json()
            order_id = order_response.get("id")

            if not order_id:
                raise Exception("Не удалось получить ID созданного заказа")

            # 2. Создаем детали заказа для каждого товара
            for product_id, item in self.cart.items():
                product = item["product"]
                detail_data = {
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": item["quantity"],
                    "price_per_unit": float(product.get("price", 0))
                }

                response = requests.post(
                    f"{self.api_url}/order-details/",
                    json=detail_data,
                    headers=self.get_auth_headers()
                )

                if response.status_code != 201:
                    raise Exception(f"Ошибка добавления деталей заказа: {response.status_code} - {response.text}")

            # Если все успешно, показываем сообщение и очищаем корзину
            QMessageBox.information(
                self,
                "Заказ оформлен",
                f"Ваш заказ №{order_id} успешно оформлен и оплачен!\n\n"
                f"Количество товаров: {sum(item['quantity'] for item in self.cart.values())}\n"
                f"Общая стоимость: {total_price:,.2f} ₽".replace(",", " ") + "\n\n"
                                                                             "Спасибо за покупку!"
            )

            # Очищаем корзину после успешного оформления
            self.cart.clear()
            self.update_cart_count()
            self.update_cart_widget()

        except Exception as e:
            # В случае ошибки показываем сообщение и сохраняем корзину
            QMessageBox.critical(
                self,
                "Ошибка оформления заказа",
                f"Не удалось оформить заказ:\n{str(e)}\n\n"
                "Пожалуйста, попробуйте позже или обратитесь в поддержку."
            )
            print(f"Ошибка при оформлении заказа: {str(e)}")

    def create_catalog_widget(self):
        """Создает виджет каталога товаров с карточками"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Верхняя панель с заголовком и кнопкой обновления
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Каталог товаров")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setObjectName("refresh-button")
        refresh_btn.setFixedSize(100, 30)
        refresh_btn.clicked.connect(self.load_products)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(refresh_btn)

        # Список товаров с карточками
        self.product_list_widget = QListWidget()
        self.product_list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.product_list_widget.setSpacing(10)
        self.product_list_widget.setStyleSheet("border: none; background-color: transparent;")
        self.product_list_widget.itemClicked.connect(self.highlight_product_card)

        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.product_list_widget)

        return widget

    def highlight_product_card(self, item):
        """Выделяет карточку товара при нажатии"""
        for i in range(self.product_list_widget.count()):
            current_item = self.product_list_widget.item(i)
            current_widget = self.product_list_widget.itemWidget(current_item)
            if current_widget:
                current_widget.setStyleSheet("""
                    QFrame#product-card {
                        background-color: white;
                        border-radius: 10px;
                        border: 1px solid #e0e0e0;
                        padding: 15px;
                        margin: 8px;
                    }
                """)

        selected_widget = self.product_list_widget.itemWidget(item)
        if selected_widget:
            selected_widget.setStyleSheet("""
                QFrame#product-card {
                    background-color: #e6f7ff;
                    border-radius: 10px;
                    border: 2px solid #3498db;
                    padding: 15px;
                    margin: 8px;
                }
            """)

    def create_cart_widget(self):
        """Создает виджет корзины"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Корзина")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin-bottom: 20px;
            color: #2c3e50;
        """)

        # Список товаров в корзине
        self.cart_list_widget = QListWidget()
        self.cart_list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.cart_list_widget.setSpacing(10)
        self.cart_list_widget.setStyleSheet("border: none; background-color: transparent;")

        layout.addWidget(title)
        layout.addWidget(self.cart_list_widget)

        # Обновляем содержимое корзины при создании виджета
        self.update_cart_widget()

        return widget

    def create_profile_widget(self):
        """Создает виджет профиля с информацией о пользователе и его заказах"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

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
            QFrame#profile-frame, QFrame#orders-frame {
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
            QPushButton#edit-btn, QPushButton#refresh-orders-btn {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 180px;
            }
            QPushButton#edit-btn:hover, QPushButton#refresh-orders-btn:hover {
                background-color: #2980b9;
            }
            QLabel#orders-title {
                font-size: 20px;
                font-weight: 600;
                color: #2c3e50;
                padding: 10px 0;
            }
            QFrame.order-item {
                background-color: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                padding: 15px;
                margin-bottom: 10px;
            }
            QLabel.order-header {
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
            }
            QLabel.order-date {
                font-size: 14px;
                color: #718096;
            }
            QLabel.order-status {
                font-size: 14px;
                font-weight: 500;
                padding: 3px 10px;
                border-radius: 4px;
            }
            QLabel.order-amount {
                font-size: 16px;
                font-weight: bold;
                color: #2ecc71;
            }
            QPushButton#back-btn {
                background-color: #95a5a6;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 180px;
            }
            QPushButton#back-btn:hover {
                background-color: #7f8c8d;
            }
        """)

        # Создаем стек для переключения между профилем и заказами
        self.profile_stack = QStackedWidget()
        layout.addWidget(self.profile_stack)

        # 1. Виджет профиля
        profile_page = QWidget()
        profile_page_layout = QVBoxLayout(profile_page)
        profile_page_layout.setContentsMargins(0, 0, 0, 0)
        profile_page_layout.setSpacing(20)

        # Заголовок профиля
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Профиль")
        title.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            """)
        title.setObjectName("title")
        title_layout.addWidget(title, alignment=Qt.AlignLeft)
        title_layout.addStretch()

        profile_page_layout.addWidget(title_container)

        # Основной контейнер для профиля
        profile_frame = QFrame()
        profile_frame.setObjectName("profile-frame")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setSpacing(15)

        # Проверяем наличие customer_id
        customer_id = self.token_data.get("customer_id")
        if not customer_id:
            error_label = QLabel("ID пользователя не найден. Невозможно загрузить данные профиля.")
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
                    f"{self.api_url}/customers/{customer_id}",
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    user_data = response.json()

                    # Создаем форму для отображения данных
                    form_layout = QFormLayout()
                    form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
                    form_layout.setHorizontalSpacing(25)
                    form_layout.setVerticalSpacing(10)

                    # Функция для создания строк формы
                    def add_form_row(label_text, value_text):
                        label = QLabel(label_text)
                        label.setProperty("fieldName", "true")
                        value = QLabel(value_text or "Не указано")
                        value.setProperty("fieldValue", "true")
                        value.setWordWrap(True)
                        form_layout.addRow(label, value)

                    # Добавляем строки
                    add_form_row("ФИО:", user_data.get("full_name"))
                    add_form_row("Телефон:", user_data.get("phone"))
                    add_form_row("Email:", user_data.get("email"))
                    add_form_row("Адрес:", user_data.get("address"))
                    add_form_row("Логин:", user_data.get("username"))

                    profile_layout.addLayout(form_layout)

                elif response.status_code == 404:
                    error_label = QLabel("Профиль пользователя не найден на сервере.")
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

            # Кнопки редактирования и просмотра заказов
            buttons_container = QWidget()
            buttons_layout = QHBoxLayout(buttons_container)
            buttons_layout.setContentsMargins(0, 15, 0, 0)
            buttons_layout.setSpacing(15)

            # Кнопка редактирования профиля
            edit_btn = QPushButton("Редактировать профиль")
            edit_btn.setObjectName("edit-btn")
            edit_btn.setIcon(QIcon(str(self.icon_dir / "edit.png")))
            edit_btn.setIconSize(QSize(16, 16))
            edit_btn.clicked.connect(lambda: self.update_profile_data(profile_frame))

            # Кнопка просмотра заказов
            orders_btn = QPushButton("Мои заказы")
            orders_btn.setObjectName("edit-btn")
            orders_btn.setIcon(QIcon(str(self.icon_dir / "orders.png")))
            orders_btn.setIconSize(QSize(16, 16))
            orders_btn.clicked.connect(self.show_orders)

            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(orders_btn)
            buttons_layout.addStretch()

            profile_layout.addWidget(buttons_container)

        profile_page_layout.addWidget(profile_frame)
        profile_page_layout.addStretch()

        # 2. Виджет заказов
        orders_page = QWidget()
        orders_page_layout = QVBoxLayout(orders_page)
        orders_page_layout.setContentsMargins(0, 0, 0, 0)
        orders_page_layout.setSpacing(15)  # Уменьшил spacing для более компактного расположения

        # Кнопка "Назад к профилю" - теперь она выше заголовка
        back_btn = QPushButton("← Назад к профилю")
        back_btn.setObjectName("back-btn")
        back_btn.clicked.connect(self.show_profile)
        orders_page_layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Заголовок "Мои заказы"
        orders_title = QLabel("Мои заказы")
        orders_title.setObjectName("title")
        orders_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        orders_page_layout.addWidget(orders_title, alignment=Qt.AlignLeft)

        # Контейнер для заказов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")

        self.orders_container = QWidget()
        self.orders_layout = QVBoxLayout(self.orders_container)
        self.orders_layout.setSpacing(15)
        self.orders_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self.orders_container)
        orders_page_layout.addWidget(scroll_area)

        # Добавляем страницы в стек
        self.profile_stack.addWidget(profile_page)
        self.profile_stack.addWidget(orders_page)

        # По умолчанию показываем профиль
        self.profile_stack.setCurrentIndex(0)

        return widget

    def toggle_orders_view(self):
        """Переключает отображение заказов и обновляет их"""
        if self.orders_container.isVisible():
            self.orders_container.hide()
        else:
            # Показываем и обновляем заказы
            self.orders_container.show()
            self.load_orders(self.orders_container)

    def show_orders(self):
        """Показывает страницу с заказами"""
        self.load_orders()
        self.profile_stack.setCurrentIndex(1)

    def show_profile(self):
        """Показывает страницу профиля"""
        self.profile_stack.setCurrentIndex(0)

    def load_orders(self):
        """Загружает и обновляет список заказов с отображением всех заказов"""
        # Очищаем контейнер перед загрузкой новых данных
        for i in reversed(range(self.orders_layout.count())):
            widget = self.orders_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        customer_id = self.token_data.get("customer_id")
        if not customer_id:
            return

        try:
            # Если товары еще не загружены, загружаем их
            if not hasattr(self, 'products') or not self.products:
                self.load_products()

            # Загружаем список заказов
            response = requests.get(
                f"{self.api_url}/orders/customer/{customer_id}",
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                orders = response.json()

                if not orders:
                    no_orders_label = QLabel("У вас пока нет заказов")
                    no_orders_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 20px;")
                    no_orders_label.setAlignment(Qt.AlignCenter)
                    self.orders_layout.addWidget(no_orders_label)
                    return

                # Загружаем детали заказов
                details_response = requests.get(
                    f"{self.api_url}/order-details/customer/{customer_id}",
                    headers=self.get_auth_headers()
                )

                order_details = {}
                if details_response.status_code == 200:
                    for detail in details_response.json():
                        if detail['order_id'] not in order_details:
                            order_details[detail['order_id']] = []
                        order_details[detail['order_id']].append(detail)

                # Сортируем заказы по дате (новые сначала)
                orders.sort(key=lambda x: x['order_date'], reverse=True)

                # Создаем карточки для всех заказов
                for order in orders:
                    order_widget = self.create_order_card(order, order_details.get(order['id'], []))
                    self.orders_layout.addWidget(order_widget)

            elif response.status_code != 404:
                error_label = QLabel(f"Ошибка загрузки заказов (код {response.status_code})")
                error_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
                error_label.setAlignment(Qt.AlignCenter)
                self.orders_layout.addWidget(error_label)

        except requests.exceptions.RequestException as e:
            error_label = QLabel(f"Ошибка подключения: {str(e)}")
            error_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            self.orders_layout.addWidget(error_label)

    def create_order_card(self, order, details):
        """Создает карточку для одного заказа"""
        card = QFrame()
        card.setObjectName("order-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок с номером заказа
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        order_number = QLabel(f"Заказ №{order['id']}")
        order_number.setObjectName("order-header")
        order_number.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")

        # Парсим дату заказа
        order_date_str = order['order_date']
        try:
            order_date = datetime.datetime.strptime(
                order_date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except ValueError:
            try:
                order_date = datetime.datetime.strptime(
                    order_date_str, "%Y-%m-%dT%H:%M:%SZ"
                )
            except ValueError:
                order_date = datetime.datetime.now()

        date_label = QLabel(order_date.strftime("%d.%m.%Y %H:%M"))
        date_label.setObjectName("order-date")
        date_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")

        status_label = QLabel(order['status'].capitalize())
        status_label.setObjectName("order-status")

        # Устанавливаем стили для разных статусов заказа
        status = order['status'].lower()
        if status == 'завершен' or status == 'completed':
            status_label.setStyleSheet("""
                background-color: #2ecc71;  /* Зеленый */
                color: white; 
                padding: 3px 10px;
                border-radius: 4px;
                font-weight: 500;
            """)
        elif status == 'отменен' or status == 'cancelled':
            status_label.setStyleSheet("""
                background-color: #e74c3c;  /* Красный */
                color: white; 
                padding: 3px 10px;
                border-radius: 4px;
                font-weight: 500;
            """)
        else:
            # Остальные статусы (по умолчанию оранжевый)
            status_label.setStyleSheet("""
                background-color: #f39c12; 
                color: white; 
                padding: 3px 10px;
                border-radius: 4px;
                font-weight: 500;
            """)

        amount_label = QLabel(f"Итого: {order['total_amount']:,.2f} ₽".replace(",", " "))
        amount_label.setObjectName("order-amount")
        amount_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71;")

        header_layout.addWidget(order_number)
        header_layout.addWidget(date_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        header_layout.addWidget(amount_label)

        layout.addWidget(header_widget)

        # Детали заказа (товары)
        if details:
            details_frame = QFrame()
            details_layout = QVBoxLayout(details_frame)
            details_layout.setSpacing(10)
            details_layout.setContentsMargins(0, 10, 0, 10)

            # Заголовок списка товаров
            products_label = QLabel("Состав заказа:")
            products_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e;")
            details_layout.addWidget(products_label)

            for detail in details:
                product_widget = QWidget()
                product_layout = QHBoxLayout(product_widget)
                product_layout.setContentsMargins(0, 5, 0, 5)

                # Проверяем, загружены ли товары
                product_name = "Неизвестный товар"
                if hasattr(self, 'products') and self.products:
                    product = next((p for p in self.products if p['id'] == detail['product_id']), None)
                    if product:
                        product_name = product.get('name', "Неизвестный товар")

                name_label = QLabel(product_name)
                name_label.setStyleSheet("font-size: 14px;")
                name_label.setMinimumWidth(200)

                quantity_label = QLabel(f"{detail['quantity']} × {detail['price_per_unit']:,.2f} ₽")
                quantity_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")

                total_label = QLabel(f"{(detail['quantity'] * detail['price_per_unit']):,.2f} ₽")
                total_label.setStyleSheet("font-size: 14px; font-weight: 500;")

                product_layout.addWidget(name_label)
                product_layout.addStretch()
                product_layout.addWidget(quantity_label)
                product_layout.addWidget(total_label)

                details_layout.addWidget(product_widget)

            layout.addWidget(details_frame)

        layout.addStretch()
        return card

    def add_order_widget(self, container, order, details, layout):
        """Добавляет виджет заказа в контейнер"""
        order_frame = QFrame()
        order_frame.setObjectName("order-item")
        order_layout = QVBoxLayout(order_frame)
        order_layout.setSpacing(10)
        order_layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок с номером заказа
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        order_number = QLabel(f"Заказ №{order['id']}")
        order_number.setObjectName("order-header")

        # Парсим дату с учетом разных возможных форматов
        order_date_str = order['order_date']
        try:
            # Попробуем первый формат (с миллисекундами)
            order_date = datetime.datetime.strptime(
                order_date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except ValueError:
            try:
                # Попробуем второй формат (без миллисекунд)
                order_date = datetime.datetime.strptime(
                    order_date_str, "%Y-%m-%dT%H:%M:%SZ"
                )
            except ValueError:
                # Если оба формата не подошли, используем текущую дату
                order_date = datetime.datetime.now()

        date_label = QLabel(order_date.strftime("%d.%m.%Y %H:%M"))
        date_label.setObjectName("order-date")

        status_label = QLabel(order['status'].capitalize())
        status_label.setObjectName("order-status")
        # Разные цвета для разных статусов
        if order['status'].lower() == 'completed':
            status_label.setStyleSheet("background-color: #2ecc71; color: white;")
        elif order['status'].lower() == 'cancelled':
            status_label.setStyleSheet("background-color: #e74c3c; color: white;")
        else:
            status_label.setStyleSheet("background-color: #f39c12; color: white;")

        amount_label = QLabel(f"{order['total_amount']:,.2f} ₽".replace(",", " "))
        amount_label.setObjectName("order-amount")

        header_layout.addWidget(order_number)
        header_layout.addWidget(date_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        header_layout.addWidget(amount_label)

        order_layout.addWidget(header_widget)

        # Детали заказа (товары)
        if details:
            details_frame = QFrame()
            details_layout = QVBoxLayout(details_frame)
            details_layout.setSpacing(8)
            details_layout.setContentsMargins(10, 10, 10, 10)

            for detail in details:
                product_widget = QWidget()
                product_layout = QHBoxLayout(product_widget)
                product_layout.setContentsMargins(0, 0, 0, 0)

                # Проверяем, загружены ли товары
                product_name = "Неизвестный товар"
                if hasattr(self, 'products') and self.products:
                    product = next((p for p in self.products if p['id'] == detail['product_id']), None)
                    if product:
                        product_name = product.get('name', "Неизвестный товар")

                name_label = QLabel(product_name)
                name_label.setStyleSheet("font-size: 14px;")
                name_label.setMinimumWidth(200)

                quantity_label = QLabel(f"{detail['quantity']} × {detail['price_per_unit']:,.2f} ₽")
                quantity_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")

                total_label = QLabel(f"{(detail['quantity'] * detail['price_per_unit']):,.2f} ₽")
                total_label.setStyleSheet("font-size: 14px; font-weight: 500;")

                product_layout.addWidget(name_label)
                product_layout.addStretch()
                product_layout.addWidget(quantity_label)
                product_layout.addWidget(total_label)

                details_layout.addWidget(product_widget)

            order_layout.addWidget(details_frame)

        layout.addWidget(order_frame)

    def update_profile_data(self, profile_frame):
        """Updates user profile data by showing an edit dialog and sending a PUT request"""
        customer_id = self.token_data.get("customer_id")
        if not customer_id:
            QMessageBox.warning(self, "Ошибка", "ID пользователя не найден.")
            return

        try:
            # First, get current user data
            response = requests.get(
                f"{self.api_url}/customers/{customer_id}",
                headers=self.get_auth_headers()
            )

            if response.status_code != 200:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось загрузить текущие данные профиля. Код ошибки: {response.status_code}")
                return

            current_data = response.json()

            # Create a dialog for editing profile data
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактирование профиля")
            dialog.setFixedSize(400, 400)

            layout = QVBoxLayout(dialog)

            # Create form layout for editable fields
            form_layout = QFormLayout()

            # Full name field
            full_name_edit = QLineEdit(current_data.get("full_name", ""))
            form_layout.addRow("ФИО:", full_name_edit)

            # Phone field
            phone_edit = QLineEdit(current_data.get("phone", ""))
            form_layout.addRow("Телефон:", phone_edit)

            # Email field
            email_edit = QLineEdit(current_data.get("email", ""))
            form_layout.addRow("Email:", email_edit)

            # Address field
            address_edit = QLineEdit(current_data.get("address", ""))
            form_layout.addRow("Адрес:", address_edit)

            # Username field
            username_edit = QLineEdit(current_data.get("username", ""))
            form_layout.addRow("Логин:", username_edit)

            # Password field (with placeholder suggesting to leave empty if not changing)
            password_edit = QLineEdit()
            password_edit.setPlaceholderText("Оставьте пустым, если не меняете")
            password_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Новый пароль:", password_edit)

            layout.addLayout(form_layout)

            # Add buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            # Show dialog
            if dialog.exec() == QDialog.Accepted:
                # Prepare update data
                update_data = {
                    "full_name": full_name_edit.text(),
                    "phone": phone_edit.text(),
                    "email": email_edit.text(),
                    "address": address_edit.text(),
                    "username": username_edit.text(),
                    "password": password_edit.text() if password_edit.text() else None
                }

                # Remove password field if empty (not changing)
                if update_data["password"] is None:
                    del update_data["password"]

                # Send PUT request to update profile
                response = requests.put(
                    f"{self.api_url}/customers/{customer_id}",
                    json=update_data,
                    headers=self.get_auth_headers()
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Данные профиля успешно обновлены.")
                    # Refresh profile display
                    self.profile_widget = self.create_profile_widget()
                    self.stack.removeWidget(self.stack.widget(2))
                    self.stack.insertWidget(2, self.profile_widget)
                    self.stack.setCurrentWidget(self.profile_widget)  # Явно переключаемся на профиль
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось обновить данные профиля. Код ошибки: {response.status_code}\n"
                                        f"Сообщение: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к серверу: {str(e)}")

    def show_prev_order(self):
        """Показывает предыдущий заказ"""
        if self.current_order_index > 0:
            self.current_order_index -= 1
            self.orders_stack.setCurrentIndex(self.current_order_index)
            self.update_navigation_buttons()

    def show_next_order(self):
        """Показывает следующий заказ"""
        if self.current_order_index < len(self.all_orders) - 1:
            self.current_order_index += 1
            self.orders_stack.setCurrentIndex(self.current_order_index)
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Обновляет состояние кнопок навигации и счетчик"""
        self.prev_btn.setDisabled(self.current_order_index == 0)
        self.next_btn.setDisabled(self.current_order_index == len(self.all_orders) - 1)
        self.order_counter.setText(f"{self.current_order_index + 1} / {len(self.all_orders)}")