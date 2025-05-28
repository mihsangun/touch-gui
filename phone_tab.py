import sys # Added for standalone testing
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, # Added for standalone testing
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton,
    QLineEdit, QTabWidget, QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QPalette, QColor # Added QPalette, QColor for standalone testing
from PyQt6.QtCore import Qt, QTimer

class PhoneTab(QWidget):
    """
    Manages the UI, state, and logic for the Phone Tab.
    This class is designed to be instantiated and added as a tab to a QTabWidget.
    """
    def __init__(self, parent=None): # parent argument is good practice for QWidgets
        super().__init__(parent)

        # --- Phone-specific State Variables ---
        self.all_contacts_data = {} # Dictionary to store {name: number}
        self.call_active = False    # Flag indicating if a call is currently active
        self.call_status_timer = QTimer(self) # Timer to clear status messages
        self.call_status_timer.setSingleShot(True)
        self.call_status_timer.timeout.connect(self.clear_call_status)

        # --- UI Setup ---
        # Main layout for the PhoneTab widget itself
        main_phone_layout = QHBoxLayout(self) # 'self' is the PhoneTab QWidget
        main_phone_layout.setSpacing(15)

        # --- Left Panel: Tabs for Contacts and Favorites ---
        left_panel_tab_widget = QTabWidget()
        left_panel_tab_widget.setObjectName("PhoneLeftPanelTabs") # For specific styling

        # -- Contacts Tab --
        contacts_tab_content = QWidget()
        contacts_tab_layout = QVBoxLayout(contacts_tab_content)
        contacts_tab_layout.setContentsMargins(0, 5, 0, 0) # Top margin for content
        self.contacts_list = QListWidget() # List to display all contacts
        contacts_tab_layout.addWidget(self.contacts_list)
        left_panel_tab_widget.addTab(contacts_tab_content, "Contacts")

        # -- Favorites Tab --
        favorites_tab_content = QWidget()
        favorites_tab_layout = QVBoxLayout(favorites_tab_content)
        favorites_tab_layout.setContentsMargins(0, 5, 0, 0)
        self.favorites_list = QListWidget() # List to display favorite contacts
        favorites_tab_layout.addWidget(self.favorites_list)
        left_panel_tab_widget.addTab(favorites_tab_content, "Favorites")

        # Connect item click signals AFTER lists are created
        self.contacts_list.itemClicked.connect(self.contact_selected)
        self.favorites_list.itemClicked.connect(self.contact_selected)

        # --- Right Panel: Call Status, Number Display, Numpad Sub-Tab ---
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(right_panel_widget)
        right_panel_layout.setSpacing(10)

        # Label to show call status (e.g., Idle, Calling..., On Call)
        self.phone_status_label = QLabel("")
        self.phone_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phone_status_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.phone_status_label.setMinimumHeight(25) # Ensure space for the label

        # Line edit to display the number being dialed or entered
        self.phone_display = QLineEdit()
        self.phone_display.setObjectName("PhoneDisplay") # For specific styling
        self.phone_display.setPlaceholderText("Enter number or select contact...")
        self.phone_display.setReadOnly(True) # Number display is filled by buttons/selection
        self.phone_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.phone_display.setFont(QFont("Arial", 18))
        self.phone_display.setMinimumHeight(35)

        # Sub-tab widget for Numpad (and potentially other phone functions later)
        phone_functions_sub_tabs = QTabWidget()
        phone_functions_sub_tabs.setObjectName("PhoneFunctionsSubTabs")

        # --- Numpad Sub-Tab ---
        numpad_tab_widget = QWidget()
        numpad_layout = QGridLayout(numpad_tab_widget)
        numpad_layout.setSpacing(5) # Tighter spacing for numpad buttons

        # Numpad button labels and their grid positions
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        positions = [(i, j) for i in range(4) for j in range(3)] # 4 rows, 3 columns

        numpad_font = QFont("Arial", 14) # Font for numpad buttons

        # Create and add numpad buttons
        for position, text in zip(positions, buttons):
            button = QPushButton(text)
            button.setFont(numpad_font)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setMinimumSize(40, 40) # Ensure buttons are reasonably sized
            # Connect button click to its handler method
            button.clicked.connect(lambda checked, txt=text: self.handle_numpad_button(txt))
            numpad_layout.addWidget(button, *position)

        # Set stretch factors for even distribution of numpad buttons
        for i in range(3): numpad_layout.setColumnStretch(i, 1)
        for i in range(5): numpad_layout.setRowStretch(i, 1) # Includes row for Delete/Call

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setFont(numpad_font)
        delete_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        delete_button.setMinimumSize(40, 40)
        delete_button.clicked.connect(self.handle_delete_button)

        # Call/End Call button (text and function change based on call state)
        self.call_button = QPushButton("Call")
        self.call_button.setFont(numpad_font)
        self.call_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.call_button.setMinimumSize(80, 40)
        self.call_button.clicked.connect(self.handle_call_button) # Initially connected to start call
        self.call_button_original_style = "background-color: #008000; border: 1px solid #006400;" # Green
        self.call_button.setStyleSheet(self.call_button_original_style)

        # Add Delete and Call buttons to the numpad grid
        numpad_layout.addWidget(delete_button, 4, 0) # Row 4, Col 0
        numpad_layout.addWidget(self.call_button, 4, 1, 1, 2) # Row 4, span Col 1 and 2

        phone_functions_sub_tabs.addTab(numpad_tab_widget, "Numpad")

        # Add elements to the right panel
        right_panel_layout.addWidget(self.phone_status_label)
        right_panel_layout.addWidget(self.phone_display)
        right_panel_layout.addWidget(phone_functions_sub_tabs, 1) # Give sub-tabs stretch

        # Add left and right panels to the main phone layout
        main_phone_layout.addWidget(left_panel_tab_widget, 1) # Left panel takes 1/3 space
        main_phone_layout.addWidget(right_panel_widget, 2)   # Right panel takes 2/3 space

        # Populate contacts and favorites lists
        self.populate_contacts()
        self.populate_favorites()

    # --- Phone Tab Specific Methods ---
    def populate_contacts(self):
        """Generates and populates the contacts list with placeholder data."""
        self.all_contacts_data.clear()
        self.contacts_list.clear()
        # Sample names for random generation
        first_names = ["Ava", "Liam", "Olivia", "Noah", "Emma", "Oliver", "Sophia", "Lucas", "Mia", "Ethan", "Isabella", "Aiden", "Riley", "Jackson", "Zoe", "Mason", "Chloe", "Elijah", "Lily", "Logan", "Grace", "Carter", "Amelia", "Jayden", "Harper", "Owen", "Evelyn", "Caleb", "Abigail", "Ryan", "Emily", "Luke", "Ella", "Gabriel", "Madison", "Isaac", "Avery", "Anthony", "Scarlett", "Dylan", "Victoria", "Wyatt", "Aria", "Nathan", "Sofia", "Joshua", "Camila", "Andrew", "Penelope", "Samuel"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Campbell", "Mitchell", "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker"]
        generated_contacts = set() # To ensure unique contact entries
        for _ in range(50): # Generate 50 contacts
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            number = f"{random.randint(100, 999):03d}{random.randint(100, 999):03d}{random.randint(1000, 9999):04d}"
            # Ensure uniqueness of (name, number) pair
            while (name, number) in generated_contacts:
                 name = f"{random.choice(first_names)} {random.choice(last_names)}"
                 number = f"{random.randint(100, 999):03d}{random.randint(100, 999):03d}{random.randint(1000, 9999):04d}"
            generated_contacts.add((name, number))
            self.all_contacts_data[name] = number # Store in dictionary
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, number) # Store number with the list item
            self.contacts_list.addItem(item)

    def populate_favorites(self):
        """Populates the favorites list with a random subset of contacts."""
        self.favorites_list.clear()
        if not self.all_contacts_data: return # Cannot populate if no contacts exist
        all_names = list(self.all_contacts_data.keys())
        num_favorites = min(10, len(all_names)) # Max 10 favorites
        favorite_names = random.sample(all_names, num_favorites) # Select random contacts
        for name in favorite_names:
            number = self.all_contacts_data.get(name)
            if number:
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, number)
                self.favorites_list.addItem(item)

    def contact_selected(self, item):
        """Handles selection of a contact from either the contacts or favorites list."""
        if self.call_active: return # Don't change display if a call is active
        number = item.data(Qt.ItemDataRole.UserRole) # Retrieve stored number
        if number:
            self.phone_display.setText(number)
            self.clear_call_status() # Clear any previous status messages

    def handle_numpad_button(self, text):
        """Appends the clicked numpad button's text to the phone display."""
        if self.call_active: return # Ignore numpad input during an active call
        current_text = self.phone_display.text()
        # Allow *, #, and digits up to a certain length (e.g., 10 digits for number part)
        if text in ['*', '#'] or (text.isdigit() and len(current_text.replace('*','').replace('#','')) < 10):
            self.phone_display.setText(current_text + text)
        self.clear_call_status()

    def handle_delete_button(self):
        """Removes the last character from the phone display."""
        if self.call_active: return # Ignore delete during an active call
        self.phone_display.setText(self.phone_display.text()[:-1]) # Remove last char
        self.clear_call_status()

    def handle_call_button(self):
        """
        Handles the 'Call' button press. Validates the number and initiates
        the simulated call process if valid.
        """
        if self.call_active: return # Should be handled by 'End Call' logic if active

        number_to_call = self.phone_display.text().strip()

        # Basic number validation
        if not number_to_call:
             self.phone_status_label.setText("Enter a number first")
             self.call_status_timer.start(3000) # Message visible for 3 seconds
             return
        if not number_to_call.isdigit() or len(number_to_call) != 10: # Simple 10-digit check
            self.phone_status_label.setText("Invalid number (must be 10 digits)")
            self.call_status_timer.start(3000)
            return

        # --- Initiate Call Simulation ---
        self.call_active = True
        self.call_button.setEnabled(False) # Disable button during "calling"
        self.call_button.setText("Calling...")
        self.call_button.setStyleSheet("background-color: #FFA500; border: 1px solid #CC8400;") # Orange
        self.phone_status_label.setText(f"Calling {number_to_call}...")
        print(f"Calling {number_to_call}...") # Debug output

        # Simulate connection delay (e.g., 2 seconds)
        QTimer.singleShot(2000, self.set_on_call_state)

    def set_on_call_state(self):
        """Transitions UI to 'On Call' state after simulated connection."""
        if not self.call_active: return # Call might have been ended before connecting

        self.phone_status_label.setText("On Call")
        print("Call Active.") # Debug output

        # Change button to "End Call"
        self.call_button.setText("End Call")
        self.call_button.setStyleSheet("background-color: #FF0000; border: 1px solid #CC0000;") # Red
        self.call_button.setEnabled(True) # Re-enable to allow ending call

        # Reconnect button click to end call functionality
        try: self.call_button.clicked.disconnect(self.handle_call_button)
        except TypeError: pass # Was not connected or already disconnected
        try: self.call_button.clicked.connect(self.set_call_ended_state)
        except TypeError: pass # Already connected (should not happen here)

    def set_call_ended_state(self):
        """Transitions UI to 'Call Ended' state and resets for a new call."""
        self.phone_status_label.setText("Call Ended")
        self.call_active = False
        print("Call Ended.") # Debug output

        # Reset call button to its original "Call" state
        self.call_button.setText("Call")
        self.call_button.setStyleSheet(self.call_button_original_style) # Green
        self.call_button.setEnabled(True)

        # Reconnect button click to start call functionality
        try: self.call_button.clicked.disconnect(self.set_call_ended_state)
        except TypeError: pass
        try: self.call_button.clicked.connect(self.handle_call_button)
        except TypeError: pass

        self.call_status_timer.start(4000) # Clear "Call Ended" message after 4s

    def clear_call_status(self):
        """Clears the phone status label if not in an active call or recently ended."""
        # Only clear informational messages, not "On Call" or "Calling..."
        if not self.call_active and self.phone_status_label.text() not in ["On Call", "Calling..."]:
             self.phone_status_label.setText("")

# --- Standalone Test ---
# This block allows testing the PhoneTab independently.
# To use, run this file (phone_tab_ui.py) directly.
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Minimal dark theme for standalone testing
    dark_palette_test = QPalette()
    dark_palette_test.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette_test.setColor(QPalette.ColorRole.WindowText, QColor(221, 221, 221)) # DDD
    dark_palette_test.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette_test.setColor(QPalette.ColorRole.Text, QColor(221, 221, 221))
    dark_palette_test.setColor(QPalette.ColorRole.Button, QColor(74, 74, 74)) #4A4A4A
    dark_palette_test.setColor(QPalette.ColorRole.ButtonText, QColor(255,255,255))
    dark_palette_test.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204)) #007ACC
    dark_palette_test.setColor(QPalette.ColorRole.HighlightedText, QColor(255,255,255))
    app.setPalette(dark_palette_test)

    # Basic stylesheet for standalone testing
    app.setStyleSheet("""
        QWidget { font-size: 15px; color: #DDD; } /* Default text color */
        QTabWidget#PhoneLeftPanelTabs > QTabBar::tab,
        QTabWidget#PhoneFunctionsSubTabs > QTabBar::tab {
             min-width: 80px; padding: 8px 10px; font-size: 14px;
             background-color: #353535; color: #BBB; margin-right: 2px;
             border: 1px solid #444; border-bottom: none;
             border-top-left-radius: 4px; border-top-right-radius: 4px;
        }
        QTabWidget#PhoneLeftPanelTabs > QTabBar::tab:selected,
        QTabWidget#PhoneFunctionsSubTabs > QTabBar::tab:selected {
            background-color: #2A2A2A; color: #FFF;
        }
        QPushButton {
            background-color: #4A4A4A; color: #FFF;
            border: 1px solid #555; padding: 8px 15px;
            border-radius: 4px; min-height: 30px;
        }
        QPushButton:hover { background-color: #5A5A5A; }
        QPushButton:pressed { background-color: #3A3A3A; }
        QLineEdit#PhoneDisplay {
            font-size: 18px; min-height: 35px;
            background-color: #2A2A2A; border: 1px solid #3e3e3e; color: white;
        }
        QListWidget {
            background-color: #2A2A2A; border: 1px solid #444;
            border-radius: 4px; color: #DDD; padding: 5px;
        }
        QListWidget::item:selected { background-color: #007ACC; color: #FFF; }
        QListWidget::item:hover:!selected { background-color: #404040; }
    """)

    # Create and show the PhoneTab widget for testing
    phone_tab_widget = PhoneTab()
    # For testing, give it a fixed size or add to a simple QMainWindow
    test_window = QMainWindow()
    test_window.setCentralWidget(phone_tab_widget)
    test_window.setWindowTitle("Phone Tab Test")
    test_window.setGeometry(300, 300, 700, 400) # Adjust size as needed
    test_window.show()

    sys.exit(app.exec())
