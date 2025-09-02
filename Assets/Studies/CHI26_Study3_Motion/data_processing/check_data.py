import pandas as pd
from scipy.stats import shapiro, levene
import itertools
import os

def main():
    participants = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    parent_folder = 'Assets/Studies/CHI26_Study3_Motion'
    input_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'
    output_folder = f'{parent_folder}/data_processing/analysis/{participant_string(participants)}'

    # Load your dataframe
    df = pd.read_excel(os.path.join(input_folder, f"{participant_string(participants)}_analysis.xlsx"))

    # === Run checks ===
    normality_results, homogeneity_results = run_checks(df)

    # Save to CSVs
    normality_results.to_csv(os.path.join(output_folder, "normality_results.csv"), index=False)
    homogeneity_results.to_csv(os.path.join(output_folder, "homogeneity_results.csv"), index=False)

    print(f"Normality results saved to {os.path.join(output_folder, 'normality_results.csv')}")
    print(f"Homogeneity results saved to {os.path.join(output_folder, 'homogeneity_results.csv')}")

def run_checks(df):
    results_normality = []
    results_homogeneity = []

    # === Normality check (Shapiro–Wilk per condition) ===
    for (temp, dur, dir), subset in df.groupby(["Temperature", "Duration", "Direction"]):
        stat, p = shapiro(subset["FeltMotion"])
        results_normality.append({
            "Temperature": temp,
            "Duration": dur,
            "Direction": dir,
            "Shapiro_W": stat,
            "p_value": p,
            "Normality_OK": 1 if p > 0.005 else 0
        })

    df_normality = pd.DataFrame(results_normality)

    # === Homogeneity of variances (Levene’s test across temperatures) ===
    # Here we check variance across Temperature levels for each Duration × Location
    for (dur, dir), subset in df.groupby(["Duration", "Direction"]):
        groups = [g["FeltMotion"].values for _, g in subset.groupby("Temperature")]
        if len(groups) > 1:  # Need at least 2 groups
            stat, p = levene(*groups)
            results_homogeneity.append({
                "Duration": dur,
                "Direction": dir,
                "Levene_W": stat,
                "p_value": p,
                "Homoscedasticity_OK": 1 if p > 0.005 else 0
            })

    df_homogeneity = pd.DataFrame(results_homogeneity)

    return df_normality, df_homogeneity

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