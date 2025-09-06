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

participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
temperatures = [9, -15]
durations = [0.1, 1, 2]
locations = [0, .25, .5, .75, 1]

parent_folder = 'Assets/Studies/CHI26_Study1_Funneling'

def main():
    # --- Configuration ---
    input_folder = f'{parent_folder}/data_processing/data'
    output_folder = f'{parent_folder}/data_processing/heatmaps/{participant_string(participants)}'
    os.makedirs(output_folder, exist_ok=True)

    for temperature in temperatures:
        for location in locations:
            for duration in durations:
                filename = f"{participant_string(participants)}_temp-{temperature}_dur-{duration}_loc-{int(location * 100)}.png"
                process_data(input_folder, output_folder, participants, filename, temperature, location, duration)

                """ for participant in participants:
                    filename = f"p{participant}_temp-{temperature}_dir-{location}_dur-{duration}.png"
                    process_data(input_folder, output_folder, participants, filename, temperature, direction, duration) """

def process_data(input_folder, output_folder, participants, filename, temperature, location, duration):
    valid_trials = {}
    for par in participants:
        valid_trials[par] = []

    # --- Loop through Excel files ---
    for data_file in os.listdir(input_folder):
        
        if data_file.endswith(('.xlsx', '.xls')) and not data_file.startswith("~"):
            file_participant = int(data_file.strip("p").strip("_data.xlsx"))
            if file_participant in participants:
                file_path = os.path.join(input_folder, data_file)

                try:
                    # Read Excel file
                    df = pd.read_excel(file_path, sheet_name=0)
                    #print(f"Loaded: {filename} with shape {df.shape}")                    

                    condition = (
                        (df["Temperature"] == temperature) &
                        (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])) &
                        (df["Location"] == location) &
                        (df["Duration"] == duration)
                        #(abs(df["Location"] - df["FeltLocation"]) <= .45)
                    )

                    valid_trials[file_participant] = df[condition]['Trial'].tolist()
                    #print(valid_trials)

                except Exception as e:
                    print(f"❌ Failed to process {data_file}: {e}")
    
    generate_heatmap(output_folder, valid_trials, temperature, filename, location)

def generate_heatmap(output_folder, trials_to_process, temperature, filename, location):
    mask_filepath = f"Assets/arm_mask.png"
    mask_img = Image.open(mask_filepath).convert("L")
    mask_array = np.array(mask_img)
    binary_mask = (mask_array > 128).astype(int)  # 1s where heatmap is allowed

    # Get heat map data
    heat_map = np.zeros(mask_array.shape)
    for par in trials_to_process:
        par_folder = os.path.join(f"{parent_folder}/drawings/", f"p{par}")
        for trial in trials_to_process[par]:
            filepath = os.path.join(par_folder, f"p{par}_trial{int(trial)}_drawing.png")
            heat_map = process_drawing(filepath, heat_map)

    sigma = 1
    heat_map = gaussian_filter(heat_map, sigma=sigma)
    masked_data = heat_map * binary_mask
    masked_alpha = np.where(binary_mask, 1.0, 0.0)

    # === Plot ===
    plt.figure(figsize=(10, 10))
    cmap = plt.cm.hot if temperature > 0 else plt.cm.bone
    plt.imshow(masked_data, cmap=cmap, interpolation='antialiased', alpha=masked_alpha)
    plt.axis('off')

    ax = plt.gca()
    circle_coords = [(330, 155), (190, 155)]
    for (x, y) in circle_coords:
        circ = Circle((x, y), radius=8, color='gray', alpha=0.8)
        ax.add_patch(circ)

    rect_center = (106, 155)
    rect = Rectangle(
        (rect_center[0] - 7.5, rect_center[1] - 7.5),
        15, 15,
        linewidth=1.5, edgecolor='gray', facecolor='gray', alpha=0.8
    )
    ax.add_patch(rect)

    circle_coords = (330 + ((190 - 330) * location), 155)
    circ = Circle(circle_coords, radius=5,
                  facecolor='red' if temperature > 0 else 'blue',
                  edgecolor='black', alpha=0.8, linewidth=1)
    ax.add_patch(circ)

    # === Save temp file first ===
    file_path = os.path.join(output_folder, filename)
    temp_path = file_path.replace(".png", "_raw.png")
    plt.savefig(temp_path, dpi=300, bbox_inches='tight')
    plt.close()

    # === Crop with Pillow ===
    crop_box = (300, 275, 1300, 775)  # (left, upper, right, lower)
    img = Image.open(temp_path)
    cropped_img = img.crop(crop_box)

    transparent_img = make_border_white_transparent(cropped_img)
    transparent_img.save(file_path)

    # Remove temp file (optional)
    os.remove(temp_path)

    print(f"Saved to {file_path} with {sum(len(par) for par in trials_to_process.values())} files processed")
    for par in trials_to_process:
        print(f"\t{par}: {trials_to_process[par]}")

def make_border_white_transparent(img, margin=150, white_thresh=250):
    """
    Turns white pixels transparent only within `margin` pixels from the border.
    """
    img = img.convert("RGBA")
    width, height = img.size
    datas = img.getdata()

    new_data = []
    for i, item in enumerate(datas):
        x = i % width
        y = i // width

        # Check if pixel is near the border
        near_border = (x < margin or x >= width - margin or 
                       y < margin or y >= height - margin)

        if near_border and item[0] > white_thresh and item[1] > white_thresh and item[2] > white_thresh:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

def process_drawing(filepath, heat_map):
    if os.path.isfile(filepath):
        #print(f"Processing {filepath}")
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
    print("Processing " + image_path)
    # Read the image
    img = cv2.imread(image_path)

    # Convert to HSV color space for better red detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define red color range in HSV (two ranges for red wrap-around)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red regions
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # Optional: clean noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

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
        #print(f"Saving to {save_path}")
        cv2.imwrite(save_path, img)
    return img

def sign(number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0
        
def participant_string(participants):
    """
    Convert list of participant numbers into compact string.
    Example: [1,2,3,6,8,10] -> 'p1-3-6-8-10'
    """
    participants = sorted(set(participants))  # remove duplicates, sort
    parts = []
    start = prev = participants[0]

    for p in participants[1:]:
        if p == prev + 1:
            prev = p
        else:
            # Close current range
            if start == prev:
                parts.append(str(start))
            else:
                parts.append(f"{start}-{prev}")
            start = prev = p
    # Close last range
    if start == prev:
        parts.append(str(start))
    else:
        parts.append(f"{start}-{prev}")

    return "p" + "-".join(parts)

main()