import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [1,2,3,4,5,6]
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

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            # Add participant number
            df["Participant"] = p

            # Compute new columns
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)

            df["DirectionMatch"] = (df["Direction"] == df["FeltDirection"]).astype(int)

            all_data.append(df)
        else:
            print(f"Warning: File not found for participant {p}")

    if not all_data:
        print("No data loaded.")
        return pd.DataFrame()

    # Combine
    combined = pd.concat(all_data, ignore_index=True)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save file named after first and last participant
    filename_out = f"{participant_string(participants)}_analysis.xlsx"
    output_path = os.path.join(output_folder, filename_out)
    combined.to_excel(output_path, index=False)

    print(f"Saved combined data to {output_path}")
    return combined, output_path

def generate_graph(df, excel_file, output_folder):
    """
    Creates bar graphs of FeltMotion probability (mean),
    grouped by Temperature × Duration, one plot per Direction.
    Only includes rows where ThermalMatch == 1 and DirectionMatch == 1.
    """
    # ✅ Keep only trials where both matches == 1
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
        -15: "blue",
        0: "gray",
        9: "red"
    }

    # Unique values
    directions = sorted(df["Direction"].unique())
    durations = sorted(df["Duration"].unique())
    temperatures = sorted(df["Temperature"].unique())

    os.makedirs(output_folder, exist_ok=True)

    for direction in directions:
        data_dir = grouped[grouped["Direction"] == direction]

        fig, ax = plt.subplots(figsize=(8, 6))

        # X positions: temperatures
        x = np.arange(len(temperatures))

        # Width of each bar cluster (smaller for spacing)
        width = 0.7 / len(durations)   # shrink from 0.8 to 0.7 for some gap
        spacing = 0.1

        for i, temp in enumerate(temperatures):
            data_temp = data_dir[data_dir["Temperature"] == temp]

            means = []
            sems = []
            for dur in durations:
                row = data_temp[data_temp["Duration"] == dur]
                if not row.empty:
                    means.append(row["FeltMotion_mean"].values[0])
                    sems.append(row["FeltMotion_sem"].values[0])
                else:
                    means.append(np.nan)
                    sems.append(0)

            # Center bars around each temperature, add small separation
            positions = (
                x + (i - (len(temperatures)-1)/2) * (width + spacing/len(temperatures))
            )

            ax.bar(positions, means, width, yerr=sems,
                   color=[temp_colors[temp]],
                   capsize=4, label=f"Temp {temp}")

        ax.set_xticks(x)
        ax.set_xticklabels([str(dur) for dur in durations])
        ax.set_xlabel("Duration")
        ax.set_ylabel("P(Felt Motion)")
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Direction = {direction}")
        ax.legend(title="Temperature")
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)

        outpath = os.path.join(output_folder, f"bar_direction_{direction}.png")
        plt.tight_layout()
        fig.savefig(outpath, dpi=300)
        plt.close()
        print(f"Saved bar plot: {outpath}")

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