from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def create_settings_tab(main_window):
    """
    Creates the Settings tab with a placeholder label.

    Args:
        main_window: A reference to the main InfotainmentSystem instance.
                     (Currently not used by this simple tab, but good practice for consistency).
    """
    settings_tab = QWidget()
    layout = QVBoxLayout(settings_tab)
    label = QLabel("Settings Placeholder")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setFont(QFont("Arial", 20))
    layout.addWidget(label)
    return settings_tab
