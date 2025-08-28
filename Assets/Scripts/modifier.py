import os
import re
from PIL import Image
import cv2

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
                
def horizontal_flip_pngs_in_folder(input_folder, output_folder=None):
    # If no output folder specified, overwrite in place
    if output_folder is None:
        output_folder = input_folder
    else:
        os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open image
            img = Image.open(input_path)

            # Flip along vertical axis (left-right flip)
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)

            # Save flipped image
            flipped_img.save(output_path)
            print(f"Flipped: {filename}")
            
def vertical_flip_pngs_in_folder(input_folder, output_folder=None):
    # If no output folder specified, overwrite in place
    if output_folder is None:
        output_folder = input_folder
    else:
        os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open image
            img = Image.open(input_path)

            # Flip along vertical axis (left-right flip)
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)

            # Save flipped image
            flipped_img.save(output_path)
            print(f"Flipped: {filename}")

def scale_and_translate_pngs_in_folder(input_folder, output_folder=None, scale=1.0, translate=(0, 0)):
    """
    Scales PNGs but keeps original canvas size.
    Content is anchored at center, with optional translation.
    Empty areas are transparent.
    """
    if output_folder is None:
        output_folder = input_folder
    else:
        os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open with alpha channel
            img = Image.open(input_path).convert("RGBA")

            # Scale image content
            new_size = (int(img.width * scale), int(img.height * scale))
            img_scaled = img.resize(new_size, Image.LANCZOS)

            # Create background with same size as original
            canvas = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))

            # Compute offsets: center + translation
            x_offset = (img.width - img_scaled.width) // 2 + translate[0]
            y_offset = (img.height - img_scaled.height) // 2 + translate[1]

            # Paste scaled image centered
            canvas.paste(img_scaled, (x_offset, y_offset), img_scaled)

            # Save output
            canvas.save(output_path, "PNG")
            print(f"Saved transformed PNG: {output_path}")

def expand_canvas(input_folder, output_folder=None, new_size=None, fill=(255, 255, 255, 0)):
    # If no output folder specified, overwrite in place
    if output_folder is None:
        output_folder = input_folder
    else:
        os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
         if filename.lower().endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            """
            Expands the canvas of an image while keeping it centered.

            Args:
                input_path (str): Path to input image.
                output_path (str): Path to save expanded image.
                new_size (tuple): (width, height) of new canvas.
                fill (tuple): RGBA background color (default: transparent).
            """
            img = Image.open(input_path).convert("RGBA")
            old_w, old_h = img.size
            new_w, new_h = new_size

            if new_w < old_w or new_h < old_h:
                raise ValueError("New size must be larger than the original image size")

            # Create new canvas
            canvas = Image.new("RGBA", (new_w, new_h), fill)

            # Calculate offset to center original image
            offset_x = (new_w - old_w) // 2
            offset_y = (new_h - old_h) // 2

            # Paste image onto canvas
            canvas.paste(img, (offset_x, offset_y), img)
            canvas.save(output_path, "PNG")
            print(f"Saved expanded image: {output_path}")



#rename_files_in_folder("Assets\Studies\CHI26_Study1_Funneling\drawings\p20", 20, 1)
#shift_images_left("Assets\Studies\CHI26_Study1_Funneling\drawings\p1", shift_pixels=50)
#shift_images_left("Assets\Studies\CHI26_Study1_Funneling\drawings\p2", shift_pixels=50)
#flip_pngs_in_folder("Assets\Studies\CHI26_Study1_Funneling\drawings\p4")
#shift_images_left("Assets\Studies\CHI26_Study1_Funneling\drawings\p4", shift_pixels=10)

for i in range(6, 7):
    path = f"D:\\UnityProjects\\TestingSuite\\Assets\\Studies\\CHI26_Study2_Saltation\\drawings\\p{i}"
    #scale_and_translate_pngs_in_folder(path, scale=.8, translate=(45,0))
    vertical_flip_pngs_in_folder(path)