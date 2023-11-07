import pygame, os
from states.state import State
from states.load_menu import LoadMenu
from states.over_world import OverWorld


class SelectMenu(State):

    def __init__(self, game):
        State.__init__(self, game)
        self.menu_options = {0: "New Game", 1: "Load Game", 2: "Options", 3: "Exit"}
        self.create_menu_options()

    def update(self, delta_time, actions):
        if actions["left_click"]:
            self.determine_clicked_option()
        if actions["1"]:
            self.selected_option = "New Game"
            self.transition_state()
        if actions["2"]:
            self.selected_option = "Load Game"
            self.transition_state()
        if actions["3"]:
            self.selected_option = "Options"
            self.transition_state()
        if actions["4"]:
            self.selected_option = "Exit"
            self.transition_state()


        self.game.reset_keys()

    def render(self, display):
        display.fill((0, 0, 0))
        for menu in self.menu_choices:
           # pygame.draw.rect(display, (20,30,40) , menu.rect)
            display.blit(menu.text_surface, menu.rect)


    def transition_state(self):
        if self.selected_option == "New Game":
            new_state = OverWorld(self.game, None)
            new_state.enter_state()
        elif self.selected_option == "Load Game":
            new_state = LoadMenu(self.game)
            new_state.enter_state()
            pass  # TO-DO
        elif self.selected_option == "Options":
            pass  # TO-DO
        elif self.selected_option == "Exit":
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()

    def determine_clicked_option(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_x // self.game.ratio_x, mouse_y // self.game.ratio_x
        for choice in self.menu_choices:
            if choice.rect.collidepoint(mouse_x, mouse_y):
                self.selected_option = choice.label
                self.transition_state()

    def create_menu_options(self):
        self.menu_choices = []
        for number, option in self.menu_options.items():
            x = self.game.GAME_W * 0.4
            y = self.game.GAME_H * 0.2 + number * self.game.GAME_H * 0.2
            label = option
            width = self.game.GAME_W * 0.4
            height = self.game.GAME_H * 0.2
            self.menu_choices.append(MenuChoice(label, x, y, width, height))


class MenuChoice:
    def __init__(self, label, x, y, width, height):
        self.text_color = (255, 0, 0)
        self.rect = pygame.Rect(x, y, width, height, )
        self.label = label
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.label, True, self.text_color)
