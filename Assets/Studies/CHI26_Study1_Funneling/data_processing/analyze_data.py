import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [6]#[1,2,3,4,5,7,9]
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
    all_data = []

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            # Add participant number
            df["Participant"] = p

            # Compute new columns
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)

            df["LocationError"] = df["Location"] - df["FeltLocation"]

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
    Creates scatterplots of Intended Location vs. average FeltLocation,
    grouped by Temperature. One plot per Duration, plus one with all durations.
    Excludes rows where ThermalMatch == 0.
    Saves both individual plots and one combined subplot figure.
    """
    # ✅ Keep only trials where ThermalMatch == 1
    df = df[df["ThermalMatch"] == 1]

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
        -15: {"color": "blue", "marker": "o", "label": "Cold"},
        0:  {"color": "gray", "marker": "o", "label": "No Thermal"},
        9:  {"color": "red", "marker": "o", "label": "Hot"}
    }

    # Define offsets for each temperature so points don't overlap on x-axis
    temp_offsets = {
        -15: -0.02,   # Cold (shift left)
        0:    0.0,    # No Thermal (centered)
        9:   +0.02    # Hot (shift right)
    }

    # Durations to plot (unique + "all")
    durations = sorted(df["Duration"].unique())
    durations.append("all")

    tables_to_save = {}
    figs = []  # store individual figure paths

    # === Individual plots ===
    for dur in durations:
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
                """ # Add labels at shifted x too
                for _, row in temp_data.iterrows():
                    plt.text(row["Location"] + temp_offsets[temp], row["FeltLocation_mean"],
                                f"{row['FeltLocation_mean']:.2f}",
                                fontsize=8, ha="center", va="bottom") """

        plt.title(title)
        plt.xlabel("Intended Location")
        plt.ylabel("Perceived Location (avg)")
        plt.xticks([0, 0.25, 0.5, 0.75, 1.0])
        plt.yticks([0, 0.25, 0.5, 0.75, 1.0])
        plt.xlim(-0.05, 1.05)
        plt.ylim(-0.05, 1.05)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        os.makedirs(output_folder, exist_ok=True)
        outpath = os.path.join(output_folder, fname)
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        plt.close()
        figs.append((title, outpath))
        print(f"Saved plot: {outpath}")

   # === Combined subplot figure ===
    nrows = 2
    ncols = int(np.ceil(len(durations) / nrows))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 5*nrows), squeeze=False)

    for idx, dur in enumerate(durations):
        ax = axes[idx // ncols, idx % ncols]

        if dur == "all":
            data = grouped_all.copy()
            title = "All Durations"
        else:
            data = grouped[grouped["Duration"] == dur].copy()
            title = f"Duration = {dur}s"

        # Clean NaNs
        data = data.dropna(subset=["FeltLocation_mean", "FeltLocation_sem"])

        # ✅ Plot each temperature separately
        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]   # <--- filter by temp
            if temp_data.empty:
                continue

            # Apply small x-offset to avoid overlap
            x_vals = temp_data["Location"] + temp_offsets[temp]

            ax.errorbar(x_vals, temp_data["FeltLocation_mean"],
                        yerr=temp_data["FeltLocation_sem"],
                        fmt=style["marker"], color=style["color"],
                        capsize=4, markersize=8, label=style["label"])

            # Add labels at shifted x too
            """ for _, row in temp_data.iterrows():
                ax.text(row["Location"] + temp_offsets[temp],
                        row["FeltLocation_mean"],
                        f"{row['FeltLocation_mean']:.2f}",
                        fontsize=8, ha="center", va="bottom") """

        ax.set_title(title)
        ax.set_xlabel("Intended Location")
        ax.set_ylabel("Perceived Location (avg)")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)

        if idx == 0:  # only put legend once
            ax.legend()
        # Hide unused axes
        for j in range(len(durations), nrows*ncols):
            fig.delaxes(axes[j // ncols, j % ncols])

        combined_path = os.path.join(output_folder, "scatter_combined.png")
        plt.tight_layout()
        fig.savefig(combined_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved combined plot: {combined_path}")

        # === Save data tables ===
        with pd.ExcelWriter(excel_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            for sheet, table in tables_to_save.items():
                table.to_excel(writer, sheet_name=sheet, index=False)
        print(f"Saved graph data tables into {excel_file}")

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