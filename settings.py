from singleton import Singleton

@Singleton
class Settings():
    version = "0.3.1"

    # The N in N-Back
    nBack = 1

    # Probability that one of the last N slides will be next
    repeatProbability = nBack/9.0

    # Time given to answer each slide, the correct answer is shown afterwards at a fraction of the time
    slideTime = 2000

    # How many slides to show during one game
    numOfSlides = 15

    # Window settings
    windowSize = (920, 820)

    # Kind of quirky, messes up resolution settings in my dev env.
    fullscreen = False

    drawNumber = True

    # Set to true to skip menu
    standalone = False

    # Unsupported
    android = False

    debug = True

    def __init__(self):
        print("Settings loaded")