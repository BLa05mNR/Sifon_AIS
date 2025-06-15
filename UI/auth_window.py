from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QStackedWidget)
from PySide6.QtGui import QFont, QPixmap, QIcon, QAction
from PySide6.QtCore import Qt
import requests
from pathlib import Path

from UI.client_window import ClientWindow


class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("АИС 'Сифон' - Авторизация")
        self.setFixedSize(800, 600)  # Увеличил высоту для дополнительной информации

        # Пути к иконкам
        self.icon_dir = Path(__file__).parent / "icons"
        self.setWindowIcon(QIcon(str(self.icon_dir / "siphon_icon.png")))
        print("Path to icons:", self.icon_dir)

        # Основной стек виджетов
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Виджет авторизации
        self.login_widget = self.create_login_widget()
        # Виджет регистрации
        self.register_widget = self.create_register_widget()

        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)

        # Стилизация
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            QLabel {
                color: #333;
                border: none;
                background: transparent;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#form_title {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            QLabel#optional {
                font-size: 12px;
                color: #7f8c8d;
                font-style: italic;
            }
            QLabel#admin_contact {
                font-size: 13px;
                color: #7f8c8d;
                margin-top: 10px;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#register_btn {
                background-color: transparent;
                color: #3498db;
                text-decoration: underline;
                border: none;
                min-width: auto;
            }
            QPushButton#register_btn:hover {
                color: #2980b9;
            }
            QPushButton#back_btn {
                background-color: #95a5a6;
            }
            QPushButton#back_btn:hover {
                background-color: #7f8c8d;
            }
            QPushButton#toggle_btn {
                background-color: transparent;
                border: none;
                padding: 0;
                min-width: 24px;
                max-width: 24px;
                margin-left: -28px;
            }
        """)

    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Логотип
        logo_label = QLabel()
        pixmap = QPixmap(str(self.icon_dir / "siphon_icon.png")).scaled(150, 150, Qt.KeepAspectRatio,
                                                                        Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Заголовок
        title_label = QLabel("АИС Сантехнического магазина 'Сифон'")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        # Форма авторизации
        form_frame = QFrame()
        form_frame.setFixedWidth(450)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)

        # Поля ввода
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        # Пароль с кнопкой показать/скрыть
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(str(self.icon_dir / "eye_show.png")))  # Нужно добавить иконки глаза
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)

        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setObjectName("toggle_btn")
        self.toggle_password_btn.setDefault(False)
        self.toggle_password_btn.setFlat(True)
        self.toggle_password_btn.setIcon(QIcon(str(self.icon_dir / "eye_show.png")))
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)

        # Кнопка входа
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.handle_login)

        # Ссылка на регистрацию
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setObjectName("register_btn")
        register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        # Контакты администратора
        admin_label = QLabel("Если возникли проблемы с доступом,\nобратитесь к администратору: +7 (123) 456-78-90")
        admin_label.setObjectName("admin_contact")
        admin_label.setAlignment(Qt.AlignCenter)

        # Сборка формы
        form_layout.addWidget(self.username_input)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(login_btn)
        form_layout.addWidget(register_btn, 0, Qt.AlignCenter)
        form_layout.addWidget(admin_label)
        form_frame.setLayout(form_layout)

        # Сборка основного лэйаута
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(form_frame)
        widget.setLayout(layout)

        return widget

    def create_register_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Логотип
        logo_label = QLabel()
        pixmap = QPixmap(str(self.icon_dir / "siphon_icon.png")).scaled(150, 150, Qt.KeepAspectRatio,
                                                                        Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Заголовок
        title_label = QLabel("Регистрация нового пользователя")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        # Форма регистрации
        form_frame = QFrame()
        form_frame.setFixedWidth(400)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(30, 30, 30, 30)

        # Поля ввода
        required_label = QLabel("* Обязательные поля")
        required_label.setObjectName("optional")

        self.reg_fullname = QLineEdit()
        self.reg_fullname.setPlaceholderText("* ФИО")

        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("* Телефон")

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email")

        self.reg_address = QLineEdit()
        self.reg_address.setPlaceholderText("Адрес")

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("* Логин")

        # Пароль с кнопкой показать/скрыть
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("* Пароль")
        self.reg_password.setEchoMode(QLineEdit.Password)

        self.reg_toggle_password_btn = QPushButton()
        self.reg_toggle_password_btn.setObjectName("toggle_btn")
        self.reg_toggle_password_btn.setDefault(False)
        self.reg_toggle_password_btn.setFlat(True)
        self.reg_toggle_password_btn.setIcon(QIcon(str(self.icon_dir / "eye_show.png")))
        self.reg_toggle_password_btn.clicked.connect(
            lambda: self.toggle_password_visibility(self.reg_password, self.reg_toggle_password_btn))

        password_layout.addWidget(self.reg_password)
        password_layout.addWidget(self.reg_toggle_password_btn)

        # Подтверждение пароля с кнопкой
        confirm_password_layout = QHBoxLayout()
        confirm_password_layout.setContentsMargins(0, 0, 0, 0)
        confirm_password_layout.setSpacing(0)

        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setPlaceholderText("* Подтверждение пароля")
        self.reg_confirm_password.setEchoMode(QLineEdit.Password)

        self.reg_toggle_confirm_password_btn = QPushButton()
        self.reg_toggle_confirm_password_btn.setObjectName("toggle_btn")
        self.reg_toggle_confirm_password_btn.setDefault(False)
        self.reg_toggle_confirm_password_btn.setFlat(True)
        self.reg_toggle_confirm_password_btn.setIcon(QIcon(str(self.icon_dir / "eye_show.png")))
        self.reg_toggle_confirm_password_btn.clicked.connect(
            lambda: self.toggle_password_visibility(self.reg_confirm_password, self.reg_toggle_confirm_password_btn))

        confirm_password_layout.addWidget(self.reg_confirm_password)
        confirm_password_layout.addWidget(self.reg_toggle_confirm_password_btn)

        # Кнопки
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("back_btn")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.handle_register)

        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(register_btn)

        # Контакты администратора
        admin_label = QLabel("По вопросам регистрации обращайтесь\nк администратору: +7 (123) 456-78-90")
        admin_label.setObjectName("admin_contact")
        admin_label.setAlignment(Qt.AlignCenter)

        # Сборка формы
        form_layout.addWidget(required_label)
        form_layout.addWidget(self.reg_fullname)
        form_layout.addWidget(self.reg_phone)
        form_layout.addWidget(self.reg_email)
        form_layout.addWidget(self.reg_address)
        form_layout.addWidget(self.reg_username)
        form_layout.addLayout(password_layout)
        form_layout.addLayout(confirm_password_layout)
        form_layout.addLayout(btn_layout)
        form_layout.addWidget(admin_label)
        form_frame.setLayout(form_layout)

        # Сборка основного лэйаута
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(form_frame)
        widget.setLayout(layout)

        return widget

    def toggle_password_visibility(self, field=None, button=None):
        """Переключение видимости пароля"""
        if field is None:
            field = self.password_input
            button = self.toggle_password_btn

        if field.echoMode() == QLineEdit.Password:
            field.setEchoMode(QLineEdit.Normal)
            button.setIcon(QIcon(str(self.icon_dir / "eye_hide.png")))
        else:
            field.setEchoMode(QLineEdit.Password)
            button.setIcon(QIcon(str(self.icon_dir / "eye_show.png")))

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return

        try:
            # 1. Выполняем вход для получения токена
            login_response = requests.post(
                "http://127.0.0.1:8000/auth/login",
                data={"username": username, "password": password},
                headers={"accept": "application/json"}
            )

            if login_response.status_code != 200:
                error_msg = login_response.json().get("detail", "Неверный логин или пароль")
                QMessageBox.warning(self, "Ошибка", error_msg)
                return

            token_data = login_response.json()
            access_token = token_data["access_token"]

            # 2. Декодируем токен, чтобы извлечь данные
            token_parts = access_token.split('.')
            if len(token_parts) == 3:
                import base64
                import json

                # Декодируем payload часть токена
                payload = token_parts[1]
                # Добавляем padding, если необходимо
                payload += '=' * (4 - len(payload) % 4)
                try:
                    decoded_payload = base64.urlsafe_b64decode(payload).decode('utf-8')
                    payload_data = json.loads(decoded_payload)

                    # Извлекаем данные пользователя
                    token_data['role'] = payload_data.get('role', 'customer')
                    token_data['username'] = payload_data.get('sub', '')
                    token_data['customer_id'] = payload_data.get('customer_id')
                    token_data['supplier_id'] = payload_data.get('supplier_id')

                except Exception as e:
                    print(f"Ошибка декодирования токена: {e}")
                    token_data['role'] = 'customer'
                    token_data['username'] = ''
                    token_data['customer_id'] = None
                    token_data['supplier_id'] = None

            QMessageBox.information(self, "Успех", "Авторизация прошла успешно!")

            # Открываем соответствующее окно в зависимости от роли пользователя
            if token_data.get('role') == 'admin':
                self.open_admin_window(token_data)
            elif token_data.get('role') == 'supplier':
                self.open_supplier_window(token_data)
            else:
                self.open_client_window(token_data)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось подключиться к серверу: {str(e)}\nОбратитесь к администратору")

    def handle_register(self):
        # Получаем данные из полей ввода
        data = {
            "full_name": self.reg_fullname.text().strip(),
            "phone": self.reg_phone.text().strip(),
            "email": self.reg_email.text().strip() or None,
            "address": self.reg_address.text().strip() or None,
            "username": self.reg_username.text().strip(),
            "password": self.reg_password.text()
        }

        # Проверка заполнения обязательных полей
        required_fields = [
            ("full_name", "ФИО"),
            ("phone", "Телефон"),
            ("username", "Логин"),
            ("password", "Пароль")
        ]

        missing_fields = [name for field, name in required_fields if not data[field]]
        if missing_fields:
            QMessageBox.warning(self, "Ошибка",
                                f"Пожалуйста, заполните обязательные поля:\n{', '.join(missing_fields)}")
            return

        # Проверка совпадения паролей
        if data["password"] != self.reg_confirm_password.text():
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        # Проверка минимальной длины пароля
        if len(data["password"]) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
            return

        try:
            # Отправка запроса на сервер
            response = requests.post(
                "http://127.0.0.1:8000/customers/",
                json=data,
                headers={"Content-Type": "application/json", "accept": "application/json"}
            )

            if response.status_code == 201:
                # После успешной регистрации выполняем автоматический вход
                login_response = requests.post(
                    "http://127.0.0.1:8000/auth/login",
                    data={"username": data["username"], "password": data["password"]},
                    headers={"accept": "application/json"}
                )

                if login_response.status_code == 200:
                    token_data = login_response.json()
                    QMessageBox.information(self, "Успех",
                                            "Регистрация прошла успешно!\nВы автоматически вошли в систему.")
                    self.open_client_window(token_data)
                else:
                    QMessageBox.information(self, "Успех",
                                            "Регистрация прошла успешно!\nТеперь вы можете войти в систему.")
                    self.stack.setCurrentIndex(0)  # Переключаемся на экран авторизации
                    self.clear_register_fields()
            else:
                error_data = response.json()
                error_msg = error_data.get("detail", "Неизвестная ошибка")
                if isinstance(error_msg, dict):
                    error_msg = "\n".join([f"{k}: {v}" for k, v in error_msg.items()])
                QMessageBox.warning(self, "Ошибка регистрации",
                                    f"Ошибка: {error_msg}\nОбратитесь к администратору: +7 (123) 456-78-90")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось подключиться к серверу: {str(e)}\nОбратитесь к администратору: +7 (123) 456-78-90")

    def clear_register_fields(self):
        """Очистка всех полей формы регистрации"""
        self.reg_fullname.clear()
        self.reg_phone.clear()
        self.reg_email.clear()
        self.reg_address.clear()
        self.reg_username.clear()
        self.reg_password.clear()
        self.reg_confirm_password.clear()

    def open_client_window(self, token_data):
        """Открывает окно клиента с полученным токеном"""
        from UI.client_window import ClientWindow
        self.client_window = ClientWindow(token_data)
        self.client_window.show()
        self.hide()

    def open_supplier_window(self, token_data):
        """Открывает окно поставщика с полученным токеном"""
        from UI.supplier_window import SupplierWindow
        self.supplier_window = SupplierWindow(token_data)
        # Передаем supplier_id в окно поставщика
        if 'supplier_id' in token_data:
            self.supplier_window.supplier_id = token_data['supplier_id']
        self.supplier_window.show()
        self.hide()

    def open_admin_window(self, token_data):
        """Открывает окно администратора с полученным токеном"""
        from UI.admin_window import AdminWindow
        self.admin_window = AdminWindow(token_data)
        self.admin_window.show()
        self.hide()