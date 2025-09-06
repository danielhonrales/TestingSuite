import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    parent_folder = 'Assets/Studies/CHI26_Study1_Funneling'
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
    filtered_data = []
    all_data = []

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            df["Participant"] = p
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
            df["LocationError"] = df["Location"] - df["FeltLocation"]

            include_mask = df["ThermalMatch"] == 1 #& (df["LocationError"] <= 0.45)
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
    print(f'Egregious Location: {(all_combined["LocationError"] > 0.45).sum()} / {all_combined["LocationError"].count()}, {(all_combined["LocationError"] > 0.45).sum() / all_combined["LocationError"].count()}')
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
    Creates scatterplots of Intended Location vs. average FeltLocation,
    grouped by Temperature. One plot per Duration, plus one with all durations.
    Excludes rows where ThermalMatch == 0.
    Saves both individual plots and one combined subplot figure.
    """
    # ✅ Keep only trials where ThermalMatch == 1
    df = df[df["ThermalMatch"] == 1]

    df["Location"] *= 10
    df["FeltLocation"] *= 10

    # Compute mean + SEM (safe SEM to avoid NaN)
    grouped = (
        df.groupby(["Location", "Temperature", "Duration"])
          .agg(FeltLocation_mean=("FeltLocation", "mean"),
               FeltLocation_sem=("FeltLocation",
                                 lambda x: 0 if len(x) <= 1 else x.std(ddof=1) / np.sqrt(len(x))))
          .reset_index()
    )

    grouped_all = (
        df.groupby(["Location", "Temperature"])
          .agg(FeltLocation_mean=("FeltLocation", "mean"),
               FeltLocation_sem=("FeltLocation",
                                 lambda x: 0 if len(x) <= 1 else x.std(ddof=1) / np.sqrt(len(x))))
          .reset_index()
    )

    # Define colors/markers per Temperature
    temp_styles = {
        -15: {"color": "#4A5EEB", "marker": "o", "label": "Cold"},
        0:  {"color": "#7A7A73", "marker": "o", "label": "Neutral"},
        9:  {"color": "#F73F52", "marker": "o", "label": "Hot"}
    }

    # Define offsets for each temperature so points don't overlap on x-axis
    temp_offsets = {
        -15: -0.02,   # Cold (shift left)
        0:    0.0,    # No Thermal (centered)
        9:   +0.02    # Hot (shift right)
    }

    # Durations to plot (unique + "all")
    durations = sorted(df["Duration"].unique())
    #durations.append("all")

    tables_to_save = {}
    figs = []  # store individual figure paths

    # === Individual plots ===
    """ for dur in durations:
        if dur == "all":
            data = grouped_all.copy()
            title = "All Durations"
            fname = "scatter_all_durations.png"
            sheet_name = "AllDurations"
        else:
            data = grouped[grouped["Duration"] == dur].copy()
            title = f"Duration = {dur}s"
            fname = f"scatter_duration_{dur}.png"
            sheet_name = f"Duration_{dur}"

        # Clean NaNs
        data = data.dropna(subset=["FeltLocation_mean", "FeltLocation_sem"])

        tables_to_save[sheet_name] = data.copy()

        plt.figure(figsize=(6, 5))
        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]
            if not temp_data.empty:
                x_vals = temp_data["Location"] + temp_offsets[temp]
                plt.errorbar(x_vals, temp_data["FeltLocation_mean"],
                                yerr=temp_data["FeltLocation_sem"],
                                fmt=style["marker"], color=style["color"],
                                capsize=4, markersize=8, label=style["label"])

        plt.title(title)
        plt.xlabel("Intended Location")
        plt.ylabel("Perceived Location (avg)")
        plt.xticks([0.0, 2.5, 5.0, 7.5, 10.0])
        plt.yticks([0.0, 2.5, 5.0, 7.5, 10.0])
        plt.xlim(-0.5, 10.5)
        plt.ylim(-0.5, 10.5)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        os.makedirs(output_folder, exist_ok=True)
        outpath = os.path.join(output_folder, fname)
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        plt.close()
        figs.append((title, outpath))
        print(f"Saved plot: {outpath}") """

    # === Combined subplot figure ===
    plt.rcParams.update({'font.size': 14})  # sets global font size

    nrows = 1
    ncols = len(durations)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 5), squeeze=False)
    axes = axes.flatten()  # make it 1D array for easy indexing

    for idx, dur in enumerate(durations):
        ax = axes[idx]

        if dur == "all":
            data = grouped_all.copy()
            title = "All Durations"
        else:
            data = grouped[grouped["Duration"] == dur].copy()
            title = f"Duration = {dur} s"

        # Clean NaNs
        data = data.dropna(subset=["FeltLocation_mean", "FeltLocation_sem"])

        # ✅ Plot each temperature separately
        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]
            if temp_data.empty:
                continue

            x_vals = temp_data["Location"] + temp_offsets[temp]

            ax.errorbar(
                x_vals,
                temp_data["FeltLocation_mean"],
                yerr=temp_data["FeltLocation_sem"],
                fmt=style["marker"], color=style["color"],
                capsize=4, markersize=8, label=style["label"]
            )

        ax.set_title(title, fontsize=18)
        ax.set_xticks([0.0, 2.5, 5.0, 7.5, 10.0])
        ax.set_yticks([0.0, 2.5, 5.0, 7.5, 10.0])
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 10.5)
        ax.grid(True, linestyle="--", alpha=0.5)

        if idx == 0:  # only put legend once
            ax.legend()

    # ✅ Add one shared axis label instead of per subplot
    fig.text(0.54, 0.04, "Intended Location (cm)", ha="center", fontsize=18)
    fig.text(0.04, 0.5, "Perceived Location (cm)", va="center", rotation="vertical", fontsize=18)

    # Increase horizontal space so y-labels don’t overlap
    plt.subplots_adjust(wspace=0.3)

    combined_path = os.path.join(output_folder, "study1_locations.png")
    plt.tight_layout(rect=[0.05, 0.05, 1, 1])  # leave space for shared labels
    fig.savefig(combined_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved combined plot: {combined_path}")

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