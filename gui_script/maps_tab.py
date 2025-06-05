import sys
import os
from pathlib import Path
# Folium is not directly used to generate the HTML anymore, but the concept was inspired by it.
# We are manually creating Leaflet HTML.
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QSplitter, QSizePolicy,
    QLineEdit
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile


# For remote debugging QWebEngineView (optional, but very helpful)
# os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '8088'

class MapsTab(QWidget):
    """
    Displays a Leaflet map in a QWebEngineView, using locally stored
    OpenStreetMap tiles from city-specific folders.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MapsTabWidgetCityTiles")

        self.current_map_html_file = None

        # --- Configuration for Local Assets ---
        self.script_dir = Path(__file__).resolve().parent
        self.base_project_gui_path = self.script_dir.parent

        # Base path for all city-specific tile sets
        self.base_tiles_path = self.base_project_gui_path / "media" / "maps" / "tiles_by_city"

        self.local_leaflet_js_path = self.base_project_gui_path / "libs" / "leaflet" / "leaflet.js"
        self.local_leaflet_css_path = self.base_project_gui_path / "libs" / "leaflet" / "leaflet.css"

        self.leaflet_js_url = f"file:///{self.local_leaflet_js_path.resolve()}" if self.local_leaflet_js_path.exists() else "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        self.leaflet_css_url = f"file:///{self.local_leaflet_css_path.resolve()}" if self.local_leaflet_css_path.exists() else "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"

        if not self.local_leaflet_js_path.exists():
            print(
                f"WARNING: Local leaflet.js not found at {self.local_leaflet_js_path}, using CDN: {self.leaflet_js_url}")
        if not self.local_leaflet_css_path.exists():
            print(
                f"WARNING: Local leaflet.css not found at {self.local_leaflet_css_path}, using CDN: {self.leaflet_css_url}")

        self.temp_maps_dir = self.script_dir / "temp_leaflet_maps"
        self.temp_maps_dir.mkdir(parents=True, exist_ok=True)

        # Saved locations now include a 'city_folder' key
        self.saved_locations = {
            "Istanbul Hagia Sophia": {"coords": (41.0086, 28.9800), "city_folder": "Istanbul", "popup": "Hagia Sophia"},
            "Barcelona Sagrada Familia": {"coords": (41.4036, 2.1744), "city_folder": "Barcelona", "popup": "Sagrada Familia"},
            "San Jose City Hall": {"coords": (37.3352, -121.8894), "city_folder": "SanJose_CA", "popup": "San Jose City Hall"}
        }
        self.default_city_folder = "Istanbul"  # Default city to show
        self.default_map_center = self.saved_locations.get("Istanbul Hagia Sophia", {}).get("coords", [41.0082, 28.9784])
        self.default_zoom = 12

        # --- UI Setup ---
        main_maps_layout = QHBoxLayout(self)
        main_maps_layout.setSpacing(0)
        main_maps_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_locations_button = QPushButton("<")
        self.toggle_locations_button.setObjectName("ToggleLocationsListButton")
        self.toggle_locations_button.setCheckable(True)
        self.toggle_locations_button.setChecked(True)
        self.toggle_locations_button.setFixedWidth(30)
        self.toggle_locations_button.clicked.connect(self.toggle_locations_list)
        main_maps_layout.addWidget(self.toggle_locations_button)

        self.maps_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.maps_splitter.setObjectName("MapsSplitter")
        self.maps_splitter.setHandleWidth(2)

        self.locations_side_panel = QWidget()
        self.locations_side_panel.setObjectName("LocationsSidePanel")
        side_panel_layout = QVBoxLayout(self.locations_side_panel)
        side_panel_layout.setContentsMargins(5, 5, 5, 5)
        side_panel_layout.setSpacing(5)

        side_panel_layout.addWidget(QLabel("Saved Locations"))
        self.locations_list_widget = QListWidget()
        self.locations_list_widget.setObjectName("SavedLocationsList")
        self.populate_saved_locations()
        self.locations_list_widget.itemClicked.connect(self.handle_location_selected)
        side_panel_layout.addWidget(self.locations_list_widget, 1)

        self.maps_splitter.addWidget(self.locations_side_panel)

        map_content_panel = QWidget()
        map_content_panel.setObjectName("MapContentPanel")
        map_view_layout = QVBoxLayout(map_content_panel)
        map_view_layout.setContentsMargins(0, 0, 0, 0)

        self.map_view = QWebEngineView()
        self.map_view.setObjectName("MapView")

        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

        self.map_view.loadFinished.connect(self.on_map_load_finished)
        self.map_view.loadStarted.connect(lambda: print("MapView: Load started..."))
        self.map_view.renderProcessTerminated.connect(self.handle_render_process_terminated)
        self.map_view.loadProgress.connect(lambda progress: print(f"MapView: Load progress: {progress}%"))

        map_view_layout.addWidget(self.map_view, 1)

        self.maps_splitter.addWidget(map_content_panel)
        self.maps_splitter.setSizes([200, 580])

        main_maps_layout.addWidget(self.maps_splitter)

        self.generate_and_load_map(
            city_folder=self.default_city_folder,
            location=self.default_map_center,
            zoom_start=self.default_zoom,
            popup_text="Welcome to İstanbul!"
        )

    def handle_render_process_terminated(self, terminationStatus, exitCode):
        print(f"CRITICAL: QWebEngineView render process terminated!")
        print(f"  Termination Status: {terminationStatus}")
        print(f"  Exit Code: {exitCode}")
        self.map_view.setHtml(
            f"<h1 style='color:red;'>Map Renderer Crashed</h1><p>Status: {terminationStatus}, Exit Code: {exitCode}</p>")

    def on_map_load_finished(self, success):
        page_url_str = self.map_view.url().toString()
        if success:
            print(f"MapView: Map HTML loaded successfully: {page_url_str}")
        else:
            print(f"MapView: Map HTML FAILED to load: {page_url_str}")
            current_file_str = str(
                self.current_map_html_file.resolve()) if self.current_map_html_file and self.current_map_html_file.exists() else "None or Not Found"
            error_html = f"""
            <html><body style='font-family: sans-serif; padding: 20px;'>
                <h1 style='color: red;'>Error Loading Map</h1>
                <p>Could not load map content into QWebEngineView.</p>
                <p><b>Attempted URL:</b> {page_url_str}</p>
                <p><b>Local File Path:</b> {current_file_str}</p>
            </body></html>"""
            self.map_view.setHtml(error_html)

    def generate_and_load_map(self, city_folder, location=None, zoom_start=None, popup_text=None, marker_location=None):
        """
        Generates an HTML file with a Leaflet map pointing to local tiles for a specific city
        and local Leaflet assets, then loads it into the QWebEngineView.
        """
        center_lat = location[0] if location else self.default_map_center[0]
        center_lon = location[1] if location else self.default_map_center[1]
        current_zoom = zoom_start if zoom_start is not None else self.default_zoom

        # Construct the local tile URL for the specific city
        city_tile_path = self.base_tiles_path / city_folder
        abs_city_tile_path_str = str(city_tile_path.resolve()).replace(os.sep, '/')

        # Ensure correct file:/// prefixing
        if abs_city_tile_path_str.startswith('/'):  # For Unix-like paths
            tile_layer_url = f"file://{abs_city_tile_path_str}/{{z}}/{{x}}/{{y}}.png"
        else:  # For Windows paths (e.g., C:/...)
            tile_layer_url = f"file:///{abs_city_tile_path_str}/{{z}}/{{x}}/{{y}}.png"

        print(f"Using tile layer URL for {city_folder}: {tile_layer_url}")

        js_url_for_html = self.leaflet_js_url
        css_url_for_html = self.leaflet_css_url

        marker_js_snippet = ""
        if marker_location and popup_text:
            marker_lat, marker_lon = marker_location
            escaped_popup_text = popup_text.replace("'", "\\'").replace("\n", "<br>")
            marker_js_snippet = f"L.marker([{marker_lat}, {marker_lon}]).addTo(map).bindPopup('{escaped_popup_text}').openPopup();"
        elif popup_text and location:
            escaped_popup_text = popup_text.replace("'", "\\'").replace("\n", "<br>")
            marker_js_snippet = f"map.openPopup('{escaped_popup_text}', [{center_lat}, {center_lon}]);"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Offline Map - {city_folder}</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <link rel="stylesheet" href="{css_url_for_html}" />
            <script src="{js_url_for_html}"></script>
            <style>html, body, #map_div {{ height: 100%; width: 100%; margin: 0; padding: 0; background-color: #ddd; }}</style>
        </head>
        <body>
            <div id="map_div"></div>
            <script>
                var map = L.map('map_div', {{ preferCanvas: true }}).setView([{center_lat}, {center_lon}], {current_zoom});
                L.tileLayer('{tile_layer_url}', {{
                    attribution: '&copy; OpenStreetMap contributors',
                    minZoom: 1, maxZoom: 18, noWrap: true,
                }}).addTo(map);
                {marker_js_snippet}
                L.control.scale({{imperial: false}}).addTo(map);
            </script>
        </body>
        </html>
        """
        try:
            if self.current_map_html_file and self.current_map_html_file.exists():
                try:
                    self.current_map_html_file.unlink()
                except OSError as e:
                    print(f"Warning: Could not delete old map file {self.current_map_html_file}: {e}")

            self.current_map_html_file = self.temp_maps_dir / f"map_{city_folder.lower()}.html"
            with open(self.current_map_html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            absolute_map_file_path_str = str(self.current_map_html_file.resolve())
            map_qurl = QUrl.fromLocalFile(absolute_map_file_path_str)

            print(f"MapView: Attempting to load map from QUrl: {map_qurl.toString()}")
            if not self.current_map_html_file.exists():
                print(f"ERROR: HTML map file does not exist at {absolute_map_file_path_str} before setUrl!")
                self.map_view.setHtml(f"<h1>Error</h1><p>Map HTML file not found.</p>")
                return

            self.map_view.setUrl(map_qurl)
            print(f"Offline map HTML generated for {city_folder}: {self.current_map_html_file}. Attempted to load.")

        except Exception as e:
            print(f"Error generating or loading Leaflet HTML map: {e}")
            import traceback;
            traceback.print_exc()
            self.map_view.setHtml(f"<h1>Error Generating Map Page</h1><p>{e}</p>")

    def populate_saved_locations(self):
        self.locations_list_widget.clear()
        for name, data_dict in self.saved_locations.items():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, data_dict)  # Store the whole dictionary
            self.locations_list_widget.addItem(item)

    def toggle_locations_list(self, checked):
        self.locations_side_panel.setVisible(checked)
        self.toggle_locations_button.setText("<" if checked else ">")

    def handle_location_selected(self, item):
        location_name = item.text()
        location_data = item.data(Qt.ItemDataRole.UserRole)

        if isinstance(location_data, dict) and "coords" in location_data and "city_folder" in location_data:
            coords = location_data["coords"]
            city_folder = location_data["city_folder"]
            popup = location_data.get("popup", location_name)  # Use location name as popup if not specified
            if isinstance(coords, tuple) and len(coords) == 2:
                self.generate_and_load_map(city_folder=city_folder, location=coords, zoom_start=13, popup_text=popup,
                                           marker_location=coords)
                print(f"Map centering on: {location_name} in {city_folder} at {coords}")
            else:
                print(f"Invalid coordinates format for location: {location_name}")
        else:
            print(f"Invalid or incomplete data for location: {location_name}")


# --- Standalone Test (Optional) ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # ... (Stylesheet and Palette for standalone test as before) ...
    dark_palette_test = QPalette();  # ... (palette setup)
    app.setPalette(dark_palette_test)
    app.setStyleSheet("QWidget { font-size: 15px; color: #DDD; background-color: #353535; } /* ... */")

    maps_tab_widget = MapsTab()
    test_window = QMainWindow()
    test_window.setCentralWidget(maps_tab_widget)
    test_window.setWindowTitle("Maps Tab Test (Local Tiles & Leaflet)")
    test_window.setGeometry(100, 100, 900, 600)
    test_window.show()


    def cleanup_temp_maps_on_exit():
        if hasattr(maps_tab_widget, 'current_map_html_file') and maps_tab_widget.current_map_html_file:
            if maps_tab_widget.current_map_html_file.exists():
                try:
                    maps_tab_widget.current_map_html_file.unlink()
                    print(f"Cleaned up map file: {maps_tab_widget.current_map_html_file}")
                    temp_maps_dir = maps_tab_widget.current_map_html_file.parent
                    if temp_maps_dir.exists() and not any(temp_maps_dir.iterdir()):
                        temp_maps_dir.rmdir()
                        print(f"Cleaned up empty directory: {temp_maps_dir}")
                except Exception as e:
                    print(f"Error during cleanup: {e}")


    app.aboutToQuit.connect(cleanup_temp_maps_on_exit)
    sys.exit(app.exec())
