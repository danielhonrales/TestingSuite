import pandas as pd
import pingouin as pg
import numpy as np
import os

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    parent_folder = 'Assets/Studies/CHI26_Study3_Motion'
    input_folder = f'{parent_folder}/data_processing/data'
    output_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'

    combined_data = process_participant_data(input_folder, participants)
    results = perform_stat_analysis(combined_data, participants, output_folder)
    print(results.head())

def process_participant_data(folder_path, participants):
    all_data = []

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            df["Participant"] = p

            all_data.append(df)
        else:
            print(f"Warning: File not found for participant {p}")

    if not all_data:
        print("No data loaded.")
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)

    return combined

def perform_stat_analysis(df, participants, output_folder):
    # Compute new columns
    df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
    print(f'Thermal Match: {df["ThermalMatch"].sum()} / {df["ThermalMatch"].count()}, {df["ThermalMatch"].sum() / df["ThermalMatch"].count()}')

    df["DirectionMatch"] = (np.sign(df["Direction"]) == np.sign(df["FeltDirection"])).astype(int)
    print(f'Direction Match: {df["DirectionMatch"].sum()} / {df["DirectionMatch"].count()}, {df["DirectionMatch"].sum() / df["DirectionMatch"].count()}')

    include_mask = (df["ThermalMatch"] == 1) & (df["DirectionMatch"] == 1)
    df_filtered = df[include_mask].copy()

    print(f'Valid Trials: {df_filtered["FeltMotion"].count()} / {df["FeltMotion"].count()}, {df_filtered["FeltMotion"].count() / df["FeltMotion"].count()}')

    # Group values by Temperature, Duration, Location
    grouped = df_filtered.groupby(["Temperature", "Duration", "Direction"])["FeltMotion"].apply(list)

    # Find the longest list length
    max_len = grouped.map(len).max()

    # Build dataframe where each column is a combo, padded with NaN to equal length
    df_expanded = pd.DataFrame({
        f"T{temp}_Dur{dur}_Dir{dir}": values + [None] * (max_len - len(values))
        for (temp, dur, dir), values in grouped.items()
    })

    filename_out = f"stat_{participant_string(participants)}.csv"
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