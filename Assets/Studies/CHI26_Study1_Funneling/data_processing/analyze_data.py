import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    participants = [1,2,5,7]
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
            df["ThermalMatch"] = (
                (df["Temperature"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))) ==
                (df["FeltThermal"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)))
            ).astype(int)

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
    grouped by Temperature. 
    - One plot per Duration, plus one with all durations (separate images)
    - One combined figure with subplots (horizontal row)
    - One combined figure with subplots (2x2 grid)
    Excludes rows where ThermalMatch == 0.
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    import os

    # ✅ Keep only trials where ThermalMatch == 1
    df = df[df["ThermalMatch"] == 1]

    # Compute mean FeltLocation per (Location, Temperature, Duration)
    grouped = (df.groupby(["Location", "Temperature", "Duration"])
                 ["FeltLocation"].mean()
                 .reset_index())

    # Define colors/markers per Temperature
    temp_styles = {
        -15: {"color": "blue", "marker": "o", "label": "Cold"},
        0:  {"color": "gray", "marker": "o", "label": "No Thermal"},
        9:  {"color": "red", "marker": "o", "label": "Hot"}
    }

    # Durations to plot (unique + "all")
    durations = sorted(df["Duration"].unique())
    durations.append("all")

    tables_to_save = {}

    # === INDIVIDUAL PLOTS (same as your version) ===
    for dur in durations:
        if dur == "all":
            data = (df.groupby(["Location", "Temperature"])
                      ["FeltLocation"].mean()
                      .reset_index())
            title = "All Durations"
            fname = "scatter_all_durations.png"
            sheet_name = "AllDurations"
        else:
            data = grouped[grouped["Duration"] == dur]
            title = f"Duration = {dur}s"
            fname = f"scatter_duration_{dur}.png"
            sheet_name = f"Duration_{dur}"

        tables_to_save[sheet_name] = data.copy()

        plt.figure(figsize=(6, 5))
        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]
            if not temp_data.empty:
                plt.scatter(temp_data["Location"], temp_data["FeltLocation"],
                            color=style["color"], marker=style["marker"],
                            s=80, label=style["label"])
                # Labels
                for _, row in temp_data.iterrows():
                    plt.text(row["Location"], row["FeltLocation"],
                             f"{row['FeltLocation']:.2f}",
                             fontsize=8, ha="center", va="bottom")

        plt.plot([0, 1], [0, 1], "k--", alpha=0.5)  # reference line
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
        print(f"Saved plot: {outpath}")

    # === COMBINED SUBPLOTS (horizontal row) ===
    fig, axes = plt.subplots(1, len(durations), figsize=(6 * len(durations), 5), sharex=True, sharey=True)
    if len(durations) == 1:
        axes = [axes]

    for ax, dur in zip(axes, durations):
        if dur == "all":
            data = (df.groupby(["Location", "Temperature"])
                      ["FeltLocation"].mean()
                      .reset_index())
            title = "All Durations"
        else:
            data = grouped[grouped["Duration"] == dur]
            title = f"Duration = {dur}s"

        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]
            if not temp_data.empty:
                ax.scatter(temp_data["Location"], temp_data["FeltLocation"],
                           color=style["color"], marker=style["marker"],
                           s=80, label=style["label"])
                for _, row in temp_data.iterrows():
                    ax.text(row["Location"], row["FeltLocation"],
                            f"{row['FeltLocation']:.2f}",
                            fontsize=8, ha="center", va="bottom")

        ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
        ax.set_title(title)
        ax.set_xlabel("Intended Location")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)

    axes[0].set_ylabel("Perceived Location (avg)")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.05))
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    combined_out = os.path.join(output_folder, "scatter_all_durations_horizontal.png")
    plt.savefig(combined_out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved combined horizontal subplot figure: {combined_out}")

    # === COMBINED SUBPLOTS (2x2 grid) ===
    n_plots = len(durations)
    rows = 2
    cols = (n_plots + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows), sharex=True, sharey=True)
    axes = axes.flatten()

    for ax, dur in zip(axes, durations):
        if dur == "all":
            data = (df.groupby(["Location", "Temperature"])
                      ["FeltLocation"].mean()
                      .reset_index())
            title = "All Durations"
        else:
            data = grouped[grouped["Duration"] == dur]
            title = f"Duration = {dur}s"

        for temp, style in temp_styles.items():
            temp_data = data[data["Temperature"] == temp]
            if not temp_data.empty:
                ax.scatter(temp_data["Location"], temp_data["FeltLocation"],
                           color=style["color"], marker=style["marker"],
                           s=80, label=style["label"])
                for _, row in temp_data.iterrows():
                    ax.text(row["Location"], row["FeltLocation"],
                            f"{row['FeltLocation']:.2f}",
                            fontsize=8, ha="center", va="bottom")

        ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
        ax.set_title(title)
        ax.set_xlabel("Intended Location")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)

    axes[0].set_ylabel("Perceived Location (avg)")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.05))
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    combined_grid_out = os.path.join(output_folder, "scatter_all_durations_grid.png")
    plt.savefig(combined_grid_out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved combined 2x2 subplot figure: {combined_grid_out}")

    # === SAVE DATA TABLES TO EXCEL ===
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