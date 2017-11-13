import libtcodpy as libtcod
import random

#these represent squares on the grid, will probably switch to a different way of doing this eventually
char_water = 0
char_boat = 1
char_miss = 2
char_hit = 3

#these are vectors representing the direction that boats are facing
north = (0,1)
south = (0,-1)
east = (1,0)
west = (-1,0)

#this isn't used anymore, but might be useful sometime so we'll keep it around
nameMap = {"Aircraft Carrier" : "AIRCR",
            "Battleship" : "BATL",
            "Submarine" : "SUB",
            "Cruiser" : "CRS",
            "Destroyer" : "DT"}

#give each ship class a different color for fun
colorMap = {"Aircraft Carrier" : libtcod.Color(142,56,142),
            "Battleship" : libtcod.Color(113,113,198),
            "Submarine" : libtcod.Color(56,142,142),
            "Cruiser" : libtcod.Color(142,142,60),
            "Destroyer" : libtcod.Color(198,113,113)}

remoteCommand = ()
#it's a boat
class BoatBooty:
    color = None
    length = 1
    direction = east
    location = (0,0)
    name = "a boat name goes here"
    shipClass = "the type of boat goes here"
    squares = []
    #the idChar is what character is drawn to the console to represent the boat on the grid
    idChar = ''
    def __init__(self, name, shipClass, length, idChar):
        self.length = length
        self.name = name
        self.shipClass = shipClass
        self.idChar = idChar
        self.color = colorMap[shipClass]


class Fleet:


    def __init__(self):
        #just something in the meantime until we get proper states
        self.ourTurn = True
        self.cursor = (4,4)

        #set up our own fleet of:
        # 1 aircraft carrier
        # 1 battleship
        # 1 submarine
        # 2 destroyers
        # 2 cruisers

        self.fleetBoats = [BoatBooty("Boat 1","Aircraft Carrier",5,'1'),
                      BoatBooty("Boat 2","Battleship",4,'2'),
                      BoatBooty("Submarine Boat","Submarine",3,'3'),
                      BoatBooty("Boat 3","Cruiser",3,'4'),
                      BoatBooty("Boat 4","Cruiser",3,'5'),
                      BoatBooty("Boat 5","Destroyer",2,'6'),
                      BoatBooty("Boat 6","Destroyer",2,'7')]


        #set up the grid
        #I'll use a dict with a tuple (x,y) as a key instead of a 2D list, I just like it better
        self.playGrid = dict()
        self.gridSize = 10

        #scale for enemy display
        self.scaleSizeX = 2
        self.scaleSizeY = 2
        #use our own console so we can composite it with stuff
        self.con = libtcod.console_new(self.gridSize, self.gridSize)
        #let's set up a console for the boat readout so we can move it around
        self.conReadout = libtcod.console_new(45, 10)

        #grid for displaying fleets from the point of view of the enemy
        self.conEnemy = libtcod.console_new(self.gridSize * self.scaleSizeX, self.gridSize * self.scaleSizeY)
        #readout for enemy fleet
        self.conReadoutEnemy = libtcod.console_new(45, 10)

        for x in range(self.gridSize):
            for y in range(self.gridSize):
                self.playGrid[(x,y)] = char_water


    #update a boat's position
    def setBoatPosition(self,boat,newLocation,newDirection):
        #if we're trying to update to an invalid position, forget it
        if(self.verifyBoatPosition(newLocation,newDirection,boat.length) == False):
            #boat crime detected, beat it before the cops come
            return False
        boat.direction = newDirection
        boat.location = newLocation
        boat.squares = []

        #figure out which squares belong to this boat
        for i in xrange(boat.length):
            x = boat.location[0] + (boat.direction[0] * i)
            y = boat.location[1] + (boat.direction[1] * i)
            boat.squares.append((x,y))
            self.playGrid[(x,y)] = char_boat

        #everything checks out at this point
        return True

    #make sure a given boat position doesn't intersect with other boats or go off the grid
    def verifyBoatPosition(self,location,direction,length):

        #verify that the actual location (origin of the boat) fits on the grid
        if (location[0] < 0 or location[1] < 0 or
            location[0] > self.gridSize - 1 or location[1] > self.gridSize - 1):
                return False

        #verify that the squares that make up the length of the boat are within the grid also
        for i in xrange(length):
            x = location[0] + (direction[0] * i)
            y = location[1] + (direction[1] * i)

            if(x > self.gridSize - 1 or x < 0 or
               y > self.gridSize - 1 or y < 0 or
               self.playGrid[(x,y)] != char_water):
                return False
        return True

    def drawReadout(self,cx,cy):
        libtcod.console_set_default_foreground(self.conReadout, libtcod.white)
        libtcod.console_print(self.conReadout,1,0, 'YOUR FLEET:')
        for o in xrange(len(self.fleetBoats)):
            libtcod.console_set_default_foreground(self.conReadout, self.fleetBoats[o].color)
            libtcod.console_print(self.conReadout,1,o + 1,
                                  self.fleetBoats[o].idChar + ": The " +
                                  self.fleetBoats[o].shipClass + ", " +
                                  self.fleetBoats[o].name)
        #blit to root console
        libtcod.console_blit(self.conReadout, 0, 0, 0, 0, 0, cx, cy)

    def drawReadoutEnemy(self,cx,cy):
        libtcod.console_set_default_foreground(self.conReadoutEnemy, libtcod.white)
        libtcod.console_print(self.conReadoutEnemy,1,0, 'ENEMY FLEET:')
        for o in xrange(len(self.fleetBoats)):
            libtcod.console_set_default_foreground(self.conReadoutEnemy, libtcod.Color(100,100,100))
            libtcod.console_print(self.conReadoutEnemy,1,o + 1,
                                  '?' + ": Unknown " +
                                  self.fleetBoats[o].shipClass)
                                  #self.fleetBoats[o].name + ".")
        #blit to root console
        libtcod.console_blit(self.conReadoutEnemy, 0, 0, 0, 0, 0, cx, cy)

    def drawGrid(self,cx,cy):
        libtcod.console_set_default_foreground(self.con, libtcod.white)
        #draw the grid
        for x in xrange(self.gridSize):
            for y in xrange(self.gridSize):
                if self.playGrid[(x,y)] == char_water:
                    libtcod.console_put_char(self.con, x, y, '\'', libtcod.BKGND_NONE)
                elif self.playGrid[(x,y)] == char_miss:
                    libtcod.console_put_char(self.con, x, y, 'X', libtcod.BKGND_NONE)
                elif self.playGrid[(x,y)] == char_hit:
                    libtcod.console_put_char(self.con, x, y, 'O', libtcod.BKGND_NONE)

        #draw the boats on top of the grid, will eventually only happen for the player's own side
        for daBoat in self.fleetBoats:
            libtcod.console_set_default_foreground(self.con, daBoat.color)
            for point in daBoat.squares:
                if self.playGrid[(point)] != char_hit:
                    libtcod.console_put_char(self.con, point[0], point[1], str(daBoat.idChar), libtcod.BKGND_NONE)
                else:
                    libtcod.console_put_char(self.con, point[0], point[1], '*', libtcod.BKGND_NONE)
        #blit to root console
        libtcod.console_blit(self.con, 0, 0, 0, 0, 0, cx, cy)

    #draws a given fleet from the perspective of the enemy

    #TODO: refactor this, it's terrible
    def drawEnemyGrid(self,fl,cx,cy):
        libtcod.console_set_default_foreground(self.conEnemy, libtcod.white)
        def placeBlock(x, y, squareType):
                #inner cell
                if (x / self.scaleSizeX % 2 == 0 and y / self.scaleSizeY % 2 == 0
                    or x / self.scaleSizeX % 2 != 0 and y / self.scaleSizeY % 2 != 0):
                    libtcod.console_set_default_background(self.conEnemy, libtcod.Color(40,40,40))
                else:
                    libtcod.console_set_default_background(self.conEnemy, libtcod.Color(60,60,60))

                #if squareType == char_hit
                if squareType == char_hit:
                    libtcod.console_set_default_foreground(self.conEnemy, libtcod.Color(215,60,60))
                    libtcod.console_put_char(self.conEnemy, x, y, 218, libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y, 191, libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x, y + 1, 192, libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y + 1, 217, libtcod.BKGND_SET)
                elif squareType == char_miss:
                    libtcod.console_set_default_foreground(self.conEnemy, libtcod.Color(98,98,98))
                    libtcod.console_put_char(self.conEnemy, x, y, 'M', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y, 'I', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y + 1, 'S', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x, y + 1, 'S', libtcod.BKGND_SET)
                else:
                    libtcod.console_put_char(self.conEnemy, x, y, ' ', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y, ' ', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x + 1, y + 1, ' ', libtcod.BKGND_SET)
                    libtcod.console_put_char(self.conEnemy, x, y + 1, ' ', libtcod.BKGND_SET)



        for x in xrange(fl.gridSize):
            for y in xrange(fl.gridSize):
                placeBlock(x*self.scaleSizeX,y*self.scaleSizeY, fl.playGrid[(x,y)])

        #draw targeting cursor if it's our turn
        if self.ourTurn:
            libtcod.console_set_default_background(self.conEnemy, libtcod.Color(20,200,20))
            libtcod.console_set_char_background(self.conEnemy, self.cursor[0] * self.scaleSizeX, self.cursor[1] * self.scaleSizeY, libtcod.Color(20,200,20))
            libtcod.console_set_char_background(self.conEnemy, self.cursor[0] * self.scaleSizeX + 1, self.cursor[1] * self.scaleSizeY, libtcod.Color(20,200,20))
            libtcod.console_set_char_background(self.conEnemy, self.cursor[0] * self.scaleSizeX + 1, self.cursor[1] * self.scaleSizeY + 1, libtcod.Color(20,200,20))
            libtcod.console_set_char_background(self.conEnemy, self.cursor[0] * self.scaleSizeX, self.cursor[1] * self.scaleSizeY + 1, libtcod.Color(20,200,20))
        #blit to root console
        libtcod.console_blit(self.conEnemy, 0, 0, 0, 0, 0, cx, cy)

    #update grid after firing at enemy fleet
    def fireRound(self,en):
        #print (en.playGrid[(self.cursor[0],self.cursor[1])])
        if en.playGrid[(self.cursor[0],self.cursor[1])] == char_boat:
            en.playGrid[(self.cursor[0],self.cursor[1])] = char_hit
            return 'hit'
        elif en.playGrid[(self.cursor[0],self.cursor[1])] == char_water:
            en.playGrid[(self.cursor[0],self.cursor[1])] = char_miss
            return 'miss'
        else:
            return 'invalid'
    def validateCursor(self,en):
        if en.playGrid[(self.cursor[0],self.cursor[1])] != char_hit and en.playGrid[(self.cursor[0],self.cursor[1])] != char_miss:
            return True
        else:
            return False
    def randomizeBoats(self):
        for b in xrange(len(self.fleetBoats)):
            x = random.randrange(self.gridSize)
            y = random.randrange(self.gridSize)
            dirs = [north, east, south, west]
            directionIndex = random.randrange(4)

            while self.setBoatPosition(self.fleetBoats[b],(x,y),dirs[directionIndex]) == False:
                x = random.randrange(self.gridSize)
                y = random.randrange(self.gridSize)
                directionIndex = random.randrange(4)

    def isDead(self):
        for b in self.fleetBoats:
            for point in b.squares:
                if self.playGrid[(point[0],point[1])] != char_hit:
                    return False
        return True

#main class for the game
class Battleship:

    def __init__(self):
        self.player = Fleet()
        self.enemy = Fleet()
        #self.enemyGrid = None

        self.stateMenu = 4
        self.stateGameOver = 5
        self.statePlayerTarget = 0
        self.statePlayerResult = 1
        self.stateEnemyTarget = 2
        self.stateEnemyResult = 3

        #self.player.randomizeBoats()
        #self.enemy.randomizeBoats()

        self.state = self.stateMenu
        self.statusText = ["It is your turn.", "Use ARROW KEYS to select target.", "confirm target with SPACE."]
    #handle input
    def handleKeys(self):
        key = libtcod.console_check_for_keypress(True)
        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'

        if self.state == self.statePlayerTarget:
            if key.vk == libtcod.KEY_LEFT and key.pressed and self.player.cursor[0] > 0:
                self.player.cursor = (self.player.cursor[0] - 1, self.player.cursor[1])
            elif key.vk == libtcod.KEY_RIGHT and key.pressed and self.player.cursor[0] < self.player.gridSize - 1:
                self.player.cursor = (self.player.cursor[0] + 1, self.player.cursor[1])
            elif key.vk == libtcod.KEY_UP and key.pressed  and self.player.cursor[1] > 0:
                self.player.cursor = (self.player.cursor[0], self.player.cursor[1] - 1)
            elif key.vk == libtcod.KEY_DOWN and key.pressed and self.player.cursor[1] < self.player.gridSize - 1:
                self.player.cursor = (self.player.cursor[0], self.player.cursor[1] + 1)
            elif key.vk == libtcod.KEY_SPACE and key.pressed:
                if self.player.validateCursor(self.enemy) != False:
                    self.state = self.statePlayerResult
                    return 'valid_shot'
        #elif self.state == self.statePlayerResult:
        #    if key.vk == libtcod.KEY_SPACE and key.pressed:
        #        self.state = self.stateEnemyTarget
        #elif self.state == self.stateEnemyResult:
        #    if key.vk == libtcod.KEY_SPACE and key.pressed:
        #        self.state = self.statePlayerTarget

    def update(self):
        
        if self.state == self.statePlayerTarget:
            self.player.ourTurn = True
            self.statusText = ["It is your turn.", "Use ARROW KEYS to select target.", "confirm target with SPACE."]
        #elif self.state == self.statePlayerResult:
        #    self.statusText = ["Shot fired at location " + str('ABCDEFGHIJ')[self.player.cursor[1]] + "," + str(self.player.cursor[0])]
        #    if self.enemy.playGrid[(self.player.cursor[0],self.player.cursor[1])] == char_hit:
        #        self.statusText.append("The shot HITS.")
        #    else:
        #        self.statusText.append("The shot MISSES.")
        #    #self.statusText.append("Press SPACE to continue.")
        elif self.state == self.stateEnemyTarget:

            self.player.ourTurn = False
            self.statusText = ["It is the enemy's turn.", "Will fortune smile upon you?"]
            #
            # #ai cursor picks random square because it sucks
            # self.enemy.cursor = (random.randrange(self.enemy.gridSize),random.randrange(self.enemy.gridSize))
            #fireResult = self.enemy.fireRound(self.player)
            # cnt = 0
            # while fireResult == 'invalid':
            #     self.enemy.cursor = (random.randrange(self.enemy.gridSize),random.randrange(self.enemy.gridSize))
            #     cnt += 1
            #     if(cnt > 100):
            #         break
            #if fireResult == 'hit':
            #     self.statusText = ["The enemy shot HITS.", "Press SPACE to continue."]
            #elif fireResult == 'miss':
            #    self.statusText = ["The enemy shot MISSES.", "Press SPACE to continue."]
            #else:
            #    self.statusText = ["Press SPACE to continue."]
            #self.state = self.stateEnemyResult
            
        #if self.state != self.stateMenu or self.state != self.stateGameOver:
        #    self.drawGameScreen()
        
    def drawGameScreen(self):
        self.player.drawGrid(1,1)
        self.player.drawReadout(11,1)

        self.player.drawEnemyGrid(self.enemy,2,13)

        rulerString = 'ABCDEFGHIJ'

        #draw the ruler for the grid, should move this somewhere not dumb
        #i'm really tired so don't hassle me about putting it here you piece of shit i will gut you
        for xx in xrange(self.player.gridSize):
            libtcod.console_put_char(0, 3 + (xx * 2), 12, str(xx), libtcod.BKGND_NONE)
        for yy in xrange(self.player.gridSize):
            libtcod.console_put_char(0, 1, 14 + (yy * 2), rulerString[yy], libtcod.BKGND_NONE)

        #enemy.drawReadoutEnemy(enemy.gridSize * enemy.scaleSizeX + 2, 13)
        libtcod.console_rect(0,self.player.gridSize * self.player.scaleSizeX + 2, 13, 50, 50, True)
        for l in xrange(len(self.statusText)):
            libtcod.console_print(0, self.player.gridSize * self.player.scaleSizeX + 2, 13+l, self.statusText[l])
        #libtcod.image_blit(img, 0, enemy.gridSize * enemy.scaleSizeX + 9, 28, libtcod.BKGND_SET, 0.25, 0.25, 0)


        #flush the console because we done a poop in it
        libtcod.console_flush()




if __name__ == '__main__':
    #set up the console window, this will eventually be replaced by something more robust (much like your posting)
    libtcod.console_set_custom_font('prestige12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(60, 50, 'ASCIIship', False)


    game = Battleship()

    #main loop
    #img = libtcod.image_load('skull.png')
    #libtcod.image_set_key_color(img,libtcod.black)



    while not libtcod.console_is_window_closed():

        game.update()

        #maybe the user wants to quit or do other things? let's find out
        shouldExit = game.handleKeys()
        if shouldExit == 'exit':
            break

