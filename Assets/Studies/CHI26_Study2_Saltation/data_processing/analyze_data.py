import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
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

            df["Participant"] = p
            df["ThermalMatch"] = (np.sign(df["Temperature"]) == np.sign(df["FeltThermal"])).astype(int)
            df["NumMatch"] = (df["numLocation"] == 3).astype(int)
            df["DirectionMatch"] = np.where(
                (df["Direction"] == 0) & (df["location1"] >= df["location2"]) & (df["location2"] >= df["location3"]),
                1,
                np.where(
                    (df["Direction"] == 1) & (df["location1"] <= df["location2"]) & (df["location2"] <= df["location3"]),
                    1,
                    0
                )
            )
            df["Displacement1"] = np.where(
                (df["Direction"] == 0),
                abs(1 - df["location1"]),
                abs(0 - df["location1"])
            )
            df["Displacement2"] = np.where(
                (df["Direction"] == 0),
                abs(1 - df["location2"]),
                abs(0 - df["location2"])
            )
            df["Displacement3"] = np.where(
                (df["Direction"] == 1),
                abs(1 - df["location3"]),
                abs(0 - df["location3"])
            )
            
            include_mask = (df["ThermalMatch"] == 1) & (df["NumMatch"] == 1) & df["DirectionMatch"] == 1
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
        -15: {"color": "blue", "marker": "o", "label": "Cold"},
        0:   {"color": "gray", "marker": "o", "label": "No Thermal"},
        9:   {"color": "red", "marker": "o", "label": "Hot"}
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

            plt.title(f"Direction = {d}, Duration = {dur}s")
            plt.xlabel("Location")
            plt.ylabel("Average Location Value")
            plt.ylim(-0.05, 1.05)
            plt.legend()
            plt.grid(True, linestyle="--", alpha=0.5)

            outpath = os.path.join(output_folder, f"scatter_dir{d}_dur{dur}.png")
            plt.savefig(outpath, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"Saved plot: {outpath}")

            subplot_data.append(("dir", d, dur, subset))


    # ---------- Combined-direction graphs ----------
    df_flipped = df.copy()

    # Flip Direction = 0 so loc1=left(0), loc3=right(1)
    mask = df_flipped["Direction"] == 0
    for col in ["location1", "location2", "location3"]:
        df_flipped.loc[mask, col] = 1 - df_flipped.loc[mask, col]

    long_df_comb = df_flipped.melt(
        id_vars=["Duration", "Temperature"],
        value_vars=["location1", "location2", "location3"],
        var_name="LocationType",
        value_name="LocationValue"
    )

    grouped_comb = (
        long_df_comb.groupby(["Duration", "Temperature", "LocationType"])
                    .agg(Location_mean=("LocationValue", "mean"),
                         Location_sem=("LocationValue",
                                       lambda x: 0 if len(x) <= 1 else x.std(ddof=1)/np.sqrt(len(x))))
                    .reset_index()
    )

    for dur in durations:
        subset = grouped_comb[grouped_comb["Duration"] == dur]
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

        plt.title(f"Combined Directions, Duration = {dur}s")
        plt.xlabel("Location (normalized left→right)")
        plt.ylabel("Average Location Value")
        plt.ylim(-0.05, 1.05)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        outpath = os.path.join(output_folder, f"scatter_combined_dur{dur}.png")
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved combined plot: {outpath}")

        subplot_data.append(("combined", None, dur, subset))

    # ---------- Master figure with all subplots ----------
    nplots = len(subplot_data)
    ncols = 3
    nrows = int(np.ceil(nplots / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 5*nrows), squeeze=False)

    for idx, (ptype, d, dur, subset) in enumerate(subplot_data):
        ax = axes[idx // ncols, idx % ncols]
        for temp, style in temp_styles.items():
            temp_data = subset[subset["Temperature"] == temp]
            if temp_data.empty:
                continue
            temp_data = temp_data.sort_values("LocationType")
            ax.errorbar(temp_data["LocationType"], temp_data["Location_mean"],
                        yerr=temp_data["Location_sem"],
                        fmt=style["marker"], color=style["color"],
                        capsize=4, markersize=6, label=style["label"], linestyle="none")

        if ptype == "dir":
            ax.set_title(f"Dir={d}, Dur={dur}s")
            ax.set_xlabel("Location")
        else:
            ax.set_title(f"Combined, Dur={dur}s")
            ax.set_xlabel("Location (normalized left→right)")

        ax.set_ylabel("Avg Location Value")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.tight_layout(rect=[0, 0, 0.9, 1])

    outpath = os.path.join(output_folder, "all_plots_grid.png")
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    print(f"Saved master grid: {outpath}")

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