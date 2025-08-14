import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import random
import os

participants = [17, 18, 19 , 20]
feltIllusions = [1, 0]
locations = [0, 0.25, 0.5, 0.75, 1.0]
temperatures = [9, -15]

def main():
    # --- Configuration ---
    input_folder = 'Assets/Studies/CHI26_Study1_Funneling/data_processing/data'         # <-- UPDATE THIS
    output_folder = 'Assets/Studies/CHI26_Study1_Funneling/data_processing/output'        # <-- UPDATE THIS
    sheet_name = 0  # Use 0 for the first sheet, or specify by name
    os.makedirs(output_folder, exist_ok=True)

    master_data = np.array((1, 8))

    # Participant, Trial, Temperature, Duration, Location, FeltLocation, FeltTemperature, FeltIllusion x 180 trials
    data_shape = np.array((180, 8))

    """ for feltIllusion in feltIllusions:
        for temperature in temperatures:
            for location in locations:
                process_data(input_folder, sheet_name, participants, feltIllusion, temperature, location)
                for participant in participants:
                    process_data(input_folder, sheet_name, [participant], feltIllusion, temperature, location) """
    
    """ for feltIllusion in feltIllusions:
        for temperature in temperatures:
            process_all_data(input_folder, sheet_name, participants, feltIllusion, temperature)
            for participant in participants:
                process_all_data(input_folder, sheet_name, [participant], feltIllusion, temperature) """
    
    for temperature in temperatures:
        for location in locations:
            process_all_feltIllusions_data(input_folder, sheet_name, participants, temperature, location)
            for participant in participants:
                process_all_feltIllusions_data(input_folder, sheet_name, [participant], temperature, location)

def process_data(input_folder, sheet_name, participants, feltIllusion, temperature, location):
    valid_trials = {}
    for par in participants:
        valid_trials[par] = []

    # --- Loop through Excel files ---
    for filename in os.listdir(input_folder):
        
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith("~"):
            file_participant = int(filename.strip("p").strip("_data.xlsx"))
            if file_participant in participants:
                file_path = os.path.join(input_folder, filename)

                # Read Excel file
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"Loaded: {filename} with shape {df.shape}")

                condition = (
                    (df["FeltIllusion"] == feltIllusion) &
                    (df["Temperature"] == temperature) &
                    (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])) &
                    (abs(df["Location"] - df["FeltLocation"]) < 0.25) &
                    (df["Location"] == location)
                )

                valid_trials[file_participant] = df[condition]['Trial'].tolist()
                print(valid_trials)

    
    generate_heatmap(valid_trials, "Assets/Studies/CHI26_Study1_Funneling/drawings", participants, feltIllusion, temperature, location)

def process_all_feltIllusions_data(input_folder, sheet_name, participants, temperature, location):
    valid_trials = {}
    for par in participants:
        valid_trials[par] = []

    # --- Loop through Excel files ---
    for filename in os.listdir(input_folder):
        
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith("~"):
            file_participant = int(filename.strip("p").strip("_data.xlsx"))
            if file_participant in participants:
                file_path = os.path.join(input_folder, filename)

                try:
                    # Read Excel file
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"Loaded: {filename} with shape {df.shape}")

                    condition = (
                        (df["Temperature"] == temperature) &
                        (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])) &
                        (abs(df["Location"] - df["FeltLocation"]) < 0.25) &
                        (df["Location"] == location)
                    )

                    valid_trials[file_participant] = df[condition]['Trial'].tolist()
                    print(valid_trials)

                except Exception as e:
                    print(f"❌ Failed to process {filename}: {e}")
    
    generate_heatmap(valid_trials, "Assets/Studies/CHI26_Study1_Funneling/drawings", participants, "all", temperature, location)

def process_all_locations_data(input_folder, sheet_name, participants, feltIllusion, temperature):
    valid_trials = {}
    for par in participants:
        valid_trials[par] = []

    # --- Loop through Excel files ---
    for filename in os.listdir(input_folder):
        
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith("~"):
            file_participant = int(filename.strip("p").strip("_data.xlsx"))
            if file_participant in participants:
                file_path = os.path.join(input_folder, filename)

                try:
                    # Read Excel file
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"Loaded: {filename} with shape {df.shape}")

                    condition = (
                        (df["FeltIllusion"] == feltIllusion) &
                        (df["Temperature"] == temperature) &
                        (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])) &
                        (abs(df["Location"] - df["FeltLocation"]) < 0.25) #&
                    )

                    valid_trials[file_participant] = df[condition]['Trial'].tolist()
                    print(valid_trials)

                except Exception as e:
                    print(f"❌ Failed to process {filename}: {e}")
    
    generate_heatmap(valid_trials, "Assets/Studies/CHI26_Study1_Funneling/drawings", participants, feltIllusion, temperature, "all")

def generate_heatmap(trials_to_process, drawings_folder, participants, feltIllusion, temperature, location):
    mask_filepath = f"Assets/arm_mask.png"
    mask_img = Image.open(mask_filepath).convert("L")
    mask_array = np.array(mask_img)
    # Convert to binary mask
    binary_mask = (mask_array > 128).astype(int)  # 1s where heatmap is allowed

    # Get heat map data
    heat_map = np.zeros(mask_array.shape)

    for par in trials_to_process:
        par_folder = os.path.join(drawings_folder, f"p{par}")
        for trial in trials_to_process[par]:
            filepath = os.path.join(par_folder, f"p{par}_trial{trial}_drawing.png")
            heat_map = process_drawing(filepath, heat_map)

    # Shift
    n_pixels = 50
    heat_map = np.roll(heat_map, shift=-n_pixels, axis=1)
    heat_map[:, -n_pixels:] = 0
    
    sigma = 1
    heat_map = gaussian_filter(heat_map, sigma=sigma)
    masked_data = heat_map * binary_mask           # Apply mask

    # Transparent background
    masked_alpha = np.where(binary_mask, 1.0, 0.0)

    # Heat map
    plt.figure(figsize=(10, 10))
    cmap = None
    if temperature < 0:
        cmap = plt.cm.bone
    else:
        cmap = plt.cm.hot
    #cmap = cmap.reversed()
    plt.imshow(masked_data, cmap=cmap, interpolation='antialiased', alpha=masked_alpha)
    plt.axis('off')

    # Coordinates where you want to place the circles (in image coordinates, i.e., pixels)
    circle_coords = [(304, 150), (505, 150)]
    circle_radius = 5
    circle_color = 'gray'
    ax = plt.gca()
    for (x, y) in circle_coords:
        circ = Circle((x, y), radius=circle_radius, color=circle_color, alpha=0.8)
        ax.add_patch(circ)

    # Rectangle center coordinates
    rect_center = (585, 150)
    rect_width = 10
    rect_height = 10
    x0 = rect_center[0] - rect_width / 2
    y0 = rect_center[1] - rect_height / 2
    rect = Rectangle((x0, y0), rect_width, rect_height,
                    linewidth=1.5, edgecolor='gray', facecolor='gray', alpha=0.8)
    ax.add_patch(rect)

    folder = drawings_folder
    if feltIllusion == "all":
        new_filepath = os.path.join(folder, f"heatmap_allillusion_temperature-{temperature}_par{participants[0]}-par{participants[-1]}_location-{int(location * 100)}")
    else:
        if location == 'all':
            new_filepath = os.path.join(folder, f"heatmap_noillusion_par{participants[0]}-par{participants[-1]}_location-all")
        else:
            new_filepath = os.path.join(folder, f"heatmap_{'illusion' if feltIllusion else 'noillusion'}_temperature-{temperature}_par{participants[0]}-par{participants[-1]}_location-{int(location * 100)}")
    plt.savefig(new_filepath, dpi=300, bbox_inches='tight')
    print(f"Saved to {new_filepath}")


def process_drawing(filepath, heat_map):
    if os.path.isfile(filepath):
        print(f"Processing {filepath}")
    #if os.path.isfile(filepath) and "Am19_thermal" in filename:
        # Convert png to array
        fill_red_circles(filepath, filepath)
        drawing = Image.open(filepath).convert("L")
        mask_array = np.array(drawing)
        binary_drawing = (mask_array > 50).astype(int)
        # Need to binary drawing to match heatmap
        heat_map += binary_drawing
        #heat_map[0:550, 300:620] += binary_drawing[0:550, 300:620]
        #heat_map[0:540, 1810:2075] += binary_drawing[0:540, 1810:2075]
    return heat_map  

def fill_red_circles(image_path, save_path=None):
    # Read the image
    img = cv2.imread(image_path)

    # Convert to HSV color space for better red detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define red color range in HSV (two ranges for red wrap-around)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red regions
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # Optional: clean noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours in red mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Fill each red contour on original image
    for cnt in contours:
        cv2.drawContours(img, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)  # Red in BGR

    # Save or return result
    if save_path:
        print(f"Saving to {save_path}")
        cv2.imwrite(save_path, img)
    return img

def sign(number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0
        
main()