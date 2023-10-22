import pygame
import numpy as np
import os
import math
import json


def create_dictionary_from_image_name(
        image_name):  # this dict will include a picture and a tuple, tuple will contain image, x, y scaling, and the type defind by
    # the image name
    # Split the image name based on underscores
    parts = image_name.split("_")
    if len(parts) != 7:
        raise ValueError("Invalid image name format: " + image_name)

        # Extract the relevant information from the image name
    wm, p, tile_type, name, number, x, y = parts
    x, y = int(x), int(y)

    # Load the image using Pygame
    image = (os.path.join(world_map_img_location, image_name + ".png"))
    # #pygame.transform.scale(pygame.image.load(os.path.join(world_map_img_location, image_name + ".png")), scales)

    # Create a dictionary with the extracted information
    image_info = {
        "image": image,
        "x_scale": x,
        "y_scale": y,
        "type": tile_type
    }

    return image_info


def create_dict_of_dicts_from_load_images(world_map_img_location):
    # Initialize an empty dictionary and a counter for unique IDs
    img_scale_type_dict = {}
    unique_id = 1

    # Iterate through all files in the specified directory and its subfolders
    for root, dirs, files in os.walk(world_map_img_location):
        for file in files:
            if file.endswith(".png"):
                image_name = os.path.splitext(file)[0]  # Remove the file extension
                img_info = create_dictionary_from_image_name(image_name)

                # Add the unique ID to the dictionary entry
                img_info["id"] = unique_id
                img_scale_type_dict[unique_id] = img_info

                # Increment the unique ID counter
                unique_id += 1

    return img_scale_type_dict


# Function to save the image dictionary to a file
def save_image_dict_as_json(image_info, filename):
    with open(filename, 'w') as file:
        json.dump(image_info, file)

# Function to load the image dictionary from a file
def load_image_dict_from_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            image_info = json.load(file)
            return image_info
    else:
        return None


def add_new_images_to_dict(world_map_img_location, image_dict):
    unique_id = max(image_dict.keys()) if image_dict else 0  # Find the highest unique ID

    for root, dirs, files in os.walk(world_map_img_location):
        for file in files:
            if file.endswith(".png"):
                image_name = os.path.splitext(file)[0]  # Remove the file extension
                img_info = create_dictionary_from_image_name(image_name)

                # Check if the image is not in the dictionary, and add it with a new ID
                if not any(
                        img_info["type"] == v["type"] and img_info["x_scale"] == v["x_scale"] and img_info["y_scale"] == v["y_scale"] and img_info["image"] ==
                        v["image"] for v in image_dict.values()):
                    unique_id += 1
                    img_info["id"] = unique_id
                    image_dict[unique_id] = img_info
    return image_dict


def mark_deleted_images(world_map_img_location, image_dict):
    def mark_deleted_images(image_dict):
        for img_id, img_info in image_dict.items():
            image_path = img_info['image']

            # Check if the image file does not exist
            if not os.path.exists(image_path):
                img_info['type'] = 'DELETED'

    return image_dict


def update_dict_to_be_congruent_with_files(world_map_img_location, image_info):
    image_info = add_new_images_to_dict(world_map_img_location, image_info)
    image_info = mark_deleted_images(world_map_img_location, image_info)
    return image_info


# Function to check if a dictionary exists, and load it if it does; otherwise, create one
def check_and_load_image_dict(world_map_img_location):
    filename = 'Dicts/main_image_world_map_dict.json'
    image_info = load_image_dict_from_json(filename)

    if image_info is not None:
        print("Image dictionary loaded.")
    else:
        print("Image dictionary does not exist. Creating a new one.")
        image_info = create_dict_of_dicts_from_load_images(world_map_img_location)  # Call your function to create the dictionary

    update_dict_to_be_congruent_with_files(world_map_img_location, image_info)
    save_image_dict_as_json(image_info, filename)

    return image_info


def is_space_available(map_array, current_row, current_col, x_scale, y_scale):
    rows, cols = map_array.shape

    # Check if there is enough space in both rows and columns
    if current_row + y_scale > rows or current_col + x_scale > cols:
        return False

    # Check if the space is already occupied by other images
    for row in range(current_row, current_row + y_scale):
        for col in range(current_col, current_col + x_scale):
            if map_array[row, col] != 0:
                return False

    return True


def place_images_on_map(map_array, img_scale_type_dict):
    rows, cols = map_array.shape

    sorted_images = sorted(img_scale_type_dict.items(), key=lambda x: img_scale_type_dict[x[0]]["image"])

    for unique_id, img_info in sorted_images:
        x_scale, y_scale = img_info["x_scale"], img_info["y_scale"]
        row_start_to_place = 0
        col_start_to_place = 0
        found = False
        for col in range(cols):
            if found:
                break
            for row in range(rows):
                # Check if the current position is empty and if there's enough space for the image
                if map_array[row, col] == 0 and row + y_scale <= rows and col + x_scale <= cols:
                    # Check if the required space is empty
                    is_space_empty = all(map_array[row + i, col + j] == 0 for i in range(y_scale) for j in range(x_scale))

                    if is_space_empty:
                        row_start_to_place = row
                        col_start_to_place = col
                        found = True
                        break

        map_array[row_start_to_place:row_start_to_place + y_scale, col_start_to_place:col_start_to_place + x_scale] = unique_id


def create_map_from_images(img_scale_type_dict, screen_height, scale):  # takes dict and screen height and scale measured in pixels to arrange the available
    # img_scale_type_dict. The created map should be 80% of the total screen_height and images should be scaled to the amount of pixels in the scale variable
    # (which would denote a x_,y_ scale availabe inside the dictionary of 1,1); if there is space for only 3 images, then each column should be 3 rows of images,
    # should output an array of rowlength determined by the amount of pictures that fit on a screen, column length by the amount of total pictures
    # If a picture is bigger than 1,1 then multiple entries on the row,column array (using numpy/pandas arrays) should have the same unique idea. For instance a
    # tree of height 2, should take up 2 rows, and 1 column. Assume that no asset will be bigger than the total amount of available pictures per column

    ARBITRARY_AMOUNT_EXTRA_COLS = 5  # for making sure it all fits on the screen
    PERCENTAGE_OF_SCREEN = 80
    # Calculate the total number of rows based on the screen height and scaling
    total_rows = int((screen_height * PERCENTAGE_OF_SCREEN / 100) / scale)
    total_width = math.ceil(
        sum(max(img_info["x_scale"], img_info["y_scale"]) for img_info in img_scale_type_dict.values()) / total_rows + ARBITRARY_AMOUNT_EXTRA_COLS)

    # Initialize the map as a 2D NumPy array filled with zeros
    map_array = np.zeros((total_rows, total_width), dtype=int)
    place_images_on_map(map_array, img_scale_type_dict)
    return map_array


# ### TEST CODE create_map_from_images
# screen_height = 1000 # is 800 after 80% reduction
# scale = 250 # fits round down 3 times in 800
# img_scale_type_dict = {
#     1: {"x_scale": 1, "y_scale": 1, "image": "wm_p_tiles_water_001_1_1.png"},
#     2: {"x_scale": 2, "y_scale": 1, "image": "wm_p_tiles_water_002_2_1.png"},
#     3: {"x_scale": 2, "y_scale": 1, "image": "wm_p_tiles_water_003_2_1.png"},
#     4: {"x_scale": 3, "y_scale": 1, "image": "wm_p_tiles_water_004_3_1.png"},
#     5: {"x_scale": 2, "y_scale": 2, "image": "wm_p_tiles_water_005_2_2.png"},
#     6: {"x_scale": 3, "y_scale": 1, "image": "wm_p_tiles_water_006_3_1.png"},
#     7: {"x_scale": 4, "y_scale": 2, "image": "wm_p_tiles_water_007_5_1.png"},
#     8: {"x_scale": 3, "y_scale": 2, "image": "wm_p_tiles_water_008_3_2.png"},
#     9: {"x_scale": 2, "y_scale": 1, "image": "wm_p_tiles_water_009_2_1.png"},
#     10: {"x_scale": 1, "y_scale": 3, "image": "wm_p_tiles_water_010_1_3.png"}
# }
#
# map_array = create_map_from_images(img_scale_type_dict, screen_height, scale)
# print(map_array)
#
# for loop which checks from 0,0 in the array and moves downwards through all columsn to check if the array is empty at that position,
# if that is the case, check if from that point onwards, additional necessary rows and columns are empty
# if so, add in the image. On the next loop, check the map array again to find new empty places


pygame.init()

WIDTH = 1800
HEIGHT = 900
screen_info = pygame.display.Info()
#WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

TILE_SIZE_WORLD = 50
TILE_SIZE_EDITOR = 100
SCALES = (100, 100)
screen = pygame.display.set_mode([WIDTH, HEIGHT])
fps = 60
timer = pygame.time.Clock()
pygame.display.set_caption('World Map Editor')

parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.path.join(parent_directory, 'Assets/Images/Backgrounds/PLACEHOLDER_STOCK_WATER.jpg')
PLACEHOLDER_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join(parent_directory, 'Assets/Images/Backgrounds/PLACEHOLDER_STOCK_WATER.png')),
                                                (WIDTH, HEIGHT))
world_map_img_location = os.path.join(parent_directory, 'Assets/Images/World_Map_Static/')

img_scale_type_dict =check_and_load_image_dict(world_map_img_location)
#img_scale_type_dict = create_dict_of_dicts_from_load_images(world_map_img_location)
#create_map_from_images(img_scale_type_dict, HEIGHT, TILE_SIZE_EDITOR)

run = True
while run:
    timer.tick(fps)
    screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False  # Exit the game when the Escape key is pressed

    # Update the display
    pygame.display.flip()
