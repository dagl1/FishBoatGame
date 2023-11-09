import pygame, os, json, math
from states.state import State
import numpy as np
import copy

class OverWorld(State):
    def __init__(self, game, save_file):
        State.__init__(self, game)

        #add in loading screen
        game.game_canvas.fill((255, 255, 255))
        self.game.draw_text(game.game_canvas, "LOADING", (0, 0, 0), self.game.GAME_W / 2, self.game.GAME_H / 2)
        game.screen.blit(pygame.transform.scale(game.game_canvas, (game.SCREEN_WIDTH, game.SCREEN_HEIGHT)), (0, 0))
        pygame.display.flip()
        self.save_file = save_file
        self.load_game_settings()
        self.load_map_to_world()
        self.tile_size = self.game.new_tile_size
        self.collision_class = CollisionMapping(self, False)
    def update(self, delta_time, actions):
        self.player.update(delta_time, actions,self)

    def load_game_settings(self):
        if self.save_file is not None:
            self.load_game_settings_from_save()
        else:
            # is new save, create new player/boat char with default start settings
            self.save_file = {}
            self.player = PlayerBoat(self.game)

    def load_game_settings_from_save(self):
        ### load in player settings
        self.player = PlayerBoat(self.game)


    def render(self, display):
        display.fill((0, 0, 0))
        self.draw_static_images_over_world(display)
        # for rect_ in self.collision_rectangles:
        #     pygame.draw.rect(display, (255,255,255), rect_ )
        self.player.render(display)

    def load_map_to_world(self):
        map_file = os.path.join(self.game.parent_directory, "Assets", "Maps", "World_Maps", "Main_Map.json")
        with open(map_file, "r") as json_file:
            data = json.load(json_file)
            self.tile_map = np.array(data['tile_map'])
            self.asset_map = np.array(data['asset_map'])

    def draw_static_images_over_world(self, display):
        begin_x = (self.player.x_position - 0.5 * self.game.GAME_W) #+ 8 * self.tile_size
        begin_y = (self.player.y_position - 0.5 * self.game.GAME_H) #+  8 * self.tile_size
        end_x = begin_x + self.game.GAME_W + 4 * self.tile_size
        end_y = begin_y + self.game.GAME_H + 4 * self.tile_size
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
    def __init__(self,game, x=3300, y=3000, money=0, fishies=0):
        self.x_position = x
        self.y_position = y
        self.money = money
        self.fishies = fishies
        self.direction = 0
        self.xy_vector = (1,0)
        self.direction_vertical_bool = False


        ### set game settings
        self.game = game
        self.acceleration_factor = 60
        self.max_speed = 1200
        self.max_speed_backwards = self.max_speed / 2
        self.size = (30, 15)
        self.turn_speed = 60
        self.current_speed = 0
        self.boat_image_original = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join(
            self.game.parent_directory, "Assets", "Images", "Dynamic assets", "Boat", "wm_p_asset_boat_collide_001_1_2.PNG")).convert_alpha(),
                                                 (1*self.game.new_tile_size, 2*self.game.new_tile_size)), 90)
        self.boat_image = pygame.transform.rotate(self.boat_image_original, -self.direction )
        self.boat_collision_rect = self.boat_image_original.get_rect(center =(self.x_position, self.y_position))
        self.current_frame, self.last_frame_time = 0, 0
        self.boat_rect = self.boat_image.get_rect(center=(self.game.GAME_W // 2, self.game.GAME_H // 2))

    def render(self, display):

        display.blit(self.boat_image, self.boat_rect)

    def update(self,delta_time, actions, over_world):
        self.boat_collision_rect = self.boat_image_original.get_rect(center =(self.x_position, self.y_position))
        self.move_based_on_acceleration(delta_time,over_world)

        if actions[ "forward"] == True:
            self.accelerate_forward(delta_time)

        if actions[ "backward"] == True:
            self.accelerate_backward(delta_time)

        if actions[ "left"] == True:
            self.direction = (self.direction - self.turn_speed * delta_time) % 360
            self.calculate_xy_vector()
            self.boat_image = pygame.transform.rotate(self.boat_image_original, -self.direction )

        if actions[ "right"] == True:
            self.direction = (self.direction + self.turn_speed * delta_time) % 360
            self.calculate_xy_vector()
            self.boat_image = pygame.transform.rotate(self.boat_image_original, -self.direction)

        if actions["f_anchor"] == True:
            self.stop_by_anchor(delta_time)
        self.ship_bobble_on_sea_animation(delta_time)

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


    def move_based_on_acceleration(self, delta_time,over_world):

        self.x_position = self.x_position + self.current_speed * delta_time * self.xy_vector[0]
        self.y_position = self.y_position + self.current_speed * delta_time * self.xy_vector[1]
        self.x_position = self.x_position % (len(over_world.tile_map) * over_world.tile_size)
        self.y_position = self.y_position % (len(over_world.tile_map[0]) * over_world.tile_size)
        self.collision_detection(delta_time,over_world)

    def collision_detection(self,delta_time,over_world):

        if self.boat_collision_rect.collidelist(over_world.collision_rectangles) != -1:

            if self.current_speed >0:
                self.x_position -= 15 * self.xy_vector[0]
                self.y_position -= 15 * self.xy_vector[1]
            else:
                self.x_position += 15 * self.xy_vector[0]
                self.y_position += 15 * self.xy_vector[1]

            self.current_speed = -self.current_speed * 0.1
            self.x_position = self.x_position + self.current_speed * delta_time * self.xy_vector[0]
            self.y_position = self.y_position + self.current_speed * delta_time * self.xy_vector[1]
            self.x_position = self.x_position % (len(over_world.tile_map) * over_world.tile_size)
            self.y_position = self.y_position % (len(over_world.tile_map[0]) * over_world.tile_size)
        # # for rectangle in  over_world.collision_rectangles:
        #     if rectangle.colliderect(self.boat_rect):
        #         print('colliding')


    def ship_bobble_on_sea_animation(self,delta_time):
        self.last_frame_time +=delta_time
        TIME_FOR_ANIMATION = 1
        frames = [self.boat_image.get_rect(center=(self.game.GAME_W // 2, self.game.GAME_H // 2)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+2)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+4)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+6)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+6)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+4)),
                  self.boat_image.get_rect(center=(self.game.GAME_W // 2, (self.game.GAME_H // 2)+2))]
        time_per_frame = TIME_FOR_ANIMATION/len(frames)
        if self.last_frame_time > time_per_frame:
            self.last_frame_time = 0
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.boat_rect = frames[self.current_frame]



    ### TODO
    # COLLISION MAPPING in OVERWORLD
    # when collide, set accel to 0, speed to opposite *0.1
    # ship loading
    # ship animation
    # change naming convention to include sea/land for collision map


class CollisionMapping:

    def __init__(self, over_world, create_new_mapping=False):
        self.over_world = over_world
        if create_new_mapping:
            self.create_rectangles_for_collision()
            self.save_collision_map()

        elif create_new_mapping == False:
            self.load_collision_map()
            self.over_world.collision_rectangles = [None] * len(self.array_with_rectangles)
            # create the actual pygamme rectangles
            for index, rectangle in enumerate(self.array_with_rectangles):
                if rectangle != []:
                    x_pos = (rectangle[0][0]) * self.over_world.tile_size
                    y_pos = (rectangle[1][0]) * self.over_world.tile_size
                    x_width = (rectangle[0][1] - rectangle[0][0]) * self.over_world.tile_size
                    y_height = (rectangle[1][1] - rectangle[1][0]) * self.over_world.tile_size
                    self.over_world.collision_rectangles[index] = pygame.Rect((x_pos, y_pos, x_width, y_height))

    def maxHist(self, row):
        # Create an empty stack. The stack holds
        # indexes of hist array / The bars stored
        # in stack are always in increasing order
        # of their heights.
        result = []

        # Top of stack
        top_val = 0

        # Initialize max area in current
        max_area = 0
        # row (or histogram)
        highest_top_val = 0
        area = 0  # Initialize area with current top
        # Run through all bars of given
        # histogram (or row)
        i = 0
        while (i < len(row)):
            # If this bar is higher than the
            # bar on top stack, push it to stack
            if (len(result) == 0) or (row[result[-1]] <= row[i]):
                result.append(i)
                i += 1
            else:
                # If this bar is lower than top of stack,
                # then calculate area of rectangle with
                # stack top as the smallest (or minimum
                # height) bar. 'i' is 'right index' for
                # the top and element before top in stack
                # is 'left index'
                top_val = row[result.pop()]
                area = top_val * i

                if (len(result)):
                    area = top_val * (i - result[-1] - 1)
                if area >= max_area:
                    max_area = max(area, max_area)
                    highest_top_val = top_val

        # Now pop the remaining bars from stack
        # and calculate area with every popped
        # bar as the smallest bar
        # print(result, max_area)
        # topvals = []
        while (len(result)):
            top_val = row[result.pop()]
            area = top_val * i
            if (len(result)):
                area = top_val * (i - result[-1] - 1)

            if area >= max_area:
                max_area = max(area, max_area)
                highest_top_val = top_val
        return max_area, highest_top_val

        # Returns area of the largest rectangle

    # with all 1s in A
    def maxRectangle(self, A_original):
        A = copy.deepcopy(A_original)
        # Calculate area for first row and
        # initialize it as result
        result, highest_top_val = self.maxHist(A[0])
        largest_row_i = 0
        # print(result)
        # iterate over row to find maximum rectangular
        # area considering each row as histogram
        for i in range(1, len(A)):
            for j in range(len(A[i])):

                # if A[i][j] is 1 then add A[i -1][j]
                if (A[i][j]):
                    A[i][j] += A[i - 1][j]

            # Update result if area with current
            # row (as last row) of rectangle) is more
            if result > self.maxHist(A[i])[0]:
                pass
            elif self.maxHist(A[i])[0] > result:
                result, highest_top_val = self.maxHist(A[i])
                largest_row_i = i

        if highest_top_val == 0:
            slices = []
            pass
        else:
            indices = []
            for col, value in enumerate(A[largest_row_i]):
                if value >= highest_top_val:
                    indices.append(col)

            contiguous_indices = self.find_largest_contiguous_set(indices)
            slices = [(largest_row_i - highest_top_val + 1, largest_row_i + 1), (min(contiguous_indices), max(contiguous_indices) + 1)]
        return slices

    def perform_largest_rectangle_iteratively_per_unique_number(self, array_2d):
        rectangles = []
        slices_rectangle = self.maxRectangle(array_2d)
        rectangles += [slices_rectangle]
        if slices_rectangle != []:
            array_2d[slices_rectangle[0][0]:slices_rectangle[0][1], slices_rectangle[1][0]:slices_rectangle[1][1]] = 0

        while sum(element for subarray in array_2d for element in subarray) > 0:

            slices_rectangle = self.maxRectangle(array_2d)
            rectangles += [slices_rectangle]

            if slices_rectangle != []:
                array_2d[slices_rectangle[0][0]:slices_rectangle[0][1], slices_rectangle[1][0]:slices_rectangle[1][1]] = 0

        return rectangles

    def perform_largest_rectangle_iteratively(self, array_2d):
        array_with_rectangles = []
        A = copy.deepcopy(array_2d)

        array_with_rectangles += self.perform_largest_rectangle_iteratively_per_unique_number(A)
        # print(array_with_rectangles)
        return array_with_rectangles

    def find_largest_contiguous_set(self, arr):
        if arr != []:

            end = 0
            longest_set_current = 1
            still_walking_set = False
            longest_set_final = 1
            start_final = 0
            end_final = 1

            for y in range(1, len(arr)):
                if arr[y] == arr[y - 1] + 1:
                    end = y
                    longest_set_current += 1
                    still_walking_set = True
                else:
                    if still_walking_set:
                        still_walking_set = False
                        if longest_set_current > longest_set_final:
                            longest_set_final = longest_set_current
                            start_final = y - longest_set_final
                            end_final = y
                        longest_set_current = 1

            if still_walking_set:
                if longest_set_current > longest_set_final:
                    longest_set_final = longest_set_current
                    start_final = 1 + y - longest_set_final
                    end_final = y + 1

            return arr[start_final:end_final]
        else:
            return []

    def create_collision_map(self):
        self.collision_map = np.zeros_like(self.over_world.tile_map)
        for x in range(len(self.over_world.tile_map)):
            for y in range(len(self.over_world.tile_map[x])):
                value_tile = self.over_world.tile_map[x][y]
                value_asset = self.over_world.asset_map[x][y]
                if value_tile != 0 and self.over_world.game.img_scale_type_dict[value_tile]["collide"]:
                    self.collision_map[x][y] = 1

                if value_asset != 0 and self.over_world.game.img_scale_type_dict[value_asset ]["collide"]:
                    self.collision_map[x][y] = 1

    def create_rectangles_for_collision(self):
        # calculate rectangle positions
        self.create_collision_map()
        self.array_with_rectangles = self.perform_largest_rectangle_iteratively(self.collision_map)

        self.over_world.collision_rectangles = [None] * len(self.array_with_rectangles)
        # create the actual pygamme rectangles
        for index, rectangle in enumerate(self.array_with_rectangles):
            if rectangle != []:
                x_pos = (rectangle[1][0]) * self.over_world.tile_size
                y_pos = (rectangle[0][0]) * self.over_world.tile_size
                x_width = (rectangle[1][1] - rectangle[1][0]) * self.over_world.tile_size
                y_height = (rectangle[0][1] - rectangle[0][0]) * self.over_world.tile_size
                self.over_world.collision_rectangles[index] = pygame.Rect((x_pos, y_pos, x_width, y_height))

    def load_collision_map(self):
        map_file = os.path.join(self.over_world.game.parent_directory, "Functions", "Dicts", "Main_Map_Collision_Rectangles.json")
        with open(map_file, "r") as json_file:
            data = json.load(json_file)
            # Convert lists back to tuples
            self.array_with_rectangles = [
                [tuple(lst) for lst in arr]
                for arr in data
            ]

    def save_collision_map(self):
        array_with_rectangles = self.array_with_rectangles
        serializable_data = [
            [list(t) for t in arr]
            for arr in array_with_rectangles
        ]
        new_list = [[[int(item) for item in subsublist] for subsublist in sublist] for sublist in serializable_data]
        map_file = os.path.join(self.over_world.game.parent_directory, "Functions", "Dicts", "Main_Map_Collision_Rectangles.json")
        with open(map_file, 'w') as file:
            json.dump(new_list, file)
