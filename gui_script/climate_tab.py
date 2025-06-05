import sys
import copy  # Import the copy module for deepcopy
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QPushButton, QSlider, QSizePolicy, QGroupBox,
    QButtonGroup
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer

# --- Constants ---
SEAT_STATE_OFF = 0
SEAT_STATE_HEAT = 1
SEAT_STATE_COOL = 2

AIR_DIST_OFF = 0
AIR_DIST_WINDSHIELD = 1
AIR_DIST_FACE = 2
AIR_DIST_FEET = 3


class ClimateTab(QWidget):
    """
    Manages the UI, state, and logic for the Climate Control Tab.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Climate-specific State Variables ---
        self.target_temp = 21.0
        self.current_temp = 18.0
        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_current_temperature)
        self.temp_timer_interval = 1000

        self.seat_states = {
            "seat_fl": SEAT_STATE_OFF, "seat_fr": SEAT_STATE_OFF,
            "seat_rl": SEAT_STATE_OFF, "seat_rr": SEAT_STATE_OFF,
        }
        self.seat_button_widgets = {}

        self.air_distribution_buttons = {}
        self.active_air_distribution = {"windshield": False, "face": True, "feet": False}

        self.climate_profiles = [None] * 3
        self.default_profile_settings = {
            "target_temp": 21.0,
            "fan_speed": 2,
            "ac_on": True,
            "recirc_on": False,
            "air_dist": {"windshield": False, "face": True, "feet": False},
            "seat_states": {"seat_fl": SEAT_STATE_OFF, "seat_fr": SEAT_STATE_OFF,
                            "seat_rl": SEAT_STATE_OFF, "seat_rr": SEAT_STATE_OFF},
            "wheel_heat_on": False,
            "front_defrost_on": False,
            "rear_defrost_on": False
        }
        self.active_profile_index = None
        self._is_applying_profile = False
        self.profile_buttons = []  # Initialize before use

        # --- UI Setup ---
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Column 1: Current Temp, Sliders, General Controls, Profiles ---
        left_column_layout = QVBoxLayout()
        left_column_layout.setSpacing(15)

        current_temp_layout = QVBoxLayout()
        current_temp_title_label = QLabel("Current Vehicle Temp")
        current_temp_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_temp_display = QLabel(f"{self.current_temp:.1f}°C")
        self.current_temp_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_temp_display.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        current_temp_layout.addWidget(current_temp_title_label)
        current_temp_layout.addWidget(self.current_temp_display)
        left_column_layout.addLayout(current_temp_layout)
        left_column_layout.addSpacing(20)

        temp_group_layout = QHBoxLayout()
        temp_label_ui = QLabel("Set Temp:")
        self.temp_value_label = QLabel(f"{int(self.target_temp)}°C")
        self.temp_value_label.setMinimumWidth(50)
        self.temp_value_label.setFont(QFont("Arial", 16))
        temp_group_layout.addWidget(temp_label_ui)
        temp_group_layout.addWidget(self.temp_value_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(16, 30)
        self.temp_slider.setValue(int(self.target_temp))
        self.temp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temp_slider.setTickInterval(1)
        self.temp_slider.setMinimumWidth(220)
        self.temp_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.temp_slider.valueChanged.connect(self.handle_temp_slider_change)
        left_column_layout.addLayout(temp_group_layout)
        left_column_layout.addWidget(self.temp_slider)

        fan_group_layout = QHBoxLayout()
        fan_label_ui = QLabel("Fan Speed:")
        self.fan_value_label = QLabel("3")
        self.fan_value_label.setMinimumWidth(50)
        self.fan_value_label.setFont(QFont("Arial", 16))
        fan_group_layout.addWidget(fan_label_ui)
        fan_group_layout.addWidget(self.fan_value_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.fan_slider = QSlider(Qt.Orientation.Horizontal)
        self.fan_slider.setRange(0, 5)
        self.fan_slider.setValue(3)
        self.fan_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fan_slider.setTickInterval(1)
        self.fan_slider.setMinimumWidth(220)
        self.fan_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.fan_slider.valueChanged.connect(self.handle_fan_slider_change)
        left_column_layout.addLayout(fan_group_layout)
        left_column_layout.addWidget(self.fan_slider)
        left_column_layout.addSpacing(10)

        general_controls_layout = QHBoxLayout()
        self.ac_button = QPushButton("A/C")
        self.ac_button.setCheckable(True)
        self.ac_button.setChecked(True)
        self.ac_button.toggled.connect(self.handle_ac_button_toggled)
        self.update_ac_button_text(True, from_profile_load=True)
        self.recirculate_button = QPushButton("Recirculate")
        self.recirculate_button.setCheckable(True)
        self.recirculate_button.setChecked(False)
        self.recirculate_button.toggled.connect(self.handle_recirc_button_toggled)
        self.update_recirc_button_text(False, from_profile_load=True)

        general_controls_layout.addWidget(self.ac_button)
        general_controls_layout.addWidget(self.recirculate_button)
        left_column_layout.addLayout(general_controls_layout)
        left_column_layout.addSpacing(15)

        profiles_group = QGroupBox("Climate Profiles")
        profiles_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        profiles_v_layout = QVBoxLayout(profiles_group)
        profiles_v_layout.setSpacing(10)

        self.profile_button_group = QButtonGroup(self)
        self.profile_button_group.setExclusive(True)

        self.profile_button1 = QPushButton("Profile 1")
        self.profile_button2 = QPushButton("Profile 2")
        self.profile_button3 = QPushButton("Profile 3")

        self.profile_buttons = [self.profile_button1, self.profile_button2, self.profile_button3]

        for i, btn in enumerate(self.profile_buttons):
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 11))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setMinimumHeight(35)
            self.profile_button_group.addButton(btn, i)
            profiles_v_layout.addWidget(btn)

        self.save_current_settings_button = QPushButton("Save to Active Profile")
        self.save_current_settings_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.save_current_settings_button.setMinimumHeight(35)
        self.save_current_settings_button.clicked.connect(self.save_current_climate_profile)
        profiles_v_layout.addWidget(self.save_current_settings_button)

        self.profile_button_group.buttonToggled.connect(self.handle_climate_profile_button_toggled)

        left_column_layout.addWidget(profiles_group, 1)

        # --- Column 2: Vehicle, Air Flow, Passenger Comfort ---
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(15)

        vehicle_systems_group = QGroupBox("Vehicle Systems")
        vehicle_systems_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        vehicle_systems_layout = QHBoxLayout(vehicle_systems_group)
        vehicle_systems_layout.setSpacing(10)
        self.wheel_heater_button = QPushButton("Steering Wheel")
        self.wheel_heater_button.setCheckable(True)
        self.wheel_heater_button.toggled.connect(self.handle_wheel_heater_toggle)
        self.wheel_heater_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.front_defrost_button = QPushButton("Front Defrost")
        self.front_defrost_button.setCheckable(True)
        self.front_defrost_button.toggled.connect(self.handle_front_defrost_toggle)
        self.front_defrost_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rear_defrost_button = QPushButton("Rear Defrost")
        self.rear_defrost_button.setCheckable(True)
        self.rear_defrost_button.toggled.connect(self.handle_rear_defrost_toggle)
        self.rear_defrost_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        vehicle_systems_layout.addWidget(self.wheel_heater_button, 1)
        vehicle_systems_layout.addWidget(self.front_defrost_button, 1)
        vehicle_systems_layout.addWidget(self.rear_defrost_button, 1)
        right_column_layout.addWidget(vehicle_systems_group, 1)

        air_flow_group = QGroupBox("Air Flow")
        air_flow_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        air_flow_buttons_layout = QHBoxLayout(air_flow_group)
        air_flow_buttons_layout.setSpacing(10)
        self.air_dist_windshield_button = QPushButton("Windshield")
        self.air_dist_face_button = QPushButton("Face")
        self.air_dist_feet_button = QPushButton("Feet")
        air_dist_buttons_defs = [
            (self.air_dist_windshield_button, "windshield"),
            (self.air_dist_face_button, "face"),
            (self.air_dist_feet_button, "feet")
        ]
        for btn, mode_key in air_dist_buttons_defs:
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.toggled.connect(lambda checked, key=mode_key: self.handle_air_distribution_toggle(key, checked))
            self.air_distribution_buttons[mode_key] = btn
            air_flow_buttons_layout.addWidget(btn, 1)
        self.update_air_distribution_styles()
        right_column_layout.addWidget(air_flow_group, 1)

        passenger_comfort_group = QGroupBox("Passenger Comfort")
        passenger_comfort_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        seat_grid_layout = QGridLayout(passenger_comfort_group)
        seat_grid_layout.setSpacing(10)
        seat_fl_button = QPushButton("Front L")
        seat_fr_button = QPushButton("Front R")
        seat_rl_button = QPushButton("Rear L")
        seat_rr_button = QPushButton("Rear R")
        seat_buttons_list_defs = [
            ("seat_fl", seat_fl_button), ("seat_fr", seat_fr_button),
            ("seat_rl", seat_rl_button), ("seat_rr", seat_rr_button)
        ]
        for seat_id, btn in seat_buttons_list_defs:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.seat_button_widgets[seat_id] = {"widget": btn, "original_text": btn.text()}
            btn.clicked.connect(lambda checked=False, sid=seat_id: self.handle_seat_button_click(sid))
        seat_grid_layout.addWidget(self.seat_button_widgets["seat_fl"]["widget"], 0, 0)
        seat_grid_layout.addWidget(self.seat_button_widgets["seat_fr"]["widget"], 0, 1)
        seat_grid_layout.addWidget(self.seat_button_widgets["seat_rl"]["widget"], 1, 0)
        seat_grid_layout.addWidget(self.seat_button_widgets["seat_rr"]["widget"], 1, 1)
        seat_grid_layout.setColumnStretch(0, 1)
        seat_grid_layout.setColumnStretch(1, 1)
        seat_grid_layout.setRowStretch(0, 1)
        seat_grid_layout.setRowStretch(1, 1)
        right_column_layout.addWidget(passenger_comfort_group, 2)

        main_layout.addLayout(left_column_layout, 1)
        main_layout.addLayout(right_column_layout, 1)

        self.update_temp_label(self.temp_slider.value(), from_profile_load=True)
        self.update_fan_label(self.fan_slider.value(), from_profile_load=True)
        self.update_current_temp_display()
        self.update_all_seat_button_styles()

        if self.profile_buttons:
            self.profile_buttons[0].setChecked(True)

    def _clear_active_profile_highlight(self):
        if self._is_applying_profile:
            return
        print("Clearing active profile highlight due to manual change.")
        self.active_profile_index = None
        self.update_profile_button_styles()

        # --- Climate Profile Methods ---

    def populate_climate_profiles_list(self):
        pass

    def handle_climate_profile_button_toggled(self, button, checked):
        if checked:
            profile_id = self.profile_button_group.id(button)
            print(f"Climate Profile {profile_id + 1} button selected.")
            self.apply_climate_profile(profile_id)

    def apply_climate_profile(self, profile_index):
        if not (0 <= profile_index < len(self.climate_profiles)):
            return

        profile_data_source = self.climate_profiles[profile_index]
        if profile_data_source is None:
            print(f"Profile {profile_index + 1} is empty. Applying default climate settings.")
            profile_data = copy.deepcopy(self.default_profile_settings)
        else:
            print(f"Applying Climate Profile {profile_index + 1}")
            profile_data = copy.deepcopy(profile_data_source)

        self._is_applying_profile = True

        # Disconnect signals
        self.temp_slider.valueChanged.disconnect(self.handle_temp_slider_change)
        self.fan_slider.valueChanged.disconnect(self.handle_fan_slider_change)
        self.ac_button.toggled.disconnect(self.handle_ac_button_toggled)
        self.recirculate_button.toggled.disconnect(self.handle_recirc_button_toggled)
        self.wheel_heater_button.toggled.disconnect(self.handle_wheel_heater_toggle)
        self.front_defrost_button.toggled.disconnect(self.handle_front_defrost_toggle)
        self.rear_defrost_button.toggled.disconnect(self.handle_rear_defrost_toggle)
        for btn in self.air_distribution_buttons.values():
            try:
                btn.toggled.disconnect()
            except TypeError:
                pass
        for btn_info in self.seat_button_widgets.values():
            try:
                btn_info["widget"].clicked.disconnect()
            except TypeError:
                pass

        # Apply settings
        self.temp_slider.setValue(int(profile_data["target_temp"]))
        self.fan_slider.setValue(profile_data["fan_speed"])
        self.ac_button.setChecked(profile_data["ac_on"])
        self.recirculate_button.setChecked(profile_data["recirc_on"])

        self.active_air_distribution = profile_data["air_dist"]
        # Update checked state of air distribution buttons based on loaded profile
        for mode_key, btn in self.air_distribution_buttons.items():
            btn.setChecked(self.active_air_distribution.get(mode_key, False))

        self.seat_states = profile_data["seat_states"]
        self.wheel_heater_button.setChecked(profile_data["wheel_heat_on"])
        self.front_defrost_button.setChecked(profile_data.get("front_defrost_on", False))
        self.rear_defrost_button.setChecked(profile_data.get("rear_defrost_on", False))

        # Update UI elements that don't auto-update from signals
        self.update_temp_label(self.temp_slider.value(), from_profile_load=True)
        self.update_fan_label(self.fan_slider.value(), from_profile_load=True)
        self.update_ac_button_text(self.ac_button.isChecked(), from_profile_load=True)
        self.update_recirc_button_text(self.recirculate_button.isChecked(), from_profile_load=True)
        self.update_air_distribution_styles()
        self.update_all_seat_button_styles()
        self.update_wheel_heater_style(self.wheel_heater_button.isChecked(), from_profile_load=True)
        self.update_front_defrost_style(self.front_defrost_button.isChecked(), from_profile_load=True)
        self.update_rear_defrost_style(self.rear_defrost_button.isChecked(), from_profile_load=True)

        # Reconnect signals
        self.temp_slider.valueChanged.connect(self.handle_temp_slider_change)
        self.fan_slider.valueChanged.connect(self.handle_fan_slider_change)
        self.ac_button.toggled.connect(self.handle_ac_button_toggled)
        self.recirculate_button.toggled.connect(self.handle_recirc_button_toggled)
        self.wheel_heater_button.toggled.connect(self.handle_wheel_heater_toggle)
        self.front_defrost_button.toggled.connect(self.handle_front_defrost_toggle)
        self.rear_defrost_button.toggled.connect(self.handle_rear_defrost_toggle)
        for mode_key, btn in self.air_distribution_buttons.items():
            btn.toggled.connect(lambda checked, key=mode_key: self.handle_air_distribution_toggle(key, checked))
        for seat_id, btn_info in self.seat_button_widgets.items():
            btn_info["widget"].clicked.connect(lambda checked=False, sid=seat_id: self.handle_seat_button_click(sid))

        self._is_applying_profile = False
        self.active_profile_index = profile_index
        self.update_profile_button_styles()

    def save_current_climate_profile(self):
        checked_button = self.profile_button_group.checkedButton()
        if not checked_button:
            print("No profile selected to save to. Please select a profile button first.")
            return

        profile_index = self.profile_button_group.id(checked_button)

        current_settings = {
            "target_temp": self.temp_slider.value(),
            "fan_speed": self.fan_slider.value(),
            "ac_on": self.ac_button.isChecked(),
            "recirc_on": self.recirculate_button.isChecked(),
            "air_dist": copy.deepcopy(self.active_air_distribution),
            "seat_states": copy.deepcopy(self.seat_states),
            "wheel_heat_on": self.wheel_heater_button.isChecked(),
            "front_defrost_on": self.front_defrost_button.isChecked(),
            "rear_defrost_on": self.rear_defrost_button.isChecked()
        }
        self.climate_profiles[profile_index] = current_settings
        print(f"Climate settings saved to Profile {profile_index + 1}")

        self.active_profile_index = profile_index
        self.update_profile_button_styles()

    def update_profile_button_styles(self):
        active_style = "QPushButton { background-color: #2ECC71; color: black; border: 1px solid #27AE60; font-weight: bold; }"
        inactive_style = "QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; }"

        for i, btn in enumerate(self.profile_buttons):
            if btn:
                if self.active_profile_index == i:
                    btn.setStyleSheet(active_style)
                else:
                    btn.setStyleSheet(inactive_style)
                if self.active_profile_index is not None:
                    btn.setChecked(self.active_profile_index == i)

    # --- Specific Control Handlers that can trigger _clear_active_profile_highlight ---
    def handle_temp_slider_change(self, value):
        self.update_temp_label(value, from_profile_load=False)

    def handle_fan_slider_change(self, value):
        self.update_fan_label(value, from_profile_load=False)

    def handle_ac_button_toggled(self, checked):
        self.update_ac_button_text(checked, from_profile_load=False)

    def handle_recirc_button_toggled(self, checked):
        self.update_recirc_button_text(checked, from_profile_load=False)

    def update_ac_button_text(self, checked, from_profile_load=False):
        self.ac_button.setText("A/C " + ("ON" if checked else "OFF"))
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_recirc_button_text(self, checked, from_profile_load=False):
        self.recirculate_button.setText("Recirc " + ("ON" if checked else "OFF"))
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_front_defrost_style(self, checked, from_profile_load=False):
        self.front_defrost_button.setStyleSheet("background-color: #E67E22; color: white;" if checked else "")
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def handle_front_defrost_toggle(self, checked):
        print(f"Front Defrost: {'ON' if checked else 'OFF'}")
        self.update_front_defrost_style(checked)

    def update_rear_defrost_style(self, checked, from_profile_load=False):
        self.rear_defrost_button.setStyleSheet("background-color: #E67E22; color: white;" if checked else "")
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def handle_rear_defrost_toggle(self, checked):
        print(f"Rear Defrost: {'ON' if checked else 'OFF'}")
        self.update_rear_defrost_style(checked)

    def handle_air_distribution_toggle(self, mode_key, checked):
        self.active_air_distribution[mode_key] = checked
        self.update_air_distribution_styles()
        print(f"Air to {mode_key}: {'ON' if checked else 'OFF'}, Current: {self.active_air_distribution}")
        if not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_air_distribution_styles(self):
        for mode_key, button in self.air_distribution_buttons.items():
            # Update button style
            button.setStyleSheet(
                "background-color: #007ACC; color: white;" if self.active_air_distribution.get(mode_key, False) else "")
            # Also update its checked state to match the model, blocking signals
            # This is important if apply_climate_profile directly sets self.active_air_distribution
            # and then calls this method to update the UI.
            is_checked_in_model = self.active_air_distribution.get(mode_key, False)
            if button.isChecked() != is_checked_in_model:
                blocked = button.signalsBlocked()
                button.blockSignals(True)
                button.setChecked(is_checked_in_model)
                button.blockSignals(blocked)

    def update_temp_label(self, value, from_profile_load=False):
        self.target_temp = float(value)
        self.temp_value_label.setText(f"{value}°C")
        if not self.temp_timer.isActive():
            self.temp_timer.start(self.temp_timer_interval)
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_fan_label(self, value, from_profile_load=False):
        self.fan_value_label.setText("Off" if value == 0 else str(value))
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_current_temperature(self):
        temp_diff = self.target_temp - self.current_temp
        adjustment_step = 0.5
        if abs(temp_diff) < adjustment_step:
            self.current_temp = self.target_temp
            self.temp_timer.stop()
        elif temp_diff > 0:
            self.current_temp += adjustment_step
        else:
            self.current_temp -= adjustment_step
        self.update_current_temp_display()

    def update_current_temp_display(self):
        self.current_temp_display.setText(f"{self.current_temp:.1f}°C")

    def handle_seat_button_click(self, seat_id):
        current_state = self.seat_states.get(seat_id, SEAT_STATE_OFF)
        next_state = (current_state + 1) % 3
        self.seat_states[seat_id] = next_state
        self.update_seat_button_style(seat_id)
        print(f"Seat {seat_id} set to state: {next_state}")
        if not self._is_applying_profile: self._clear_active_profile_highlight()

    def update_seat_button_style(self, seat_id):
        button_info = self.seat_button_widgets.get(seat_id)
        if not button_info: return
        button = button_info["widget"]
        original_text = button_info["original_text"]
        state = self.seat_states.get(seat_id)
        button.setStyleSheet("")
        if state == SEAT_STATE_HEAT:
            button.setText("Heating...")
            button.setStyleSheet("background-color: #E67E22; border: 1px solid #D35400;")
        elif state == SEAT_STATE_COOL:
            button.setText("Cooling...")
            button.setStyleSheet("background-color: #3498DB; border: 1px solid #2980B9;")
        else:
            button.setText(original_text)

    def update_all_seat_button_styles(self):
        for seat_id in self.seat_button_widgets.keys():
            self.update_seat_button_style(seat_id)

    def update_wheel_heater_style(self, checked, from_profile_load=False):
        self.wheel_heater_button.setStyleSheet(
            "background-color: #E67E22; border: 1px solid #D35400;" if checked else "")
        if not from_profile_load and not self._is_applying_profile: self._clear_active_profile_highlight()

    def handle_wheel_heater_toggle(self, checked):
        print("Wheel Heater: ON" if checked else "Wheel Heater: OFF")
        self.update_wheel_heater_style(checked)


# --- Standalone Test ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_palette_test = QPalette()
    dark_palette_test.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette_test.setColor(QPalette.ColorRole.WindowText, QColor(221, 221, 221))
    app.setPalette(dark_palette_test)
    app.setStyleSheet("""
        QWidget { font-size: 15px; color: #DDD; }
        QGroupBox { font-size: 12px; font-weight: bold; border: 1px solid #555; border-radius: 5px; margin-top: 10px; padding: 10px;}
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px;}
        QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; padding: 8px 15px; border-radius: 4px; min-height: 30px; }
        QPushButton:hover { background-color: #5A5A5A; }
        QListWidget { background-color: #2A2A2A; border: 1px solid #444; border-radius: 4px; color: #DDD; padding: 5px; }
        QListWidget::item:selected { background-color: #007ACC; color: white; } 
        QSlider::groove:horizontal { border: 1px solid #5A5A5A; height: 12px; background: #404040; margin: 2px 0; border-radius: 6px; }
        QSlider::handle:horizontal { background: #007ACC; border: 1px solid #005C99; width: 20px; margin: -4px 0; border-radius: 10px; }
    """)
    climate_tab_widget = ClimateTab()
    test_window = QMainWindow();
    test_window.setCentralWidget(climate_tab_widget)
    test_window.setWindowTitle("Climate Tab Test");
    test_window.setGeometry(300, 300, 800, 550)
    test_window.show()
    sys.exit(app.exec())
