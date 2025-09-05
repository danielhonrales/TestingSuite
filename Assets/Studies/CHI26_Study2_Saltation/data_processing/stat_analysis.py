import pandas as pd
import pingouin as pg
import numpy as np
import os

def main():
    participants = [1,2,3,4,5,7,8,9,10,11,12,13,14,15,16]
    parent_folder = 'Assets/Studies/CHI26_Study2_Saltation'
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

    df["correctNum"] = df["numLocation"] == 3
    print(f'numLocation: {df["correctNum"].sum()} / {df["correctNum"].count()}, {df["correctNum"].sum() / df["correctNum"].count()}')

    include_mask = (df["ThermalMatch"] == 1) & (df["correctNum"] == 1)
    #((df["Location"] == 0) & (df["FeltLocation"] > 0.5)) | ((df["Location"] == 1) & (df["FeltLocation"] < 0.5))
    df_filtered = df[include_mask].copy()

    df_filtered["Location1Error"] = np.where(
        df_filtered["Direction"] == 0,
        (1 - df_filtered["location1"]).abs(),
        (0 - df_filtered["location1"]).abs()
    )
    df_filtered["Location2Error"] = np.where(
        df_filtered["Direction"] == 0,
        (1 - df_filtered["location2"]).abs(),
        (0 - df_filtered["location2"]).abs()
    )
    df_filtered["Location3Error"] = np.where(
        df_filtered["Direction"] == 1,
        (1 - df_filtered["location3"]).abs(),
        (0 - df_filtered["location3"]).abs()
    )

    print(f'Valid Trials: {df_filtered["Location1Error"].count()} / {df["Participant"].count()}, {df_filtered["Location1Error"].count() / df["Participant"].count()}')

    df_expanded = {}

    for loc_col in ["Location1Error", "Location2Error", "Location3Error"]:
        grouped = df_filtered.groupby(["Temperature", "Duration", "Direction"])[loc_col].apply(list)

        max_len = grouped.map(len).max()

        expanded = pd.DataFrame({
            f"{loc_col}_T{temp}_D{dur}_Dir{direction}": values + [None] * (max_len - len(values))
            for (temp, dur, direction), values in grouped.items()
        })

        df_expanded[loc_col] = expanded

    df_final = pd.concat(df_expanded.values(), axis=1)

    filename_out = f"stat_{participant_string(participants)}.csv"
    output_path = os.path.join(output_folder, filename_out)
    print(f"Saved to {output_path}")
    df_final.to_csv(output_path, index=False)

    return df_final

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