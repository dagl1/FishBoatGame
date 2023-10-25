import pygame
import numpy as np
import os
import math
import json
import time
from datetime import datetime




def create_dictionary_from_image_name(world_map_img_location_file,
                                      image_name):  # this dict will include a picture and a tuple, tuple will contain image, x, y scaling, and the type defind by
    # the image name
    # Split the image name based on underscores

    parts = image_name[0].split("_")

    if len(parts) != 7:
        raise ValueError("Invalid image name format: " + image_name[0])

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
    def __init__(self, map_name, position_in_row, wrapper_rect, min_row_height_, current_objects):
        self.map_name = map_name
        self.text_x = wrapper_rect.left + (wrapper_rect.width - 300) // 2
        self.text_y = wrapper_rect.top + position_in_row * min_row_height_ + 20
        self.delete_button = Button((wrapper_rect.left + wrapper_rect.width - 100, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                    "Delete", (255, 0, 0), 'Delete Map', self, current_objects)
        self.edit_name_button = Button((wrapper_rect.left + wrapper_rect.width - 220, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                       "Edit Map", (0, 255, 0), 'Edit Map', self, current_objects)
        self.edit_map_button = Button((wrapper_rect.left + wrapper_rect.width - 240, (position_in_row + 1) * min_row_height_ - 40, 100, 40),
                                      "Change Name", (0, 0, 255), 'Edit Map_Name', self, current_objects)
        self.font = pygame.font.Font(None, 36)
        self.text_color = (0, 0, 0)
        # self.preview_selection = preview_selection

    def draw(self, surface):
        map_name_text = self.font.render(self.map_name, True, self.text_color)
        surface.blit(map_name_text, (self.text_x, self.text_y))
        self.delete_button.draw(surface)
        self.edit_name_button.draw(surface)
        self.edit_map_button.draw(surface)

    def handle_event(self, event_):
        self.delete_button.handle_event(event_)
        self.edit_name_button.handle_event(event_)
        self.edit_map_button.handle_event(event_)



class CreateNewMap(SelectionMaps):
    def __init__(self, map_name, position_in_row, wrapper_rect, min_row_height_,current_objects):
        super().__init__("Create new map", 0, wrapper_rect, min_row_height_, current_objects)
        self.font = pygame.font.Font(None, 58)
        # Remove the unnecessary buttons
        del self.delete_button
        del self.edit_name_button
        del self.edit_map_button

        # Create a single "Create Map" button
        self.create_map_button = Button((wrapper_rect.left + wrapper_rect.width - 300, (position_in_row+1) * min_row_height_ +50, 150, 40),
                                        "Create Map", (0, 255, 0), 'Create Map', self,current_objects)

    def draw(self, surface):
        map_name_text = self.font.render(self.map_name, True, self.text_color)
        surface.blit(map_name_text, (self.text_x, self.text_y))
        self.create_map_button.draw(surface)

    def handle_events(self,event_):
        self.create_map_button.handle_event(event_)


class Button:
    def __init__(self, rect, label, button_color=(0, 0, 255), button_type=None, button_object=None, current_objects=None):
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
        self.current_objects = current_objects
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
                    set_state_of_editor('change map name popup')
                    create_popup_change_name_menu()
                    print('button pressed')

                elif self.button_type == 'Create Map' and self.button_object is not None:
                    print('button Create Map pressed')
                    self.current_objects.load_empty_map_to_current()

    #
    # showingMap1 = Selection_maps(currently_selected_maps[0],1, main_rect, min_row_height)
    # showingMap2 = Selection_maps(currently_selected_maps[1],2, main_rect, min_row_height)
    # showingMap3 = Selection_maps(currently_selected_maps[2],3, main_rect, min_row_height)
    #
def create_popup_change_name_menu():
    pass

class PopUpScreen:
    def __init__(self):
        pass

class MapSelectionOptions:
    def __init__(self, min_row_height_, amount_of_rows_, main_rect_, color=(255, 255, 255),current_objects = None):
        self.min_row_height_ = min_row_height_
        self.amount_of_rows_ = amount_of_rows_
        self.main_rect_ = main_rect_
        self.color = color
        self.current_objects = current_objects

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.main_rect_)
        for i in range(1, self.amount_of_rows_):
            pygame.draw.line(surface, (0, 0, 0), (self.main_rect_.left, self.main_rect_.top + i * self.min_row_height_),
                             (self.main_rect_.left + self.main_rect_.width, self.main_rect_.top + i * self.min_row_height_), 2)

    def handle_events(self, event_):
        pass

class WorldMap:

    def __init__(self, current_object,image_dict):
        self.size = None
        self.name = None
        self.last_edited = None
        self.time_created = None
        self.tile_map = None
        self.asset_map = None
        self.current_object = current_object
        self.image_dict = image_dict
        self.grid_portion_on_screen = np.zeros((1,1))
        self.xbounds = slice(1,2)
        self.ybounds = slice(1,2)

        self.new_tile_size = TILE_SIZE_WORLD // self.current_object.location_of_screen_on_map_and_zoom_level[2]
        self.amount_of_tiles_shown_on_screen_width = math.floor(WIDTH//self.new_tile_size)
        self.amount_of_tiles_shown_on_screen_height = math.floor(HEIGHT//self.new_tile_size)

    def create_empty_world_map(self, name="New Map", size=(10240, 10240)):
        self.size = size
        self.name = name
        self.last_edited =  datetime.now().strftime("%d/%m/%Y %H:%M:%S") # placeholder
        self.time_created = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.tile_map = np.zeros(self.size)
        self.asset_map = np.zeros(self.size)

    def load_world_map_from_json(self, location_):
        pass
        ## This function requires some changes to how things are shown/saved, which requires modification of how the availalbe maps are loaded
        # In particular, the buttons, and therefore the maps,  need to have both the name and the path of the map separately accesible
        # location_ = location_ + self.name  + ".json"
        # with open(location_, 'r') as json_file:
        #     data = json.load(json_file)
        #     self.size = tuple(data['size'])
        #     self.name = data['name']
        #     self.last_edited = data['last_edited']
        #     self.time_created = data['time_created']
        #     self.tile_map = np.array(data['tile_map'])
        #     self.asset_map = np.array(data['asset_map'])

    def save_world_map_to_json(self, location_):
        location_ = location_ + self.name + ".json"
        data = {
            'size': list(self.size),
            'name': self.name,
            'last_edited': self.last_edited,
            'time_created': self.time_created,
            'tile_map': self.tile_map.tolist(),
            'asset_map': self.asset_map.tolist()
        }

        with open(location_, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    def draw(self,surface):

        pass

    def load_objects_to_currently_drawn_map(self, tile_coordinates):

        pass

    def unload_objects_from_currently_drawn_map(self, tile_coordinates):
        pass

    def update_loaded_objects_in_currently_drawn_map(self):
        #check which tiles to add
        #check which tiles to remove
        self.load_tiles_to_currently_drawn_map()
        self.unload_tiles_from_currently_drawn_map()
        pass

    def define_bounds_of_currently_drawn_map(self): # initalize the current grid (also used when zoom level is changed
        self.new_tile_size = TILE_SIZE_WORLD // self.current_object.location_of_screen_on_map_and_zoom_level[2]
        self.amount_of_tiles_shown_on_screen_width = math.floor(WIDTH // self.new_tile_size)
        self.amount_of_tiles_shown_on_screen_height = math.floor(HEIGHT // self.new_tile_size)

        x, y, width, height = self.calculate_bounds()
        # Create xbounds and ybounds
        self.xbounds = slice(x, x + width)
        self.ybounds = slice(y, y + height)


        self.load_objects_to_currently_drawn_map((self.xbounds,self.ybounds)) ## Initialize the tiles/objects

    def calculate_bounds(self):
        x = self.current_object.location_of_screen_on_map_and_zoom_level[0]
        y = self.current_object.location_of_screen_on_map_and_zoom_level[1]
        width = self.amount_of_tiles_shown_on_screen_width
        height = self.amount_of_tiles_shown_on_screen_height

        return x, y, width, height
    def update_map_bounds(self):

        xchange = self.location_of_screen_on_map_and_zoom_level[0] - self.OLD_location_of_screen_on_map_and_zoom_level[0]
        ychange = self.location_of_screen_on_map_and_zoom_level[1] - self.OLD_location_of_screen_on_map_and_zoom_level[1]

        if xchange != 0:
            if xchange > 0:
                new_colums_x = slice(xchange+self.xbounds.stop, xchange+self.xbounds.stop+1)
                to_remove_columns_x = slice(xchange+self.xbounds.start, xchange+self.xbounds.start+1)
            elif xchange < 0:
                new_colums_x = slice(self.xbounds.start + xchange , self.xbounds.start + xchange + 1)
                to_remove_columns_x = slice(self.xbounds.stop + xchange,  self.xbounds.stop + xchange + 1)
            new_columns = (new_colums_x, self.ybounds)
            to_remove_columns = (to_remove_columns_x, self.ybounds)

            self.load_objects_to_currently_drawn_map(new_columns)
            self.unload_objects_from_currently_drawn_map(to_remove_columns)
            self.xbounds = slice(self.xbounds.start + xchange,self.xbounds.stop + xchange)

        if ychange != 0:
            if ychange > 0:
                new_rows_y = slice(self.ybounds.start, self.ybounds.stop + ychange)
                to_remove_rows_y = slice(self.ybounds.start, self.ybounds.start + ychange)
            elif ychange < 0:
                new_rows_y = slice(self.ybounds.start + ychange, self.ybounds.stop)
                to_remove_rows_y = slice(self.ybounds.stop + ychange, self.ybounds.stop)
            new_rows = (self.xbounds, new_rows_y)
            to_remove_rows = (self.xbounds, to_remove_rows_y)

            self.load_objects_to_currently_drawn_map(new_rows)
            self.unload_objects_from_currently_drawn_map(to_remove_rows)
            self.ybounds = slice(self.ybounds.start + xchange, self.ybounds.stop + xchange)











class CurrentObjects:
    def __init__(self, available_maps_, min_row_height_, amount_of_rows_):
        self.selected_maps = self.initialize_selected_maps(available_maps_, min_row_height_, amount_of_rows_)
        self.currently_interatable_objects = self.selected_maps
        self.currently_drawn_objects = self.selected_maps
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        self.background = PLACEHOLDER_BACKGROUND
        self.run = True
        self.editor_state = 1
        self.location_of_screen_on_map_and_zoom_level = (3000, 3000, 5) #5 is regular zoom, will move log2() up or down (so 4 is zoom level shows twice as much).
        self.OLD_location_of_screen_on_map_and_zoom_level = (3000, 3000, 5) #zoom of 5 means that the regular tile size is 5 times smaller than what it will be


    def add_to_drawn_objects_list(self, object_to_add, put_to_front=False):
        if put_to_front:
            self.currently_drawn_objects.insert(0, object_to_add)
        else:
            self.currently_drawn_objects.append(object_to_add)

    def add_to_interactable_list_list(self, object_to_add, put_to_front=False):
        if put_to_front:
            self.currently_interatable_objects.insert(0, object_to_add)
        else:
            self.currently_interatable_objects.append(object_to_add)

    def perform_loop_actions(self):  # checks the currently drawn and interactable objects and runs their draw and handle_events code
        self.screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.run = False  # Exit the game when the Escape key is pressed
            for interactable in self.currently_interatable_objects:
                interactable.handle_events(event)

        for drawable in self.currently_drawn_objects:
            drawable.draw(self.screen)

    def initialize_selected_maps(self,available_maps_, min_row_height_, amount_of_rows_):
        selected_maps_ = [CreateNewMap("Create NEW MAP", 0,main_rect,min_row_height_ ,self)]
        if len(available_maps_)>0:
            for iterator_available_map in range(amount_of_rows_-1):
                if len(available_maps_) <= iterator_available_map:
                    name = available_maps_[iterator_available_map]
                    selected_maps_.append(SelectionMaps(name, iterator_available_map + 1, main_rect, min_row_height_, self))
        return selected_maps_

    def load_empty_map_to_current(self):
        print('dddd')


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
fps = 60
timer = pygame.time.Clock()
pygame.display.set_caption('World Map Editor')

parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
world_map_img_location = os.path.join(parent_directory, 'Assets/Images/World_Map_Static/')
available_maps_location = os.path.join(parent_directory, 'Assets/Maps/World_Maps/')

img_scale_type_dict = check_and_load_image_dict(world_map_img_location)
map_array = create_map_from_images(img_scale_type_dict, HEIGHT, TILE_SIZE_EDITOR)
available_maps = check_available_world_maps(available_maps_location)

PLACEHOLDER_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join(parent_directory, 'Assets/Images/Backgrounds/PLACEHOLDER_STOCK_WATER.png')),
                                                (WIDTH, HEIGHT))
main_rect = calculate_main_rect_editor()

AMOUNT_OF_ROWS_TO_SHOW = 4
MINIMAL_ROW_SIZE_IN_PIXELS = 157
min_row_height = max(MINIMAL_ROW_SIZE_IN_PIXELS, main_rect.height // AMOUNT_OF_ROWS_TO_SHOW)
amount_of_rows = math.floor(main_rect.height / min_row_height)

main_current_object = CurrentObjects(available_maps, min_row_height, amount_of_rows)
main_current_object.add_to_drawn_objects_list(MapSelectionOptions(min_row_height,amount_of_rows,main_rect),True,)



run = True
while main_current_object.run:
    timer.tick(fps)
    main_current_object.perform_loop_actions()





    # if editor_state == 1:  # world_map_selector
    #     screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))
    #     choose_from_available_world_maps(currently_selected_maps, min_row_height, amount_of_rows)
    #     # load map to current map for editing
    #
    #
    # elif editor_state == 3:  # opened loading menu
    #     pass  # keep
    #     draw_map_specific_background(background)
    #     draw_map_to_screen(map_array)
    #     draw_loading_menu_on_top_of_screen()
    #     allow_interaction_loading_menu()
    #
    # elif editor_state == 2:  # main editing mode:
    #     pass  # main code
    #     draw_map_specific_background(background)
    #     screen.blit(PLACEHOLDER_BACKGROUND, (0, 0))
    #     draw_map_to_screen(map_array)
    #     allow_interaction_editor()

    # Update the display
    pygame.display.flip()
