import math
import os
import time
import requests  # For making HTTP requests to download tiles
from pathlib import Path
from PIL import Image  # For checking if downloaded content is a valid image
from io import BytesIO

# --- Configuration for Locations ---
# Define a list of locations, each with a name and its bounding box
LOCATIONS = [
    {
        "name": "Istanbul_Detailed",
        "min_lat": 40.95,
        "max_lat": 41.05,
        "min_lon": 28.90,
        "max_lon": 29.10
    },
    {
        "name": "Barcelona_Detailed",
        "min_lat": 41.30,
        "max_lat": 41.50,  # Slightly adjusted for better coverage
        "min_lon": 2.10,
        "max_lon": 2.20
    },
    {
        "name": "SanJose_CA_Detailed",  # Using underscore for directory-friendly name
        "min_lat": 37.20,
        "max_lat": 37.40,
        "min_lon": -122.00,  # West is negative
        "max_lon": -121.70
    }
]

# Define the range of zoom levels to download for each city
# Be very careful with higher zoom levels for large areas - it's exponential!
# For city-level detail, you might want higher zoom levels but for smaller areas.
# This is a global setting for all cities in this version.
MIN_ZOOM = 12  # Good for city overview
MAX_ZOOM = 16  # Detailed city view (adjust as needed, 14 can be many tiles for a dense city)

# Base URL for the OpenStreetMap tile server (or your chosen provider)
# Ensure you comply with their usage policy!
TILE_SERVER_URL_TEMPLATE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

# Directory to save the tiles
# Tiles for all cities will go into subdirectories here, e.g., OUTPUT_DIR/Istanbul/z/x/y.png
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_PROJECT_GUI_PATH = SCRIPT_DIR.parent
# Main output directory for all maps
BASE_OUTPUT_DIR = BASE_PROJECT_GUI_PATH / "media" / "maps" / "tiles_by_city"

# Delay between tile requests in seconds (to be respectful to the server)
REQUEST_DELAY = 0.5  # Increase if you get rate-limited or for larger downloads

# User-Agent for requests
HEADERS = {
    'User-Agent': 'MyMultiCityTileDownloader/1.0 (Educational Use; contact:youremail@example.com)'
}


# --- Helper Functions ---

def deg2num(lat_deg, lon_deg, zoom):
    """Converts lat/lon to tile X/Y coordinates for a given zoom."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    """Converts tile X/Y coordinates to lat/lon of the NW corner."""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def download_tile(z, x, y, city_output_dir):
    """Downloads a single tile and saves it to the city's specific directory."""
    tile_url = TILE_SERVER_URL_TEMPLATE.format(z=z, x=x, y=y)
    # Tiles are saved under city_output_dir/z/x/y.png
    tile_path_dir = city_output_dir / str(z) / str(x)
    tile_path_dir.mkdir(parents=True, exist_ok=True)
    tile_filepath = tile_path_dir / f"{y}.png"

    if tile_filepath.exists():
        print(f"Tile {z}/{x}/{y} for {city_output_dir.name} already exists. Skipping.")
        return True

    print(f"Downloading tile: {tile_url} to {tile_filepath}")
    try:
        response = requests.get(tile_url, headers=HEADERS, timeout=15)  # Increased timeout
        response.raise_for_status()

        try:
            Image.open(BytesIO(response.content)).verify()
        except Exception as img_e:
            print(f"Warning: Downloaded content for {tile_url} is not a valid image. Error: {img_e}. Skipping.")
            return False

        with open(tile_filepath, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading tile {tile_url}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred for tile {tile_url}: {e}")
        return False


# --- Main Download Logic ---
def main():
    print(f"Starting map tile download for multiple cities...")
    print(f"Base output directory: {BASE_OUTPUT_DIR.resolve()}")
    print(f"Global Zoom Levels: {MIN_ZOOM} to {MAX_ZOOM}")
    print(f"Request Delay: {REQUEST_DELAY} seconds")
    print("WARNING: This can download a very large number of files and take a long time.")
    print("Please ensure you comply with the tile server's usage policy.")

    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    overall_downloaded_count = 0
    overall_failed_count = 0

    for location_info in LOCATIONS:
        city_name = location_info["name"]
        min_lat = location_info["min_lat"]
        max_lat = location_info["max_lat"]
        min_lon = location_info["min_lon"]
        max_lon = location_info["max_lon"]

        # Create a specific output directory for this city
        city_output_dir = BASE_OUTPUT_DIR / city_name
        city_output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- Processing City: {city_name} ---")
        print(f"  Output directory: {city_output_dir.resolve()}")
        print(f"  Bounding Box: LAT=({min_lat}, {max_lat}), LON=({min_lon}, {max_lon})")

        total_tiles_for_city = 0
        for z in range(MIN_ZOOM, MAX_ZOOM + 1):
            xmin, ymax = deg2num(max_lat, min_lon, z)
            xmax, ymin = deg2num(min_lat, max_lon, z)
            num_x_tiles = xmax - xmin + 1
            num_y_tiles = ymin - ymax + 1
            tiles_in_zoom = num_x_tiles * num_y_tiles
            total_tiles_for_city += tiles_in_zoom
            print(f"  Zoom level {z}: {num_x_tiles} x {num_y_tiles} = {tiles_in_zoom} tiles")

        print(f"  Total tiles to potentially download for {city_name}: {total_tiles_for_city}")
        confirm = input(f"  Do you want to proceed with {city_name}? (yes/no): ")
        if confirm.lower() != 'yes':
            print(f"  Download for {city_name} cancelled by user.")
            continue  # Skip to the next city

        city_downloaded_count = 0
        city_failed_count = 0

        for z in range(MIN_ZOOM, MAX_ZOOM + 1):
            print(f"\n  Processing zoom level: {z} for {city_name}")
            xtile_start, ytile_start = deg2num(max_lat, min_lon, z)
            xtile_end, ytile_end = deg2num(min_lat, max_lon, z)

            print(
                f"    Tile range for zoom {z}: X from {xtile_start} to {xtile_end}, Y from {ytile_start} to {ytile_end}")

            for x in range(xtile_start, xtile_end + 1):
                for y in range(ytile_start, ytile_end + 1):
                    if download_tile(z, x, y, city_output_dir):  # Pass city_output_dir
                        city_downloaded_count += 1
                    else:
                        city_failed_count += 1
                    time.sleep(REQUEST_DELAY)

        print(f"\n  Download complete for {city_name}.")
        print(f"  Successfully processed/verified for {city_name}: {city_downloaded_count} tiles.")
        print(f"  Failed to download for {city_name}: {city_failed_count} tiles.")
        overall_downloaded_count += city_downloaded_count
        overall_failed_count += city_failed_count

    print(f"\n--- Overall Download Summary ---")
    print(f"Total tiles successfully processed/verified across all cities: {overall_downloaded_count}")
    print(f"Total tiles failed to download across all cities: {overall_failed_count}")


if __name__ == "__main__":
    main()
