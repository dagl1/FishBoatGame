import pygame
import numpy as np
import os
import math
import json


def create_dictionary_from_image_name(world_map_img_location_file,
                                      image_name):  # this dict will include a picture and a tuple, tuple will contain image, x, y scaling, and the type defind by
    # the image name
    # Split the image name based on underscores

    parts = image_name[0].split("_")

    if len(parts) != 7:
        raise ValueError("Invalid image name format: " + image_name)

        # Extract the relevant information from the image name
    wm, p, tile_type, name, number, x, y = parts
    x, y = int(x), int(y)

    # Load the image using Pygame
    image = (os.path.join(world_map_img_location_file, image_name[0] + image_name[1]))
    # #pygame.transform.scale(pygame.image.load(os.path.join(world_map_img_location, image_name + ".png")), scales)

    # Create a dictionary with the extracted information
    image_info = {
        "image": image,
        "x_scale": x,
        "y_scale": y,
        "type": tile_type
    }

    return image_info


def create_dict_of_dicts_from_load_images(world_map_img_location_):
    # Initialize an empty dictionary and a counter for unique IDs
    img_scale_type_dict_ = {}
    unique_id = 1
    # Iterate through all files in the specified directory and its subfolders
    for root, dirs, files in os.walk(world_map_img_location_):
        for file in files:
            if file.endswith(".png"):
                world_map_img_location_file = os.path.dirname(os.path.join(root, file))
                image_name = os.path.splitext(file)  # Remove the file extension
                img_info = create_dictionary_from_image_name(world_map_img_location_file, image_name)

                # Add the unique ID to the dictionary entry
                img_info["id"] = unique_id
                img_scale_type_dict_[unique_id] = img_info

                # Increment the unique ID counter
                unique_id += 1

    return img_scale_type_dict_


# Function to save the image dictionary to a file
def save_image_dict_as_json(image_info, filename):
    with open(filename, 'w') as file:
        json.dump(image_info, file)


# Function to load the image dictionary from a file
def load_image_dict_from_json(filename):
    if os.path.exists(filename):
        if os.path.getsize(filename) > 0:
            with open(filename, 'r') as file:
                image_info = json.load(file)
                return image_info

    return None


def add_new_images_to_dict(world_map_img_location_, image_dict):
    unique_id = int(max(image_dict.keys()) if image_dict else 0)  # Find the highest unique ID)
    for root, dirs, files in os.walk(world_map_img_location_):
        for file in files:
            if file.endswith(".png") or file.endswith(".PNG"):
                world_map_img_location_file = os.path.dirname(os.path.join(root, file))
                image_name = os.path.splitext(file)  # Remove the file extension
                img_info = create_dictionary_from_image_name(world_map_img_location_file, image_name)
                # Check if the image is not in the dictionary, and add it with a new ID
                if not any(
                        img_info["type"] == v["type"] and img_info["x_scale"] == v["x_scale"] and img_info["y_scale"] == v["y_scale"] and img_info["image"] ==
                        v["image"] for v in image_dict.values()):
                    unique_id += 1
                    img_info["id"] = unique_id
                    image_dict[unique_id] = img_info
    return image_dict


def mark_deleted_images(world_map_img_location_, image_dict):
    for img_id, img_info in image_dict.items():
        image_path = img_info['image']
        # Check if the image file does not exist
        if not os.path.exists(image_path):
            img_info['type'] = 'DELETED'

    return image_dict


def update_dict_to_be_congruent_with_files(world_map_img_location_, image_info):
    image_info = add_new_images_to_dict(world_map_img_location_, image_info)
    image_info = mark_deleted_images(world_map_img_location_, image_info)
    return image_info


# Function to check if a dictionary exists, and load it if it does; otherwise, create one
def check_and_load_image_dict(world_map_img_location_):
    filename = 'Dicts/main_image_world_map_dict.json'
    image_info = load_image_dict_from_json(filename)

    if image_info is not None:
        print("Image dictionary loaded.")
    else:
        print("Image dictionary does not exist. Creating a new one.")
        image_info = create_dict_of_dicts_from_load_images(world_map_img_location_)  # Call your function to create the dictionary

    update_dict_to_be_congruent_with_files(world_map_img_location_, image_info)
    save_image_dict_as_json(image_info, filename)

    return image_info


def is_space_available(map_array_, current_row, current_col, x_scale, y_scale):
    rows, cols = map_array_.shape

    # Check if there is enough space in both rows and columns
    if current_row + y_scale > rows or current_col + x_scale > cols:
        return False

    # Check if the space is already occupied by other images
    for row in range(current_row, current_row + y_scale):
        for col in range(current_col, current_col + x_scale):
            if map_array_[row, col] != 0:
                return False

    return True


def place_images_on_map(map_array_, img_scale_type_dict_):
    rows, cols = map_array_.shape
    sorted_images = sorted(img_scale_type_dict_.items(), key=lambda x: img_scale_type_dict_[x[0]]["image"])

    for unique_id, img_info in sorted_images:
        if img_info['type'] != "DELETED":

            x_scale, y_scale = img_info["x_scale"], img_info["y_scale"]
            row_start_to_place = 0
            col_start_to_place = 0
            found = False
            for col in range(cols):
                if found:
                    break
                for row in range(rows):
                    # Check if the current position is empty and if there's enough space for the image
                    if map_array_[row, col] == 0 and row + y_scale <= rows and col + x_scale <= cols:
                        # Check if the required space is empty
                        is_space_empty = all(map_array_[row + i, col + j] == 0 for i in range(y_scale) for j in range(x_scale))

                        if is_space_empty:
                            row_start_to_place = row
                            col_start_to_place = col
                            found = True
                            break

            map_array_[row_start_to_place:row_start_to_place + y_scale, col_start_to_place:col_start_to_place + x_scale] = unique_id
    return map_array_


def create_map_from_images(img_scale_type_dict_, screen_height, scale):  # takes dict and screen height and scale measured in pixels to arrange the available
    # img_scale_type_dict. The created map should be 80% of the total screen_height and images should be scaled to the amount of pixels in the scale variable
    # (which would denote a x_,y_ scale availabe inside the dictionary of 1,1); if there is space for only 3 images, then each column should be 3 rows of images
    # should output an array of rowlength determined by the amount of pictures that fit on a screen, column length by the amount of total pictures
    # If a picture is bigger than 1,1 then multiple entries on the row,column array (using numpy/pandas arrays) should have the same unique idea. For instance a
    # tree of height 2, should take up 2 rows, and 1 column. Assume that no asset will be bigger than the total amount of available pictures per column

    ARBITRARY_AMOUNT_EXTRA_COLS = 5  # for making sure it all fits on the screen
    PERCENTAGE_OF_SCREEN = 80
    # Calculate the total number of rows based on the screen height and scaling
    total_rows = int((screen_height * PERCENTAGE_OF_SCREEN / 100) / scale)
    total_width = math.ceil(
        sum(max(img_info["x_scale"], img_info["y_scale"]) for img_info in img_scale_type_dict_.values()) / total_rows + ARBITRARY_AMOUNT_EXTRA_COLS)

    # Initialize the map as a 2D NumPy array filled with zeros
    map_array_ = np.zeros((total_rows, total_width), dtype=int)
    map_array_ = place_images_on_map(map_array_, img_scale_type_dict_)
    print(map_array_)
    return map_array_


def set_state_of_editor(option):  # will determine if we are in map select, or editing mode, or menu loading
    editor_state_ = 1
    if option == 'world_map_selector':
        editor_state_ = 1
    elif option == 'world_map_editing_mode':
        editor_state_ = 2
    elif option == 'world_map_menu_screen':
        editor_state_ = 3

    return editor_state_


def check_available_world_maps(available_maps_location_):
    available_maps_ = []

    if os.path.exists(available_maps_location_) and os.path.isdir(available_maps_location_):
        for file in os.listdir(available_maps_location_):
            if file.lower().endswith(".json"):
                available_maps_.append(os.path.join(available_maps_location_, file))

    return available_maps_


def calculate_main_rect_editor():
    # Define dimensions for the main rectangle
    rect_width = int(WIDTH * 0.7)
    rect_height = int(HEIGHT * 0.7)
    rect_x = int((WIDTH - rect_width) / 2)
    rect_y = int((HEIGHT - rect_height) / 2)

    main_rect_object = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    return main_rect_object


class SelectionMaps:
    def __init__(self, map_name, position_in_row, wrapper_rect, min_row_height_):
        self.map_name = map_name
        self.text_x = wrapper_rect.left + (wrapper_rect.width - 300) // 2
        self.text_y = wrapper_rect.top + position_in_row * min_row_height_ + 20
        self.delete_button = Button((wrapper_rect.left + wrapper_rect.width - 100, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                    "Delete", (255, 0, 0), 'Delete Map', self)
        self.edit_name_button = Button((wrapper_rect.left + wrapper_rect.width - 220, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                       "Edit Map", (0, 255, 0), 'Edit Map', self)
        self.edit_map_button = Button((wrapper_rect.left + wrapper_rect.width - 240, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                      "Change Name", (0, 0, 255), 'Edit Map_Name', self)
        self.font = pygame.font.Font(None, 36)
        self.text_color = (0, 0, 0)
        # self.preview_selection = preview_selection

    def draw(self, surface):
        map_name_text = self.font.render(self.map_name, True, self.text_color)
        screen.blit(map_name_text, (self.text_x, self.text_y))
        self.delete_button.draw(surface)
        self.edit_name_button.draw(surface)
        self.edit_map_button.draw(surface)


class CreateNewMap(SelectionMaps):
    def __init__(self, map_name, position_in_row, wrapper_rect, min_row_height_):
        super().__init__("Create new map", 0, wrapper_rect, min_row_height_)
        self.font = pygame.font.Font(None, 58)
        # Remove the unnecessary buttons
        del self.delete_button
        del self.edit_name_button
        del self.edit_map_button

        # Create a single "Create Map" button
        self.create_map_button = Button((wrapper_rect.left + wrapper_rect.width - 300, (position_in_row+1) * min_row_height_ +50, 150, 40),
                                        "Create Map", (0, 255, 0), 'Create Map', self)

    def draw(self, surface):
        map_name_text = self.font.render(self.map_name, True, self.text_color)
        screen.blit(map_name_text, (self.text_x, self.text_y))
        self.create_map_button.draw(surface)


class Button:
    def __init__(self, rect, label, button_color=(0, 0, 255), button_type=None, button_object=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.button_color = button_color
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.text_surface = self.font.render(self.label, True, self.text_color)
        self.text_x = self.rect.centerx - self.text_surface.get_width() / 2
        self.text_y = self.rect.centery - self.text_surface.get_height() / 2
        self.button_object = button_object
        self.button_type = button_type

    def draw(self, surface):
        # Draw the button's rectangle
        pygame.draw.rect(surface, self.button_color, self.rect)
        # Blit the text onto the surface
        surface.blit(self.text_surface, (self.text_x, self.text_y))

    def handle_event(self, event_):
        if event_.type == pygame.MOUSEBUTTONDOWN and event_.button == 1:
            mouse_x, mouse_y = event_.pos
            if self.rect.collidepoint(mouse_x, mouse_y):
                if self.button_type == 'Delete Map' and self.button_object is not None:
                    pass
                elif self.button_type == 'Edit Map' and self.button_object is not None:
                    pass
                elif self.button_type == 'Edit Map_Name' and self.button_object is not None:
                    pass
                elif self.button_type == 'Create Map' and self.button_object is not None:
                    pass

    #
    # showingMap1 = Selection_maps(currently_selected_maps[0],1, main_rect, min_row_height)
    # showingMap2 = Selection_maps(currently_selected_maps[1],2, main_rect, min_row_height)
    # showingMap3 = Selection_maps(currently_selected_maps[2],3, main_rect, min_row_height)
    #


def initialize_selected_maps(available_maps_, min_row_height_, amount_of_rows_):
    selected_maps_ = [CreateNewMap("Create NEW MAP", 0,main_rect,min_row_height_ )]
    if len(available_maps_) >= amount_of_rows_:
        amount_of_maps_to_add = amount_of_rows_
    else:
        amount_of_maps_to_add = len(available_maps_)
    for iterator_available_map in range(amount_of_maps_to_add):
        name = available_maps_[[iterator_available_map]]
        selected_maps_.append(SelectionMaps(name, iterator_available_map + 1, main_rect, min_row_height_))
    return selected_maps_


# big rectangle
# Rectangle for holding already existing maps
# Scroll bar
# create new map option at top
# some text

def draw_options_on_screen(currently_selected_maps_, min_row_height_, amount_of_rows_):
    pygame.draw.rect(screen, (255, 255, 255), main_rect)
    # Draw the divisions for the rows
    for i in range(1, amount_of_rows_):
        pygame.draw.line(screen, (0, 0, 0), (main_rect.left, main_rect.top + i * min_row_height_),
                         (main_rect.left + main_rect.width, main_rect.top + i * min_row_height_), 2)

    # if len(currently_selected_maps_) >= amount_of_rows_ - 1:  # -1 since the first is reseverd for the create empty map
    #     amount_of_maps_to_show = amount_of_rows_ - 1  #
    # else:
    #     amount_of_maps_to_show = len(currently_selected_maps_)

    for selected_map in currently_selected_maps_[0:amount_of_rows_]:

        selected_map.draw(screen)


def handle_clicking_on_options(currently_selected_maps_):
    pass


def choose_from_available_world_maps(currently_selected_maps_, min_row_height_, amount_of_rows_):
    draw_options_on_screen(currently_selected_maps_, min_row_height_, amount_of_rows_)
    handle_clicking_on_options(currently_selected_maps_)
    # load_selected_world_map()
    # create_new_empty_world_map()


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
# WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

TILE_SIZE_WORLD = 50
TILE_SIZE_EDITOR = 100
SCALES = (100, 100)
screen = pygame.display.set_mode([WIDTH, HEIGHT])
fps = 60
timer = pygame.time.Clock()
pygame.display.set_caption('World Map Editor')

parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLACEHOLDER_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join(parent_directory, 'Assets/Images/Backgrounds/PLACEHOLDER_STOCK_WATER.png')),
                                                (WIDTH, HEIGHT))
world_map_img_location = os.path.join(parent_directory, 'Assets/Images/World_Map_Static/')
# print(world_map_img_location)
img_scale_type_dict = check_and_load_image_dict(world_map_img_location)
map_array = create_map_from_images(img_scale_type_dict, HEIGHT, TILE_SIZE_EDITOR)

available_maps_location = os.path.join(parent_directory, 'Assets/Maps/World_Maps/')
available_maps = check_available_world_maps(available_maps_location)
print(available_maps)
editor_state = set_state_of_editor('world_map_selector')

main_rect = calculate_main_rect_editor()
AMOUNT_OF_ROWS_TO_SHOW = 4
MINIMAL_ROW_SIZE_IN_PIXELS = 160
min_row_height = max(MINIMAL_ROW_SIZE_IN_PIXELS, main_rect.height // AMOUNT_OF_ROWS_TO_SHOW)
amount_of_rows = math.ceil(main_rect.height / min_row_height)
currently_selected_maps = initialize_selected_maps(available_maps, min_row_height, amount_of_rows)
print(currently_selected_maps)

run = True
while run:
    timer.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False  # Exit the game when the Escape key is pressed

    if editor_state == 1:  # world_map_selector
        screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))
        choose_from_available_world_maps(currently_selected_maps, min_row_height, amount_of_rows)
        # load map to current map for editing


    elif editor_state == 3:  # opened loading menu
        pass  # keep
        draw_map_specific_background(background)
        draw_map_to_screen(map_array)
        draw_loading_menu_on_top_of_screen()
        allow_interaction_loading_menu()

    elif editor_state == 2:  # main editing mode:
        pass  # main code
        draw_map_specific_background(background)
        screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))
        draw_map_to_screen(map_array)
        allow_interaction_editor()

    # Update the display
    pygame.display.flip()
