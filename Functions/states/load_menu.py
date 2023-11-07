import pygame, os, json
from states.state import State
from states.over_world import OverWorld

class LoadMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_save_games()
        self.create_menu_options()


    def update(self, delta_time, actions):
        if actions["left_click"]:
            self.determine_clicked_option()
        self.game.reset_keys()

    def render(self, display):
        display.fill((0, 0, 0))
        for menu in self.menu_choices:
            # pygame.draw.rect(display, (20,30,40) , menu.rect)
            display.blit(menu.text_surface, menu.rect)

    def transition_state(self):
        new_state = OverWorld(self.game, self.selected_option )
        new_state.enter_state()
        pass


    def determine_clicked_option(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_x // self.game.ratio_x, mouse_y // self.game.ratio_x
        for choice in self.menu_choices:
            if choice.rect.collidepoint(mouse_x, mouse_y):
                self.selected_option = choice.save_dict
                self.transition_state()

    def create_menu_options(self):
        self.menu_choices = []
        for number, option in self.menu_options.items():
            x = self.game.GAME_W * 0.4
            y = self.game.GAME_H * 0.05 + number * self.game.GAME_H * 0.2
            width = self.game.GAME_W * 0.4
            height = self.game.GAME_H * 0.05
            self.menu_choices.append(SaveChoice(x, y, width, height,option))


    def load_save_games(self):
        self.menu_options = {}
        counter = 0
        save_dir = os.path.join(self.game.parent_directory, "Assets", "Saves")
        for filename in os.listdir(save_dir):
            filepath = os.path.join(save_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".json"):
                with open(filepath, "r") as json_file:
                    data = json.load(json_file)
                    self.menu_options[counter] = data
                counter += 1


class SaveChoice:
    def __init__(self,  x, y, width, height, save_dict):
        self.text_color = (255, 0, 0)
        self.rect = pygame.Rect(x, y, width, height)
        self.save_dict = save_dict
        self.label = save_dict["image"]
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.label, True, self.text_color)


