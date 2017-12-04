'''
'''
import sys,time,random

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

        self.compiledPosResults = {"correct": 0, "avoid": 0, "miss": 0, "wrong": 0}
        self.compiledSoundResults = {"correct": 0, "avoid": 0, "miss": 0, "wrong": 0}

        self.menu = UI.activities.Menu()
        self.grid1 = UI.activities.Game1()
        self.grid2 = UI.activities.Game2()
        self.grid3 = UI.activities.Game3()

        self.gridArray = [self.grid1,self.grid2,self.grid3]

        self.curGridIndex = 0
        self.game = self.grid1

        self.board_position = {1:[80,80],2:[40,30],3:[120,120]}
        self.currentTotalSlidesElapsed = 0
        self.switchAddOn = 0
        self.warmup_slides = 3
        self.thresholdSwitchGame = 0.5

    def stop(self):
        self.save()
        print('Position Results')
        print("Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.compiledPosResults))
        print('Sound Results')
        print("Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.compiledSoundResults))
        #pygame.time.set_timer(USEREVENT+1, 0)
        #pygame.time.set_timer(QUIT, self.settings.slideTime/4)
        #pygame.time.set_timer(QUIT, 0)
        time.sleep(2)
        pygame.quit()
        sys.exit()

    def getPositionWinPercentage(self):
        totalSlides = (self.currentTotalSlidesElapsed + self.game.getSlidesElapsed())
        correct = self.compiledPosResults['correct']+self.compiledPosResults['avoid']
        return (correct/1.0/totalSlides)

    def save(self):
        print("Saving results to CSV...")
        with open("./output.csv", "w+") as f:
            f.read()
            position_results = "\n{correct},{wrong},{avoid},{miss}".format(**self.compiledPosResults)
            sound_results = "\n{correct},{wrong},{avoid},{miss}".format(**self.compiledSoundResults)
            f.writelines([position_results, sound_results])
    #SLIDE AFTER SWITCH AND LAST SIDE BEFORE STOP ARE NOT REGISTERING!!
    def run(self):
        if self.settings.standalone:
            self.game.start()

        if self.drawMenu:
            self.screen.blit(self.menu.draw(), (0, 0))

        time.sleep(2)
        while True:

            if (self.currentTotalSlidesElapsed + self.game.getSlidesElapsed()) >= (self.settings.numOfSlides + self.switchAddOn):
                self.game.checkAnswer()
                print('STOP GAME!')
                print('This Games Results')
                print( "Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.game.results))
                self.updateCompiledResults()
                if self.getPositionWinPercentage() > 0.3:
                    file = open('n.txt', 'w')
                    file.write(str(self.settings.nBack + 1))
                    file.close()
                self.stop()

            if self.game.getCurrentGamePercentage() < self.thresholdSwitchGame and self.game.getSlidesElapsed() > self.warmup_slides:
               self.game.checkAnswer()
               print('SWITCH GRID')
               self.switchAddOn += 1
               self.currentTotalSlidesElapsed += self.game.getSlidesElapsed()
               print('This Games Results')
               print("Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.game.results))
               self.updateCompiledResults()

               nextGrid = random.randint(0,1)
               if nextGrid == self.curGridIndex:
                   self.curGridIndex = self.curGridIndex - 1
               else:
                   self.curGridIndex = nextGrid


               self.game = self.gridArray[self.curGridIndex]
               self.game.start_grid()
               time.sleep(1)


            #initiates the drawing of the game and then results
            self.draw()

            # Streams in user actions
            self.handler()

            pygame.display.flip()

    def updateCompiledResults(self):
        for key in self.game.results:
            self.compiledPosResults[key] += self.game.results[key]
            try:
                self.compiledSoundResults[key] += self.game.results_sound[key]
            except AttributeError:
                pass

    def draw(self):

        #Change this code to change the Grid!!
        if self.drawGame:

           self.screen.blit(self.game.draw_grid1(), (self.board_position[2][0], self.board_position[2][1]))

        if self.drawResults:
            self.screen.blit(self.results.draw(), (0, 0))
    
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
                    try:
                        self.game.trigger_sound()
                    except:
                        pass

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
                #print("Correct: {correct}\nWrong: {wrong}\nAvoided: {avoid}\nMissed: {miss}".format(**self.compiledPosResults))


settings = Settings.Instance()
pygame.init()
nback = NBack()
pygame.display.set_caption('N-Back')
nback.run()
