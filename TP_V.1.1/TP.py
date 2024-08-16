# background = 1400 * 600
# note: number "250" in code basically means 250ms; however, since python's timerDelay
# is not precise, 250 is basically 1 second(1000ms) you can see in game.

import math, copy, random

from cmu_112_graphics import *

#################################################
# OOPs
#################################################

# Plant class
class Plants:
    # default plants 
    def __init__(self):
        self.leftX = None
        self.damage = 1
        self.health = self.fullHealth = 6
        self.time = 0
        self.cooldown = 200 # approx. 10 seconds

    def location(self, x, y):
        self.x = x
        self.y = y

    def getAttacked(self, app, damage):
        self.health -= damage
        if self.leftX == None:
            self.leftX = self.x + 35 # initializing self.leftX
        self.leftX = self.leftX - 70 / self.fullHealth * damage # the bar is 70 pixels long
        if self.health <= 0:
            row, col = self.index
            app.lawnPlants[row][col] = None
    
    def drawHealthBar(self, app, canvas):
        canvas.create_rectangle(self.x - 35, self.y - 35,
                                self.x + 35, self.y - 45, fill = 'red')
        if self.leftX != None:
            canvas.create_rectangle(self.leftX, self.y - 35,
                                    self.x + 35, self.y - 45, fill = 'black')

# Shooter sub-class
class Shooter(Plants):
    def __init__(self):
        super().__init__()
        self.bullets = []
        self.attackSpeed = 1.5 # shoots every 1.5 seconds
        self.time = self.attackSpeed * 250 # the plant is ready to shoot
        self.slowDown = 0 # default shooter does not slow down zombies

    # These functions are used by all shooter plants
    def timerFired(self, app):
        self.time += app.timerDelay
        for index in range(len(self.bullets)):
            self.bullets[index] += 10            
            if self.bullets[0] >= 800: # first bullet out of range
                self.bullets.pop(0)
                break
        for zombie in app.zombies:
            if self.y - zombie.y == 25: # if the plant and the zombie is on the same row
                self.attack(app)
                if len(self.bullets) != 0 and zombie.x - self.bullets[0] <= 20:
                    zombie.getAttacked(app, self.damage)
                    # slow the zombie down in some cases(i.e. if the snow pea hits the zombie, slow the zombie down)
                    zombie.dx += self.slowDown
                    # if they touch, the bullet disappear
                    self.bullets.pop(0)

    def attack(self, app):
        # attacks every self.attackSpeed seconds
        if self.time >= self.attackSpeed * 250:
            self.bullets.append(self.x)
            self.time = 0

class Peashooter(Shooter):
    def __init__(self):
        super().__init__()
        self.cost = 100

    def drawPea(self, app, canvas):
        for x in self.bullets:
            canvas.create_image(x, self.y, image = getCachedPhotoImage(app, app.pea))

    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.peashooterCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.peashooter))

class Repeater(Shooter):
    def __init__(self):
        super().__init__()
        self.cost = 200
        self.shoot = True
    
    # override timerFired function
    def timerFired(self, app):
        self.time += app.timerDelay
        for index in range(len(self.bullets)):
            self.bullets[index] += 10            
            if self.bullets[0] >= 800: # first bullet out of range
                self.bullets.pop(0)
                break
        for zombie in app.zombies:
            if self.y - zombie.y == 25: # if the plant and the zombie is on the same row
                if self.shoot:
                    self.attack1(app) # shoots the first pea
                else:
                    self.attack2(app) # shoots the second pea
                if len(self.bullets) != 0 and zombie.x - self.bullets[0] <= 20:
                    zombie.getAttacked(app, self.damage)
                    # if they touch, the bullet disappear
                    self.bullets.pop(0)  

    def attack1(self, app):
        # attacks every self.attackSpeed*0.8 seconds
        if self.time >= self.attackSpeed * 200:
            self.bullets.append(self.x)
            self.time = 0
            self.shoot = False

    def attack2(self, app):
        # attacks every self.attackSpeed*0.2 seconds
        if self.time >= self.attackSpeed * 50:
            self.bullets.append(self.x)
            self.time = 0
            self.shoot = True
    
    def drawPea(self, app, canvas):
        for x in self.bullets:
            canvas.create_image(x, self.y, image = getCachedPhotoImage(app, app.pea))

    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.repeaterCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.repeater))

class Snowpea(Shooter):
    def __init__(self):
        super().__init__()
        self.cost = 175
        self.slowDown = 0.3

    def drawPea(self, app, canvas):
        for x in self.bullets:
            canvas.create_image(x, self.y, image = getCachedPhotoImage(app, app.frozenPea))

    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.snowpeaCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.snowpea))

# Projectile sub-class
class Projectile(Plants):
    # the default dx(the distance between the projectile plant and zombie) is 800
    def __init__(self):
        super().__init__()
        self.distance = 800
        self.bulletX = self.bulletY = -10 # initializing bullet
        self.times = 4
        self.bullet = False
        self.attackSpeed = 3
        self.time = self.attackSpeed * 250 # the plant is ready to shoot

    def timerFired(self, app):
        if self.bullet:
            self.getChanges(app)
            self.hitZombie(app)
            if self.time >= self.attackSpeed * 250:
                self.bullet = False # disappear if it didn't touch the zombie
        # get the first zombie at the same row
        else:
            self.bulletX = self.bulletY = -10 #reset the bullet position

        self.time += app.timerDelay
        for zombie in app.zombies:
                if self.y - zombie.y == 25: # if the plant and the zombie is on the same row
                    if self.time >= self.attackSpeed * 250:
                        self.attack(app)
                        self.time = 0               

    # complex physics calculation(very complex!!!!! It took me 5 hours to figure it out!!)
    # numbers are based on the graphics layout
    # the 125 as a denominator basically means it happens every half second
    # the *2, *4, etc. will basically make the parabola bigger
    # Every "self.times" is 171.8 pixels, and the times depend on self.distance
    # self.distance is the distance between the plant and the first zombie in the row
    def getChanges(self, app):
        v0 = (14.7 / math.sin(app.theta)) * 2
        self.times = self.distance / 171.8
        self.bulletX = self.x + (v0 * self.time / 125) * math.cos(app.theta) * self.times
        self.bulletY = self.y - ((v0 * math.sin(app.theta) * self.time / 125) - 0.5 * app.g * (self.time / 125) ** 2) * 4

    def attack(self, app):
        self.distance = 800 # reset self.distance
        for zombie in app.zombies:
            if self.y - zombie.y == 25: # if the plant and the zombie is on the same row
                if zombie.isMoving:
                    # zombie is moving 25 times per second
                    currDistance = zombie.x - self.x + zombie.dx * 25 * self.attackSpeed
                else:
                    currDistance = zombie.x - self.x
                if currDistance < self.distance:
                    self.distance = currDistance
        self.bullet = True
    
    def hitZombie(self, app):
        for zombie in app.zombies:
            if (zombie.x - self.bulletX <= 50 and zombie.y - self.bulletY <= 20 and
                self.y - zombie.y == 25): # on the same row
                zombie.getAttacked(app, self.damage)
                # reset the bullet
                self.bullet = False

class KernelPult(Projectile):
    def __init__(self):
        super().__init__()
        self.cost = 100
        self.bulletType = "Kernel"

    # override hitZombie because kernel pult will stop the zombie from moving
    # if a butter hits the zombie
    def hitZombie(self, app):
        for zombie in app.zombies:
            if (zombie.x - self.bulletX <= 50 and zombie.y - self.bulletY <= 20 and
                self.y - zombie.y == 25): # on the same row
                zombie.getAttacked(app, self.damage)
                # reset the bullet
                self.bullet = False
                if self.bulletType == "Butter":
                    zombie.dx = 0
    
    # override attack function, everytime a kernel pult attacks it will 
    # have a chance shooting butter to stop the zombie for 3 seconds.
    def attack(self, app):
        self.distance = 800 # reset self.distance
        for zombie in app.zombies:
            if self.y - zombie.y == 25: # if the plant and the zombie is on the same row
                if zombie.isMoving:
                    # zombie is moving 25 times per second
                    currDistance = zombie.x - self.x + zombie.dx * 25 * self.attackSpeed
                else:
                    currDistance = zombie.x - self.x
                if currDistance < self.distance:
                    self.distance = currDistance
        self.bullet = True
        # this deternmines what kernel pult shoots
        butterChance = random.randint(1, 5) # 20% chance shooting butter
        if butterChance == 1:
            self.bulletType = "Butter"
        else:
            self.bulletType = "Kernel"


    def drawBullet(self, app, canvas):
        if self.bulletType == "Butter":
            canvas.create_image(self.bulletX, self.bulletY, image = getCachedPhotoImage(app, app.butter))
        else:
            canvas.create_image(self.bulletX, self.bulletY, image = getCachedPhotoImage(app, app.kernel))

    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.kernelPultCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.kernelPult))

# Sun sub-class
class Sun(Plants):
    def __init__(self):
        super().__init__()
        self.produce = False

    def timerFired(self, app):
        self.time += app.timerDelay
        # the time is weird, 250ms here is 1000ms shown on screen so just ignore the number
        if self.time >= self.productionSpeed * 250:
            self.produce = True
            self.time = 0
            # reset the production speed between 15-24 seconds
            self.productionSpeed = random.randint(15, 24)

    # collect the sun
    def mousePressed(self, app, event):
        # the sun will disappear and the sun count will increase
        if self.produce:
            self.produce = False
            app.sunCount += 25

    def containsSun(self, x, y):
        # the sun is 59 * 59 pixels
        return (self.x - 30 < x < self.x + 30 and self.y - 30 < y < self.y + 30)

class Sunflower(Sun):
    def __init__(self):
        super().__init__()
        self.cooldown = 100 # approx. 5 seconds
        self.cost = 50
        # it produces a sun between every 15-24 seconds
        self.productionSpeed = random.randint(15, 24)
        self.damage = 0
    
    def drawSun(self, app, canvas):
        if self.produce:
            canvas.create_image(self.x, self.y, image = getCachedPhotoImage(app, app.sun))

    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.sunflowerCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.sunflower))

# Shield sub-class
class Shield(Plants):
    def __init__(self):
        super().__init__()
        self.cooldown = 600 # approx. 30 seconds

class Wallnut(Shield):
    def __init__(self):
        super().__init__()
        self.health = self.fullHealth = 72
        self.cost = 50
        self.damage = 0
    
    def drawCard(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.wallnutCard))

    def drawPlant(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.wallnut))

# Zombie class
class Zombies:
    def __init__(self):
        self.attack = False
        self.eatTime = 0
        self.moveTime = 0

    def getZombieLocation(self, app):
        # the zombie always pick the weakest row
        self.row = Zombies.findWeakRow(app) + 1
        self.x = app.width # app.width
        self.y = 65 + (self.row - 0.5) * app.lawnBoxHeight # get the cy
        self.leftX = self.x + 20

    @staticmethod
    def findWeakRow(app):
        bestRow = None
        bestAttack = None
        bestHealth = None
        for row in range(len(app.lawnPlants)):
            currAttack = 0
            currHealth = 0
            for plant in app.lawnPlants[row]: # plants in a row
                if plant != None:
                    currHealth += plant.health
                    currAttack += plant.damage
            # initialize best row to row 0
            if bestAttack == None and bestHealth == None:
                bestRow = row
                bestAttack = currAttack
                bestHealth = currHealth
            # elif the curr attack is less than the best attack and
            # the curr health is around best health, update best row
            elif currAttack < bestAttack and currHealth - 5 < bestHealth:
                bestRow = row
                bestAttack = currAttack
                bestHealth = currHealth
            # elif the row has the same damage but less health, update
            elif currAttack == bestAttack and currHealth < bestHealth:
                bestRow = row
                bestAttack = currAttack
                bestHealth = currHealth
        return bestRow

    # zombies are generated harder as time goes on
    @staticmethod
    def timerFired(app):
        app.zombieTime += app.timerDelay
        if app.zombieTime >= app.nextGenTime * 250:
            Zombies.generateZombie(app)

            # update app.zombieInterval
            minSec, maxSec = app.zombieInterval
            if minSec > 0:
                minSec -= 1
            if maxSec > 5:
                maxSec -= 1
                app.zombieInterval = (minSec, maxSec)

            # update app.zombieLevel
            if app.zombieLevel >= 4:
                app.zombieLevel -= 1

            # update app.nextGenTime
            app.nextGenTime = Zombies.getNextGenerationTime(app)

            # reset the timer
            app.zombieTime = 0
        for zombie in app.zombies:
            zombie.moveZombie(app)

    @staticmethod
    def getNextGenerationTime(app):
        minSec, maxSec = app.zombieInterval
        nextGenTime = random.randint(minSec, maxSec)
        return nextGenTime

    @staticmethod
    def generateZombie(app):
        # the lower number the app.zombieLevel is, the higher chance coneheadZombie(harder) is picked
        r = random.randint(1, app.zombieLevel)
        if r == 1:
            coneheadZombie = ConeheadZombie()
            coneheadZombie.index = len(app.zombies)
            coneheadZombie.getZombieLocation(app)
            app.zombies.append(coneheadZombie)
        else:
            browncoatZombie = BrowncoatZombie()
            browncoatZombie.index = len(app.zombies)
            browncoatZombie.getZombieLocation(app)
            app.zombies.append(browncoatZombie)

    def moveZombie(self, app):
        self.attackPlants(app)
        self.eatTime += app.timerDelay
        self.moveTime += app.timerDelay
        # reset the speed every 3 seconds
        if self.moveTime >= 3 * 250:
            self.dx = self.fulldx
            self.moveTime = 0

        if self.attack == False:
            self.x += self.dx
            self.leftX += self.dx
            self.isMoving = True
        else:
            self.isMoving = False

    def attackPlants(self, app):
        for row in range(len(app.lawnPlants)):
            # zombie and the plant are on the same row
            if row + 1 == self.row:
                for plant in app.lawnPlants[row]:
                    if plant != None and self.x - plant.x <= 40:
                        self.attack = True
                        if self.eatTime >= 1 * 250: # zombie attacks every 1 second
                            plant.getAttacked(app, self.damage)
                            self.eatTime = 0
                        return
        self.attack = False

    def getAttacked(self, app, damage):
        self.health -= damage
        self.leftX -= 70 / self.fullHealth * damage
        if self.health <= 0:
            # remove the zombie from the list
            app.zombies.pop(self.index)
            # update the rest of the list
            for zombie in app.zombies:
                if zombie.index > self.index:
                    zombie.index -= 1
    
    def drawHealthBar(self, app ,canvas):
        canvas.create_rectangle(self.x - 50, self.y - 60,
                                self.x + 20, self.y - 70, fill = 'red')
        canvas.create_rectangle(self.leftX, self.y - 60,
                                self.x + 20, self.y - 70, fill = 'black')

    def redrawZombie(self, app, canvas):
        self.drawZombie(app, canvas, self.x ,self.y)
        self.drawHealthBar(app ,canvas)

class BrowncoatZombie(Zombies):
    def __init__(self):
        super().__init__()
        self.damage = 1
        self.health = self.fullHealth = 10
        self.dx = self.fulldx = -0.65

    def drawZombie(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.browncoatZombie))

class ConeheadZombie(Zombies):
    def __init__(self):
        super().__init__()
        self.damage = 1
        self.health = self.fullHealth = 28
        self.dx = self.fulldx = -0.65

    def drawZombie(self, app, canvas, x, y):
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.coneheadZombie))

#################################################
# app starts from here
#################################################

# copied from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#cachingPhotoImages
def getCachedPhotoImage(app, image):
    # stores a cached version of the PhotoImage in the PIL/Pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def appStarted(app):
    # whole background is 1400 * 600 pixels
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/3/38/Background1.jpg/revision/latest?cb=20160502033025
    app.backgroundImage = app.loadImage("Background1.jpeg")

    # load start page
    # url = https://tcrf.net/images/thumb/e/e9/PVZIOS_oldtitle.png/500px-PVZIOS_oldtitle.png
    startPage = app.loadImage("StartPage.png")
    app.startPage = app.scaleImage(startPage, 8/5)

    # load pause page
    # It's a screenshot from pvz so there is no url
    pausePage = app.loadImage("PausePage.png")
    app.pausePage = app.scaleImage(pausePage, 1/4)

    # load plants' image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/0/09/1769829-plant_peashooter_thumb.png/revision/latest/scale-to-width-down/183?cb=20200213115004
    peashooter = app.loadImage("Peashooter.png")
    app.peashooter = app.scaleImage(peashooter, 1/3)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/1/15/PeashooterSeedPacket.png/revision/latest?cb=20171030025422
    app.peashooterCard = app.loadImage("PeashooterCard.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/d/d2/Sunflower2009HD.png/revision/latest/scale-to-width-down/166?cb=20210727202431
    sunflower = app.loadImage("Sunflower.png")
    app.sunflower = app.scaleImage(sunflower, 1/3)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/8/81/SunflowerSeedPacket.png/revision/latest?cb=20171030030055
    app.sunflowerCard = app.loadImage("SunflowerCard.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/7/77/PvZ1HDWallNut.png/revision/latest/scale-to-width-down/160?cb=20220404001152
    wallnut = app.loadImage("Wallnut.png")
    app.wallnut = app.scaleImage(wallnut, 1/3)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/4/4b/Wall-nutSeedPacket.png/revision/latest?cb=20171030031251
    app.wallnutCard = app.loadImage("WallnutCard.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/a/a7/SP2009HD1.png/revision/latest/scale-to-width-down/250?cb=20170907050807
    snowpea = app.loadImage("Snowpea.png")
    app.snowpea = app.scaleImage(snowpea, 1/3)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/e/ed/SnowPeaSeedPacket.png/revision/latest?cb=20180103005826
    app.snowpeaCard = app.loadImage("SnowpeaCard.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/a/a9/RepeaterHD.png/revision/latest?cb=20171004061201
    repeater = app.loadImage("Repeater.png")
    app.repeater = app.scaleImage(repeater, 2/5)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/7/7a/RepeaterSeedPacket.png/revision/latest?cb=20171030033720
    app.repeaterCard = app.loadImage("RepeaterCard.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/e/eb/Kernel_Pult.png/revision/latest/scale-to-width-down/185?cb=20201226145323
    kernelPult = app.loadImage("KernelPult.png")
    app.kernelPult = app.scaleImage(kernelPult, 2/5)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/4/46/Kernel-pultSeedPacket.png/revision/latest?cb=20171101052813
    app.kernelPultCard = app.loadImage("KernelPultCard.png")

    # load peas' image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/7/7d/ProjectilePea.png/revision/latest?cb=20110415055741
    app.pea = app.loadImage("Pea.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/e/eb/ProjectileSnowPea.png/revision/latest?cb=20110331121534
    app.frozenPea = app.loadImage("FrozenPea.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/1/12/Cornpult_butter.png/revision/latest?cb=20110331062601
    app.butter = app.loadImage("Butter.png")
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/0/06/Cornpult_kernal.png/revision/latest?cb=20110624205420
    app.kernel = app.loadImage("Kernel.png")


    # load zombies' image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/a/a6/ZombieHD.png/revision/latest/scale-to-width-down/115?cb=20141029062941
    browncoatZombie = app.loadImage("Browncoat_Zombie.png")
    app.browncoatZombie = app.scaleImage(browncoatZombie, 16/25)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/2/26/ConeHead_Zombie.png/revision/latest/scale-to-width-down/96?cb=20201226144523
    coneheadZombie = app.loadImage("Conehead_Zombie.png")
    app.coneheadZombie = app.scaleImage(coneheadZombie, 16/25)

    # load sun image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/b/b8/Sun_PvZ2.png/revision/latest?cb=20160323031552
    sun = app.loadImage("Sun.png")
    app.sun = app.scaleImage(sun, 1/3)

    # load game over image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/d/d2/PvZ1ZombiesWon.png/revision/latest/scale-to-width-down/250?cb=20160123100344
    zombiesWon = app.loadImage("ZombiesWon.png")
    app.zombiesWon = app.scaleImage(zombiesWon, 5/2)

    # load you win image
    # url = https://cdna.artstation.com/p/assets/images/images/017/557/322/large/marvic-yao-gameover.jpg?1556478404
    playerWon = app.loadImage("PlayerWon.jpg")
    app.playerWon = app.scaleImage(playerWon, 2/5)

    # load progress bar image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/9/99/FlagMeter.png/revision/latest?cb=20160523010313
    progressBar = app.loadImage("ProgressBar.png")
    app.progressBar = progressBar.crop((0, 0, 158, 23))

    # load shovel image
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/f/f4/Shovel.jpg/revision/latest/smart/width/250/height/250?cb=20100319124445
    shovel = app.loadImage("Shovel.jpg")
    app.shovel = app.scaleImage(shovel, 2/7)
    # url = https://static.wikia.nocookie.net/plantsvszombies/images/b/ba/Shovel2.png/revision/latest?cb=20120319163030
    useShovel = app.loadImage("useShovel.png")
    app.useShovel = app.scaleImage(useShovel, 2/3)

    startGame(app)
    # these are related to the game difficulty
    app.zombieInterval = (20, 30) # zombies generates every 20-30 seconds
    app.zombieLevel = 10 # Difficulty, lower number = harder
    app.replayedTime = 0
    # game starts
    app.mode = "startStage"
    
def startGame(app):
    # start from the left end when app started
    app.croppedLeft = 0
    app.croppedRight = 800
    app.croppedBackground = app.backgroundImage.crop((app.croppedLeft, 0, app.croppedRight, app.height))
    app.imageWidth, app.imageHeight = app.backgroundImage.size
    app.timerDelay = 10

    # these are for stage 2 to draw the button
    app.buttonCx = 233
    app.buttonCy = 570
    app.buttonDx = 70
    app.buttonDy = 20

    # these are the data for the empty plant boxes
    app.boxWidth = 50
    app.boxHeight = 70

    # this records the box index during the last click
    app.box = None

    # these are the data for the squares on the lawn
    app.lawnBoxWidth = 81
    app.lawnBoxHeight = 95

    # chosen plant and mouse position(x, y)
    app.plant = None
    app.currentLawnBox = None
    app.mousePos = (-1, -1)

    # these are for projectile motion
    app.theta = math.pi/4
    app.g = 9.8

    # zombies' standing position when picking plants
    app.zombiePosition = [(650, 150), (700, 180), (530, 270), (680, 280), (740, 360),
                          (670, 380), (600, 430), (720, 500), (530, 500)]

    # initialize plants                      
    peashooter = Peashooter()
    sunflower = Sunflower()
    wallnut = Wallnut()
    snowpea = Snowpea()
    repeater = Repeater()
    kernelPult = KernelPult()

    # The selected plants layout
    app.selectedPlants = [None] * 6

    # This records the plants' cooldown
    app.cooldown = [-1] * len(app.selectedPlants)

    # The available plants layout
    app.allPlants = [[peashooter, sunflower, wallnut, snowpea, repeater, kernelPult, None, None],
                     [None, None, None, None, None, None, None, None],
                     [None, None, None, None, None, None, None, None],
                     [None, None, None, None, None, None, None, None],
                     [None, None, None, None, None, None, None, None]]
    # The lawn layout
    app.lawnPlants = [[None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None]]
    # These creates dictionaries that store the x&y data
    app.selectedPlantsDict = dict()
    app.allPlantsDict = dict()

    # It randomly generates the zombie's type and put all zombies into a list
    # The zombies are displayed when the player is choosing plants
    app.startingZombie = []
    for zombieIndex in range(len(app.zombiePosition)):
        zombieName = zombieIndex
        # Zombies are more likely to be browncoat zombies
        zomebieType = random.choice([BrowncoatZombie, BrowncoatZombie, ConeheadZombie])
        zombieName = zomebieType()
        app.startingZombie.append(zombieName)

    # used in stage 4 to generate zombies
    app.zombieTime = 0
    app.nextGenTime = 20 # Next zombie's generation time, 20 sec as default
    app.zombies = []

    # This set the sun to 50 when game starts
    app.sunCount = 50
    app.sunTime = 0 # the counter for the sun falling from the sky
    app.isSun = False # if there is a sun falling from the sky
    app.sunX = 600

    # records the shovel status
    app.hasShovel = False

    # game is not paused
    app.pause = False

    # records the game time
    app.gameTime = 0
    app.winTime = 300 # win after 300 seconds(5 minutes)
    app.leftX = 755 # for the progress bar
    app.move = 150 / app.winTime # pixel move per second

#################################################
# start stage
#################################################

'''
At this stage, the user will click on the button to start the game
'''
# if the user clicks on the button, game starts
def startStage_mousePressed(app, event):
    if 135 <= event.x <= 640 and 500 <= event.y <= 555:
        app.mode = "stage1"

def startStage_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.startPage))

def startStage_redrawAll(app, canvas):
    startStage_drawBackground(app, canvas)

#################################################
# stage 1
#################################################

'''
At this stage, the background will scroll to the right and let player pick the 
plants. After the player id done, it'll go to the next stage
'''

# When it hits the edge, it'll stop and let the player pick the plants
def stage1_timerFired(app):
    if app.croppedRight >= app.imageWidth:
        app.mode = "stage2"
        return
    app.croppedLeft += 10
    app.croppedRight += 10
    app.croppedBackground = app.backgroundImage.crop((app.croppedLeft, 0, app.croppedRight, app.height))

def stage1_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.croppedBackground))

def stage1_redrawAll(app, canvas):
    stage1_drawBackground(app, canvas)

#################################################
# stage 2
#################################################

'''
At this stage, the player will pick the plants and see the zombies that will 
appear in this level
'''

# if the player clicks on the button, game starts
def stage2_mousePressed(app, event):
    if (event.x >= app.buttonCx - app.buttonDx and 
        event.x <= app.buttonCx + app.buttonDx and 
        event.y >= app.buttonCy - app.buttonDy and 
        event.y <= app.buttonCy + app.buttonDy):
        if None not in app.selectedPlants:
            app.mode = "stage3"
        else:
            print("You must choose six plants!")
            return

    # if the player clicks on a selected plant, move it to all plants(unselected plants)
    elif stage2_isSelectedPlants(app, event.x, event.y) != None:
        shouldBreak = False
        box = stage2_isSelectedPlants(app, event.x, event.y)
        for row in range(len(app.allPlants)):
            for col in range(len(app.allPlants[0])):
                if app.allPlants[row][col] == None:
                    app.allPlants[row][col] = app.selectedPlants[box]
                    shouldBreak = True
                    break
            if shouldBreak == True:
                break
        app.selectedPlants[box] = None

    # if the player clicks on a unselected plant, move it to selected plants
    elif stage2_isAllPlants(app, event.x, event.y) != None:
        # if there are no more slots, do nothing
        if None not in app.selectedPlants:
            print("No more slots!!")
        else:
            row, col = stage2_isAllPlants(app, event.x, event.y)
            for index in range(len(app.selectedPlants)):
                if app.selectedPlants[index] == None:
                    app.selectedPlants[index] = app.allPlants[row][col]
                    break
            app.allPlants[row][col] = None

# it checks if the given x and y data is a selected plant's box
def stage2_isSelectedPlants(app, inputX, inputY):
    # This stores the data in the dictionary
    startX = 100
    startY = 10
    gap = 7
    for box in range(len(app.selectedPlants)):
        cx = startX + app.boxWidth * (box + 0.5)
        cy = startY + app.boxHeight * (0.5)
        app.selectedPlantsDict[box] = (cx, cy)
        startX += gap
    # if the x, y is in a box, return the corresponding box index
    for key in app.selectedPlantsDict:
        x, y = app.selectedPlantsDict[key]
        leftX = x - 25
        rightX = x + 25
        upY = y - 35
        downY = y + 35

        if leftX <= inputX <= rightX and upY <= inputY <= downY:
            return key
    return None

# it checks if the given x and y data is a all plant's box
def stage2_isAllPlants(app, inputX, inputY):
    # This stores the data in the dictionary
    startX = 15
    startY = 130
    gap = 5
    for col in range(len(app.allPlants[0])):
        for row in range(len(app.allPlants)):
            cx = startX + app.boxWidth * (col + 0.5)
            cy = startY + app.boxHeight * (row + 0.5)
            app.allPlantsDict[(row, col)] = (cx, cy)
            startY += gap
        startY = 130
        startX += gap

    # if the x, y is in a box, return the corresponding row and col
    for key in app.allPlantsDict:
        x, y = app.allPlantsDict[key]
        leftX = x - 25
        rightX = x + 25
        upY = y - 35
        downY = y + 35

        if leftX <= inputX <= rightX and upY <= inputY <= downY:
            return key
    return None

# This draws all the zombies in the list
def stage2_drawZombies(app, canvas):
    for zombieIndex in range(len(app.startingZombie)):
        zombie = app.startingZombie[zombieIndex]
        x, y = app.zombiePosition[zombieIndex]
        zombie.drawZombie(app, canvas, x, y)
        
# This draws the background
def stage2_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.croppedBackground))

# This draws the box that contains the selected plants
def stage2_drawSelectionBox(app, canvas):
    canvas.create_rectangle(0, 0, 450, 90, fill = 'tomato4')

# This draws the individual boxes that contain the plants player selected
def stage2_drawSelection(app, canvas):
    # The lines below draw the sun icon
    canvas.create_image(50, 40, image = getCachedPhotoImage(app, app.sun))
    canvas.create_rectangle(25, 65, 75, 85, fill = 'lemon chiffon')
    canvas.create_text(50, 75, text = app.sunCount, font = 'Arial 15 bold')
    # The lines below draw the plant boxes
    startX = 100
    startY = 10
    gap = 7
    for box in range(len(app.selectedPlants)):
        plant = app.selectedPlants[box]
        if plant == None:
            canvas.create_rectangle(startX + app.boxWidth * box, startY,
                                    startX + app.boxWidth * (box + 1), startY + app.boxHeight,
                                    fill = 'tomato3')
        else:
            plant.drawCard(app, canvas, startX + app.boxWidth * (box + 0.5), startY + app.boxHeight * (0.5))
        # It adds a gap between each box
        startX += gap

# This draws the big box that contains all the plants
def stage2_drawChoosePlantBox(app, canvas):
    canvas.create_rectangle(0, 90, 465, 600, fill = 'tomato4')
    canvas.create_text(233, 110, text = 'CHOOSE YOUR PLANTS!', fill = 'orange3',
                       font = 'Times 20 bold')

# This draws the individual box that contains one plant
def stage2_drawPlantBox(app, canvas):
    startX = 15
    startY = 130
    gap = 5
    for col in range(len(app.allPlants[0])):
        for row in range(len(app.allPlants)):
            plant = app.allPlants[row][col]
            # if there are no plants, draw a empty box
            if plant == None:
                canvas.create_rectangle(startX + app.boxWidth * col, startY + app.boxHeight * row,
                                    startX + app.boxWidth * (col + 1), startY + app.boxHeight * (row + 1),
                                    fill = 'tomato3')
            else:
                plant.drawCard(app, canvas, startX + app.boxWidth * (col + 0.5), startY + app.boxHeight * (row + 0.5))

            # It adds a gap between each row
            startY += gap
        # It resets the startY so the next col will line up with the others
        startY = 130
        # It adds a gap between each col
        startX += gap

# This draws the button at the bottom which allows players to start the game
def stage2_drawStartButton(app, canvas):
    canvas.create_rectangle(app.buttonCx - app.buttonDx, app.buttonCy - app.buttonDy, 
                            app.buttonCx + app.buttonDx, app.buttonCy + app.buttonDy, 
                            fill = 'tomato3')
    canvas.create_text(app.buttonCx, app.buttonCy, text = 'LET\'S ROCK!', 
                       fill = 'tomato4',font = 'Arial 20 bold')

def stage2_redrawAll(app, canvas):
    stage2_drawBackground(app, canvas)
    stage2_drawZombies(app, canvas)
    stage2_drawSelectionBox(app, canvas)
    stage2_drawSelection(app, canvas)
    stage2_drawChoosePlantBox(app, canvas)
    stage2_drawPlantBox(app,canvas)
    stage2_drawStartButton(app, canvas)

#################################################
# stage 3
#################################################

'''
At this stage, the background will move to the middle and the game starts. The 
background will not change anymore in the future
'''

def stage3_timerFired(app):
    if app.croppedLeft <= 220:
        app.mode = "stage4"
    app.croppedLeft -= 10
    app.croppedRight -= 10
    app.croppedBackground = app.backgroundImage.crop((app.croppedLeft, 0, app.croppedRight, app.height))

def stage3_drawSelectionBox(app, canvas):
    canvas.create_rectangle(0, 0, 450, 90, fill = 'tomato4')

# This draws the individual boxes that contain the plants player selected(copied from stage 2 but without the if statement)
def stage3_drawSelection(app, canvas):
    # The lines below draw the sun icon
    canvas.create_image(50, 40, image = getCachedPhotoImage(app, app.sun))
    canvas.create_rectangle(25, 65, 75, 85, fill = 'lemon chiffon')
    canvas.create_text(50, 75, text = app.sunCount, font = 'Arial 15 bold')
    # The lines below draw the plant boxes
    startX = 100
    startY = 10
    gap = 7
    for box in range(len(app.selectedPlants)):
        plant = app.selectedPlants[box]
        plant.drawCard(app, canvas, startX + app.boxWidth * (box + 0.5), startY + app.boxHeight * (0.5))
        # It adds a gap between each box
        startX += gap

def stage3_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.croppedBackground))

def stage3_redrawAll(app, canvas):
    stage3_drawBackground(app, canvas)
    stage3_drawSelectionBox(app, canvas)
    stage3_drawSelection(app, canvas)

#################################################
# stage 4
#################################################

'''
At this stage, game starts. The players will need to plant the plants to avoid zombies
from eating their brains.
'''

# When it hits the middle, it'll stop scrolling and start the game
def stage4_timerFired(app):
    app.croppedBackground = app.backgroundImage.crop((220, 0, 1020, app.height))
    if app.pause:
        return
    stage4_isLost(app)
    stage4_dropSkySun(app)
    stage4_updateCooldown(app)
    Zombies.timerFired(app)
    app.gameTime += app.timerDelay
    if app.gameTime % 250 == 0: # This changes the progress bar
        app.leftX -= app.move
        if app.leftX <= 605:
            app.mode = "playerWon"
    for row in range(len(app.lawnPlants)):
        for col in range(len(app.lawnPlants[0])):
            plant = app.lawnPlants[row][col]
            # if the plant is a shooter or projectile or sun, run the timerFired funtion
            if isinstance(plant, Shooter) or isinstance(plant, Projectile) or isinstance(plant, Sun):
                plant.timerFired(app)

def stage4_keyPressed(app, event):
    if event.key == "p":
        app.pause = not app.pause

def stage4_mousePressed(app, event):
    # if the player clicks on "resume game", game continues
    if app.pause:
        if app.width//2 - 100 <= event.x <= app.width//2 + 100 and app.height//2 + 75 <= event.y <= app.height//2 + 100:
            app.pause = False
        else:
            return
    # if the player clicks on a selected plants
    if stage4_isSelectedPlants(app, event.x, event.y) != None:
        app.box = stage4_isSelectedPlants(app, event.x, event.y)
        # if a plant is not in cool down, then the player can use it
        if app.cooldown[app.box] <= 0:
            app.plant = app.selectedPlants[app.box]
            app.mousePos = event.x, event.y
    # elif the player clicks on the sun from the sky
    elif (app.sunX - 30 <= event.x <= app.sunX + 30 and 70 <= event.y <= 130 and app.isSun):
        app.sunCount += 25
        app.isSun = False
    # elif the player clicks on the lawn area
    elif 30 <= event.x <= 758 and 90 <= event.y <= 565:
        row, col = stage4_getLawnBoxIndex(app, event.x, event.y)
        plant = app.lawnPlants[row][col]
        # if the player clicks on a sun
        if isinstance(plant, Sun):
            if plant.containsSun(event.x, event.y):
                plant.mousePressed(app, event)
    # elif the player clicks on the shovel
    elif 460 <= event.x <= 510 and 5 <= event.y <= 69:
        app.hasShovel = True
        app.mousePos = event.x, event.y

def stage4_mouseDragged(app, event):
    if app.pause:
        return
    # 30 + 9 * 81 = 758
    # 90 + 5 * 95 = 565
    if app.plant != None:
        app.mousePos = event.x, event.y
        if event.x <= 758 and event.y <= 565:
            app.currentLawnBox = stage4_getLawnBoxIndex(app, event.x, event.y)
        else:
            app.currentLawnBox = None
    elif app.hasShovel:
        app.mousePos = event.x, event.y
        app.currentLawnBox = stage4_getLawnBoxIndex(app, event.x, event.y)

def stage4_mouseReleased(app, event):
    if app.pause:
        return
    if app.plant != None and app.currentLawnBox != None:
        row, col = app.currentLawnBox
        # if there is already a plant, do nothing
        if app.lawnPlants[row][col] == None:
            plant = copy.deepcopy(app.plant)
            newSun = app.sunCount - plant.cost
            # if the sun is not enough, do nothing
            if newSun < 0:
                app.plant = None
                app.currentLawnBox = None
                return
            app.sunCount = newSun
            plant.index = (row, col)
            app.lawnPlants[row][col] = plant
            app.cooldown[app.box] = app.plant.cooldown # update cooldown

    elif app.hasShovel and app.currentLawnBox != None:
        row, col = app.currentLawnBox
        if app.lawnPlants[row][col] != None:
            app.lawnPlants[row][col] = None
    app.hasShovel = False
    app.plant = None
    app.currentLawnBox = None

# it checks if the given x and y data is a selected plant's box(copied from stage 2)
def stage4_isSelectedPlants(app, inputX, inputY):
    # This stores teh data in the dictionary
    startX = 100
    startY = 10
    gap = 7
    for box in range(len(app.selectedPlants)):
        cx = startX + app.boxWidth * (box + 0.5)
        cy = startY + app.boxHeight * (0.5)
        app.selectedPlantsDict[box] = (cx, cy)
        startX += gap
    # if the x, y is in a box, return the corresponding box index
    for key in app.selectedPlantsDict:
        x, y = app.selectedPlantsDict[key]
        leftX = x - 25
        rightX = x + 25
        upY = y - 35
        downY = y + 35

        if leftX <= inputX <= rightX and upY <= inputY <= downY:
            return key
    return None

# This gets the lawn box's index
def stage4_getLawnBoxIndex(app, x, y):
    # startX = 30, startY = 90, app.lawnBoxWidth = 81, app.lawnBoxHeight = 95
    x -= 30
    y -=90
    boxRow = y // 95
    boxCol = x // 81
    if boxRow >= 0 and boxCol >= 0:
        return (boxRow, boxCol)

# A sun will fall from the sky every 5 seconds
def stage4_dropSkySun(app):
    app.sunTime += app.timerDelay
    if app.sunTime >= 5 * 250:
        app.isSun = True
        app.sunX = random.randint(50, 750)
        app.sunTime = 0

# this updates the cooldown
def stage4_updateCooldown(app):
    for i in range(len(app.cooldown)):
        if app.cooldown[i] > 0:
            app.cooldown[i] -= 1

def stage4_isLost(app):
    for zombie in app.zombies:
        if zombie.x <= 0:
            app.mode = "zombiesWon"

def stage4_isWin(app):
    if app.gameTime >= app.winTime * 250: # if the user play for 5 minutes without losing
        app.mode = "playerWon"

def stage4_drawPausePage(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.pausePage))

def stage4_drawProgressBar(app, canvas):
    canvas.create_image(680, 585, image = getCachedPhotoImage(app, app.progressBar))
    canvas.create_rectangle(app.leftX, 580, 755, 590, fill = 'green')

def stage4_drawLevel(app, canvas):
    canvas.create_text(550, 585, text = f'level 1-{app.replayedTime}', font = 'Airal 15 bold')

def stage4_drawSkySun(app, canvas):
    if app.isSun:
        canvas.create_image(app.sunX, 100, image = getCachedPhotoImage(app, app.sun))

# This draws the box that contains the selected plants(copied from stage 2)
def stage4_drawSelectionBox(app, canvas):
    canvas.create_rectangle(0, 0, 450, 90, fill = 'tomato4')
    canvas.create_image(485, 37, image = getCachedPhotoImage(app, app.shovel))

# This draws the individual boxes that contain the plants player selected(copied from stage 2 but without the if statement)
def stage4_drawSelection(app, canvas):
    # The lines below draw the sun icon
    canvas.create_image(50, 40, image = getCachedPhotoImage(app, app.sun))
    canvas.create_rectangle(25, 65, 75, 85, fill = 'lemon chiffon')
    canvas.create_text(50, 75, text = app.sunCount, font = 'Arial 15 bold')
    # The lines below draw the plant boxes
    startX = 100
    startY = 10
    gap = 7
    for box in range(len(app.selectedPlants)):
        plant = app.selectedPlants[box]
        plant.drawCard(app, canvas, startX + app.boxWidth * (box + 0.5), startY + app.boxHeight * (0.5))
        # It adds a gap between each box
        startX += gap

# It draws the shovel if user has it
def stage4_drawShovel(app, canvas):
    if app.hasShovel:
        x, y = app.mousePos
        canvas.create_image(x, y, image = getCachedPhotoImage(app, app.useShovel))

# It draws the current plant
def stage4_drawPlant(app, canvas):
    if app.plant != None:
        x, y = app.mousePos
        app.plant.drawPlant(app, canvas, x, y)

# It draws the box that indicates the plant's position
def stage4_drawPlantBox(app, canvas):
    startX = 30
    startY = 90
    if app.currentLawnBox != None:
        blackRow, blackCol = app.currentLawnBox
    else:
        return
    canvas.create_rectangle(startX + app.lawnBoxWidth * blackCol, startY + app.lawnBoxHeight * blackRow, 
                                    startX + app.lawnBoxWidth * (blackCol + 1), startY + app.lawnBoxHeight * (blackRow + 1),
                                    fill = 'black')

# if a plant is in cooldown, draw black box on top of it
def stage4_drawCooldown(app, canvas):
    for i in range(len(app.cooldown)):
        if app.cooldown[i] > 0: 
            x, y = app.selectedPlantsDict[i]
            # adjust x and y to the top left of the box
            x -= app.boxWidth * 0.5
            y -= app.boxHeight * 0.5
            # this calculates the percentage time left of cooldown
            p = app.cooldown[i] / app.selectedPlants[i].cooldown
            
            canvas.create_rectangle(x, y, x+app.boxWidth, y+app.boxHeight*p, fill = "black")

# It draws the plants onto the lawn
def stage4_drawLawnPlants(app, canvas):
    startX = 30
    startY = 90
    for row in range(len(app.lawnPlants)):
        for col in range(len(app.lawnPlants[0])):
            if app.lawnPlants[row][col] != None:
                cx = startX + app.lawnBoxWidth * (col + 0.5)
                cy = startY + app.lawnBoxHeight * (row + 0.5)
                plant = app.lawnPlants[row][col]
                # it lets the plants store the location once it's placed on the lawn
                plant.location(cx, cy)
                plant.drawPlant(app, canvas, cx, cy)

def stage4_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.croppedBackground))

def stage4_redrawAll(app, canvas):
    stage4_drawBackground(app, canvas)
    stage4_drawSelectionBox(app, canvas)
    stage4_drawSelection(app, canvas)
    stage4_drawPlantBox(app, canvas)
    stage4_drawCooldown(app, canvas)
    stage4_drawLawnPlants(app, canvas)
    for zombie in app.zombies:
        zombie.redrawZombie(app, canvas)
    # This draws the plants' peas(bullets)
    for row in range(len(app.lawnPlants)):
        for col in range(len(app.lawnPlants[0])):
            plant = app.lawnPlants[row][col]
            if isinstance(plant, Plants):
                plant.drawHealthBar(app, canvas)
                if isinstance(plant, Shooter):
                    plant.drawPea(app, canvas)
                elif isinstance(plant, Projectile):
                    plant.drawBullet(app, canvas)
                elif isinstance(plant, Sun):
                    plant.drawSun(app, canvas)
    stage4_drawSkySun(app, canvas)
    stage4_drawProgressBar(app, canvas)
    stage4_drawLevel(app, canvas)
    stage4_drawPlant(app, canvas)
    stage4_drawShovel(app, canvas)
    if app.pause:
        stage4_drawPausePage(app, canvas)

#################################################
# zombies won mode
#################################################
'''
The user will click on the button to replay the game
'''
def zombiesWon_mousePressed(app, event):
    if (app.width//2 - 50 <= event.x <= app.width//2 + 50 and 
        app.height//2 - 20 <= event.y <= app.height//2 + 20):
        startGame(app)
        # reset the difficulty to the previous level
        app.zombieInterval = (20 - app.replayedTime * 5, 30 - app.replayedTime * 5)
        app.zombieLevel = 10 - app.replayedTime * 2
        app.mode = "stage1"

def zombiesWon_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.zombiesWon))

def zombiesWon_drawButtonAndText(app, canvas):
    canvas.create_text(app.width//2, app.height//2 - 90, text = "Press the button to play again",
                                                    font = 'Arial 30 bold', fill = 'brown')
    canvas.create_rectangle(app.width//2 - 50, app.height//2 - 20, 
                            app.width//2 + 50, app.height//2 + 20, 
                            fill = 'green')
    canvas.create_text(app.width//2, app.height//2, text = "Press me!", font = 'Arial 20 bold')

def zombiesWon_redrawAll(app, canvas):
    zombiesWon_drawBackground(app, canvas)
    zombiesWon_drawButtonAndText(app, canvas)

#################################################
# player won mode
#################################################

def playerWon_mousePressed(app, event):
    if (app.width//2 - 100 <= event.x <= app.width//2 + 100 and 
        app.height//2 + 70 <= event.y <= app.height//2 + 110):
        startGame(app)
        # the game becomes harder every time
        app.replayedTime += 1
        app.zombieInterval = (20 - app.replayedTime * 5, 30 - app.replayedTime * 5)
        app.zombieLevel = 10 - app.replayedTime * 2
        app.mode = "stage1"

def playerWon_drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
                        image = getCachedPhotoImage(app, app.playerWon))

def playerWon_drawButtonAndText(app, canvas):
    canvas.create_text(app.width//2, app.height//2 - 130, text = "Do you want to play again in a harder mode?",
                                                    font = 'Arial 30 bold', fill = 'grey')
    canvas.create_rectangle(app.width//2 - 100, app.height//2 + 70, 
                            app.width//2 + 100, app.height//2 + 110, 
                            fill = 'grey')
    canvas.create_text(app.width//2, app.height//2 + 90, text = "Press me to play!", font = 'Arial 20 bold')

def playerWon_redrawAll(app, canvas):
    playerWon_drawBackground(app, canvas)
    playerWon_drawButtonAndText(app, canvas)

#################################################
# run app
#################################################

runApp(width=800, height=600)