
import random, time

import pygame
from pygame.locals import *
from settings import Settings
import os

from . import widgets

_image_library = {}

def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
            canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
            image = pygame.image.load(canonicalized_path).convert()
            _image_library[path] = image
    return image


class Activity:
    def __init__(self):
        settings = Settings.Instance()
        self.surface = pygame.Surface(settings.windowSize).convert()
        self.windowSize = settings.windowSize


class Menu(Activity):
    def __init__(self):
        Activity.__init__(self)
        self.version = Settings.Instance().version

        self.titleFont = pygame.font.Font("fonts/freesansbold.ttf", 50)
        self.menuFont = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.smallFont = pygame.font.Font("fonts/freesansbold.ttf", 15)

        newgameKey = "Escape"
        triggerKey = "Space"

        titleText = self.titleFont.render("Welcome to N-Back!", True, (255,255,0))
        titleVersion = self.smallFont.render("Version " + self.version, True, (255,255,0))
        self.title = pygame.Surface((650,200)).convert()
        self.title.blit(titleText, (self.title.get_width()/2-titleText.get_width()/2, self.title.get_height()/2-titleText.get_height()/2))
        self.title.blit(titleVersion, (self.title.get_width()/2-titleVersion.get_width()/2, (self.title.get_height()/2-titleVersion.get_height()/2)+40))

        self.controlsBox = widgets.TextBox("Controls\n  New Game - {0}\n  Trigger N-Back - {1}".format(newgameKey, triggerKey), self.menuFont, (270,100), color=(0,0,50), textColor=(255,255,0), radius=10)

    def draw(self):
        self.surface.blit(self.title, ( (self.surface.get_width()/2-self.title.get_width()/2), (self.surface.get_height()/2-self.title.get_height()/2)-100 ))
        #self.surface.blit(self.controls, ( 25, (self.windowSize[1]-self.controls.get_height())-25 ))
        self.surface.blit(self.controlsBox.draw(), ( 25, (self.windowSize[1]-self.controlsBox.draw().get_height())-25 ))

        return self.surface

#Sets the Game Grid and what it looks like
class Game(Activity):
    corner_radius = 10

    #Dictates the size of the game board
    board_surface_size = (800, 800)
    board_surface_color = (200, 200, 200)
    cell_surface_size = (100, 100)
    cell_surface_color = (50, 50, 50)
    background_color = (255, 255, 255)


    def __init__(self):
        Activity.__init__(self)
        self.settings = Settings.Instance()

        self.results = {}
        self.history = []
        self.reset()

        #Defines the positions that the box can appear in each slide
        #self.positions = {i+1: (self.corner_radius + 100*(i % 3), self.corner_radius + 100*(int(i/3)))
        #                  for i in range(9)}

        self.positions = {1: (100,100),
                          2: (300,100),
                          3: (500,100),
                          4: (100,300),
                          5: (300,300),
                          6: (500,300),
                          7: (100,500),
                          8: (300,500),
                          9: (500,500),
                         }


        self.normalFont = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.smallFont = pygame.font.Font("fonts/freesansbold.ttf", 15)
        self.cellFont = pygame.font.Font("fonts/freesansbold.ttf", 70)

        self.show_answer = False
        self.triggered_loc = False
        self.triggered_sound = False


    #Draw function to draw Grid1
    def draw_grid1(self):
        self.surface.fill(self.background_color)
        self.surface = pygame.Surface(self.board_surface_size).convert_alpha()
        board_surface = pygame.Surface.copy(self.surface)
        grid_img = get_image('Grid1.png')
        board_surface.blit(grid_img, (0,0))


        if not self.show_answer or not self.early_slide():
            box_img = get_image('grid1_box.png')
            board_surface.blit(box_img, (self.positionX, self.positionY, 100, 100))

        self.surface.blit(board_surface, ((self.windowSize[0]-board_surface.get_width())/2,
                                          (self.windowSize[1]-board_surface.get_height())/2,
                                           700,700))

        return self.surface

    def draw(self):
        self.surface.fill(self.background_color)

        board_surface_base = widgets.Box(self.board_surface_size, self.board_surface_color, self.corner_radius).draw()
        board_surface = pygame.Surface.copy(board_surface_base)

        if not self.show_answer or not self.early_slide():
            cell_surface_base = widgets.Box(self.cell_surface_size, self.cell_surface_color, self.corner_radius).draw()
            cell_surface = pygame.Surface.copy(cell_surface_base)

            #drawNumber is a setting to determin if a number goes along with the block
            if self.settings.drawNumber:
                cell_number = self.cellFont.render(str(self.history[-1]), True, (255, 255, 255))
                cell_surface.blit(cell_number, (50-cell_number.get_width()/2, 50-cell_number.get_height()/2))
            board_surface.blit(cell_surface, (self.positionX, self.positionY, 100, 100))

        self.surface.blit(board_surface, ((self.windowSize[0]-board_surface.get_width())/2,
                                          (self.windowSize[1]-board_surface.get_height())/2))

        return self.surface

    def reset(self):
        self.results = {"correct": 0, "avoid": 0, "miss": 0, "wrong": 0}
        self.history = []


    #Called first in the Main Code
    def start(self):
        self.reset()
        self.nextSlide()

        #This sets the time between each slide
        pygame.time.set_timer(USEREVENT+1, int(self.settings.slideTime))


    def start_grid(self):
        self.reset()
        self.nextSlide()



    def pause(self):
        if self.activeGame:
            pygame.time.set_timer(USEREVENT+1, 0)
        else:
            pygame.time.set_timer(USEREVENT+1, self.slideTime)
        self.activeGame = not self.activeGame
        self.drawMenu = not self.drawMenu

    def stop(self):
        self.save()
        print("Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.results))
        pygame.time.set_timer(USEREVENT+1, 0)
        pygame.time.set_timer(QUIT, self.settings.slideTime)


    def save(self):
        """Saves result to CSV"""
        print("Saving results to CSV...")
        with open("./output.csv", "w+") as f:
            f.read()
            write_data = "\n{correct},{wrong},{avoid},{miss}".format(**self.results)
            f.write(write_data)

    def setNoAnswer(self):
        self.cell_surface_color = (50, 50, 50)

    def setCorrectAnswer(self):
        self.cell_surface_color = (25, 200, 25)

    def setWrongAnswer(self):
        self.cell_surface_color = (200, 25, 25)

    def early_slide(self):
        return len(self.history) < 1+self.settings.nBack

    def trigger_loc(self):
        if self.early_slide():
            print("Too early!")
            return

        if not self.triggered_loc:
            self.triggered_loc = True
            self.checkAnswer()
        else:
            print("Already triggered")

    def checkAnswer(self):
        if self.early_slide():
            return

        nBackPos = self.history[-(1+self.settings.nBack)]
        pos = self.currentPosition()

        if self.triggered_loc:
            if nBackPos == pos:
                self.results["correct"] += 1
                self.setCorrectAnswer()
                print("Correct, {0} is equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
            elif nBackPos != pos:
                self.results["wrong"] += 1
                self.setWrongAnswer()
                print("Wrong, {0} is not equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
        else:
            if nBackPos != pos:
                self.results["avoid"] += 1
                self.setCorrectAnswer()
                print("Avoided it, {0} is not equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
            elif nBackPos == pos:
                self.results["miss"] += 1
                self.setWrongAnswer()
                print("Missed it, {0} is equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))

    #Picks the next square that will pop up
    def nextSlide(self):
        position = random.randint(1, 9)

        #Records the position of the next square
        self.history.append(position)

        if self.settings.debug:
            print("Slide number {0} generated with value: {1}".format(len(self.history), self.history[-1]))

        self.triggered_loc = False

        #First time positionX and positonY are initialized since nextSlide is run in the start() fcn
        self.positionX = self.positions[self.currentPosition()][0]
        self.positionY = self.positions[self.currentPosition()][1]

    def currentPosition(self):
        return self.history[-1]

    def showSlideSwitch(self):
        self.show_answer = not self.show_answer

        if not self.show_answer:
            self.setNoAnswer()
            pygame.time.set_timer(USEREVENT+1, self.settings.slideTime)
            self.nextSlide()
        else:
            self.checkAnswer()
            pygame.time.set_timer(USEREVENT+1, int(self.settings.slideTime/4))
            if len(self.history) >= self.settings.numOfSlides:
                # If enough slides have passed
                self.stop()


class Game1(Game):
    def __init__(self):
        Game.__init__(self)
        self.history_sound = []
        self.sound_bank = [ "Audio/1.wav",
                            "Audio/2.wav",
                            "Audio/3.wav",
                            "Audio/4.wav",
                            "Audio/5.wav",
                            "Audio/6.wav",
                            "Audio/7.wav",
                            "Audio/8.wav",
                            "Audio/9.wav"]

    def currentSound(self):
        return self.history_sound[-1]

    def reset(self):
        self.results = {"correct": 0, "avoid": 0, "miss": 0, "wrong": 0}
        self.history = []
        self.history_sound = []

    def early_slide_sound(self):
        return len(self.history_sound) < 1+self.settings.nBack

    def trigger_sound(self):
        if self.early_slide_sound():
            print("Too early!")
            return

        if not self.triggered_sound:
            self.triggered_sound = True
            #self.checkAnswer()
        else:
            print("Already triggered")


    def draw_grid1(self):
        self.surface.fill(self.background_color)
        self.surface = pygame.Surface(self.board_surface_size).convert_alpha()
        board_surface = pygame.Surface.copy(self.surface)
        grid_img = get_image('Grid1.png')
        board_surface.blit(grid_img, (0,0))


        if not self.show_answer or not self.early_slide():
            box_img = get_image('grid1_box.png')
            board_surface.blit(box_img, (self.positionX, self.positionY, 100, 100))

        self.surface.blit(board_surface, ((self.windowSize[0]-board_surface.get_width())/2,
                                          (self.windowSize[1]-board_surface.get_height())/2,
                                           700,700))

        return self.surface

    def checkAnswer(self):
        if self.early_slide()==False:
            nBackPos = self.history[-(1+self.settings.nBack)]
            nBackSound = self.history_sound[-(1+self.settings.nBack)]

            pos = self.currentPosition()
            cur_sound = self.currentSound()

            '''
            if self.triggered_loc:
                if nBackPos == pos:
                    self.results["correct"] += 1
                    self.setCorrectAnswer()
                    print("Correct, {0} is equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
                elif nBackPos != pos:
                    self.results["wrong"] += 1
                    self.setWrongAnswer()
                    print("Wrong, {0} is not equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
            else:
                if nBackPos != pos:
                    self.results["avoid"] += 1
                    self.setCorrectAnswer()
                    print("Avoided it, {0} is not equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
                elif nBackPos == pos:
                    self.results["miss"] += 1
                    self.setWrongAnswer()
                    print("Missed it, {0} is equal to {1} with nBack={2}.".format(nBackPos, pos, self.settings.nBack))
        '''

        if self.early_slide_sound():
            return

        if self.triggered_sound:
            if nBackSound == cur_sound:
                self.results["correct"] += 1
                self.setCorrectAnswer()
                print("(Sound) Correct, {0} is equal to {1} with nBack={2}.".format(nBackSound, cur_sound, self.settings.nBack))
            elif nBackSound != cur_sound:
                self.results["wrong"] += 1
                self.setWrongAnswer()
                print("(Sound) Wrong, {0} is not equal to {1} with nBack={2}.".format(nBackSound, cur_sound, self.settings.nBack))
        else:
            if nBackSound != cur_sound:
                self.results["avoid"] += 1
                self.setCorrectAnswer()
                print("(Sound) Avoided it, {0} is not equal to {1} with nBack={2}.".format(nBackSound, cur_sound, self.settings.nBack))
            elif nBackSound == cur_sound:
                self.results["miss"] += 1
                self.setWrongAnswer()
                print("(Sound) Missed it, {0} is equal to {1} with nBack={2}.".format(nBackSound, cur_sound, self.settings.nBack))


    def nextSlide(self):
        position = random.randint(1, 9)

        #Records the position of the next square
        self.history.append(position)

        if self.settings.debug:
            pass
            #print("Slide number {0} generated with value: {1}".format(len(self.history), self.history[-1]))

        self.triggered_loc = False

        #First time positionX and positonY are initialized since nextSlide is run in the start() fcn
        self.positionX = self.positions[self.currentPosition()][0]
        self.positionY = self.positions[self.currentPosition()][1]

        #SOUNDDDDDD
        sound = random.randint(1, 2)

        #Records the position of the next square
        self.history_sound.append(sound)

        if self.settings.debug:
            print("Slide number {0} generated with SOUND: {1}".format(len(self.history_sound), self.history_sound[-1]))

        #sound = pygame.mixer.Sound(self.sound_bank[sound-1])
        #sound.play()
        time.sleep(0.5)

        self.triggered_sound = False



    def showSlideSwitch(self):
        self.show_answer = not self.show_answer

        if not self.show_answer:
            self.setNoAnswer()
            pygame.time.set_timer(USEREVENT+1, self.settings.slideTime)
            self.nextSlide()
        else:
            self.checkAnswer()
            pygame.time.set_timer(USEREVENT+1, int(self.settings.slideTime/5))
            if len(self.history) >= self.settings.numOfSlides:
                # If enough slides have passed
                self.stop()


        '''
        if not self.show_answer:
            self.setNoAnswer()
            pygame.time.set_timer(USEREVENT+1, self.settings.slideTime)
            self.nextSlide()
        else:
            self.checkAnswer()
            #pygame.time.set_timer(USEREVENT+1, int(self.settings.slideTime/4))
            time.sleep(0.2)
            if len(self.history) >= self.settings.numOfSlides:
                # If enough slides have passed
                self.stop()
        '''


class Game2(Game):
    board_surface_size = (1000, 1000)
    board_surface_color = (200, 200, 200)
    cell_surface_size = (100, 100)
    cell_surface_color = (50, 50, 50)
    background_color = (255, 255, 255)

    def __init__(self):
        Game.__init__(self)
        self.positions = {1: (400,115),
                          2: (248,222),
                          3: (165,350),
                          4: (250,480),
                          5: (402,542),
                          6: (553,480),
                          7: (640,350),
                          8: (550,225),
                          9: (400,340),
                         }

    def draw_grid1(self):
        self.surface.fill(self.background_color)
        self.surface = pygame.Surface(self.board_surface_size).convert_alpha()
        board_surface = pygame.Surface.copy(self.surface)
        grid_img = get_image('Grid2.png')
        board_surface.blit(grid_img, (-50,100))


        if not self.show_answer or not self.early_slide():
            box_img = get_image('grid1_box.png')
            board_surface.blit(box_img, (self.positionX, self.positionY, 100, 100))

        self.surface.blit(board_surface, ((self.windowSize[0]-board_surface.get_width())/2,
                                          (self.windowSize[1]-board_surface.get_height())/2))

        return self.surface


class Game3(Game):
    board_surface_size = (1000, 1000)
    board_surface_color = (200, 200, 200)
    cell_surface_size = (100, 100)
    cell_surface_color = (50, 50, 50)
    background_color = (255, 255, 255)

    def __init__(self):
        Game.__init__(self)
        self.positions = {1: (80,155),
                          2: (245,255),
                          3: (430,340),
                          4: (258,430),
                          5: (80,510),
                          6: (615,240),
                          7: (762,150),
                          8: (613,430),
                          9: (775,508),
                         }

    def draw_grid1(self):
        self.surface.fill(self.background_color)
        self.surface = pygame.Surface(self.board_surface_size).convert_alpha()
        board_surface = pygame.Surface.copy(self.surface)
        grid_img = get_image('Grid3.png')

        board_surface.blit(grid_img, (-50,100))


        if not self.show_answer or not self.early_slide():
            box_img = get_image('grid1_box.png')
            box_img = pygame.transform.scale(box_img,(60,60))
            board_surface.blit(box_img, (self.positionX, self.positionY, 30, 30))

        self.surface.blit(board_surface, ((self.windowSize[0]-board_surface.get_width())/2,
                                          (self.windowSize[1]-board_surface.get_height())/2))

        return self.surface



class Results(Activity):
    def __init__(self, results):
        Activity.__init__(self)

        self.surface.convert_alpha()
        #self.surface.fill((255,255,255,100))

        self.normalFont = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.smallFont = pygame.font.Font("fonts/freesansbold.ttf", 15)

        self.panelSurfaceBase = pygame.Surface((150, self.windowSize[1]))
        self.panelSurfaceBase.fill((50, 50, 50))

        self.panelSurfaceLeft = pygame.Surface.copy(self.panelSurfaceBase)
        self.panelSurfaceRight = pygame.Surface.copy(self.panelSurfaceBase)

        self.panelSurfaceLeft = pygame.Surface.copy(self.panelSurfaceBase)
        self.panelSurfaceRight = pygame.Surface.copy(self.panelSurfaceBase)

        resultsHeader = self.normalFont.render("Results", True, (255, 255, 0))
        resultsCorrect = self.smallFont.render("Correct: {0}".format(results["correct"]), True, (255, 255, 0))
        resultsWrong = self.smallFont.render("Wrong: {0}".format(results["wrong"]), True, (255, 255, 0))
        resultsAvoid = self.smallFont.render("Avoided: {0}".format(results["avoid"]), True, (255, 255, 0))
        resultsMiss = self.smallFont.render("Missed: {0}".format(results["miss"]), True, (255, 255, 0))
        self.panelSurfaceRight.blit(resultsHeader, (10, 10))
        self.panelSurfaceRight.blit(resultsCorrect, (10, 40))
        self.panelSurfaceRight.blit(resultsWrong, (10, 60))
        self.panelSurfaceRight.blit(resultsAvoid, (10, 80))
        self.panelSurfaceRight.blit(resultsMiss, (10, 100))

        self.surface.blit(self.panelSurfaceLeft, (0, 0))
        self.surface.blit(self.panelSurfaceRight, ((self.windowSize[0]-self.panelSurfaceRight.get_width()), 0))

    def draw(self):
        return self.surface
