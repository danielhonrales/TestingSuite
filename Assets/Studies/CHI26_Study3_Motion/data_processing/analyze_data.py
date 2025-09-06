import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    parent_folder = 'Assets/Studies/CHI26_Study3_Motion'
    input_folder = f'{parent_folder}/data_processing/data'
    output_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'

    combined_data, excel_file = process_participant_data(input_folder, participants, output_folder)
    generate_graph(combined_data, excel_file, output_folder)

def process_participant_data(folder_path, participants, output_folder):
    """
    Reads Excel files named 'p#_responses.xlsx' for given participants,
    combines data, computes ThermalMatch and LocationError columns,
    and saves results to 'p#-p#_analysis.xlsx'.

    Args:
        folder_path (str): Path to folder containing Excel files.
        participants (list of int): List of participant numbers to include.
        output_folder (str): Path to save the combined analysis file.

    Returns:
        pd.DataFrame: Combined processed DataFrame.
    """
    all_data = []
    filtered_data = []

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            # Add participant number
            df["Participant"] = p

            # Compute new columns
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
            df["DirectionMatch"] = (df["Direction"] == df["FeltDirection"]).astype(int)

            include_mask = (df["ThermalMatch"] == 1) & (df["DirectionMatch"] == 1)
            df_filtered = df[include_mask].copy()

            all_data.append(df)
            filtered_data.append(df_filtered)
        else:
            print(f"Warning: File not found for participant {p}")

    if not all_data:
        print("No data loaded.")
        return pd.DataFrame()

    all_combined = pd.concat(all_data, ignore_index=True)
    filtered_combined = pd.concat(filtered_data, ignore_index=True)
    os.makedirs(output_folder, exist_ok=True)

    print(f'Thermal Match: {all_combined["ThermalMatch"].sum()} / {all_combined["ThermalMatch"].count()}, {all_combined["ThermalMatch"].sum() / all_combined["ThermalMatch"].count()}')
    print(f'Direction Match: {all_combined["DirectionMatch"].sum()} / {all_combined["DirectionMatch"].count()}, {all_combined["DirectionMatch"].sum() / all_combined["DirectionMatch"].count()}')
    print(f'Valid Trials: {filtered_combined["Participant"].count()} / {all_combined["Participant"].count()}, {filtered_combined["Participant"].count() / all_combined["Participant"].count()}')

    # Save file named after first and last participant
    filename_out = f"{participant_string(participants)}_analysis.xlsx"
    output_path = os.path.join(output_folder, filename_out)
    filtered_combined.to_excel(output_path, index=False)
    filename_out_csv = f"{participant_string(participants)}_analysis.csv"
    output_path_csv = os.path.join(output_folder, filename_out_csv)
    filtered_combined.to_csv(output_path_csv, index=False)

    print(f"Saved combined data to {output_path}")
    return filtered_combined, output_path

def generate_graph(df, excel_file, output_folder):
    """
    Creates bar graphs of FeltMotion probability (mean),
    grouped by Temperature × Duration, one plot per Direction.
    Only includes rows where ThermalMatch == 1 and DirectionMatch == 1.
    """
    # ✅ Keep only trials where both matches == 1
    # Filter data
    df = df[(df["ThermalMatch"] == 1) & (df["DirectionMatch"] == 1)]

    # Compute mean + SEM of FeltMotion
    grouped = (
        df.groupby(["Direction", "Temperature", "Duration"])
        .agg(FeltMotion_mean=("FeltMotion", "mean"),
            FeltMotion_sem=("FeltMotion",
                            lambda x: 0 if len(x) <= 1 else x.std(ddof=1) / np.sqrt(len(x))))
        .reset_index()
    )

    # Colors for temperatures
    temp_colors = {
        -15: {"color": "#4A5EEB", "label": "Cold"},
        0: {"color": "#7A7A73", "label": "Neutral"},
        9: {"color": "#F73F52", "label": "Hot"}
    }

    # Unique values
    directions = sorted(df["Direction"].unique())
    durations = sorted(df["Duration"].unique())
    temperatures = sorted(df["Temperature"].unique())

    os.makedirs(output_folder, exist_ok=True)

    # === Create one figure with subplots ===
    fig, axes = plt.subplots(1, len(directions), figsize=(8*len(directions), 6), sharey=True)

    if len(directions) == 1:
        axes = [axes]  # make iterable if only one direction

    x = np.arange(len(durations))  # X positions: durations
    width = 0.7 / len(temperatures)   # bar width
    spacing = 0.1

    for ax, direction in zip(axes, directions):
        data_dir = grouped[grouped["Direction"] == direction]

        for i, temp in enumerate(temperatures):
            data_temp = data_dir[data_dir["Temperature"] == temp]

            means, sems = [], []
            for dur in durations:
                row = data_temp[data_temp["Duration"] == dur]
                if not row.empty:
                    means.append(row["FeltMotion_mean"].values[0])
                    sems.append(row["FeltMotion_sem"].values[0])
                else:
                    means.append(np.nan)
                    sems.append(0)

            # Center bars around each duration
            positions = (
                x + (i - (len(temperatures)-1)/2) * (width + spacing/len(temperatures))
            )

            ax.bar(positions, means, width, yerr=sems,
                color=temp_colors[temp]["color"],
                capsize=4, label=f"{temp_colors[temp]['label']}")

        ax.set_xticks(x)
        ax.set_xticklabels([str(d) + " s" for d in durations])
        ax.set_xlabel("Duration")
        ax.set_title(f"{'Elbow-To-Wrist' if direction == 0 else 'Wrist-To-Elbow'}")
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)
        ax.set_ylim(0, 1.05)

    # Shared Y label
    axes[0].set_ylabel("Probability of Perceiving Motion")
    axes[0].legend(title="Temperature")

    # Save combined figure
    outpath = os.path.join(output_folder, "study3_probabilities.png")
    plt.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close()
    print(f"Saved combined bar plot: {outpath}")

    # Save grouped table to Excel
    with pd.ExcelWriter(excel_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        grouped.to_excel(writer, sheet_name="FeltMotion_Prob", index=False)
    print(f"Saved FeltMotion probability table into {excel_file}")

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