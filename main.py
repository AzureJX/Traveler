from cmu_graphics import *
import numpy as np
from classes import *
import random
from PIL import Image
import copy

# global constants
FPS = 100
DT = 1/FPS

def vec(x, y):
    return np.array([x, y])

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

# This function is adapted from the code from the mini-lecture: physics in game
def updateRoc(roc, vxBuffer, vyBuffer):
    roc_a = roc.f / roc.m
    roc.v[0] = roc.v[0] + (roc_a[0] * DT)
    roc.v[0] = roc.v[0] * (1 + vxBuffer) # independent of the direction of the force
    roc.v[1] = roc.v[1] + vyBuffer * (roc_a[1] * DT)
    roc.d[0] = roc.d[0] + (roc.v[0] * DT)
    roc.f = vec(0, 0)

# This function is based on the code from the mini-lecture: physics in game
def addGravity(hole, roc): # update the gravitational force
    g = 1000
    d = hole.d - roc.d
    d_squared = np.dot(d, d)
    d_hat = d / (d_squared ** 0.5) # unit vector
    f_g = g * hole.m * roc.m / d_squared
    roc.f = roc.f + (f_g * d_hat)

def generateBlackHole(app):
    x = random.randint(40, app.width-40)
    r = random.randint(45, 70) # radius of the hole
    hole = Black_Hole(vec(x, -r), vec(0, 0), r, app.blackHoleImage)
    return hole

def generatePlanet(app):
    x = random.randint(30, app.width-30)
    planetList = [Jupiter(vec(x, -40), app.juIm), Mars(vec(x, -40), app.maIm), 
                  Neptune(vec(x, -40), app.neIm), Venus(vec(x, -40), app.veIm)] # total image length is 80
    planet = random.choice(planetList)
    return planet

def landOnPlanet(app):
    if app.planets != []:
        for planet in app.planets:
            if not planet.asked and distance(planet.d[0], planet.d[1], app.rocket.d[0], app.rocket.d[1]) <= planet.l+20:
                app.canLandPlanet = planet.name
                app.paused = True
                planet.asked = True

def drawPopUpWindow(app): 
    image = CMUImage(Image.open('images/popupback.jpg'))
    drawImage(image, app.width/2, app.height/2, width = 500, height = 170, align = 'center')
    drawLabel(f'Do you want to land on {app.canLandPlanet}?', app.width/2, 320,
              size = 20, font = 'orbitron', fill = 'white', bold = True)
    app.comfirmButton.draw()
    app.cancelButton.draw()

def onAppStart(app):
    app.width = 800
    app.height = 700
    app.maxDistance = 0
    restart(app)

def restart(app):
    app.juIm = CMUImage(Image.open('images/jupiter.png'))
    app.maIm = CMUImage(Image.open('images/mars.png'))
    app.veIm = CMUImage(Image.open('images/venus.png'))
    app.neIm = CMUImage(Image.open('images/neptune.png'))
    app.backgroundImage = CMUImage(Image.open('images/background.jpg'))
    app.blackHoleImage = CMUImage(Image.open('images/blackhole.png'))
    app.healthBarImage = CMUImage(Image.open('images/healthbar.png'))
    app.steps = 10
    app.auto = False
    app.autoTimer = 0
    app.paused = False
    app.rocketYSpeed = -600
    app.rocketAutoYSpeed = -1500
    app.rocketMass = 100000
    app.blackHoles = [generateBlackHole(app)] #generateBlackHole(app) # Black_Hole(vec(400, 300), vec(0, 0), 40, app.blackHoleImage)
    app.rocket = Rocket(vec(app.width/2, 600), vec(0, app.rocketYSpeed), app.rocketMass, 30)
    app.planets = [] # Venus(vec(400, 500), app.veIm)
    app.BHtimer = 0
    app.PNtimer = 0
    app.vxBuffer = 0
    app.vyBuffer = 0.1
    app.normalRocV = 0
    app.timeInterval = 50
    app.accelerate = False
    app.rocketPower = 1000
    app.autoRocPower = 1800 ####
    app.normalRocketPower = 1000
    app.fuel = 100
    app.normalFuelDepletionRate = 0.05
    app.backHeight = 0
    app.PNBHratio = 1.5
    app.canLandPlanet = None
    app.healthColor = 'lightgreen'
    app.mineMax = 30
    app.jewels = 0 ####
    app.menu = False
    app.distance = 0
    app.pauseButton = Pause_Button(1,1,1,1)
    app.exitButton = Exit_Button(1, 1, 1, 1)
    app.gameOverButton = GameOver_Button(1, 1, 1, 1)
    app.autoButton = Auto_Button(1, 1, 1, 1, app)
    app.comfirmButton = Button(app.width/2 - 100, 380, 85, 38, 17, 'Confirm') 
    app.cancelButton = Button(app.width/2 + 100, 380, 85, 38, 17, 'Cancel')
    app.showAutoEnd = False # for auto drive
    app.showTimer = 0
    app.fuelDie = False
    app.holeDie = False
    app.gameOver = False
    app.storeValue = True
    app.nonAccRocketPower = 1000

def start_onScreenActivate(app):
    restart(app)
    app.vyBuffer = 0
    while app.blackHoles[0].d[0] == app.width / 2:
        app.blackHoles = [generateBlackHole(app)]

def start_redrawAll(app):
    drawImage(app.backgroundImage, 0, app.backHeight, width = app.width, height = app.height)
    drawImage(app.backgroundImage, 0, app.backHeight - app.height, width = app.width, height = app.height)
    for hole in app.blackHoles: # black holes
        hole.draw()
    canDrawPlanet = True # planets
    for planet in app.planets:
        for hole in app.blackHoles:
            limit = hole.r + planet.l/2 + 20
            if distance(hole.d[0], hole.d[1], planet.d[0], planet.d[1]) <= limit:
                canDrawPlanet = False
        if canDrawPlanet:
            planet.draw()
        canDrawPlanet = True
    app.rocket.draw() # rocket
    drawLabel('TRAVELLER', 400, 175, fill='white', size=50, font='orbitron', bold=True)
    drawLabel('Your Highest Score', 400, 325, fill = 'white', size = 40, font='orbitron')
    drawLabel(f'{int(app.maxDistance)} km', 400, 375, fill = 'white', size = 35, font='orbitron')
    drawLabel('Press the spacebar to start the game', 400, 485, fill='white',size=25, font='orbitron')

def start_onKeyPress(app, key):
    if key == 'space':
        restart(app)
        setActiveScreen('space')
    # elif key == 'r':
    #     restart(app)

def start_onStep(app):
    updatePlanet(app)
    if app.autoTimer == 0 or app.autoTimer >= app.steps: # update best action
        app.bestAction = findBestAction(app)
        # print(app.bestAction)
        app.autoTimer = 0
    # print('0', app.rocket.v, app.blackHoles[0].d) #####    
    autoTakeStep(app)
    app.autoTimer += 1
    # print('1', app.rocket.v, app.blackHoles[0].d) #####
    moveBackground(app)
    app.distance -= app.rocket.v[1] * DT

# def space_onKeyPress(app, key):
#     if key == 'p':
#         app.paused = not app.paused
#     elif key == 'r':
#         restart(app)

def space_onMousePress(app, mouseX, mouseY):
    if app.exitButton.clickOn(mouseX, mouseY):
        app.maxDistance = app.distance
        setActiveScreen('start')
    if not app.paused and not app.auto and app.autoButton.clickOn(mouseX, mouseY) and app.jewels > 0:
        app.auto = True
        app.normalRocV = app.rocket.v.copy()
        app.rocket.v[1] = app.rocketAutoYSpeed
        app.normalRocketPower = app.rocketPower
    elif app.auto and app.autoButton.clickOn(mouseX, mouseY):
        app.auto = False
        app.rocket.v = app.normalRocV
        app.rocketPower = app.normalRocketPower
    if app.gameOver and app.gameOverButton.clickOn(mouseX, mouseY) and not app.auto:
        setActiveScreen('start')
    if app.comfirmButton.clickOn(mouseX, mouseY) and app.canLandPlanet != None:
        setActiveScreen(app.canLandPlanet)
        app.canLandPlanet = None
    elif app.cancelButton.clickOn(mouseX, mouseY):
        app.canLandPlanet = None
        app.paused = False
    if not app.paused and app.pauseButton.clickOn(mouseX, mouseY) and app.canLandPlanet == None:
        app.paused = True
        app.pauseButton.paused = True
        app.menu = True
    elif app.paused and app.pauseButton.clickOn(mouseX, mouseY) and app.canLandPlanet == None:
        app.paused = False
        app.pauseButton.paused = False
        app.menu = False

def space_onKeyHold(app, keys):
    if not app.auto:
        if 'left' in keys:
            app.rocket.f[0] -= app.rocketPower * app.rocketMass
        elif 'right' in keys:
            app.rocket.f[0] += app.rocketPower * app.rocketMass
        if 'space' in keys:
            app.accelerate = True

def space_onKeyRelease(app, key):
    if key == 'space':
        app.accelerate = False
        app.rocketPower = app.nonAccRocketPower
        app.storeValue = True

def updateGrav(app):
    app.BHtimer += 1 # for black holes and rocket
    if app.BHtimer >= app.timeInterval: # generate hole
        hole = generateBlackHole(app)
        app.blackHoles.append(hole)
        app.BHtimer = 0
    i = 0
    while i < len(app.blackHoles):
        hole = app.blackHoles[i]
        if hole.d[1] > app.height + hole.r: # delete out of screen holes
            app.blackHoles.pop(i)
        elif hole.d[1] < app.rocket.d[1]: # holes that are above the rocket
            addGravity(hole, app.rocket) # add to the net force
            hole.angle = (hole.angle + 1) % 360 # rotate the black hole
            i += 1
        else:
            i += 1
    # print('a: ', app.rocket.f/100000)
    # print('f: ', app.rocket.f)
    updateRocketHolePosition(app)

def updateRocketHolePosition(app):  
    if app.rocket.v[0] > 300: # limit horizontal speed
        app.rocket.v[0] = 300
        app.vxBuffer = -0.5
    elif app.rocket.v[0] < -300:
        app.rocket.v[0] = -300
        app.vxBuffer = -0.5
    else:
        app.vxBuffer = 0
    updateRoc(app.rocket, app.vxBuffer, app.vyBuffer) # update d and v
    preventGoOut(app)
    for hole in app.blackHoles:
        hole.d[1] -= (app.rocket.v[1] * DT)
    # print('v: ', app.rocket.v, 'd: ', app.blackHoles[0].d[1]) ###

def updatePlanet(app):
    app.PNtimer += 1 # for planets
    if app.PNtimer >= 1.5 * app.timeInterval: ######
        planet = generatePlanet(app)
        app.planets.append(planet)
        app.PNtimer = 0
    for planet in app.planets:
        planet.d[1] -= (app.rocket.v[1] * DT)
    i = 0
    while i < len(app.planets):
        planet = app.planets[i]
        if planet.d[1] > app.height + planet.l:
            app.planets.pop(i)
        else:
            i += 1

def accelerate(app):
    if app.storeValue:
        app.nonAccRocketPower = app.rocketPower
        app.storeValue = False
    if app.accelerate: # fuel depletion
        app.rocketPower += 250
        app.fuel -= app.normalFuelDepletionRate + 0.00005 * app.rocketPower # greater power, faster fuel depletion
    else:
        app.fuel -= app.normalFuelDepletionRate
    
def moveBackground(app):
    if app.backHeight >= app.height:
        app.backHeight = 0
    else:
        app.backHeight -= float(app.rocket.v[1] * DT)

def preventGoOut(app):
    if app.rocket.d[0] < app.rocket.width / 2:
        app.rocket.d[0] = app.rocket.width / 2
    elif app.rocket.d[0] > app.width - app.rocket.width / 2:
        app.rocket.d[0] = app.width - app.rocket.width / 2

def space_onStep(app):
    if not app.paused and app.auto: # This should be the first
        if app.autoTimer == 0 or app.autoTimer >= app.steps: # update best action
            app.bestAction = findBestAction(app)
            app.autoTimer = 0
        # print('0', app.rocket.v, app.blackHoles[0].d) #####    
        autoTakeStep(app)
        app.autoTimer += 1
        # print('1', app.rocket.v, app.blackHoles[0].d) #####
        moveBackground(app)
        updatePlanet(app)
        app.distance -= app.rocket.v[1] * DT
        app.jewels -= 3
        if app.jewels <= 0: # ending auto drive
            app.auto = False
            app.rocket.v = app.normalRocV
            app.rocketPower = app.normalRocketPower
            app.jewels = 0
            app.showAutoEnd = True
    elif not gameOver(app) and not app.auto:
        if not app.paused: # also pause when game over
            if app.showAutoEnd:
                app.showTimer += 1
                if app.showTimer >= 30:
                    app.showAutoEnd = False
            #print(app.rocket.v[1]) #####
            updateGrav(app)
            updatePlanet(app)
            accelerate(app)
            # print(app.rocketPower, app.fuel) ###
            moveBackground(app)
            landOnPlanet(app) # when get close to a planet
            if app.fuel > 20:
                app.healthColor = 'lightgreen'
            else:
                app.healthColor = 'red'
            app.distance -= app.rocket.v[1] * DT
    elif gameOver(app) and not app.auto:
        app.showAutoEnd = False
        app.paused = True
        if app.distance > app.maxDistance:
            app.maxDistance = app.distance
    if app.holeDie:
        hole = app.blackHoles[0]
        if app.rocket.d[0] - hole.d[0] > 10:
            app.rocket.d[0] -= 3
        elif hole.d[0] - app.rocket.d[0] > 10:
            app.rocket.d[0] += 3
        if app.rocket.opacity > 0:
            app.rocket.opacity -= 5
    elif app.fuelDie:
        if app.rocket.d[1] <= app.height + app.rocket.height/2:
            app.rocket.d[1] += 8
        if app.rocket.opacity > 0:
            app.rocket.opacity -= 5

############################################################
# Auto Drive Start
############################################################

def takeStepAuto_test(app):
    updateRocketHolePosition(app)

def takeStepAuto(app):
    app.BHtimer += 1 # for black holes and rocket
    if app.BHtimer >= app.timeInterval: # generate hole
        hole = generateBlackHole(app)
        app.blackHoles.append(hole)
        app.BHtimer = 0
    i = 0
    while i < len(app.blackHoles):
        hole = app.blackHoles[i]
        if hole.d[1] > app.height + hole.r: # delete out of screen holes
            app.blackHoles.pop(i)
        elif hole.d[1] < app.rocket.d[1]: # holes that are above the rocket
            hole.angle = (hole.angle + 1) % 360 # rotate the black hole
            i += 1
        else:
            i += 1
    # print('a: ', app.rocket.f/100000)
    # print('f: ', app.rocket.f)
    updateRocketHolePosition(app)

def emergencyAcc(app):
    for hole in app.blackHoles:
        if distance(app.rocket.d[0], app.rocket.d[1], hole.d[0], hole.d[1]) < 250:
            app.rocketPower = 10000
            # print('Emerg')

def autoTakeStep(app):
    if app.bestAction == 'left':
        app.rocketPower = app.autoRocPower
        emergencyAcc(app)
        app.rocket.f[0] -= app.rocketPower * app.rocketMass
        # print(app.rocketPower, app.rocket.f[0])
        takeStepAuto(app)
    elif app.bestAction == 'right':
        app.rocketPower = app.autoRocPower
        emergencyAcc(app)
        app.rocket.f[0] += app.rocketPower * app.rocketMass
        takeStepAuto(app)
    elif app.bestAction == 'stay':
        app.rocketPower = app.autoRocPower
        takeStepAuto(app)

def left(app):
    app.rocketPower = app.autoRocPower
    for _ in range(app.steps):
        app.rocket.f[0] -= app.rocketPower * app.rocketMass
        takeStepAuto_test(app)
    return score(app)

def right(app):
    app.rocketPower = app.autoRocPower
    for _ in range(app.steps):
        app.rocket.f[0] += app.rocketPower * app.rocketMass
        takeStepAuto_test(app)
    return score(app)

def stay(app):
    app.rocketPower = app.autoRocPower
    for _ in range(app.steps):
        takeStepAuto_test(app)
    return score(app)

def score(app):
    score = 100
    for hole in app.blackHoles:
        if hole.d[1] < app.rocket.d[1] + app.rocket.height:
            dist = distance(app.rocket.d[0], app.rocket.d[1], hole.d[0], hole.d[1])
            score -= 100/(dist**0.6)
    distanceToEdge = min(app.width-app.rocket.d[0], app.rocket.d[0])
    score -= 200/(distanceToEdge)
    if distanceToEdge < 50:
        score -= 10000
    return score

def makeCopy(app):
    rocketCopy = app.rocket.__deepcopy__({}) # make copy
    blackHolesCopy = []
    for hole in app.blackHoles:
        blackHolesCopy.append(hole.__deepcopy__({}))
    return rocketCopy, blackHolesCopy

def findBestAction(app):
    rocketCopy, blackHolesCopy = makeCopy(app)

    bestScore = left(app) # 1
    # print('1', bestScore)
    bestAction = 'left'
    app.rocket, app.blackHoles = rocketCopy, blackHolesCopy
    rocketCopy, blackHolesCopy = makeCopy(app)
    
    currScore = right(app) # 2
    # print('2', bestScore)
    if currScore > bestScore:
        bestScore = currScore
        bestAction = 'right'
    app.rocket, app.blackHoles = rocketCopy, blackHolesCopy
    rocketCopy, blackHolesCopy = makeCopy(app)
    
    currScore = stay(app) # 3
    # print('3', bestScore)
    if currScore > bestScore:
        bestScore = currScore
        bestAction = 'stay'
    app.rocket, app.blackHoles = rocketCopy, blackHolesCopy
    return bestAction

############################################################
# Auto Drive End
############################################################

def gameOver(app):
    if app.fuel < 0:
        app.fuelDie = True
        app.gameOver = True
        return True
    for hole in app.blackHoles:
        if distance(hole.d[0], hole.d[1], app.rocket.d[0], app.rocket.d[1]) <= hole.limit:
            app.holeDie = True
            app.gameOver = True
            return True
    return False

def drawHealthBar(app):
    image = app.healthBarImage
    drawImage(image, 30, 80, width=230, height=50) # fuel tank
    if app.fuel > 0:
        drawRect(60, 97, app.fuel * 2, 11, fill = app.healthColor)

def space_redrawAll(app):
    drawImage(app.backgroundImage, 0, app.backHeight, width = app.width, height = app.height)
    drawImage(app.backgroundImage, 0, app.backHeight - app.height, width = app.width, height = app.height)
    for hole in app.blackHoles: # black holes
        hole.draw()
    canDrawPlanet = True # planets
    for planet in app.planets:
        for hole in app.blackHoles:
            limit = hole.r + planet.l/2 + 20
            if distance(hole.d[0], hole.d[1], planet.d[0], planet.d[1]) <= limit:
                canDrawPlanet = False
        if canDrawPlanet:
            planet.draw()
        canDrawPlanet = True
    app.rocket.draw() # rocket
    drawHealthBar(app)
    if app.canLandPlanet != None and not app.gameOver:
        drawPopUpWindow(app)
    app.pauseButton.draw()
    drawLabel('Distance Travelled:', 780, 150,
              fill='white', align='right', size=18, font='orbitron', bold=True) # fill
    drawLabel(f'{int(app.distance)} km', 775, 180,
              fill='white', align='right', size=18, font='orbitron', bold=True) # fill
    if app.menu and not app.gameOver:
        drawMenu(app)
    app.exitButton.draw()
    app.autoButton.draw()
    if app.showAutoEnd and not app.gameOver and not app.paused:
        drawLabel('Auto Drive Ended', 400, 350, fill='white', size=45, font='orbitron') # fill
    if app.gameOver and not app.auto:
        drawGameOver(app)

def drawMenu(app):
    drawImage(CMUImage(Image.open('images/popupback.jpg')), 400, 385, 
              width=350, height=430, align='center')
    drawLabel('STATUS', 400, 195, size = 30, fill = 'white', bold=True, font='orbitron')
    drawLabel('Rocket Power:', 365, 260, size = 23, fill = 'gold', bold=True, font='orbitron')
    drawLabel('Max Mining Gain:', 375, 330, size = 23, fill = 'gold', bold=True, font='orbitron')
    drawLabel('Jewels:', 320, 400, size = 23, fill = 'gold', bold=True, font='orbitron')
    drawLabel('Vertical Speed:', 370, 470, size = 23, fill = 'gold', bold=True, font='orbitron')
    drawLabel(f'{app.rocketPower} MW', 470, 295, size = 23, fill = 'lightgreen', bold=True, font='orbitron')
    drawLabel(f'{app.mineMax} %', 490, 370, size = 23, fill = 'lightgreen', bold=True, font='orbitron')
    drawLabel(f'{app.jewels} pounds', 450, 435, size = 23, fill = 'lightgreen', bold=True, font='orbitron')
    drawLabel(f'{-app.rocket.v[1]} km/h', 460, 505, size = 23, fill = 'lightgreen', bold=True, font='orbitron')
    # if app.auto:
    #     drawLabel(f'{-app.rocketAutoYSpeed} km/h', 460, 505, size = 23, fill = 'lightgreen', bold=True, font='orbitron')
    # else:
    #     drawLabel(f'{-app.rocketYSpeed} km/h', 460, 505, size = 23, fill = 'lightgreen', bold=True, font='orbitron')

def drawGameOver(app):
    drawImage(CMUImage(Image.open('images/popupback.jpg')), 400, 350, 
              width=550, height=200, align='center')
    app.gameOverButton.draw()
    if app.fuelDie:
        drawLabel('RUN OUT OF FUEL', 400, 315, size=30, fill='white', font='orbitron', bold=True)
    elif app.holeDie:
        drawLabel('EATEN BY BLACK HOLE', 400, 315, size=30, fill='white', font='orbitron', bold=True)

############################################################
# Jupiter Screen
############################################################

def Jupiter_onScreenActivate(app):
    app.newStorm = None
    app.jupiterStorms = []
    app.jupiterInt = False
    app.mine = Mine('JUPITER', app.mineMax)
    app.jTimer = 0
    app.add = False

def Jupiter_redrawAll(app):
    drawImage(CMUImage(Image.open('images/jupiterland.jpg')), 0, 0, width = app.width, height = app.height)
    app.exitButton.draw()
    if app.newStorm != None:
        app.newStorm.draw()
    for storm in app.jupiterStorms:
        storm.draw()
    app.mine.draw()
    if app.jupiterInt:
        drawLabel('What a beautiful storm!', 400, 100, 
                  size = 20, font = 'orbitron', fill='white', bold=True)
        drawLabel('You will be able to mine up to 10 more percent in future mining!',
                  400, 130, size = 20, font = 'orbitron', fill='white', bold=True)
    drawLabel('Press and hold the mouse', 570 , 580, size=20, font = 'orbitron', fill='white')
    drawLabel('to make storms on Jupiter!', 570 , 620, size=20, font = 'orbitron', fill='white')
def Jupiter_onMousePress(app, mouseX, mouseY):
    if app.exitButton.clickOn(mouseX, mouseY):
        setActiveScreen('space')
        app.paused = False
    app.mine.buttonControl(mouseX, mouseY)
    if not app.mine.mineButton.clickOn(mouseX, mouseY):
        app.newStorm = Storm(mouseX, mouseY)

def Jupiter_onMouseRelease(app, mouseX, mouseY):
    if app.newStorm != None:
        app.jupiterStorms.append(app.newStorm)
        app.jupiterInt = True
        if not app.add:
            app.mineMax += 10
            app.add = True
    app.newStorm = None

def Jupiter_onStep(app):
    if app.newStorm != None:
        app.newStorm.r += 2
    i = 0
    while i < len(app.jupiterStorms):
        storm = app.jupiterStorms[i]
        storm.r += 1
        storm.opacity -= 1
        if storm.opacity <= 0:
            app.jupiterStorms.pop(i)
        else:
            i += 1
    app.mine.takeMineStep(app)
    if app.jupiterInt:
        app.jTimer += 1
        if app.jTimer >= 60:
            app.jupiterInt = False

############################################################
# Mars Screen
############################################################

def Mars_onScreenActivate(app):
    app.headLocation = None
    app.rootLocation = None
    app.marsPlants = []
    app.marsInt = False
    app.mine = Mine('MARS', app.mineMax)
    app.mTimer = 0
    app.add = False
    app.saplingImage = CMUImage(Image.open('images/sapling.png'))

def Mars_redrawAll(app):
    drawImage(CMUImage(Image.open('images/marsland.png')), 0, 0, width = app.width, height = app.height)
    app.exitButton.draw()
    for plant in app.marsPlants:
        headLoc = plant[0]
        rootLoc = plant[1]
        if headLoc[1] < rootLoc[1]:
            drawImage(app.saplingImage, headLoc[0], headLoc[1], 
                      width = 60, height = rootLoc[1]-headLoc[1], align = 'top')
    app.mine.draw()
    if app.marsInt:
        drawLabel('Thanks for planting on Mars! You gained 100 extra rocket power!', 
                  400, 100, size = 20, font = 'orbitron', fill='white', bold=True)
    drawLabel('Press and drag the mouse', 570, 580, size=20, font = 'orbitron', fill='white')
    drawLabel('to plant trees on Mars!', 570, 620, size=20, font = 'orbitron', fill='white')

def Mars_onMouseDrag(app, mouseX, mouseY):
    app.headLocation = mouseX, mouseY
    plant = (app.headLocation, app.rootLocation)
    app.marsPlants.append(plant)
    app.marsInt = True
    if not app.add:
        app.rocketPower += 100
        app.add = True

def Mars_onMousePress(app, mouseX, mouseY):
    if app.exitButton.clickOn(mouseX, mouseY):
        setActiveScreen('space')
        app.paused = False
    app.rootLocation = mouseX, mouseY
    app.headLocation = None
    app.mine.buttonControl(mouseX, mouseY)

def Mars_onStep(app):
    app.mine.takeMineStep(app)
    if app.marsInt:
        app.mTimer += 1
        if app.mTimer >= 50:
            app.marsInt = False

############################################################
# Venus Screen
############################################################

def Venus_onScreenActivate(app):
    app.vTimer = 0
    app.QA = VenusQA()

def Venus_redrawAll(app):
    drawImage(CMUImage(Image.open('images/venusland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/venusgod.png')), 380, 425, 
              width = 280, height = 500, align='center')
    drawLabel('Welcome to Venus!', 400, 60, size = 26, fill='white',bold=True, font='orbitron')
    drawLabel('Answer me three questions, and I will let you go.', 
              400, 100, size = 26, fill='white', bold=True, font='orbitron')
    
def Venus_onStep(app):
    app.vTimer += 1
    if app.vTimer == 50:
        setActiveScreen('vQA')

def vQA_onScreenActivate(app):
    app.QA.generateQA()

def vQA_redrawAll(app):
    drawImage(CMUImage(Image.open('images/venusland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/venusgod.png')), 200, 425, 
              width = 250, height = 450, align='center')
    app.QA.QAdraw()

def vQA_onMousePress(app, mx, my):
    app.QA.mouseControl(mx, my, app)

def VenusEnd_redrawAll(app):
    drawImage(CMUImage(Image.open('images/venusland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/venusgod.png')), 275, 425, 
              width = 280, height = 500, align='center')
    drawImage(CMUImage(Image.open('images/jewel.png')), 575, 560, 
              width = 200, height = 200, align='center')
    app.exitButton.draw()
    app.QA.endDraw()

def VenusEnd_onMousePress(app, mouseX, mouseY):
    if app.exitButton.clickOn(mouseX, mouseY):
        setActiveScreen('space')
        app.paused = False

############################################################
# Neptune Screen
############################################################

def Neptune_onScreenActivate(app):
    app.nTimer = 0
    app.QA = NeptuneQA()

def Neptune_redrawAll(app):
    drawImage(CMUImage(Image.open('images/neptuneland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/neptunegod.png')), 380, 425, 
              width = 435, height = 500, align='center')
    drawLabel('Welcome to Neptune!', 400, 60, size = 26, fill='white',bold=True, font='orbitron')
    drawLabel('Answer me three questions, and I will let you go.', 
              400, 100, size = 26, fill='white', bold=True, font='orbitron')
    
def Neptune_onStep(app):
    app.nTimer += 1
    if app.nTimer == 50:
        setActiveScreen('nQA')

def nQA_onScreenActivate(app):
    app.QA.generateQA()

def nQA_redrawAll(app):
    drawImage(CMUImage(Image.open('images/neptuneland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/neptunegod.png')), 260, 410, 
              width = 390, height = 450, align='center')
    app.QA.QAdraw()

def nQA_onMousePress(app, mx, my):
    app.QA.mouseControl(mx, my, app)

def NeptuneEnd_redrawAll(app):
    drawImage(CMUImage(Image.open('images/neptuneland.jpg')), 0, 0,
              width = app.width, height = app.height)
    drawImage(CMUImage(Image.open('images/neptunegod.png')), 275, 425, 
              width = 435, height = 500, align='center')
    drawImage(CMUImage(Image.open('images/jewel.png')), 615, 580, 
              width = 200, height = 200, align='center')
    app.exitButton.draw()
    app.QA.endDraw()

def NeptuneEnd_onMousePress(app, mouseX, mouseY):
    if app.exitButton.clickOn(mouseX, mouseY):
        setActiveScreen('space')
        app.paused = False

def main():
    runAppWithScreens(initialScreen='start')

main()