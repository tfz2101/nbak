'''
'''
import sys,time

import pygame
from pygame.locals import *

import UI
from settings import Settings

class NBack:
    #Constructor
    def __init__(self):
        self.clock = pygame.time.Clock()
        
        self.settings = Settings.Instance()

        #Sets Window Size
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode(self.settings.windowSize, pygame.FULLSCREEN, 32)
        else:
            self.screen = pygame.display.set_mode(self.settings.windowSize, 0, 32)

        #standalone is True if One wants to skip the menu
        self.drawMenu = True if not self.settings.standalone else False
        self.drawGame = False if not self.settings.standalone else True
        self.drawResults = False

        self.menu = UI.activities.Menu()
        self.grid1 = UI.activities.Game1()
        self.grid2 = UI.activities.Game2()
        self.grid3 = UI.activities.Game3()

        self.game = self.grid1

        self.board_position = {1:[80,80],2:[40,30],3:[120,120]}

        self.currentGridScore = 1
        self.counter = 0

    def run(self):
        if self.settings.standalone:
            self.game.start()

        if self.drawMenu:
            self.screen.blit(self.menu.draw(), (0, 0))

        time.sleep(2)
        while True:
            #Streams in user actions
            self.handler()

            #initiates the drawing of the game and then results
            self.draw()

            pygame.display.flip()


    def draw(self):
        #Mechanism to change grids - should be based on the score on the current grid - CHANGE!!!!!!!!
        self.counter = self.counter + 1
        if self.counter >= 100000000:
            self.currentGridScore = -1
            self.counter = 0

        #Change this code to change the Grid!!
        if self.drawGame:
           if self.currentGridScore < 0:
                self.game = self.grid2
                self.game.start_grid()
           self.screen.blit(self.game.draw_grid1(), (self.board_position[2][0], self.board_position[2][1]))



        self.currentGridScore = 1

        #if self.drawResults:
        #    self.screen.blit(self.results.draw(), (0, 0))
    
    def handler(self):
        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            #Checks for Menu actions
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.game.triggered_loc = True

            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    pass

                #This checks if the player preses Spacebar, which is the event that the player uses to submit answer
                elif event.key == K_SPACE:
                    self.game.trigger_loc()

                elif event.key == K_a:
                    self.game.trigger_sound()

                #If menu starts at startup
                elif not self.settings.standalone:
                    if event.key == K_ESCAPE:
                        self.drawMenu = False
                        self.drawGame = True
                        self.game.start()
                    elif event.key == K_F1:
                        self.drawResults = not self.drawResults
                        if self.drawResults:
                            self.results = UI.activities.Results(self.game.results)


            elif event.type == USEREVENT+1:
                self.game.showSlideSwitch()






settings = Settings.Instance()
pygame.init()
nback = NBack()
pygame.display.set_caption('N-Back')
nback.run()
