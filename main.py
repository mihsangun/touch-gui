import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QGridLayout, QPushButton, QSlider, QLineEdit,
    QSizePolicy, QListWidget, QListWidgetItem, QFrame, QSplitter
    # QStackedWidget is no longer needed here
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer

# --- Import Tab Creation Functions/Classes ---
from car_control_tab import CarControlTab
from media_tab import MediaTab # This should be media_tab_ui_v9_py
from phone_tab import PhoneTab
from climate_tab import ClimateTab
from settings_tab import create_settings_tab


# --- Dark Theme Palette ---
dark_palette = QPalette()
dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(46, 204, 113))
dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))


class InfotainmentSystem(QMainWindow):
    """
    Main window class for the automotive infotainment system GUI.
    Coordinates all tabs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automotive Infotainment System")
        self.setGeometry(100, 100, 800, 480)

        # Central widget is now a simple QWidget holding the QTabWidget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # --- Create and Add Tabs using imported functions/classes ---
        self.car_control_tab_instance = CarControlTab(parent=self)
        self.tabs.addTab(self.car_control_tab_instance, "Car Controls")

        # MediaTab constructor no longer needs main_window_ref as fullscreen is reverted
        self.media_tab_instance = MediaTab(parent=self)
        self.tabs.addTab(self.media_tab_instance, "Media")

        self.phone_tab_instance = PhoneTab(parent=self)
        self.tabs.addTab(self.phone_tab_instance, "Phone")

        self.climate_tab_instance = ClimateTab(parent=self)
        self.tabs.addTab(self.climate_tab_instance, "Climate")

        self.tabs.addTab(create_settings_tab(self), "Settings")

    # Fullscreen methods are removed from InfotainmentSystem as they are no longer used
    # by the reverted MediaTab.

# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setPalette(dark_palette)
    app.setStyleSheet("""
        QWidget { font-size: 15px; }
        QTabWidget::pane { 
            border: 1px solid #444; background-color: #2A2A2A; 
            border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; 
        }
        QTabBar::tab { 
            min-width: 90px; padding: 15px 10px; font-size: 15px; 
            border: 1px solid #444; border-bottom: none; 
            border-top-left-radius: 4px; border-top-right-radius: 4px; 
            background-color: #353535; color: #BBB; margin-right: 2px; 
        }
        QTabBar::tab:selected { 
            background-color: #2A2A2A; color: #FFF; 
            border-color: #444; border-bottom-color: #2A2A2A; 
        }
        QTabBar::tab:!selected { margin-top: 2px; background-color: #404040; }
        QTabWidget#PhoneLeftPanelTabs > QTabBar::tab, 
        QTabWidget#PhoneFunctionsSubTabs > QTabBar::tab { 
            min-width: 80px; padding: 8px 10px; font-size: 14px; 
        }
        QPushButton { 
            background-color: #4A4A4A; color: #FFF; 
            border: 1px solid #555; padding: 8px 15px; 
            border-radius: 4px; min-height: 30px; 
        }
        QTabWidget#PhoneFunctionsSubTabs QGridLayout QPushButton { padding: 5px; font-size: 16px; }
        QPushButton#ToggleMediaListButton {
            min-width: 25px; max-width: 25px; padding: 5px 2px; 
            font-size: 18px; font-weight: bold; border-radius: 0px; 
            background-color: #303030; border: 1px solid #444; 
            border-left: none; border-right: none; 
        }
        QPushButton#ToggleMediaListButton:hover { background-color: #404040; }
        QPushButton:hover { background-color: #5A5A5A; border: 1px solid #666; }
        QPushButton:pressed { background-color: #3A3A3A; }
        QPushButton:checked { background-color: #007ACC; border: 1px solid #005C99; }
        QPushButton:disabled { background-color: #3A3A3A; color: #888; border: 1px solid #444; }
        QLabel { color: #DDD; }
        QLineEdit { 
            background-color: #353535; border: 1px solid #555; 
            padding: 5px 10px; font-size: 14px; border-radius: 4px; 
            color: #FFF; min-height: 25px; 
        }
        QLineEdit#PhoneDisplay { font-size: 18px; min-height: 35px; }
        QListWidget { 
            background-color: #2A2A2A; border: 1px solid #444; 
            border-radius: 4px; color: #DDD; padding: 5px; 
        }
        QListWidget::item { padding: 8px 5px; border-bottom: 1px solid #383838; }
        QListWidget::item:last-child { border-bottom: none; }
        QListWidget::item:selected { background-color: #2ECC71; color: black; border-radius: 3px; }
        QListWidget::item:hover:!selected { background-color: #404040; }
        QWidget#MediaSidePanel { background-color: #303030; border-right: 1px solid #444; }
        QWidget#MediaContentPanel { background-color: #2A2A2A; border-left: 1px solid #444; }
        QSplitter::handle { background-color: #555; }
        QSplitter::handle:horizontal { width: 2px; }
        QSplitter::handle:vertical { height: 2px; }
        QSplitter::handle:pressed { background-color: #007ACC; }
        QSlider::groove:horizontal { 
            border: 1px solid #5A5A5A; height: 12px; 
            background: #404040; margin: 2px 0; border-radius: 6px; 
        }
        QSlider::handle:horizontal { 
            background: #007ACC; border: 1px solid #005C99; 
            width: 20px; margin: -4px 0; border-radius: 10px; 
        }
        QSlider::add-page:horizontal { background: #666; border-radius: 6px; }
        QSlider::sub-page:horizontal { background: #007ACC; border-radius: 6px; }
        QGroupBox { 
            font-size: 16px; font-weight: bold; 
            border: 1px solid #555; border-radius: 5px; 
            margin-top: 10px; padding: 10px;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; subcontrol-position: top left; 
            padding: 0 5px; left: 10px;
        }
        QRadioButton { padding: 5px; }
    """)
    window = InfotainmentSystem()
    window.show()
    sys.exit(app.exec())
