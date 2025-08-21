import os
import re
from PIL import Image

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

def shift_images_left(folder_path, shift_pixels):
    """
    Reads all PNGs in a folder and shifts their content left by `shift_pixels`.
    
    Args:
        folder_path (str): Path to the folder containing PNGs.
        shift_pixels (int): Number of pixels to shift left.
        save_suffix (str): Suffix to add to new filenames (default "_shifted").
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            img_path = os.path.join(folder_path, filename)
            img = Image.open(img_path)

            # Create a new blank (transparent) image
            shifted = Image.new("RGBA", img.size, (0, 0, 0, 0))

            # Paste original image shifted left
            shifted.paste(img, (-shift_pixels, 0))

            # Save new file
            name, ext = os.path.splitext(filename)
            save_path = os.path.join(folder_path, f"{name}{ext}")
            shifted.save(save_path)

            print(f"Saved shifted image: {save_path}")

def delete_shifted_files(folder_path, keyword="shifted"):
    """
    Delete all files in the folder whose name contains the keyword.
    
    Args:
        folder_path (str): Path to the folder.
        keyword (str): Substring to match in filenames (default "shifted").
    """
    for filename in os.listdir(folder_path):
        if keyword in filename:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

#rename_files_in_folder("Assets\Studies\CHI26_Study1_Funneling\drawings\p20", 20, 1)
#shift_images_left("Assets\Studies\CHI26_Study2_Saltation\drawings\p1", shift_pixels=50)
#shift_images_left("Assets\Studies\CHI26_Study1_Funneling\drawings\p2", shift_pixels=50)
delete_shifted_files("Assets\Studies\CHI26_Study2_Saltation\drawings\p4", "meta")