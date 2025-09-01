import pandas as pd
import pingouin as pg
import numpy as np
import os
from PIL import Image

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12]
    parent_folder = 'Assets/Studies/CHI26_Study1_Funneling'
    input_folder = f'{parent_folder}/data_processing/data'
    drawings_folder = f'{parent_folder}/drawings'
    output_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'

    combined_data = process_participant_data(input_folder, drawings_folder, participants, output_folder)
    results = perform_stat_analysis(combined_data, participants, output_folder)
    print(results.head())

def process_participant_data(folder_path, drawings_folder, participants, output_folder):
    all_data = []

    # Fixed mapping from Location → pixel column
    location_to_column = {
        0.00: 330,
        0.25: 295,
        0.50: 260,
        0.75: 225,
        1.00: 190
    }

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            # Add Participant column (if not already there)
            df["Participant"] = p

            contains_red_list = []

            for _, row in df.iterrows():
                trial = int(row["Trial"])
                location = row["Location"]
                col_index = location_to_column.get(location, None)

                # Build path to PNG
                img_path = os.path.join(drawings_folder, f"p{p}", f"p{p}_trial{trial}_drawing.png")

                if os.path.exists(img_path):
                    img = Image.open(img_path).convert("RGB")
                    width, height = img.size

                    # Map Location (0–1 scale) to pixel column
                    col_index = min(max(col_index, 0), width - 1)

                    # Extract the column of pixels
                    pixels = [img.getpixel((col_index, y)) for y in range(height)]

                    # Check if any pixel is "red"
                    contains_red = 1 if any(r > 200 and g < 50 and b < 50 for (r, g, b) in pixels) else 0
                else:
                    print(f"Warning: Image not found for {img_path}, defaulting as 0")
                    contains_red = 0

                contains_red_list.append(contains_red)

            # Add results column
            df["ThermalAtLocation"] = contains_red_list
            all_data.append(df)
        else:
            print(f"Warning: File not found for participant {p}")

    if not all_data:
        print("No data loaded.")
        return pd.DataFrame()

    # Combine across participants
    combined = pd.concat(all_data, ignore_index=True)

    """ filename_out = f"drawingstat_{participant_string(participants)}.csv"
    output_path = os.path.join(output_folder, filename_out)
    print(f"Saved to {output_path}")
    combined.to_csv(output_path, index=False) """

    return combined

def perform_stat_analysis(df, participants, output_folder):

    # Compute new columns
    df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
    print(f'Thermal Match: {df["ThermalMatch"].sum()} / {df["ThermalMatch"].count()}, {df["ThermalMatch"].sum() / df["ThermalMatch"].count()}')

    df["LocationError"] = df["FeltLocation"] - df["Location"]

    include_mask = (df["ThermalMatch"] == 1) & (df["LocationError"] < 0.5)#& \
    #((df["Location"] == 0) & (df["FeltLocation"] > 0.5)) | ((df["Location"] == 1) & (df["FeltLocation"] < 0.5))
    df_filtered = df[include_mask].copy()

    print(f'Valid Trials: {df_filtered["LocationError"].count()} / {df["Location"].count()}, {df_filtered["LocationError"].count() / df["Location"].count()}')

    # Group values by Temperature, Duration, Location
    grouped = df_filtered.groupby(["Temperature", "Duration", "Location"])["ThermalAtLocation"].apply(list)

    # Find the longest list length
    max_len = grouped.map(len).max()

    # Build dataframe where each column is a combo, padded with NaN to equal length
    df_expanded = pd.DataFrame({
        f"T{temp}_D{dur}_L{loc}": values + [None] * (max_len - len(values))
        for (temp, dur, loc), values in grouped.items()
    })

    filename_out = f"drawingstat_{participant_string(participants)}.csv"
    output_path = os.path.join(output_folder, filename_out)
    print(f"Saved to {output_path}")
    df_expanded.to_csv(output_path, index=False)

    return df_expanded

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