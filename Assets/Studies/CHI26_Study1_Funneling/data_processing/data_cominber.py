import os
import re
import pandas as pd

# --- Configure Paths ---
conditions_folder = 'Assets/Studies/CHI26_Study1_Funneling/trial_info'
responses_folder = 'Assets/Studies/CHI26_Study1_Funneling/trial_responses'
output_folder = 'Assets/Studies/CHI26_Study1_Funneling/data_processing/data'  # Optional: to save combined files
identifier_pattern = r"p\d+"   # Regex pattern to identify matching key (e.g., p12)

# --- Create output folder if needed ---
os.makedirs(output_folder, exist_ok=True)

# --- Helper function to map files by identifier ---
def get_files_by_identifier(folder):
    file_map = {}
    for fname in os.listdir(folder):
        if fname.endswith(('.csv')):
            match = re.search(identifier_pattern, fname.lower())
            if match:
                key = match.group(0)  # e.g., 'p12'
                file_map[key] = os.path.join(folder, fname)
    return file_map

# --- Get Excel file names (only files ending with .xls or .xlsx) ---
files1 = get_files_by_identifier(conditions_folder)
files2 = get_files_by_identifier(responses_folder)

# --- Get intersecting filenames (pairs) ---
common_keys = set(files1.keys()) & set(files2.keys())

# --- Process each matched pair ---
for key in common_keys:
    path1 = files1[key]
    path2 = files2[key]

    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    df2 = df2.iloc[:, 1:]
    df2 = df2.drop_duplicates(subset='trialNumber', keep='last')

    # Combine data: choose method
    combined = pd.concat([df1, df2], axis=1)  # side-by-side

    # Insert trial column at 2nd column
    # Reorder columns: move column at index 4 to index 1
    cols = list(combined.columns)
    col_to_move = cols.pop(4)
    cols.insert(1, col_to_move)
    combined = combined[cols]

    # Rename Headers
    combined.columns = ['Participant', 'Trial', 'Temperature', 'Duration', 'Location', 'FeltThermal', 'FeltLocation']

    # Save combined result
    out_path = os.path.join(output_folder, f"{key}_data.xlsx")
    combined.to_excel(out_path, index=False)
    print(f"Combined {key}: saved to {out_path}")