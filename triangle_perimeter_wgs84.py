import math
import tkinter as tk
from tkinter import messagebox

# Mean Earth radius in meters (WGS84 approximation)
EARTH_RADIUS_M = 6371008.8


def deg_to_rad(deg):
    """Convert degrees to radians"""
    return deg * math.pi / 180.0


def haversine_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg):
    """
    Calculate the distance between two points using the Haversine formula.
    Inputs in degrees, output in meters.
    """
    lat1 = deg_to_rad(lat1_deg)
    lon1 = deg_to_rad(lon1_deg)
    lat2 = deg_to_rad(lat2_deg)
    lon2 = deg_to_rad(lon2_deg)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    distance = EARTH_RADIUS_M * c
    return distance


class TrianglePerimeterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Triangle Perimeter Calculator (WGS84)")

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        # Title
        title_label = tk.Label(
            frame,
            text="Triangle Perimeter from Three WGS84 Coordinates",
            font=("Tahoma", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # Table headers
        headers = ["Point", "Latitude (°)", "Longitude (°)"]
        for col, h in enumerate(headers):
            lbl = tk.Label(frame, text=h, font=("Tahoma", 10, "bold"))
            lbl.grid(row=1, column=col, padx=5, pady=5)

        # Point 1
        tk.Label(frame, text="Point 1").grid(row=2, column=0, padx=5, pady=5)
        self.lat1_entry = tk.Entry(frame, width=15)
        self.lon1_entry = tk.Entry(frame, width=15)
        self.lat1_entry.grid(row=2, column=1, padx=5, pady=5)
        self.lon1_entry.grid(row=2, column=2, padx=5, pady=5)

        # Point 2
        tk.Label(frame, text="Point 2").grid(row=3, column=0, padx=5, pady=5)
        self.lat2_entry = tk.Entry(frame, width=15)
        self.lon2_entry = tk.Entry(frame, width=15)
        self.lat2_entry.grid(row=3, column=1, padx=5, pady=5)
        self.lon2_entry.grid(row=3, column=2, padx=5, pady=5)

        # Point 3
        tk.Label(frame, text="Point 3").grid(row=4, column=0, padx=5, pady=5)
        self.lat3_entry = tk.Entry(frame, width=15)
        self.lon3_entry = tk.Entry(frame, width=15)
        self.lat3_entry.grid(row=4, column=1, padx=5, pady=5)
        self.lon3_entry.grid(row=4, column=2, padx=5, pady=5)

        # Calculate button
        calc_button = tk.Button(
            frame,
            text="Calculate Perimeter",
            command=self.calculate_perimeter
        )
        calc_button.grid(row=5, column=0, columnspan=3, pady=10)

        # Result label
        self.result_label = tk.Label(
            frame,
            text="Perimeter: ---",
            font=("Tahoma", 11, "bold"),
            fg="blue"
        )
        self.result_label.grid(row=6, column=0, columnspan=3, pady=(5, 0))

        # Unit note
        self.unit_label = tk.Label(
            frame,
            text="Units: meters and kilometers (using mean Earth radius)",
            font=("Tahoma", 9),
            fg="gray"
        )
        self.unit_label.grid(row=7, column=0, columnspan=3, pady=(2, 0))

    def read_coordinate(self, entry_lat, entry_lon, point_name):
        """Read and validate coordinates"""
        try:
            lat = float(entry_lat.get())
            lon = float(entry_lon.get())
        except ValueError:
            raise ValueError(f"Invalid input for {point_name}. Please enter numeric values.")

        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude for {point_name} must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude for {point_name} must be between -180 and 180.")

        return lat, lon

    def calculate_perimeter(self):
        try:
            lat1, lon1 = self.read_coordinate(self.lat1_entry, self.lon1_entry, "Point 1")
            lat2, lon2 = self.read_coordinate(self.lat2_entry, self.lon2_entry, "Point 2")
            lat3, lon3 = self.read_coordinate(self.lat3_entry, self.lon3_entry, "Point 3")

            # Side lengths
            d12 = haversine_distance(lat1, lon1, lat2, lon2)
            d23 = haversine_distance(lat2, lon2, lat3, lon3)
            d31 = haversine_distance(lat3, lon3, lat1, lon1)

            perimeter_m = d12 + d23 + d31
            perimeter_km = perimeter_m / 1000.0

            self.result_label.config(
                text=f"Perimeter: {perimeter_m:,.2f} m  (~ {perimeter_km:,.3f} km)"
            )

        except ValueError as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TrianglePerimeterApp(root)
    root.mainloop()
