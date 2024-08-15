import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import webbrowser

def extract_metadata(file_path):
    image = Image.open(file_path)
    exif_data = image._getexif()
    metadata = {}

    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "MakerNote":  # Skip MakerNote tag
                continue
            if tag_name == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                metadata[tag_name] = gps_data
            else:
                metadata[tag_name] = value
    return metadata

def format_metadata(metadata):
    formatted_metadata = ""
    for key, value in metadata.items():
        if isinstance(value, dict):
            formatted_metadata += f"{key}:\n"
            for sub_key, sub_value in value.items():
                formatted_metadata += f"  {sub_key}: {sub_value}\n"
        else:
            formatted_metadata += f"{key}: {value}\n"
    return formatted_metadata

def get_decimal_coordinates(gps_info):
    def convert_to_degrees(value):
        d, m, s = value[0], value[1], value[2]
        return d + (m / 60.0) + (s / 3600.0)

    lat = gps_info.get("GPSLatitude")
    lat_ref = gps_info.get("GPSLatitudeRef")
    lon = gps_info.get("GPSLongitude")
    lon_ref = gps_info.get("GPSLongitudeRef")

    if lat and lon and lat_ref and lon_ref:
        lat = convert_to_degrees(lat)
        lon = convert_to_degrees(lon)

        if lat_ref != "N":
            lat = -lat
        if lon_ref != "E":
            lon = -lon

        return lat, lon
    return None

def open_location_in_map(lat, lon):
    map_url = f"https://www.google.com/maps?q={lat},{lon}"
    webbrowser.open(map_url)

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        metadata = extract_metadata(file_path)
        formatted_metadata = format_metadata(metadata)

        gps_info = metadata.get("GPSInfo")
        if gps_info:
            coordinates = get_decimal_coordinates(gps_info)
            if coordinates:
                lat, lon = coordinates
                # Open the location in Google Maps
                open_location_in_map(lat, lon)

                formatted_metadata += f"\nLatitude: {lat}\nLongitude: {lon}\n"

        metadata_textbox.delete(1.0, tk.END)
        metadata_textbox.insert(tk.END, formatted_metadata)

# Create the main window
root = ctk.CTk()
root.title("Metadata Extractor")
root.geometry("600x400")

# Configure customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Create and place widgets
select_button = ctk.CTkButton(root, text="Select Image", command=select_file)
select_button.pack(pady=20)

metadata_textbox = ctk.CTkTextbox(root, width=550, height=300)
metadata_textbox.pack(pady=10)

# Start the main event loop
root.mainloop()
