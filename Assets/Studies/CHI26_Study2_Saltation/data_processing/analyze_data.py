import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [1,2,3,4,5,7,8,9,10,11,12,13,14,15,16]
    parent_folder = 'Assets/Studies/CHI26_Study2_Saltation'
    input_folder = f'{parent_folder}/data_processing/data'
    output_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'

    combined_data, excel_file = process_participant_data(input_folder, participants, output_folder)
    generate_graph(combined_data, excel_file, output_folder)

def process_participant_data(folder_path, participants, output_folder):
    filtered_data = []
    all_data = []

    for p in participants:
        filename = os.path.join(folder_path, f"p{p}_data.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)

            # Location correction to flip wrist - elbow
            df["location1"] = 1 - df["location1"]
            df["location2"] = 1 - df["location2"]
            df["location3"] = 1 - df["location3"]

            df["Participant"] = p
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
            df["NumMatch"] = (df["numLocation"] == 3).astype(int)
            df["DirectionMatch"] = np.where(
                (df["Direction"] == 1) & (df["location1"] >= df["location2"]) & (df["location2"] >= df["location3"]),
                1,
                np.where(
                    (df["Direction"] == 0) & (df["location1"] <= df["location2"]) & (df["location2"] <= df["location3"]),
                    1,
                    0
                )
            )
            df["Displacement1"] = np.where(
                (df["Direction"] == 1),
                abs(1 - df["location1"]),
                abs(0 - df["location1"])
            )
            df["Displacement2"] = np.where(
                (df["Direction"] == 1),
                abs(1 - df["location2"]),
                abs(0 - df["location2"])
            )
            df["Displacement3"] = np.where(
                (df["Direction"] == 0),
                abs(1 - df["location3"]),
                abs(0 - df["location3"])
            )
            
            include_mask = (df["ThermalMatch"] == 1) & (df["NumMatch"] == 1) #& df["DirectionMatch"] == 1
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
    print(f'Num Match: {all_combined["NumMatch"].sum()} / {all_combined["NumMatch"].count()}, {all_combined["NumMatch"].sum() / all_combined["NumMatch"].count()}')
    print(f'Direction Match: {all_combined["DirectionMatch"].sum()} / {all_combined["DirectionMatch"].count()}, {all_combined["DirectionMatch"].sum() / all_combined["DirectionMatch"].count()}')
    print(f'Valid Trials: {filtered_combined["Participant"].count()} / {all_combined["Participant"].count()}, {filtered_combined["Participant"].count() / all_combined["Participant"].count()}')

    # Melt the location columns into long format
    reformatted_df = pd.wide_to_long(
        filtered_combined,
        stubnames=["location", "Displacement"],
        i=[
            "Participant", "Trial", "Temperature", "Duration", "Direction",
            "FeltThermal", "numLocation", "extraLocations",
            "ThermalMatch", "NumMatch", "DirectionMatch"
        ],
        j="Location",
        sep="",
        suffix="\\d+"
    ).reset_index().rename(columns={"location": "FeltLocation"})

    filename_out = f"{participant_string(participants)}_analysis.xlsx"
    output_path = os.path.join(output_folder, filename_out)
    reformatted_df.to_excel(output_path, index=False)
    filename_out_csv = f"{participant_string(participants)}_analysis.csv"
    output_path_csv = os.path.join(output_folder, filename_out_csv)
    reformatted_df.to_csv(output_path_csv, index=False)

    print(f"Saved combined data to {output_path}")
    return filtered_combined, output_path


import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def generate_graph(df, excel_file, output_folder):
    """
    Creates scatterplots of location1–3 averages,
    grouped by Temperature, split by Direction × Duration,
    plus combined-direction graphs (with Direction=0 flipped).
    """
    df = df[(df["ThermalMatch"] == 1) & (df["NumMatch"] == 1)]
    df['location1'] *= 10
    df['location2'] *= 10
    df['location3'] *= 10
    df['Displacement1'] *= 10
    df['Displacement2'] *= 10
    df['Displacement3'] *= 10

    # ---------- Per-direction graphs ----------
    long_df = df.melt(
        id_vars=["Direction", "Duration", "Temperature"],
        value_vars=["location1", "location2", "location3"],
        var_name="LocationType",
        value_name="LocationValue"
    )

    grouped = (
        long_df.groupby(["Direction", "Duration", "Temperature", "LocationType"])
               .agg(Location_mean=("LocationValue", "mean"),
                    Location_sem=("LocationValue",
                                  lambda x: 0 if len(x) <= 1 else x.std(ddof=1)/np.sqrt(len(x))))
               .reset_index()
    )

    temp_styles = {
        -15: {"color": "#4A5EEB", "marker": "o", "label": "Cold"},
        0:   {"color": "#7A7A73", "marker": "o", "label": "Neutral"},
        9:   {"color": "#F73F52", "marker": "o", "label": "Hot"},
    }

    temp_offsets = {
        -15: -0.02,   # Cold (shift left)
        0:    0.0,    # No Thermal (centered)
        9:   +0.02    # Hot (shift right)
    }

    directions = sorted(grouped["Direction"].unique())
    durations = sorted(grouped["Duration"].unique())

    # store plots for combined figure
    subplot_data = []

    for d in directions:
        for dur in durations:
            subset = grouped[(grouped["Direction"] == d) & (grouped["Duration"] == dur)]
            if subset.empty:
                continue

            plt.figure(figsize=(6,5))
            for temp, style in temp_styles.items():
                temp_data = subset[subset["Temperature"] == temp]
                if temp_data.empty:
                    continue
                temp_data = temp_data.sort_values("LocationType")
                x_vals = temp_data["LocationType"]
                y_vals = temp_data["Location_mean"]
                y_errs = temp_data["Location_sem"]

                plt.errorbar(x_vals, y_vals, yerr=y_errs,
                             fmt=style["marker"], color=style["color"],
                             capsize=4, markersize=8, label=style["label"])

            plt.title("Elbow-to-Wrist" if d == 0 else "Wrist-to-Elbow" f"Direction = {d}, Duration = {dur}s")
            plt.xlabel("Pulse Order")
            plt.ylabel("Perceived Location (cm)")
            plt.ylim(-0.05, 1.05)
            plt.legend()
            plt.grid(True, linestyle="--", alpha=0.5)

            outpath = os.path.join(output_folder, f"scatter_dir{d}_dur{dur}.png")
            plt.savefig(outpath, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"Saved plot: {outpath}")

            subplot_data.append(("dir", d, dur, subset))

    plt.rcParams.update({'font.size': 12})  # sets global font size

    # ---------- Master figure: per-direction only ----------
    dir_plots = [p for p in subplot_data if p[0] == "dir"]
    if dir_plots:
        durations_in_dir = sorted(set(p[2] for p in dir_plots))
        directions_in_dir = sorted(set(p[1] for p in dir_plots))

        nrows = len(directions_in_dir)
        ncols = len(durations_in_dir)
        fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 4*nrows), squeeze=False)

        # direction labels for rows
        dir_labels = {0: "Elbow\n-to-\nWrist", 1: "Wrist\n-to-\nElbow"}

        for (ptype, d, dur, subset) in dir_plots:
            row = directions_in_dir.index(d)
            col = durations_in_dir.index(dur)
            ax = axes[row, col]

            for temp, style in temp_styles.items():
                temp_data = subset[subset["Temperature"] == temp]
                if temp_data.empty:
                    continue
                temp_data = temp_data.sort_values("LocationType")

                # ✅ map x-axis tick labels to P1, P2, P3
                base_x = np.arange(1, len(temp_data) + 1)   # [1,2,3] for P1,P2,P3
                x_vals = base_x + temp_offsets[temp] 
                ax.errorbar(x_vals, temp_data["Location_mean"],
                            yerr=temp_data["Location_sem"],
                            fmt=style["marker"], color=style["color"],
                            capsize=4, markersize=6,
                            label=style["label"], linestyle="none")

            ax.set_title(f"{'Elbow-to-Wrist' if d == 0 else 'Wrist-to-Elbow'}, {dur} s")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.set_xticks([1, 2, 3])
            ax.set_xticklabels(["P1", "P2", "P3"])
            ax.set_yticks([0.0, 2.5, 5.0, 7.5, 10.0])

            # ✅ Show y-axis label + ticks only for first column
            if col == 0:
                ax.set_ylabel("Perceived Location (cm)")
            else:
                ax.set_ylabel("")
                ax.set_yticklabels([])

            # ✅ Show x-axis label only for bottom row
            if row == nrows - 1:
                ax.set_xlabel("Pulse Order")
            else:
                ax.set_xlabel("")

        """ # Add row labels inside, anchored to first column axes
        for row, d in enumerate(directions_in_dir):
            ax = axes[row, 0]  # first column axis of this row
            ax.annotate(dir_labels[d],
                        xy=(0, 0.5), xycoords='axes fraction',   # middle of y-axis
                        xytext=(-100, 0), textcoords='offset points',  # shift left
                        va='center', ha='center', rotation='horizontal',
                        fontsize=14, fontweight="bold") """

        # Shared legend in top-left of the first subplot
        handles, labels = axes[0, 0].get_legend_handles_labels()
        axes[0, 0].legend(handles, labels, loc="upper left", frameon=True)

        fig.tight_layout(rect=[0, 0, 1, 1])

        outpath = os.path.join(output_folder, "study2_locations.png")
        fig.savefig(outpath, dpi=300)
        plt.close(fig)
        print(f"Saved direction-only grid: {outpath}")

    # ---------- Master figure: combined-direction only (Displacement) ----------
    # Prepare displacement data separately
    disp_long_df = df.melt(
        id_vars=["Direction", "Duration", "Temperature"],
        value_vars=["Displacement1", "Displacement2", "Displacement3"],
        var_name="DisplacementType",
        value_name="DisplacementValue"
    )

    disp_grouped = (
        disp_long_df.groupby(["Duration", "Temperature", "DisplacementType"])
                    .agg(Disp_mean=("DisplacementValue", "mean"),
                         Disp_sem=("DisplacementValue",
                                   lambda x: 0 if len(x) <= 1 else x.std(ddof=1)/np.sqrt(len(x))))
                    .reset_index()
    )

    # Filter to only durations available
    durations_in_comb = sorted(disp_grouped["Duration"].unique())
    ncols = len(durations_in_comb)
    nrows = 1

    fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 4), squeeze=False)

    for col, dur in enumerate(durations_in_comb):
        ax = axes[0, col]
        subset = disp_grouped[disp_grouped["Duration"] == dur]

        for temp, style in temp_styles.items():
            temp_data = subset[subset["Temperature"] == temp]
            if temp_data.empty:
                continue

            # map x-axis to P1, P2, P3
            x_vals = ["P1", "P2", "P3"]
            x_vals = base_x + temp_offsets[temp] 
            ax.errorbar(x_vals, temp_data["Disp_mean"], 
                        yerr=temp_data["Disp_sem"],
                        fmt=style["marker"], color=style["color"],
                        capsize=4, markersize=6, label=style["label"], linestyle="none")

        ax.set_title(f"{dur} s")
        ax.set_xlabel("Pulse Order")

        # ✅ Only first column gets y-axis label
        if col == 0:
            ax.set_ylabel("Absolute Displacement (cm)")
        else:
            ax.set_ylabel("")
            ax.set_yticklabels([])

        ax.set_ylim(-0.05, 0.55)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["P1", "P2", "P3"])
        ax.set_yticks([0.0, 2.5, 5.0, 7.5, 10.0])
        
        # ✅ Show x-axis label only for bottom row
        if col == 1:
            ax.set_xlabel("Pulse Order")
        else:
            ax.set_xlabel("")

    # Shared legend in top-left of first subplot
    handles, labels = axes[0, 0].get_legend_handles_labels()
    axes[0, 0].legend(handles, labels, loc="upper left", frameon=True)

    fig.tight_layout()

    outpath = os.path.join(output_folder, "study2_displacement.png")
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    print(f"Saved combined-displacement grid: {outpath}")

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