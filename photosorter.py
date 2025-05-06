# -*- coding: utf-8 -*-
"""
@author: Jamesasome
"""
import os
import shutil
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from tinytag import TinyTag

def get_image_datetime(image_path):
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()

        datetime_tags = ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]

        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)

            if tag in datetime_tags:
                if isinstance(data, bytes):
                    try:
                        data = data.decode('utf-8', errors='ignore')
                    except Exception:
                        data = data.hex()
                return data
        return None

    except UnidentifiedImageError:
        print(f"Skipping invalid image: {image_path}")
        return None
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def list_files_walk(start_path='.'):
    file_list = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def check_make_directory(folder_name, output_path):
    target_folder = os.path.join(output_path, folder_name)
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

def path_transfer(original_path, folder_name, output_path):
    filename = os.path.basename(original_path)
    return os.path.join(output_path, folder_name, filename)

# Specify the directory paths
directory_path = input("Image Directory:")
directory_output = input("Directory Output:")
supported_image = [".jpg", ".jpeg", ".gif", ".png"]

# Ensure output directory exists
if not os.path.exists(directory_output):
    os.mkdir(directory_output)

# Get all files
a = list_files_walk(directory_path)

for x in a:
    ext = os.path.splitext(x)[1].lower()
    
    # Check if it's an image
    if ext in supported_image:
        d = get_image_datetime(x)
        if d:
            year = d[:4]
            check_make_directory(year, directory_output)
            target_path = path_transfer(x, year, directory_output)
            shutil.move(x, target_path)
            print(f"Moved {x} to {target_path}")
        else:
            print(f"No EXIF datetime found for {x}, skipping.")

    # Check if it's a supported video/audio using TinyTag
    elif TinyTag.is_supported(x):
        try:
            tag = TinyTag.get(x)
            year = tag.year
            if year and len(year) >= 4:
                year = year[:4]
                check_make_directory(year, directory_output)
                target_path = path_transfer(x, year, directory_output)
                shutil.move(x, target_path)
                print(f"Moved {x} to {target_path}")
            else:
                print(f"No year info found for {x}, skipping.")
        except Exception as e:
            print(f"Error reading metadata for {x}: {e}")
    else:
        print("Not an image or supported video/audio file: " + x)
