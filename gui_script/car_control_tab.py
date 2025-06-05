import sys
import random  # Added for random data simulation
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QPushButton, QSlider, QGroupBox, QRadioButton, QButtonGroup,
    QSizePolicy
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer  # Added QTimer


class CarControlTab(QWidget):
    """
    Manages the UI and logic for the Car Control Tab, including
    cruise information, performance modes, and seat position adjustments.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CarControlTab")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Cruise Information Group ---
        cruise_info_group = QGroupBox("Cruise Information")
        cruise_info_group.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        # Main horizontal layout for cruise info items
        cruise_info_main_layout = QHBoxLayout()
        cruise_info_main_layout.setSpacing(20)  # Spacing between Speed, Fuel, Range blocks

        # Speed Block
        speed_block_layout = QVBoxLayout()
        speed_block_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center items in this block
        self.speed_label = QLabel("Speed")  # Simplified label
        self.speed_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Larger and Bold
        self.speed_value_label = QLabel("0 km/h")
        self.speed_value_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))  # Larger and Bold
        self.speed_value_label.setStyleSheet("color: #2ECC71;")
        speed_block_layout.addWidget(self.speed_label)
        speed_block_layout.addWidget(self.speed_value_label)
        cruise_info_main_layout.addLayout(speed_block_layout)
        cruise_info_main_layout.addStretch(1)  # Add stretch after speed block

        # Fuel Consumption Block
        fuel_block_layout = QVBoxLayout()
        fuel_block_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fuel_consumption_label = QLabel("Avg. Fuel")  # Simplified label
        self.fuel_consumption_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Larger and Bold
        self.fuel_consumption_value_label = QLabel("0.0 L/100km")
        self.fuel_consumption_value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))  # Larger and Bold
        fuel_block_layout.addWidget(self.fuel_consumption_label)
        fuel_block_layout.addWidget(self.fuel_consumption_value_label)
        cruise_info_main_layout.addLayout(fuel_block_layout)
        cruise_info_main_layout.addStretch(1)  # Add stretch after fuel block

        # Range Block
        range_block_layout = QVBoxLayout()
        range_block_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.range_label = QLabel("Est. Range")  # Simplified label
        self.range_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Larger and Bold
        self.range_value_label = QLabel("0 km")
        self.range_value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))  # Larger and Bold
        range_block_layout.addWidget(self.range_label)
        range_block_layout.addWidget(self.range_value_label)
        cruise_info_main_layout.addLayout(range_block_layout)
        # No stretch after the last block if we want them to distribute space

        cruise_info_group.setLayout(cruise_info_main_layout)
        main_layout.addWidget(cruise_info_group)

        self.cruise_data_timer = QTimer(self)
        self.cruise_data_timer.timeout.connect(self.update_cruise_data)
        self.cruise_data_timer.start(1500)

        self.current_speed = 0
        self.base_avg_fuel_consumption = 7.5
        self.base_estimated_range = 450
        self.mode_avg_fuel_consumption = self.base_avg_fuel_consumption
        self.mode_estimated_range = self.base_estimated_range

        # --- Performance Mode Group ---
        performance_group = QGroupBox("Performance Mode")
        performance_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        performance_layout = QHBoxLayout()

        self.performance_button_group = QButtonGroup(self)
        self.performance_button_group.setExclusive(True)

        self.perf_eco_button = QPushButton("Eco")
        self.perf_comfort_button = QPushButton("Comfort")
        self.perf_sport_button = QPushButton("Sport")

        perf_buttons = [self.perf_eco_button, self.perf_comfort_button, self.perf_sport_button]
        for btn in perf_buttons:
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 12))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setMinimumHeight(40)
            self.performance_button_group.addButton(btn)
            performance_layout.addWidget(btn)

        self.perf_eco_button.setChecked(True)
        self.current_performance_mode = "Eco"
        self.set_performance_mode_effects()
        self.update_performance_button_styles()

        self.performance_button_group.buttonClicked.connect(self.handle_performance_mode_change)
        performance_group.setLayout(performance_layout)
        main_layout.addWidget(performance_group)

        # --- Select Seat Group ---
        select_seat_group = QGroupBox("Select Seat to Adjust")
        select_seat_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        select_seat_layout = QHBoxLayout()

        self.seat_selection_group = QButtonGroup(self)
        self.seat_selection_group.setExclusive(True)

        self.driver_seat_select_button = QPushButton("Driver")
        self.passenger_seat_select_button = QPushButton("Front Passenger")

        seat_select_buttons = [self.driver_seat_select_button, self.passenger_seat_select_button]
        for btn in seat_select_buttons:
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 12))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setMinimumHeight(40)
            self.seat_selection_group.addButton(btn)
            select_seat_layout.addWidget(btn)

        self.driver_seat_select_button.setChecked(True)
        self.current_selected_seat = "Driver"
        self.update_seat_selection_button_styles()
        self.seat_selection_group.buttonClicked.connect(self.handle_seat_selection_change)
        select_seat_group.setLayout(select_seat_layout)
        main_layout.addWidget(select_seat_group)

        # --- Seat Position Control Group ---
        self.seat_control_group = QGroupBox(f"{self.current_selected_seat} Seat Position")
        self.seat_control_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        seat_layout = QGridLayout()
        seat_layout.setSpacing(10)

        seat_layout.addWidget(QLabel("Forward/Backward:"), 0, 0)
        self.seat_fb_slider = QSlider(Qt.Orientation.Horizontal)
        self.seat_fb_slider.setRange(0, 10);
        self.seat_fb_slider.setValue(5)
        self.seat_fb_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.seat_fb_slider.valueChanged.connect(self.driver_seat_fb_changed)
        seat_layout.addWidget(self.seat_fb_slider, 0, 1)
        self.seat_fb_label = QLabel("5")
        seat_layout.addWidget(self.seat_fb_label, 0, 2)

        seat_layout.addWidget(QLabel("Recline Angle:"), 1, 0)
        self.seat_recline_slider = QSlider(Qt.Orientation.Horizontal)
        self.seat_recline_slider.setRange(0, 10);
        self.seat_recline_slider.setValue(3)
        self.seat_recline_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.seat_recline_slider.valueChanged.connect(self.driver_seat_recline_changed)
        seat_layout.addWidget(self.seat_recline_slider, 1, 1)
        self.seat_recline_label = QLabel("3")
        seat_layout.addWidget(self.seat_recline_label, 1, 2)

        seat_layout.addWidget(QLabel("Height:"), 2, 0)
        self.seat_height_slider = QSlider(Qt.Orientation.Horizontal)
        self.seat_height_slider.setRange(0, 5);
        self.seat_height_slider.setValue(2)
        self.seat_height_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.seat_height_slider.valueChanged.connect(self.driver_seat_height_changed)
        seat_layout.addWidget(self.seat_height_slider, 2, 1)
        self.seat_height_label = QLabel("2")
        seat_layout.addWidget(self.seat_height_label, 2, 2)

        preset_layout = QHBoxLayout()
        self.preset1_button = QPushButton("Preset 1")
        self.preset2_button = QPushButton("Preset 2")
        self.save_preset_button = QPushButton("Save Current Preset")
        self.preset1_button.clicked.connect(lambda: self.load_seat_preset(1))
        self.preset2_button.clicked.connect(lambda: self.load_seat_preset(2))
        self.save_preset_button.clicked.connect(self.save_current_seat_preset)

        preset_layout.addWidget(self.preset1_button)
        preset_layout.addWidget(self.preset2_button)
        preset_layout.addStretch()
        preset_layout.addWidget(self.save_preset_button)
        seat_layout.addLayout(preset_layout, 3, 0, 1, 3)

        self.seat_control_group.setLayout(seat_layout)
        main_layout.addWidget(self.seat_control_group)
        main_layout.addStretch(1)

        self.seat_presets = {
            "Driver": {
                1: {"fb": 2, "recline": 7, "height": 1},
                2: {"fb": 8, "recline": 4, "height": 4}
            },
            "Front Passenger": {
                1: {"fb": 3, "recline": 6, "height": 2},
                2: {"fb": 7, "recline": 5, "height": 3}
            }
        }
        self.active_preset_for_current_seat = None
        self.last_interacted_preset_slot = {
            "Driver": 1,
            "Front Passenger": 1
        }
        self.update_preset_button_styles()
        self.load_seat_preset(self.last_interacted_preset_slot[self.current_selected_seat])

    def update_cruise_data(self):
        speed_change = random.randint(-5, 5)
        self.current_speed += speed_change
        if self.current_speed < 0: self.current_speed = 0
        if self.current_speed > 180: self.current_speed = 180
        self.speed_value_label.setText(f"{self.current_speed} km/h")

        current_display_fuel = self.mode_avg_fuel_consumption + random.uniform(-0.3, 0.3)
        current_display_fuel = max(2.0, min(current_display_fuel, 20.0))
        self.fuel_consumption_value_label.setText(f"{current_display_fuel:.1f} L/100km")

        current_display_range = self.mode_estimated_range + random.randint(-10, 10)
        current_display_range = max(0, current_display_range)
        self.range_value_label.setText(f"{current_display_range} km")

    def handle_performance_mode_change(self, button):
        self.current_performance_mode = button.text()
        self.set_performance_mode_effects()
        self.update_performance_button_styles()
        print(f"Performance Mode set to: {self.current_performance_mode}")

    def set_performance_mode_effects(self):
        if self.current_performance_mode == "Eco":
            self.mode_avg_fuel_consumption = self.base_avg_fuel_consumption * 0.8
            self.mode_estimated_range = self.base_estimated_range * 1.2
        elif self.current_performance_mode == "Sport":
            self.mode_avg_fuel_consumption = self.base_avg_fuel_consumption * 1.3
            self.mode_estimated_range = self.base_estimated_range * 0.7
        else:  # Comfort
            self.mode_avg_fuel_consumption = self.base_avg_fuel_consumption
            self.mode_estimated_range = self.base_estimated_range
        self.fuel_consumption_value_label.setText(f"{self.mode_avg_fuel_consumption:.1f} L/100km")
        self.range_value_label.setText(f"{int(self.mode_estimated_range)} km")

    def update_performance_button_styles(self):
        default_style = "QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; } QPushButton:hover { background-color: #5A5A5A; } QPushButton:pressed { background-color: #3A3A3A; }"
        eco_active_style = "QPushButton { background-color: #2ECC71; color: black; border: 1px solid #27AE60; font-weight: bold; } QPushButton:hover { background-color: #29B865; } QPushButton:pressed { background-color: #25A25A; }"
        comfort_active_style = "QPushButton { background-color: #3498DB; color: white; border: 1px solid #2980B9; font-weight: bold; } QPushButton:hover { background-color: #2C81B8; } QPushButton:pressed { background-color: #256DA4; }"
        sport_active_style = "QPushButton { background-color: #E74C3C; color: white; border: 1px solid #C0392B; font-weight: bold; } QPushButton:hover { background-color: #D35400; } QPushButton:pressed { background-color: #A93226; }"

        buttons_and_styles = [
            (self.perf_eco_button, eco_active_style),
            (self.perf_comfort_button, comfort_active_style),
            (self.perf_sport_button, sport_active_style)
        ]
        for button, active_style_str in buttons_and_styles:
            if button:
                button.setStyleSheet(active_style_str if button.isChecked() else default_style)

    def handle_seat_selection_change(self, button):
        self.current_selected_seat = button.text()
        self.seat_control_group.setTitle(f"{self.current_selected_seat} Seat Position")
        print(f"Selected seat for adjustment: {self.current_selected_seat}")
        self.update_seat_selection_button_styles()
        self.active_preset_for_current_seat = None
        if self.current_selected_seat not in self.last_interacted_preset_slot:
            self.last_interacted_preset_slot[self.current_selected_seat] = 1
        self.load_seat_preset(self.last_interacted_preset_slot[self.current_selected_seat])
        self.update_preset_button_styles()

    def update_seat_selection_button_styles(self):
        default_style = "QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; } QPushButton:hover { background-color: #5A5A5A; } QPushButton:pressed { background-color: #3A3A3A; }"
        active_style = "QPushButton { background-color: #5DADE2; color: white; border: 1px solid #3498DB; font-weight: bold; } QPushButton:hover { background-color: #4A90E2; } QPushButton:pressed { background-color: #3071A9; }"
        for button in self.seat_selection_group.buttons():
            if button:
                button.setStyleSheet(active_style if button.isChecked() else default_style)

    def driver_seat_fb_changed(self, value):
        self.seat_fb_label.setText(str(value))
        print(f"{self.current_selected_seat} Seat Forward/Backward: {value}")
        self.active_preset_for_current_seat = None
        self.update_preset_button_styles()

    def driver_seat_recline_changed(self, value):
        self.seat_recline_label.setText(str(value))
        print(f"{self.current_selected_seat} Seat Recline Angle: {value}")
        self.active_preset_for_current_seat = None
        self.update_preset_button_styles()

    def driver_seat_height_changed(self, value):
        self.seat_height_label.setText(str(value))
        print(f"{self.current_selected_seat} Seat Height: {value}")
        self.active_preset_for_current_seat = None
        self.update_preset_button_styles()

    def load_seat_preset(self, preset_number):
        seat_specific_presets = self.seat_presets.get(self.current_selected_seat, {})
        preset = seat_specific_presets.get(preset_number)
        if preset:
            slider_connections = [
                (self.seat_fb_slider, self.driver_seat_fb_changed),
                (self.seat_recline_slider, self.driver_seat_recline_changed),
                (self.seat_height_slider, self.driver_seat_height_changed)
            ]
            for slider, handler in slider_connections:
                try:
                    slider.valueChanged.disconnect(handler)
                except TypeError:
                    pass

            self.seat_fb_slider.setValue(preset["fb"])
            self.seat_recline_slider.setValue(preset["recline"])
            self.seat_height_slider.setValue(preset["height"])

            self.seat_fb_label.setText(str(preset["fb"]))
            self.seat_recline_label.setText(str(preset["recline"]))
            self.seat_height_label.setText(str(preset["height"]))

            for slider, handler in slider_connections:
                slider.valueChanged.connect(handler)

            self.active_preset_for_current_seat = preset_number
            self.last_interacted_preset_slot[self.current_selected_seat] = preset_number
            print(f"Loaded Preset {preset_number} for {self.current_selected_seat}")
        else:
            print(f"Preset {preset_number} for {self.current_selected_seat} not found. Sliders unchanged.")
            self.active_preset_for_current_seat = None
        self.update_preset_button_styles()

    def save_current_seat_preset(self):
        current_settings = {
            "fb": self.seat_fb_slider.value(),
            "recline": self.seat_recline_slider.value(),
            "height": self.seat_height_slider.value()
        }
        if self.current_selected_seat not in self.seat_presets:
            self.seat_presets[self.current_selected_seat] = {}

        preset_to_save = self.last_interacted_preset_slot.get(self.current_selected_seat, 1)

        self.seat_presets[self.current_selected_seat][preset_to_save] = current_settings
        self.active_preset_for_current_seat = preset_to_save
        print(f"Saved current settings to Preset {preset_to_save} for {self.current_selected_seat}")
        self.update_preset_button_styles()

    def update_preset_button_styles(self):
        default_style = "QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; } QPushButton:hover { background-color: #5A5A5A; } QPushButton:pressed { background-color: #3A3A3A; }"
        active_preset_style = "QPushButton { background-color: #F39C12; color: black; border: 1px solid #D35400; font-weight: bold; } QPushButton:hover { background-color: #E67E22; } QPushButton:pressed { background-color: #C0392B; }"

        buttons_to_update = [
            (getattr(self, 'preset1_button', None), 1, "Preset 1"),
            (getattr(self, 'preset2_button', None), 2, "Preset 2")
        ]
        for button_widget, preset_num, base_text in buttons_to_update:
            if button_widget:
                button_widget.setText(base_text)
                button_widget.setStyleSheet(
                    active_preset_style if self.active_preset_for_current_seat == preset_num else default_style)


# --- Standalone Test ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_palette_test = QPalette()
    dark_palette_test.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette_test.setColor(QPalette.ColorRole.WindowText, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette_test.setColor(QPalette.ColorRole.Text, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Button, QColor(74, 74, 74))
    dark_palette_test.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette_test.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
    dark_palette_test.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
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
        QSlider::groove:horizontal { 
            border: 1px solid #5A5A5A; height: 12px; 
            background: #404040; margin: 2px 0; border-radius: 6px; 
        }
        QSlider::handle:horizontal { 
            background: #007ACC; border: 1px solid #005C99; 
            width: 20px; margin: -4px 0; border-radius: 10px; 
        }
    """)

    car_control_tab_widget = CarControlTab()
    test_window = QMainWindow()
    test_window.setCentralWidget(car_control_tab_widget)
    test_window.setWindowTitle("Car Control Tab Test")
    test_window.setGeometry(300, 300, 550, 600)
    test_window.show()
    sys.exit(app.exec())
