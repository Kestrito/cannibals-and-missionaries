import pygame
import sys
import asyncio

##Castaways/Passengers:
##0 - None
##1 - Cannibal
##2 - Missionary

##Sides:
##False - Left
##True - Right

##Game Flags:
##0 - Continue
##1 - Lost (Missionaries devoured on left side)
##2 - Lost (Missionaries devoured on right side)
##3 - Won

##Screens:
##0 - Home
##1 - Instructions
##2 - Game
##3 - Lost
##4 - Won

##Emotion flags:
##0 - Hungry (Cannibal) / Calm (Missionary)
##1 - Happy (Cannibal) / Devoured (Missionary)

class Screens:
    def __init__(self):
        self.game = Game(self)
        self.setup()

    ##Setup the game and go to home screen
    def setup(self):
        self.game.setup()
        self.home()

    def home(self):
        self.screen = 0

    ##Go to instructions screen
    def instructions(self):
        self.screen = 1

    ##Start game
    def start(self):
        self.game.start()
        self.screen = 2

    ##Losing screen
    def lost(self):
        self.screen = 3

    ##Winning screen
    def won(self):
        self.screen = 4

class Game:
    def __init__(self, screens):
        self.screens = screens

    ##Setup the game parameters
    def setup(self):
        self.raft = [0, 0]
        self.side = False
        self.islands = [[[1, 1, 1], [2, 2, 2]],
                        [[0, 0, 0], [0, 0, 0]]]
        self.flag = -1

    ##Start game
    def start(self):
        self.flag = 0

    ##Put a castaway in the raft
    def embark(self, castaway_index, passenger_index):
        i, j, k = castaway_index
        castaway = self.islands[i][j][k]
        self.islands[i][j][k] = 0
        self.raft[passenger_index] = castaway

    ##Take a castaway off the raft
    def disembark(self, passenger_index):
        passenger = self.raft[passenger_index]
        i, j = self.side, passenger - 1
        k = self.islands[i][j].index(0)
        self.raft[passenger_index] = 0
        self.islands[i][j][k] = passenger

    ##Sail the raft to the other side
    def sail(self):
        self.side = not self.side
        i = self.side
        for passenger_index in range(2):
            passenger = self.raft[passenger_index]
            if passenger != 0:
                j = passenger - 1
                k = self.islands[i][j].index(0)
                self.raft[passenger_index] = 0
                self.islands[i][j][k] = passenger
        self.check_island()

    ##Check the conditions of each island
    def check_island(self):
        for i in range(2):
            canni_count = self.islands[i][0].count(1)
            missi_count = self.islands[i][1].count(2)
            ##More cannibals than missionaries = Lose
            if missi_count and canni_count > missi_count:
                self.flag = i + 1
                return self.screens.lost()
        ##Everyone on the right island = Win
        if self.islands[1] == [[1, 1, 1], [2, 2, 2]]:
            self.flag = 3
            return self.screens.won()

##Screen configurations
pygame.init()
WIDTH = 1280
HEIGHT = 720
MAIN_SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cannibals and Missionaries")

##Convert castaway index to castaway's position in screen
CASTAWAY_POS = {(0, 0, 0): (0, 220),
                (0, 0, 1): (120, 190),
                (0, 0, 2): (240, 220),
                (0, 1, 0): (0, 330),
                (0, 1, 1): (100, 330),
                (0, 1, 2): (200, 280),
                (1, 0, 0): (920, 220),
                (1, 0, 1): (1040, 190),
                (1, 0, 2): (1160, 220),
                (1, 1, 0): (960, 280),
                (1, 1, 1): (1060, 330),
                (1, 1, 2): (1160, 330)}

##Convert raft side to raft's position in screen
RAFT_POS = {0: (400, 220),
            1: (610, 220)}

##Convert raft side and passanger index to passenger's position in screen
PASSENGER_POS = {(0, 0): (420, 270),
                 (0, 1): (530, 270),
                 (1, 0): (630, 270),
                 (1, 1): (740, 270)}

##Convert island side, human type and emotion flag to human sprites
HUMAN_SPRITES = {(0, 1, 0): pygame.image.load("Images/canni_grr.png").convert_alpha(),
                 (0, 1, 1): pygame.image.load("Images/canni_yeah.png").convert_alpha(),
                 (0, 2, 0): pygame.image.load("Images/missi_bless.png").convert_alpha(),
                 (0, 2, 1): pygame.image.load("Images/missi_soup.png").convert_alpha()}
for human in (1, 2):
    for emt_flag in range(2):
        sprite = HUMAN_SPRITES[0, human, emt_flag]
        HUMAN_SPRITES[1, human, emt_flag] = pygame.transform.flip(sprite, True, False)

##Convert raft side to raft sprites
RAFT_SPRITES = {0: pygame.image.load("Images/raft.png").convert_alpha()}
RAFT_SPRITES[1] = pygame.transform.flip(RAFT_SPRITES[0], True, False)

##All main screen components
GAME_SCREENS = {'background': pygame.image.load("Images/background.png").convert(),
                'home': pygame.image.load("Images/home.png").convert_alpha(),
                'instructions': pygame.image.load("Images/instructions.png").convert_alpha(),
                'lost': pygame.image.load("Images/lost.png").convert_alpha(),
                'won': pygame.image.load("Images/won.png").convert_alpha()}
##Collisions for game buttons
BUTTON_COLLISIONS = {'play': pygame.Rect(570, 340, 180, 120),
                     'instructions': pygame.Rect(430, 470, 400, 120)}

##Flag that defines the emotion of each castaway
def emotion_flag(castaway, castaway_side, flag):
    match castaway, castaway_side:
        case 1, 0:
            return flag in (1, 3)
        case 1, 1:
            return flag in (2, 3)
        case 2, 0:
            return flag == 1
        case 2, 1:
            return flag == 2

def blit_sprites(game):
    ##Blit the castaways' sprites
    for i in range(2):
        for j in range(2):
            for k in range(3):
                castaway = game.islands[i][j][k]
                if not castaway:
                    continue
                emt_flag = emotion_flag(castaway, i, game.flag)
                sprite = HUMAN_SPRITES[(i, castaway, emt_flag)]
                spr_pos = CASTAWAY_POS[(i, j, k)]
                MAIN_SCREEN.blit(sprite, spr_pos)
    ##Blit the raft's sprite
    sprite = RAFT_SPRITES[game.side]
    spr_pos = RAFT_POS[game.side]
    MAIN_SCREEN.blit(sprite, spr_pos)
    ##Blit the passengers' sprites
    for passenger_index in range(2):
        passenger = game.raft[passenger_index]
        if not passenger:
            continue
        sprite = HUMAN_SPRITES[(game.side, passenger, 0)]
        spr_pos = PASSENGER_POS[(game.side, passenger_index)]
        MAIN_SCREEN.blit(sprite, spr_pos)

##Check if sprite was clicked
def check_collision(sprite, spr_pos, click_pos):
    spr_rect = sprite.get_rect(topleft=spr_pos)
    return spr_rect.collidepoint(click_pos)

def click_sprites(game, click_pos):
    if not all(game.raft):
        ##React for the castaways' sprites
        for j in reversed(range(2)):
            for k in range(3):
                castaway = game.islands[game.side][j][k]
                if not castaway:
                    continue
                castaway_index = (game.side, j, k)
                sprite = HUMAN_SPRITES[(game.side, castaway, 0)]
                spr_pos = CASTAWAY_POS[castaway_index]
                if check_collision(sprite, spr_pos, click_pos):
                    return game.embark(castaway_index, game.raft.index(0))
    ##React for passengers' sprites
    for passenger_index in range(2):
        passenger = game.raft[passenger_index]
        if not passenger:
            continue
        sprite = HUMAN_SPRITES[(game.side, passenger, 0)]
        spr_pos = PASSENGER_POS[(game.side, passenger_index)]
        if check_collision(sprite, spr_pos, click_pos):
            return game.disembark(passenger_index)
    ##React for raft's sprite
    if any(game.raft):
        sprite = RAFT_SPRITES[game.side]
        spr_pos = RAFT_POS[game.side]
        if check_collision(sprite, spr_pos, click_pos):
            return game.sail()

##Print the necessary elements for each screen
def update_screens(screens):
    MAIN_SCREEN.blit(GAME_SCREENS['background'], (0, 0))
    blit_sprites(screens.game)
    match screens.screen:
        case 0:
            MAIN_SCREEN.blit(GAME_SCREENS['home'], (0, 0))
        case 1:
            MAIN_SCREEN.blit(GAME_SCREENS['instructions'], (0, 0))
        case 3:
            MAIN_SCREEN.blit(GAME_SCREENS['lost'], (0, 0))
        case 4:
            MAIN_SCREEN.blit(GAME_SCREENS['won'], (0, 0))
    pygame.display.flip()

##Check how each screen reacts to clicks
def click_screens(screens, click_pos):
    match screens.screen:
        ##Home screen
        case 0:
            if BUTTON_COLLISIONS['play'].collidepoint(click_pos):
                screens.start()
            elif BUTTON_COLLISIONS['instructions'].collidepoint(click_pos):
                screens.instructions()
        ##Instruction screen
        case 1:
            screens.home()
        ##Game screen
        case 2:
            click_sprites(screens.game, click_pos)
        ##Losing or winning screens
        case _:
            screens.setup()
    update_screens(screens)

##Create the object that stores the current screen
screens = Screens()
update_screens(screens)

##Main loop
async def main():
    while True:
        for event in pygame.event.get():
            ##Check for click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_pos = pygame.mouse.get_pos()
                    click_screens(screens, click_pos)
        await asyncio.sleep(0)

asyncio.run(main())
