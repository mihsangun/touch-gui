import sys
from pathlib import Path  # Import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QPushButton, QGroupBox, QSizePolicy, QMainWindow
)
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap  # Import QPixmap
from PyQt6.QtCore import Qt, QTimer, QDateTime


class HomePage(QWidget):
    """
    Manages the UI and logic for the Home Page, including clock, date, logo,
    and navigation buttons to other tabs.
    """

    def __init__(self, main_window_ref, parent=None):
        super().__init__(parent)
        self.main_window_ref = main_window_ref  # Reference to InfotainmentSystem
        self.setObjectName("HomePageWidget")

        home_layout = QVBoxLayout(self)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(15)

        # --- Date, Logo, and Time Display ---
        datetime_logo_container_layout = QHBoxLayout()
        datetime_logo_container_layout.setSpacing(15)

        self.date_label = QLabel()
        self.date_label.setObjectName("DateLabel")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.date_label.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        datetime_logo_container_layout.addWidget(self.date_label, 2, Qt.AlignmentFlag.AlignRight)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("LogoLabel")
        self.logo_label.setMinimumSize(96, 96)
        self.logo_label.setMaximumSize(192, 192)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        try:
            script_dir = Path(__file__).resolve().parent
            logo_dir = script_dir.parent / "logo"
            logo_file_name = "logo2.png"
            logo_path = logo_dir / logo_file_name

            print(f"Attempting to load logo from: {logo_path.resolve()}")

            if logo_path.exists() and logo_path.is_file():
                pixmap = QPixmap(str(logo_path))
                if pixmap.isNull():
                    self.logo_label.setText("Logo\nFailed\nLoad")
                    self.logo_label.setFont(QFont("Arial", 64))
                    print(
                        f"Error: QPixmap failed to load the image from {logo_path.resolve()}. The file might be corrupted or not a valid image format.")
                else:
                    self.logo_label.setPixmap(pixmap.scaled(
                        self.logo_label.maximumWidth(), self.logo_label.maximumHeight(),
                        Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    ))
            else:
                self.logo_label.setText("Logo\nN/A")
                self.logo_label.setFont(QFont("Arial", 16))
                print(f"Logo file not found. Checked absolute path: {logo_path.resolve()}")
                print(f"Please ensure '{logo_file_name}' exists in the directory '{logo_dir.resolve()}'")
        except Exception as e:
            self.logo_label.setText("Logo\nError")
            self.logo_label.setFont(QFont("Arial", 16))
            print(f"An unexpected error occurred while loading logo: {e}")
            import traceback
            traceback.print_exc()

        datetime_logo_container_layout.addWidget(self.logo_label, 1, Qt.AlignmentFlag.AlignCenter)

        self.time_label = QLabel()
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.time_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        datetime_logo_container_layout.addWidget(self.time_label, 2, Qt.AlignmentFlag.AlignLeft)

        home_layout.addLayout(datetime_logo_container_layout, 0)  # Row for date/time/logo, no vertical stretch

        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

        # --- Navigation Buttons Grid ---
        nav_buttons_group = QGroupBox()
        nav_buttons_group.setStyleSheet("QGroupBox { border: none; }")
        grid_layout = QGridLayout(nav_buttons_group)
        grid_layout.setSpacing(20)

        button_font = QFont("Arial", 18, QFont.Weight.Bold)

        btn_car_controls = QPushButton("Car Controls")
        btn_media = QPushButton("Media Player")
        btn_phone = QPushButton("Phone")
        btn_climate = QPushButton("Climate")
        btn_settings = QPushButton("Settings")
        btn_maps = QPushButton("Maps (Spare)")

        # Define a single blue color for active buttons
        active_button_color_hex = "#3498DB"  # A nice blue
        disabled_button_color_hex = "#BDC3C7"  # Grey for spare/disabled
        button_text_color = "white"
        disabled_button_text_color = "black"

        buttons_config = [
            (btn_car_controls, 0),
            (btn_media, 1),
            (btn_phone, 2),
            (btn_climate, 3),
            (btn_settings, 4),
            (btn_maps, None)  # Spare button
        ]

        row, col = 0, 0
        for btn, tab_index in buttons_config:
            btn.setFont(button_font)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setObjectName("HomePageNavButton")

            current_bg_color = active_button_color_hex
            current_text_color = button_text_color

            if tab_index is None:  # Spare button
                current_bg_color = disabled_button_color_hex
                current_text_color = disabled_button_text_color
                btn.setEnabled(False)
            else:
                btn.clicked.connect(lambda checked=False, idx=tab_index: self.main_window_ref.navigate_to_tab(idx))

            btn.setStyleSheet(f"""
                QPushButton#HomePageNavButton {{
                    background-color: {current_bg_color};
                    color: {current_text_color}; 
                    border: 1px solid #333; 
                    padding: 10px;
                    border-radius: 8px;
                }}
                QPushButton#HomePageNavButton:hover {{
                    background-color: {QColor(current_bg_color).lighter(115).name() if tab_index is not None else current_bg_color};
                }}
                QPushButton#HomePageNavButton:pressed {{
                    background-color: {QColor(current_bg_color).darker(115).name() if tab_index is not None else current_bg_color};
                }}
                QPushButton#HomePageNavButton:disabled {{
                    background-color: {disabled_button_color_hex}; 
                    color: {disabled_button_text_color};
                }}
            """)

            grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Ensure the grid layout itself expands
        for r_idx in range(row + 1):
            grid_layout.setRowStretch(r_idx, 1)
        for c_idx in range(3):
            grid_layout.setColumnStretch(c_idx, 1)

        # Give the nav_buttons_group a high stretch factor to fill remaining space
        home_layout.addWidget(nav_buttons_group, 1)  # Changed stretch factor to 1 (or any positive value)

    def update_datetime(self):
        """Updates the clock and date label."""
        current_datetime = QDateTime.currentDateTime()
        date_string = current_datetime.toString("dddd, MMMM d, yyyy")  # Corrected year format
        time_string = current_datetime.toString("hh:mm:ss AP")

        if hasattr(self, 'date_label'):
            self.date_label.setText(date_string)
        if hasattr(self, 'time_label'):
            self.time_label.setText(time_string)


# --- Standalone Test (Optional) ---
if __name__ == '__main__':
    app = QApplication(sys.argv)


    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Mock Main Window for Home Page Test")
            self.home_page = HomePage(self)
            self.setCentralWidget(self.home_page)
            self.setGeometry(300, 300, 800, 600)

        def navigate_to_tab(self, tab_index):
            print(f"Mock Main: Navigating to tab index {tab_index}")


    script_dir_test = Path(__file__).resolve().parent
    logo_dir_test = script_dir_test.parent / "logo"
    logo_dir_test.mkdir(parents=True, exist_ok=True)
    dummy_logo_path = logo_dir_test / "logo.jpg"
    if not dummy_logo_path.exists():
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new('RGB', (128, 128), color='darkgray')
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            d.text((30, 55), "Logo", fill=(255, 255, 0), font=font)
            img.save(dummy_logo_path)
            print(f"Created dummy logo for test: {dummy_logo_path}")
        except ImportError:
            dummy_logo_path.touch(exist_ok=True)
            print(f"Pillow not found, created empty dummy logo: {dummy_logo_path}")
        except Exception as e:
            print(f"Could not create dummy logo: {e}")

    dark_palette_test = QPalette()
    dark_palette_test.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette_test.setColor(QPalette.ColorRole.WindowText, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette_test.setColor(QPalette.ColorRole.Text, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Button, QColor(74, 74, 74))
    dark_palette_test.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    app.setPalette(dark_palette_test)
    app.setStyleSheet("""
        QWidget { font-size: 15px; color: #DDD; }
        QGroupBox { border: none; }
        /* Styles for HomePageNavButton are now set inline */
        QLabel#DateLabel, QLabel#TimeLabel { color: #E0E0E0; }
        QLabel#LogoLabel { border: 1px solid #444; } 
    """)

    test_window = MockMainWindow()
    test_window.show()
    sys.exit(app.exec())
