
import cython
import os, time, pygame, json
from states.state import State
from states.title import Title



class Game:
    def __init__(self):
        pygame.init()
        self.GAME_W, self.GAME_H = 480, 270
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1920, 1080
        self.ratio_x, self.ratio_y = self.SCREEN_WIDTH//self.GAME_W, self.SCREEN_HEIGHT//self.GAME_H
        self.game_canvas = pygame.Surface((self.GAME_W, self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.running, self.playing = True, True
        self.actions = {"left": False, "right": False, "forward": False, "backward": False, "action1": False, "action2": False, "start": False, "left_click": False,
                        "f_anchor": False, "1": False, "2": False, "3": False, "4": False }
        self.dt, self.prev_time = 0, 0
        self.state_stack = []
        self.TILE_SIZE_WORLD = 100
        self.ZOOM_LEVEL = 2
        self.load_assets()
        self.load_states()



    def load_assets(self):
        self.parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.world_map_static_dir = os.path.join(self.parent_directory, 'Assets/Images/World_Map_Static/')
        self.world_map_tiles_dir = os.path.join(self.world_map_static_dir, "Tiles")
        self.world_map_assets_dir = os.path.join(self.world_map_static_dir, "Assets")

        ###/// refactor to over_world
        self.img_scale_type_dict = self.check_and_load_image_dict(self.world_map_static_dir)
        self.new_tile_size = self.TILE_SIZE_WORLD // self.ZOOM_LEVEL
        for item in self.img_scale_type_dict.values():
            if item["type"] == "asset":
                item["loaded_image"] = pygame.transform.scale(pygame.image.load(item["image"]).convert_alpha(),
                                                                  (self.new_tile_size * item["x_scale"],
                                                                   self.new_tile_size * item["y_scale"]))

            elif item["type"] == "tile":
                item["loaded_image"] = pygame.transform.scale(pygame.image.load(item["image"]).convert(),
                                                                  (self.new_tile_size * item["x_scale"],
                                                                   self.new_tile_size * item["y_scale"]))
        self.img_scale_type_dict = {int(v['id']): v for v in self.img_scale_type_dict.values()}

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()


    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_a:
                    self.actions['left'] = True
                if event.key == pygame.K_d:
                    self.actions['right'] = True
                if event.key == pygame.K_w:
                    self.actions['forward'] = True
                if event.key == pygame.K_s:
                    self.actions['backward'] = True
                if event.key == pygame.K_SPACE:
                    self.actions['start'] = True
                if event.key == pygame.K_f:
                    self.actions['f_anchor'] = True

                if event.key == pygame.K_1:
                    self.actions['1'] = True
                if event.key == pygame.K_2:
                    self.actions['2'] = True
                if event.key == pygame.K_3:
                    self.actions['3'] = True
                if event.key == pygame.K_4:
                    self.actions['4'] = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.actions['left'] = False
                if event.key == pygame.K_d:
                    self.actions['right'] = False
                if event.key == pygame.K_w:
                    self.actions['forward'] = False
                if event.key == pygame.K_s:
                    self.actions['backward'] = False
                if event.key == pygame.K_SPACE:
                    self.actions['start'] = False
                if event.key == pygame.K_f:
                    self.actions['f_anchor'] = False
                if event.key == pygame.K_1:
                    self.actions['1'] = False
                if event.key == pygame.K_2:
                    self.actions['2'] = False
                if event.key == pygame.K_3:
                    self.actions['3'] = False
                if event.key == pygame.K_4:
                    self.actions['4'] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.actions["left_click"] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.actions["left_click"] = False

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        # Render current state to the screen
        #self.game_canvas.blit()
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))
        pygame.display.flip()

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False

    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def draw_text(self, surface, text, color, x, y):
        self.font = pygame.font.Font(None, 36)
        text_surface = self.font.render(text, True, color)
        #text_surface.set_colorkey((0,0,0))
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)


    def check_and_load_image_dict(self,world_map_img_location_):
        filename = 'Dicts/main_image_world_map_dict.json'
        image_info = self.load_image_dict_from_json(filename)

        if image_info is not None:
            print("Image dictionary loaded.")
        else:
            print("Image dictionary does not exist. Creating a new one.")
            image_info = self.create_dict_of_dicts_from_load_images(world_map_img_location_)  # Call your function to create the dictionary

        self.update_dict_to_be_congruent_with_files(world_map_img_location_, image_info)
        self.save_image_dict_as_json(image_info, filename)

        return image_info

    def add_new_images_to_dict(self,world_map_img_location_, image_dict):
        unique_id = int(max(image_dict.keys()) if image_dict else 0)  # Find the highest unique ID)
        for root, dirs, files in os.walk(world_map_img_location_):
            for file in files:
                if file.endswith(".png") or file.endswith(".PNG"):
                    world_map_img_location_file = os.path.dirname(os.path.join(root, file))
                    image_name = os.path.splitext(file)  # Remove the file extension
                    img_info = self.create_dictionary_from_image_name(world_map_img_location_file, image_name)
                    # Check if the image is not in the dictionary, and add it with a new ID
                    if not any(
                            img_info["type"] == v["type"] and img_info["x_scale"] == v["x_scale"] and img_info["y_scale"] == v["y_scale"] and img_info[
                                "image"] ==
                            v["image"] for v in image_dict.values()):
                        unique_id += 1
                        img_info["id"] = unique_id
                        image_dict[unique_id] = img_info
        return image_dict

    def save_image_dict_as_json(self,image_info, filename):
        with open(filename, 'w') as file:
            json.dump(image_info, file)

    def load_image_dict_from_json(self, filename):
        if os.path.exists(filename):
            if os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    image_info = json.load(file)
                    return image_info

        return None

    def create_dict_of_dicts_from_load_images(self,world_map_img_location_):
        # Initialize an empty dictionary and a counter for unique IDs
        img_scale_type_dict_ = {}
        unique_id = 1
        # Iterate through all files in the specified directory and its subfolders
        for root, dirs, files in os.walk(world_map_img_location_):
            for file in files:
                if file.endswith(".png"):
                    world_map_img_location_file = os.path.dirname(os.path.join(root, file))
                    image_name = os.path.splitext(file)  # Remove the file extension
                    img_info = self.create_dictionary_from_image_name(world_map_img_location_file, image_name)

                    # Add the unique ID to the dictionary entry
                    img_info["id"] = unique_id
                    img_scale_type_dict_[unique_id] = img_info

                    # Increment the unique ID counter
                    unique_id += 1

        return img_scale_type_dict_

    def create_dictionary_from_image_name(self, world_map_img_location_file,
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

        # Create a dictionary with the extracted information
        image_info = {
            "image": image,
            "x_scale": x,
            "y_scale": y,
            "type": tile_type
        }

        return image_info

    def mark_deleted_images(self, world_map_img_location_, image_dict):
        for img_id, img_info in image_dict.items():
            image_path = img_info['image']
            # Check if the image file does not exist
            if not os.path.exists(image_path):
                img_info['type'] = 'DELETED'

        return image_dict

    def update_dict_to_be_congruent_with_files(self, world_map_img_location_, image_info):
        image_info = self.add_new_images_to_dict(world_map_img_location_, image_info)
        image_info = self.mark_deleted_images(world_map_img_location_, image_info)
        return image_info

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()
