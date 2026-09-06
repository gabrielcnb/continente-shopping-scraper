from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
from fuzzywuzzy import fuzz
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QProgressBar, QLabel, QTextEdit, QPushButton, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class ShoppingWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, shopping_list):
        super().__init__()
        self.shopping_list = shopping_list
        self.running = True

    def run(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        driver = uc.Chrome(options=chrome_options, version_main=132)

        # Open the main site
        self.status.emit("Opening the Continente site...")
        driver.get("https://www.continente.pt/")
        time.sleep(3)

        # Accept the cookie banner
        try:
            cookies_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            cookies_button.click()
            time.sleep(2)
            self.log.emit("✓ Cookies accepted")
        except:
            self.log.emit("⚠ Cookie button not found")

        total_items = len(self.shopping_list)
        
        # Walk through every item on the list
        for index, item in enumerate(self.shopping_list, 1):
            if not self.running:
                break

            self.status.emit(f"Processing: {item}")
            self.progress.emit(int((index / total_items) * 100))

            # Per-item search flow
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "input-custom-label-search"))
            )
            search_input.clear()
            search_input.send_keys(item)
            search_input.send_keys(Keys.RETURN)

            time.sleep(3)

            products = driver.find_elements(By.CLASS_NAME, "product-tile")
            matched_product = None
            best_score = 0

            if products:
                # Fuzzy-match the search term against the returned tiles
                self.log.emit(f"🔍 Searching: {item}")

                self.log.emit(f"✓ Product '{item}' processed")
            else:
                self.log.emit(f"❌ No product found for '{item}'")

        self.status.emit("Shopping finished!")
        self.finished.emit()
        driver.quit()

    def stop(self):
        self.running = False

class ShoppingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Continente Shopping Assistant')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                background-color: #333333;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
            QTextEdit {
                background-color: #333333;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                selection-background-color: #4CAF50;
                selection-color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
                transition: background-color 0.3s;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #333333;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status label
        self.status_label = QLabel("Waiting to start...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        layout.addWidget(self.progress_bar)

        # Log area
        log_label = QLabel("Activity Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(300)
        layout.addWidget(self.log_text)

        # Start button
        self.start_button = QPushButton("Start Shopping")
        self.start_button.clicked.connect(self.start_shopping)
        layout.addWidget(self.start_button)

        self.setMinimumSize(600, 500)
        self.center()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def start_shopping(self):
        self.start_button.setEnabled(False)
        self.worker = ShoppingWorker(shopping_list)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.shopping_finished)
        self.worker.start()

    def append_log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def shopping_finished(self):
        self.start_button.setEnabled(True)
        self.start_button.setText("Shopping Finished!")

if __name__ == '__main__':
    # Search terms stay in Portuguese: they are queries against continente.pt
    shopping_list = """
    Água continente 6 litros
    peito de frango 700g continente
    batata palha continente
    feijão continente
    açúcar continente
    arroz continente
    mel continente
    ovo 12 unidades
    sal grosso
    iogurte continente morango
    banana
    laranja
    brócolos
    cenoura
    pasta de dente continente
    lenço incontinencia
    lenço de rosto água micelar
    chocolate continente
    spray glade
    picanha américa do sul
    """.strip().splitlines()

    app = QApplication(sys.argv)
    window = ShoppingUI()
    window.show()
    sys.exit(app.exec())