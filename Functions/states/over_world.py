import pygame, os, json, math
from states.state import State
import numpy as np

class OverWorld(State):
    def __init__(self, game, save_file):
        State.__init__(self, game)
        self.save_file = save_file
        self.load_game_settings()
        self.load_map_to_world()
        self.tile_size = 50

    def update(self, delta_time, actions):
        self.player.update(delta_time, actions)

    def load_game_settings(self):
        if self.save_file is not None:
            self.load_game_settings_from_save()
        else:
            # is new save, create new player/boat char with default start settings
            self.save_file = {}
            self.player = PlayerBoat()

    def load_game_settings_from_save(self):
        ### load in player settings
        self.player = PlayerBoat()


    def render(self, display):
        display.fill((0, 0, 0))
        self.draw_static_images_over_world(display)

    def load_map_to_world(self):
        map_file = os.path.join(self.game.parent_directory, "Assets", "Maps", "World_Maps", "Main_Map.json")
        with open(map_file, "r") as json_file:
            data = json.load(json_file)
            self.tile_map = np.array(data['tile_map'])
            self.asset_map = np.array(data['asset_map'])

    def draw_static_images_over_world(self, display):
        begin_x = (self.player.x_position - 0.5 * self.game.GAME_W) - 4 * self.tile_size
        begin_y = (self.player.y_position - 0.5 * self.game.GAME_H) - 4 * self.tile_size
        end_x = begin_x + self.game.GAME_W + 4 * self.tile_size
        end_y = begin_y + self.game.GAME_W + 4 * self.tile_size
        begin_grid_x = math.floor(begin_x / self.tile_size)
        begin_grid_y = math.floor(begin_y / self.tile_size)
        end_grid_x = math.floor(end_x / self.tile_size)
        end_grid_y = math.floor(end_y / self.tile_size)
        offset_x = begin_x % self.tile_size
        offset_y = begin_y % self.tile_size

        for index_x, x in enumerate(range(begin_grid_x,end_grid_x)):
            for index_y, y in enumerate(range(begin_grid_y,end_grid_y)):
                x = x %len(self.tile_map)
                y = y %len(self.tile_map[x])
                value = self.tile_map[x][y]
                value_asset = self.asset_map[x][y]
                if value != 0:
                    display.blit(self.game.img_scale_type_dict[value]["loaded_image"], (index_x * self.tile_size - offset_x, index_y * self.tile_size - offset_y))
                if value_asset != 0:
                    display.blit(self.game.img_scale_type_dict[value_asset]["loaded_image"],
                                 (index_x * self.tile_size - offset_x, index_y * self.tile_size - offset_y))

        # # draw tiles based on stepsize


        # draw assets


class PlayerBoat:
    ### add in other things in inventory later
    def __init__(self, x=3000, y=3000, money=0, fishies=0):
        self.x_position = x
        self.y_position = y
        self.money = money
        self.fishies = fishies
        self.direction = 0
        self.xy_vector = (1,0)


        ### set game settings
        self.acceleration_factor = 60
        self.max_speed = 1200
        self.max_speed_backwards = self.max_speed / 2
        self.size = (30, 15)
        self.turn_speed = 60
        self.current_speed = 0

    def update(self,delta_time, actions):
        self.move_based_on_acceleration(delta_time)
        if actions[ "forward"] == True:
            self.accelerate_forward(delta_time)

        if actions[ "backward"] == True:
            self.accelerate_backward(delta_time)

        if actions[ "left"] == True:
            self.direction = (self.direction - self.turn_speed * delta_time) % 360
            self.calculate_xy_vector()

        if actions[ "right"] == True:
            self.direction = (self.direction + self.turn_speed * delta_time) % 360
            self.calculate_xy_vector()

        if actions["f_anchor"] == True:
            self.stop_by_anchor(delta_time)
    def calculate_xy_vector(self):
        x_vector = math.cos(math.radians(self.direction))
        y_vector = math.sin(math.radians(self.direction))
        self.xy_vector = (x_vector, y_vector)

    def accelerate_forward(self, delta_time):
        self.current_speed = self.current_speed + self.acceleration_factor * delta_time
        if self.current_speed >= self.max_speed:
            self.current_speed = self.max_speed

    def accelerate_backward(self, delta_time):
        self.current_speed = self.current_speed - self.acceleration_factor * delta_time
        if self.current_speed <= - self.max_speed_backwards:
            self.current_speed = - self.max_speed_backwards

    def stop_by_anchor(self, delta_time):
        if self.current_speed < - 10:
            self.current_speed = self.current_speed + 5 * self.acceleration_factor * delta_time

        elif self.current_speed > 10:
            self.current_speed = self.current_speed - 5 * self.acceleration_factor * delta_time
        else:
            self.current_speed = 0


    def move_based_on_acceleration(self, delta_time):

        self.x_position = self.x_position + self.current_speed * delta_time * self.xy_vector[0]
        self.y_position = self.y_position + self.current_speed * delta_time * self.xy_vector[1]




    def rotate_ship(self):
        pass
    def ship_animation_during_rotation(self):
        pass

    def ship_bobble_on_sea_animation(self):
        pass

    ### TODO
    # COLLISION MAPPING in OVERWORLD
    # when collide, set accel to 0, speed to opposite *0.1
    # ship loading
    # ship animation
    # change naming convention to include sea/land for collision map

