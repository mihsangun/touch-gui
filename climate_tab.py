import sys # Added for standalone testing
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, # Added for standalone testing
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton,
    QSlider, QSizePolicy
)
from PyQt6.QtGui import QFont, QPalette, QColor # Added for standalone testing
from PyQt6.QtCore import Qt, QTimer

# --- Constants ---
# Define constants for seat states for clarity
SEAT_STATE_OFF = 0
SEAT_STATE_HEAT = 1
SEAT_STATE_COOL = 2

class ClimateTab(QWidget):
    """
    Manages the UI, state, and logic for the Climate Control Tab.
    This class is designed to be instantiated and added as a tab to a QTabWidget.
    """
    def __init__(self, parent=None): # parent argument is good practice for QWidgets
        super().__init__(parent)

        # --- Climate-specific State Variables ---
        self.target_temp = 21.0 # Initial target temperature
        self.current_temp = 18.0 # Initial current temperature
        self.temp_timer = QTimer(self) # Timer for simulating gradual temperature change
        self.temp_timer.timeout.connect(self.update_current_temperature)
        self.temp_timer_interval = 1000 # Update current temp every 1000ms (1 second)

        self.seat_states = { # Store state (Off, Heat, Cool) for each seat button
            "seat_fl": SEAT_STATE_OFF, # Front Left
            "seat_fr": SEAT_STATE_OFF, # Front Right
            "seat_rl": SEAT_STATE_OFF, # Rear Left
            "seat_rr": SEAT_STATE_OFF, # Rear Right
        }
        # Store button widgets and their original text
        self.seat_button_widgets = {} # Format: { "seat_id": {"widget": QPushButton, "original_text": "Text"} }


        # --- UI Setup ---
        # Main layout for the ClimateTab widget itself
        main_layout = QHBoxLayout(self) # 'self' is the ClimateTab QWidget
        main_layout.setSpacing(20)

        # --- Column 1: Sliders, AC/Recirc, Current Temp ---
        left_column_layout = QVBoxLayout()
        left_column_layout.setSpacing(15)

        # Temperature Control
        temp_group_layout = QHBoxLayout()
        temp_label_ui = QLabel("Set Temp:")
        self.temp_value_label = QLabel(f"{int(self.target_temp)}°C")
        self.temp_value_label.setMinimumWidth(40)
        self.temp_value_label.setFont(QFont("Arial", 14))
        temp_group_layout.addWidget(temp_label_ui)
        temp_group_layout.addWidget(self.temp_value_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(16, 30)
        self.temp_slider.setValue(int(self.target_temp))
        self.temp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temp_slider.setTickInterval(1)
        self.temp_slider.setMinimumWidth(180) # Increased min width for sliders
        self.temp_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.temp_slider.valueChanged.connect(self.update_temp_label)

        left_column_layout.addLayout(temp_group_layout)
        left_column_layout.addWidget(self.temp_slider)

        # Fan Speed Control
        fan_group_layout = QHBoxLayout()
        fan_label_ui = QLabel("Fan Speed:")
        self.fan_value_label = QLabel("3")
        self.fan_value_label.setMinimumWidth(40)
        self.fan_value_label.setFont(QFont("Arial", 14))
        fan_group_layout.addWidget(fan_label_ui)
        fan_group_layout.addWidget(self.fan_value_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.fan_slider = QSlider(Qt.Orientation.Horizontal)
        self.fan_slider.setRange(0, 5)
        self.fan_slider.setValue(3)
        self.fan_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fan_slider.setTickInterval(1)
        self.fan_slider.setMinimumWidth(180) # Increased min width for sliders
        self.fan_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.fan_slider.valueChanged.connect(self.update_fan_label)

        left_column_layout.addLayout(fan_group_layout)
        left_column_layout.addWidget(self.fan_slider)
        left_column_layout.addSpacing(20) # Add some space

        # AC and Recirculate Buttons (Moved to left column)
        ac_recirc_layout = QHBoxLayout()
        self.ac_button = QPushButton("A/C On/Off")
        self.ac_button.setCheckable(True)
        self.ac_button.setChecked(True)
        self.recirculate_button = QPushButton("Recirculate On/Off")
        self.recirculate_button.setCheckable(True)
        self.recirculate_button.setChecked(False)
        ac_recirc_layout.addWidget(self.ac_button)
        ac_recirc_layout.addWidget(self.recirculate_button)
        left_column_layout.addLayout(ac_recirc_layout)
        left_column_layout.addSpacing(10)


        # Current Temp Display (Moved to left column)
        current_temp_layout = QVBoxLayout()
        current_temp_title_label = QLabel("Current Vehicle Temp") # Clarified label
        current_temp_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_temp_display = QLabel(f"{self.current_temp:.1f}°C")
        self.current_temp_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_temp_display.setFont(QFont("Arial", 30, QFont.Weight.Bold)) # Increased font size
        current_temp_layout.addWidget(current_temp_title_label)
        current_temp_layout.addWidget(self.current_temp_display)
        left_column_layout.addLayout(current_temp_layout)

        left_column_layout.addStretch(1) # Push elements towards the top

        # --- Column 2: Seat/Wheel Controls ---
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(10)
        right_column_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        seat_wheel_grid_layout = QGridLayout()
        seat_wheel_grid_layout.setSpacing(10)

        # Wheel Heater Button
        self.wheel_heater_button = QPushButton("Steering Wheel")
        self.wheel_heater_button.setCheckable(True)
        self.wheel_heater_button.toggled.connect(self.handle_wheel_heater_toggle)
        self.wheel_heater_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.wheel_heater_button.setMinimumHeight(60) # Increased minimum height
        seat_wheel_grid_layout.addWidget(self.wheel_heater_button, 0, 0, 1, 2)

        # Seat Buttons
        seat_fl_button = QPushButton("Front Left Seat")
        seat_fr_button = QPushButton("Front Right Seat")
        seat_rl_button = QPushButton("Rear Left Seat")
        seat_rr_button = QPushButton("Rear Right Seat")

        seat_buttons_list_defs = [
            ("seat_fl", seat_fl_button),
            ("seat_fr", seat_fr_button),
            ("seat_rl", seat_rl_button),
            ("seat_rr", seat_rr_button)
        ]

        for seat_id, btn in seat_buttons_list_defs:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(60) # Increased minimum height
            self.seat_button_widgets[seat_id] = {"widget": btn, "original_text": btn.text()} # Store widget and original text
            btn.clicked.connect(lambda checked=False, sid=seat_id: self.handle_seat_button_click(sid))


        seat_wheel_grid_layout.addWidget(self.seat_button_widgets["seat_fl"]["widget"], 1, 0)
        seat_wheel_grid_layout.addWidget(self.seat_button_widgets["seat_fr"]["widget"], 1, 1)
        seat_wheel_grid_layout.addWidget(self.seat_button_widgets["seat_rl"]["widget"], 2, 0)
        seat_wheel_grid_layout.addWidget(self.seat_button_widgets["seat_rr"]["widget"], 2, 1)


        # Set column stretch for the grid to make buttons expand
        seat_wheel_grid_layout.setColumnStretch(0, 1)
        seat_wheel_grid_layout.setColumnStretch(1, 1)
        # Set row stretch for the grid rows to allow buttons to expand vertically
        seat_wheel_grid_layout.setRowStretch(0, 1) # Wheel button row
        seat_wheel_grid_layout.setRowStretch(1, 1) # Front seats row
        seat_wheel_grid_layout.setRowStretch(2, 1) # Rear seats row


        right_column_layout.addLayout(seat_wheel_grid_layout)
        # Removed addStretch(1) from right_column_layout to allow grid to take more vertical space

        # --- Add columns to main layout ---
        main_layout.addLayout(left_column_layout, 1)
        main_layout.addLayout(right_column_layout, 2) # Give right column more stretch factor

        # Initialize UI states specific to this tab
        self.update_temp_label(int(self.target_temp))
        self.update_current_temp_display()
        self.update_all_seat_button_styles()


    # --- Climate Tab Specific Methods ---
    def update_temp_label(self, value):
        """Updates the target temperature value and label when the slider changes."""
        self.target_temp = float(value)
        self.temp_value_label.setText(f"{value}°C")
        if not self.temp_timer.isActive():
            self.temp_timer.start(self.temp_timer_interval)

    def update_fan_label(self, value):
        """Updates the fan speed label when the slider changes."""
        fan_text = "Off" if value == 0 else str(value)
        self.fan_value_label.setText(fan_text)

    def update_current_temperature(self):
        """Simulates gradual change of current temperature towards the target."""
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
        """Updates the text of the current temperature display label."""
        self.current_temp_display.setText(f"{self.current_temp:.1f}°C")

    def handle_seat_button_click(self, seat_id):
        """Cycles through states (Off -> Heat -> Cool -> Off) for the clicked seat button."""
        current_state = self.seat_states.get(seat_id, SEAT_STATE_OFF)
        next_state = (current_state + 1) % 3
        self.seat_states[seat_id] = next_state
        self.update_seat_button_style(seat_id) # This will now also update text
        print(f"Seat {seat_id} set to state: {next_state} (0=Off, 1=Heat, 2=Cool)")

    def update_seat_button_style(self, seat_id):
        """Updates the appearance and text of a single seat button based on its state."""
        button_info = self.seat_button_widgets.get(seat_id)
        if not button_info: return

        button = button_info["widget"]
        original_text = button_info["original_text"]
        state = self.seat_states.get(seat_id)

        button.setStyleSheet("") # Reset to default stylesheet style

        if state == SEAT_STATE_HEAT:
            button.setText("Heating...")
            button.setStyleSheet("background-color: #E67E22; border: 1px solid #D35400;") # Orange/Red for Heat
        elif state == SEAT_STATE_COOL:
            button.setText("Cooling...")
            button.setStyleSheet("background-color: #3498DB; border: 1px solid #2980B9;") # Blue for Cool
        else: # SEAT_STATE_OFF
            button.setText(original_text)
            # Off state uses the default style applied by the global stylesheet

    def update_all_seat_button_styles(self):
        """Updates the style and text of all seat buttons, typically called on initialization."""
        for seat_id in self.seat_button_widgets.keys(): # Iterate through the new dict
            self.update_seat_button_style(seat_id)

    def handle_wheel_heater_toggle(self, checked):
        """Handles the steering wheel heater button toggle signal."""
        if checked:
            self.wheel_heater_button.setStyleSheet("background-color: #E67E22; border: 1px solid #D35400;") # Orange/Red for On
            # self.wheel_heater_button.setText("Wheel Heat (ON)") # Optional: change text
            print("Wheel Heater: ON")
        else:
            self.wheel_heater_button.setStyleSheet("") # Reset to default
            # self.wheel_heater_button.setText("Steering Wheel") # Optional: reset text
            print("Wheel Heater: OFF")

# --- Standalone Test ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Minimal dark theme for standalone testing
    dark_palette_test = QPalette()
    dark_palette_test.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette_test.setColor(QPalette.ColorRole.WindowText, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette_test.setColor(QPalette.ColorRole.Text, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Button, QColor(74, 74, 74))
    dark_palette_test.setColor(QPalette.ColorRole.ButtonText, QColor(255,255,255))
    dark_palette_test.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
    dark_palette_test.setColor(QPalette.ColorRole.HighlightedText, QColor(255,255,255))
    app.setPalette(dark_palette_test)
    app.setStyleSheet("""
        QWidget { font-size: 15px; color: #DDD; }
        QPushButton { 
            background-color: #4A4A4A; color: #FFF; 
            border: 1px solid #555; padding: 8px 15px; 
            border-radius: 4px; min-height: 30px; 
        }
        QPushButton:hover { background-color: #5A5A5A; }
        QPushButton:checked { background-color: #007ACC; border: 1px solid #005C99; }
        QSlider::groove:horizontal { 
            border: 1px solid #5A5A5A; height: 12px; 
            background: #404040; margin: 2px 0; border-radius: 6px; 
        }
        QSlider::handle:horizontal { 
            background: #007ACC; border: 1px solid #005C99; 
            width: 20px; margin: -4px 0; border-radius: 10px; 
        }
    """)

    climate_tab_widget = ClimateTab()
    test_window = QMainWindow()
    test_window.setCentralWidget(climate_tab_widget)
    test_window.setWindowTitle("Climate Tab Test")
    test_window.setGeometry(300, 300, 700, 350) # Adjusted size for better view
    test_window.show()
    sys.exit(app.exec())
