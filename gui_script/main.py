import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QGridLayout, QPushButton, QSlider, QLineEdit,
    QSizePolicy, QListWidget, QListWidgetItem, QFrame, QSplitter
    # QStackedWidget might not be needed if home page is removed
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer, QDateTime  # QDateTime not used if home page is removed

# --- Import Tab Creation Functions/Classes ---
# from home_page_ui import HomePage # Commented out Home Page
from car_control_tab import CarControlTab
from media_tab import MediaTab
from phone_tab import PhoneTab
from climate_tab import ClimateTab
from maps_tab import MapsTab
from settings_tab import create_settings_tab


# from maps_tab_ui import MapsTab # Commented out Maps Tab


# --- Theme Palettes ---
def get_dark_palette():
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
    return dark_palette


def get_light_palette():
    light_palette = QPalette()
    light_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(230, 230, 230))
    light_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    light_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    light_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    light_palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
    light_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    light_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
    light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120))
    light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
    return light_palette


# Stylesheets (remains the same as your provided version)
DARK_STYLESHEET = """
    QWidget { font-size: 15px; }
    QTabWidget::pane { border: 1px solid #444; background-color: #2A2A2A; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; }
    QTabBar::tab { min-width: 90px; padding: 15px 10px; font-size: 15px; border: 1px solid #444; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; background-color: #353535; color: #BBB; margin-right: 2px; }
    QTabBar::tab:selected { background-color: #2A2A2A; color: #FFF; border-color: #444; border-bottom-color: #2A2A2A; }
    QTabBar::tab:!selected { margin-top: 2px; background-color: #404040; }
    QTabWidget#PhoneLeftPanelTabs > QTabBar::tab, QTabWidget#PhoneFunctionsSubTabs > QTabBar::tab { min-width: 80px; padding: 8px 10px; font-size: 14px; }
    QTabWidget#MediaTypeSubTabs > QTabBar::tab { min-width: 80px; padding: 8px 10px; font-size: 14px; background-color: #353535; color: #BBB; margin-right: 2px; border: 1px solid #444; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;}
    QTabWidget#MediaTypeSubTabs > QTabBar::tab:selected { background-color: #2A2A2A; color: #FFF; }
    QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; padding: 8px 15px; border-radius: 4px; min-height: 30px; }
    QTabWidget#PhoneFunctionsSubTabs QGridLayout QPushButton { padding: 5px; font-size: 16px; }
    QPushButton#ToggleMediaListButton, QPushButton#ToggleLocationsListButton { min-width: 25px; max-width: 25px; padding: 5px 2px; font-size: 18px; font-weight: bold; border-radius: 0px; background-color: #303030; border: 1px solid #444; border-left: none; border-right: none; }
    QPushButton#ToggleMediaListButton:hover, QPushButton#ToggleLocationsListButton:hover { background-color: #404040; }
    QPushButton:hover { background-color: #5A5A5A; border: 1px solid #666; }
    QPushButton:pressed { background-color: #3A3A3A; }
    QPushButton:checked { background-color: #007ACC; border: 1px solid #005C99; }
    QPushButton:disabled { background-color: #3A3A3A; color: #888; border: 1px solid #444; }
    QLabel { color: #DDD; }
    /* QLabel#DateTimeLabel { color: #E0E0E0; } */ /* Commented out as Home Page is removed */
    /* QPushButton#HomePageNavButton { } */ /* Commented out as Home Page is removed */
    QLineEdit { background-color: #353535; border: 1px solid #555; padding: 5px 10px; font-size: 14px; border-radius: 4px; color: #FFF; min-height: 25px; }
    QLineEdit#PhoneDisplay { font-size: 18px; min-height: 35px; }
    QListWidget { background-color: #2A2A2A; border: 1px solid #444; border-radius: 4px; color: #DDD; padding: 5px; }
    QListWidget::item { padding: 8px 5px; border-bottom: 1px solid #383838; }
    QListWidget::item:last-child { border-bottom: none; }
    QListWidget::item:selected { background-color: #2ECC71; color: black; border-radius: 3px; }
    QListWidget::item:hover:!selected { background-color: #404040; }
    QWidget#MediaSidePanel, QWidget#LocationsSidePanel { background-color: #303030; border-right: 1px solid #444; }
    QWidget#MediaContentPanel, QWidget#MapContentPanel { background-color: #2A2A2A; border-left: 1px solid #444; }
    QSplitter::handle { background-color: #555; }
    QSplitter::handle:horizontal { width: 2px; }
    QSplitter::handle:vertical { height: 2px; }
    QSplitter::handle:pressed { background-color: #007ACC; }
    QSlider::groove:horizontal { border: 1px solid #5A5A5A; height: 12px; background: #404040; margin: 2px 0; border-radius: 6px; }
    QSlider::handle:horizontal { background: #007ACC; border: 1px solid #005C99; width: 20px; margin: -4px 0; border-radius: 10px; }
    QSlider::add-page:horizontal { background: #666; border-radius: 6px; }
    QSlider::sub-page:horizontal { background: #007ACC; border-radius: 6px; }
    QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #555; border-radius: 5px; margin-top: 10px; padding: 10px; color: #DDD;}
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; color: #DDD;}
    QRadioButton { padding: 5px; color: #DDD;}
    QComboBox { background-color: #353535; color: white; border: 1px solid #555; padding: 5px; border-radius: 3px; min-width: 100px;}
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView { background-color: #353535; color: white; selection-background-color: #007ACC; }
"""

LIGHT_STYLESHEET = """ 
    QWidget { font-size: 15px; background-color: #f0f0f0; color: #333; }
    QTabWidget::pane { border: 1px solid #c0c0c0; background-color: #e9e9e9; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; }
    QTabBar::tab { min-width: 90px; padding: 15px 10px; font-size: 15px; border: 1px solid #c0c0c0; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; background-color: #e0e0e0; color: #444; margin-right: 2px; }
    QTabBar::tab:selected { background-color: #e9e9e9; color: #000; border-color: #c0c0c0; border-bottom-color: #e9e9e9; }
    QTabBar::tab:!selected { margin-top: 2px; background-color: #d0d0d0; }
    QTabWidget#PhoneLeftPanelTabs > QTabBar::tab, QTabWidget#PhoneFunctionsSubTabs > QTabBar::tab { min-width: 80px; padding: 8px 10px; font-size: 14px; }
    QTabWidget#MediaTypeSubTabs > QTabBar::tab { min-width: 80px; padding: 8px 10px; font-size: 14px; background-color: #e0e0e0; color: #444; margin-right: 2px; border: 1px solid #c0c0c0; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;}
    QTabWidget#MediaTypeSubTabs > QTabBar::tab:selected { background-color: #e9e9e9; color: #000; }
    QPushButton { background-color: #e1e1e1; color: #333; border: 1px solid #adadad; padding: 8px 15px; border-radius: 4px; min-height: 30px; }
    QTabWidget#PhoneFunctionsSubTabs QGridLayout QPushButton { padding: 5px; font-size: 16px; }
    QPushButton#ToggleMediaListButton, QPushButton#ToggleLocationsListButton { min-width: 25px; max-width: 25px; padding: 5px 2px; font-size: 18px; font-weight: bold; border-radius: 0px; background-color: #d0d0d0; border: 1px solid #b0b0b0; border-left: none; border-right: none; }
    QPushButton#ToggleMediaListButton:hover, QPushButton#ToggleLocationsListButton:hover { background-color: #c0c0c0; }
    QPushButton:hover { background-color: #dadada; border: 1px solid #999; }
    QPushButton:pressed { background-color: #c0c0c0; }
    QPushButton:checked { background-color: #0078d7; border: 1px solid #005394; color: white; }
    QPushButton:disabled { background-color: #d0d0d0; color: #888; border: 1px solid #b0b0b0; }
    QLabel { color: #333; }
    /* QLabel#DateTimeLabel { color: #222; } */
    /* QPushButton#HomePageNavButton { background-color: #e8e8e8; color: #333; border: 1px solid #b0b0b0; padding: 10px; border-radius: 8px; } */
    /* QPushButton#HomePageNavButton:hover { background-color: #d8d8d8; } */
    /* QPushButton#HomePageNavButton:pressed { background-color: #c8c8c8; } */
    QLineEdit { background-color: #ffffff; border: 1px solid #c0c0c0; padding: 5px 10px; font-size: 14px; border-radius: 4px; color: #333; min-height: 25px; }
    QLineEdit#PhoneDisplay { font-size: 18px; min-height: 35px; }
    QListWidget { background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 4px; color: #333; padding: 5px; }
    QListWidget::item { padding: 8px 5px; border-bottom: 1px solid #e0e0e0; }
    QListWidget::item:last-child { border-bottom: none; }
    QListWidget::item:selected { background-color: #0078d7; color: white; border-radius: 3px; } 
    QListWidget::item:hover:!selected { background-color: #e0e0e0; }
    QWidget#MediaSidePanel, QWidget#LocationsSidePanel { background-color: #e0e0e0; border-right: 1px solid #c0c0c0; }
    QWidget#MediaContentPanel, QWidget#MapContentPanel { background-color: #e9e9e9; border-left: 1px solid #c0c0c0; }
    QSplitter::handle { background-color: #c0c0c0; }
    QSplitter::handle:horizontal { width: 2px; }
    QSplitter::handle:vertical { height: 2px; }
    QSplitter::handle:pressed { background-color: #0078d7; }
    QSlider::groove:horizontal { border: 1px solid #c0c0c0; height: 12px; background: #d0d0d0; margin: 2px 0; border-radius: 6px; }
    QSlider::handle:horizontal { background: #0078d7; border: 1px solid #005394; width: 20px; margin: -4px 0; border-radius: 10px; }
    QSlider::add-page:horizontal { background: #e0e0e0; border-radius: 6px; }
    QSlider::sub-page:horizontal { background: #0078d7; border-radius: 6px; }
    QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #c0c0c0; border-radius: 5px; margin-top: 10px; padding: 10px; color: #333;}
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; color: #333;}
    QRadioButton { padding: 5px; color: #333;}
    QComboBox { background-color: #ffffff; color: #333; border: 1px solid #c0c0c0; padding: 5px; border-radius: 3px; min-width: 100px;}
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView { background-color: #ffffff; color: #333; selection-background-color: #0078d7; selection-color: white; }
"""


class InfotainmentSystem(QMainWindow):
    """
    Main window class for the automotive infotainment system GUI.
    Displays a tabbed interface for functions.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automotive Infotainment System")
        self.setGeometry(100, 100, 800, 480)
        self.current_theme_name = "Dark"

        # Central widget is now directly the QTabWidget container
        self.central_tab_widget_container = QWidget()
        self.setCentralWidget(self.central_tab_widget_container)
        main_layout = QVBoxLayout(self.central_tab_widget_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainAppTabs")
        main_layout.addWidget(self.tabs)

        # --- Create and Add Functional Tabs ---
        self.car_control_tab_instance = CarControlTab(parent=self)
        self.tabs.addTab(self.car_control_tab_instance, "Car Controls")

        self.media_tab_instance = MediaTab(parent=self)
        self.tabs.addTab(self.media_tab_instance, "Media")

        self.phone_tab_instance = PhoneTab(parent=self)
        self.tabs.addTab(self.phone_tab_instance, "Phone")

        self.climate_tab_instance = ClimateTab(parent=self)
        self.tabs.addTab(self.climate_tab_instance, "Climate")

        settings_tab_content = create_settings_tab(self.media_tab_instance, self)
        self.tabs.addTab(settings_tab_content, "Settings")

        self.maps_tab_instance = MapsTab(parent=self) # Commented out Maps Tab
        self.tabs.addTab(self.maps_tab_instance, "Maps")

        # Home button tab and QStackedWidget for home page are removed/commented
        # home_button_tab = QWidget()
        # self.tabs.addTab(home_button_tab, "Home")
        # self.tabs.currentChanged.connect(self.check_for_home_tab_selection)

    def apply_theme(self, theme_name):
        """Applies the selected theme (Dark or Light) to the application."""
        self.current_theme_name = theme_name
        if theme_name == "Light":
            QApplication.instance().setPalette(get_light_palette())
            QApplication.instance().setStyleSheet(LIGHT_STYLESHEET)
        else:  # Default to Dark
            QApplication.instance().setPalette(get_dark_palette())
            QApplication.instance().setStyleSheet(DARK_STYLESHEET)
        print(f"Theme applied: {theme_name}")


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setPalette(get_dark_palette())
    app.setStyleSheet(DARK_STYLESHEET)

    window = InfotainmentSystem()
    window.show()
    sys.exit(app.exec())
