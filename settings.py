from singleton import Singleton

@Singleton
class Settings():
    version = "0.3.1"

    with open('n.txt', 'r') as myfile:
        data = myfile.read().replace('\n', '')

    # The N in N-Back
    nBack = int(data)
    print('N Level', nBack)
    # Probability that one of the last N slides will be next
    repeatProbability = 0.5

    # Time given to answer each slide, the correct answer is shown afterwards at a fraction of the time
    slideTime = 2000

    # How many slides to show during one game
    numOfSlides = 8

    # Window settings
    windowSize = (910, 800)

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