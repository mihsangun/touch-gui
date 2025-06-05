import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QFileDialog, QMessageBox, QMainWindow,
    QButtonGroup, QGridLayout  # Added QButtonGroup
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from pathlib import Path


# This function will create the settings tab content
def create_settings_tab(media_tab_ref, main_window_ref):
    """
    Creates the Settings tab with options to configure media source paths and application theme.
    Args:
        media_tab_ref: A direct reference to the MediaTab instance.
        main_window_ref: Reference to the main InfotainmentSystem window.
    """
    settings_tab_widget = QWidget()
    main_layout = QVBoxLayout(settings_tab_widget)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(25)
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    # --- Media Source Paths Group ---
    media_paths_group = QGroupBox("Media Source Directories")
    media_paths_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    paths_layout = QGridLayout(media_paths_group)
    paths_layout.setSpacing(10)

    paths_layout.addWidget(QLabel("Music Folder Path:"), 0, 0)
    music_path_edit = QLineEdit()
    music_path_edit.setObjectName("MusicPathEdit")
    if media_tab_ref and hasattr(media_tab_ref, 'music_source_dir'):
        music_path_edit.setText(str(media_tab_ref.music_source_dir))
    else:
        script_dir = Path(__file__).resolve().parent
        default_music_path = script_dir.parent / "media" / "music"
        music_path_edit.setText(str(default_music_path))
        if not media_tab_ref: print("Warning (SettingsTab Init): media_tab_ref is None for music path.")

    music_browse_button = QPushButton("Browse...")
    paths_layout.addWidget(music_path_edit, 0, 1)
    paths_layout.addWidget(music_browse_button, 0, 2)

    paths_layout.addWidget(QLabel("Video Folder Path:"), 1, 0)
    video_path_edit = QLineEdit()
    video_path_edit.setObjectName("VideoPathEdit")
    if media_tab_ref and hasattr(media_tab_ref, 'video_source_dir'):
        video_path_edit.setText(str(media_tab_ref.video_source_dir))
    else:
        script_dir = Path(__file__).resolve().parent
        default_video_path = script_dir.parent / "media" / "video"
        video_path_edit.setText(str(default_video_path))
        if not media_tab_ref: print("Warning (SettingsTab Init): media_tab_ref is None for video path.")

    video_browse_button = QPushButton("Browse...")
    paths_layout.addWidget(video_path_edit, 1, 1)
    paths_layout.addWidget(video_browse_button, 1, 2)
    paths_layout.setColumnStretch(1, 1)

    update_paths_button = QPushButton("Update Media Paths")
    update_paths_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    update_paths_button.setMinimumHeight(40)
    paths_layout.addWidget(update_paths_button, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

    # --- Theme Selection Group ---
    theme_group = QGroupBox("Application Theme")
    theme_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    theme_layout = QHBoxLayout(theme_group)
    theme_layout.setSpacing(10)

    theme_button_group = QButtonGroup(settings_tab_widget)  # Parent to the tab widget
    theme_button_group.setExclusive(True)  # Only one theme button can be active

    dark_theme_button = QPushButton("Dark Theme")
    dark_theme_button.setFont(QFont("Arial", 12))
    dark_theme_button.setCheckable(True)
    dark_theme_button.setObjectName("DarkThemeButton")  # For specific styling if needed
    theme_button_group.addButton(dark_theme_button)
    theme_layout.addWidget(dark_theme_button)

    light_theme_button = QPushButton("Light Theme")
    light_theme_button.setFont(QFont("Arial", 12))
    light_theme_button.setCheckable(True)
    light_theme_button.setObjectName("LightThemeButton")
    theme_button_group.addButton(light_theme_button)
    theme_layout.addWidget(light_theme_button)

    theme_layout.addStretch(1)

    def update_theme_button_styles():
        """Visually indicates the active theme button."""
        # Define styles for active/inactive theme buttons
        # These styles might need to be adjusted based on the global stylesheet
        # to ensure they override correctly or blend well.
        active_style = "QPushButton { background-color: #007ACC; color: white; border: 1px solid #005C99; font-weight: bold; }"
        inactive_style = "QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; }"  # Example, adjust as needed

        if hasattr(main_window_ref, 'current_theme_name'):
            if main_window_ref.current_theme_name == "Dark":
                dark_theme_button.setChecked(True)
                dark_theme_button.setStyleSheet(active_style)
                light_theme_button.setStyleSheet(inactive_style)
            elif main_window_ref.current_theme_name == "Light":
                light_theme_button.setChecked(True)
                light_theme_button.setStyleSheet(active_style)
                dark_theme_button.setStyleSheet(inactive_style)
            else:  # Default to dark if unknown
                dark_theme_button.setChecked(True)
                dark_theme_button.setStyleSheet(active_style)
                light_theme_button.setStyleSheet(inactive_style)
        else:  # Fallback if main_window_ref doesn't have the attribute yet
            dark_theme_button.setChecked(True)  # Default to Dark
            dark_theme_button.setStyleSheet(active_style)
            light_theme_button.setStyleSheet(inactive_style)

    def on_theme_button_clicked(button):
        selected_theme = "Dark"  # Default
        if button == light_theme_button:
            selected_theme = "Light"
        elif button == dark_theme_button:
            selected_theme = "Dark"

        if hasattr(main_window_ref, 'apply_theme'):
            main_window_ref.apply_theme(selected_theme)
            # QMessageBox.information(main_window_ref, "Theme Applied", f"{selected_theme} theme has been applied.")
            update_theme_button_styles()  # Update styles after applying
        else:
            QMessageBox.critical(main_window_ref, "Error", "Could not apply theme via main window.")

    theme_button_group.buttonClicked.connect(on_theme_button_clicked)
    update_theme_button_styles()  # Set initial active button style

    # --- Connections ---
    def browse_music_folder():
        folder_path = QFileDialog.getExistingDirectory(main_window_ref, "Select Music Folder")
        if folder_path:
            music_path_edit.setText(folder_path)

    def browse_video_folder():
        folder_path = QFileDialog.getExistingDirectory(main_window_ref, "Select Video Folder")
        if folder_path:
            video_path_edit.setText(folder_path)

    def apply_media_paths():
        music_path = music_path_edit.text()
        video_path = video_path_edit.text()
        if not music_path or not video_path:
            QMessageBox.warning(main_window_ref, "Input Error", "Both music and video paths must be specified.")
            return
        if not Path(music_path).is_dir() or not Path(video_path).is_dir():
            QMessageBox.warning(main_window_ref, "Path Error", "One or both specified paths are not valid directories.")
            return
        if media_tab_ref and hasattr(media_tab_ref, 'set_media_source_paths'):
            media_tab_ref.set_media_source_paths(music_path, video_path)
            QMessageBox.information(main_window_ref, "Success", "Media paths updated. Media tab will refresh.")
        else:
            QMessageBox.critical(main_window_ref, "Error", "Could not access MediaTab to update paths.")

    music_browse_button.clicked.connect(browse_music_folder)
    video_browse_button.clicked.connect(browse_video_folder)
    update_paths_button.clicked.connect(apply_media_paths)

    main_layout.addWidget(media_paths_group)
    main_layout.addWidget(theme_group)
    main_layout.addStretch(1)

    return settings_tab_widget


# --- Standalone Test ---
if __name__ == '__main__':
    app = QApplication(sys.argv)


    class MockMediaTab:
        music_source_dir = Path("../media/music")
        video_source_dir = Path("../media/video")

        def set_media_source_paths(self, music_path, video_path):
            print(f"MockMediaTab: Music path set to {music_path}")
            print(f"MockMediaTab: Video path set to {video_path}")
            self.music_source_dir = Path(music_path)
            self.video_source_dir = Path(video_path)


    class MockMainWindow(QMainWindow):
        media_tab_instance = MockMediaTab()
        current_theme_name = "Dark"

        def apply_theme(self, theme_name):
            print(f"MockMainWindow: Applying theme - {theme_name}")
            self.current_theme_name = theme_name
            # In a real app, this would change QPalette and app.setStyleSheet
            # For the test, we need to manually call update_theme_button_styles
            # if the settings_widget was accessible here, or the settings_widget
            # would need a way to be notified of theme changes.
            # For simplicity, the test won't visually update the button styles on mock apply.


    mock_main = MockMainWindow()

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
        QGroupBox { 
            font-size: 16px; font-weight: bold; 
            border: 1px solid #555; border-radius: 5px; 
            margin-top: 10px; padding: 10px;
        }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
        QPushButton { 
            background-color: #4A4A4A; color: #FFF; 
            border: 1px solid #555; padding: 8px 15px; 
            border-radius: 4px; min-height: 30px; 
        }
        QPushButton:hover { background-color: #5A5A5A; }
        QPushButton:checked { /* Default checked style, will be overridden by specific theme button styles */
            background-color: #007ACC; color: white; border: 1px solid #005C99;
        }
        QLineEdit { 
            background-color: #353535; border: 1px solid #555; 
            padding: 5px 10px; font-size: 14px; border-radius: 4px; 
            color: #FFF; min-height: 25px; 
        }
    """)

    settings_widget = create_settings_tab(mock_main.media_tab_instance, mock_main)

    test_window = QMainWindow()
    test_window.setCentralWidget(settings_widget)
    test_window.setWindowTitle("Settings Tab Test")
    test_window.setGeometry(300, 300, 600, 350)
    test_window.show()

    sys.exit(app.exec())
