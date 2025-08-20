import os
import re

def rename_files_in_folder(folder_path, old_num, new_num):
    """
    Replace 'p{old_num}' with 'p{new_num}' in all filenames in a folder.
    
    Args:
        folder_path (str): Path to the folder.
        old_num (int): The number in 'p#' to replace.
        new_num (int): The new number to use in 'p$'.
    """
    pattern = re.compile(rf"p{old_num}(?=\D|$)")  # match p# only when followed by non-digit or end of string
    
    for filename in os.listdir(folder_path):
        new_filename = pattern.sub(f"p{new_num}", filename)
        
        if new_filename != filename:  # only rename if there's a change
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            print(f"Renaming: {filename} → {new_filename}")
            os.rename(old_path, new_path)

rename_files_in_folder("Assets\Studies\CHI26_Study1_Funneling\drawings\p20", 20, 1)