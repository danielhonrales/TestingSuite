import itertools
import random
import pandas as pd
import os

# Study 1
""" "Temperature": [9, 6, 0, -12, -15],
"Duration": [0.1, 0.5, 1, 1.5, 2],
"Location": [0, 0.25, 0.5, 0.75, 1] """

# Study 2
""" "Temperature": [9, 6, 0, -12, -15],
"Duration": [0.1, 0.2, 0.3, 0.4, 0.5],
"Direction": [0, 1] """

# Study 3
""" "Temperature": [9, 6, 0, -12, -15],
"Duration": [0.1, 0.5, 1.0, 1.5, 2.0],
"Direction": [0, 1] """

# Conditions
factors = {
    "Temperature": [9, 6, 0, -12, -15],
    "Duration": [0.1, 0.2, 0.3, 0.4, 0.5],
    "Direction": [0, 1]
}

block_factor = None
repetitions = 3

# Create the output folder
output_folder = '../Studies/CHI26_Study2_Saltation/trial_info'
os.makedirs(output_folder, exist_ok=True)

# Generate all possible combinations
def generate_combinations():
    return list(itertools.product(*factors.values()))

# Generate the randomized orders with repetitions for a given number of participants
def generate_trial_sets(num_participants):
    trial_sets = []
    all_combinations = generate_combinations()
    for participant in range(1, num_participants + 1):
        trial_set = []

        # if blocking
        #randomized_distances = random.sample(distances, len(distances))
        #for distance in randomized_distances:

        repeated_combinations = all_combinations * repetitions
        random.shuffle(repeated_combinations)

        for combination in repeated_combinations:
            trial_info = {'Participant': participant}
            for i in range(len(combination)):
                trial_info[list(factors.keys())[i]] = combination[i]
            trial_set.append(trial_info)

        trial_sets.append(trial_set)
    return trial_sets

# Save each participant's order in a unique Excel file
def save_to_csv(trial_sets):
    for trial_set in trial_sets:
        participant_number = trial_set[0]['Participant']
        df = pd.DataFrame(trial_set)
        file_name = f'p{participant_number}_trial_set.csv'
        file_path = os.path.join(output_folder, file_name)
        try: 
            df.to_csv(file_path, index=False)
            print(f"Saved {file_name}")
        except Exception as e:
            print(f"Failed to save {file_name}")

# Generate and save orders for 16 participants
num_participants = 16
trial_sets = generate_trial_sets(num_participants)
save_to_csv(trial_sets)