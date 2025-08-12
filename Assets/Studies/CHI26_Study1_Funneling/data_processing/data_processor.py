import os
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuration ---
input_folder = 'Assets/Studies/CHI26_Study1_Funneling/data_processing/data'         # <-- UPDATE THIS
output_folder = 'Assets/Studies/CHI26_Study1_Funneling/data_processing/output'        # <-- UPDATE THIS
sheet_name = 0  # Use 0 for the first sheet, or specify by name

os.makedirs(output_folder, exist_ok=True)

# --- Loop through Excel files ---
for filename in os.listdir(input_folder):
    if filename.endswith(('.xlsx', '.xls')):
        file_path = os.path.join(input_folder, filename)

        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Loaded: {filename} with shape {df.shape}")

            # --- Simple data processing example ---
            # Try plotting the first 2 numeric columns
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) < 2:
                print(f"⚠️ Not enough numeric columns in {filename} to plot.")
                continue

            x = df[numeric_cols[0]]
            y = df[numeric_cols[1]]

            # --- Plot ---
            plt.figure(figsize=(8, 5))
            plt.plot(x, y, marker='o')
            plt.title(f"{filename} — {numeric_cols[1]} vs {numeric_cols[0]}")
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
            plt.grid(True)

            # --- Save plot ---
            out_name = os.path.splitext(filename)[0] + "_plot.png"
            out_path = os.path.join(output_folder, out_name)
            plt.savefig(out_path)
            plt.close()
            print(f"✅ Saved plot: {out_path}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")