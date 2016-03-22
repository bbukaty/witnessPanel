import pygame
import math

black = (  0,  0,    0)
white = (255, 255, 255)
blue =  (  0,   0, 255)
green = (  0, 255,   0)
red =   (255,   0,   0)
clear = (1,1,1)
up = 0
right = 1
down = 2
left = 3

class Trace():
    def __init__(self, maze, startpos):
        #starting circle
        self.fullradius = int(maze.linewidth*1.15)
        self.currentradius = self.fullradius//3#start circle starts part of the way filled, as it does in game
        self.donegrowing = False
        self.width = maze.linewidth
        self.radius = self.width/2
        self.xborder = maze.wspace//2
        self.yborder = maze.hspace//2
        self.mazebarriers = maze.barriers
        self.mazesquaresize = maze.squaresize
        self.gridsquaresize = maze.squaresize+maze.linewidth
        self.color = maze.tracecolor
        self.pos = startpos
        self.startpos = tuple(startpos)
        self.path = [((self.pos[0] - self.xborder - self.width/2)/(self.mazesquaresize+self.width),
                            (self.pos[1] - self.yborder - self.width/2)/(self.mazesquaresize+self.width)),] #starting grid position for path
        self.pixelpath = [self.startpos]
        self.isonrow = True
        self.isoncolumn = True
        self.xtravelled = 0
        self.ytravelled = 0

        
    def update(self):
        #starting circle expansion
        if not self.donegrowing:
            if self.currentradius < self.fullradius:
                self.currentradius += math.ceil((self.fullradius - self.currentradius)/5)#dictates speed of start circle filling
            else:
                self.donegrowing = True
                
        #trace head movement
        mousepos = pygame.mouse.get_pos()
        diffx = mousepos[0] - self.pos[0] #diff between center of line head and mouse, not top left corner
        diffy = -mousepos[1] + self.pos[1] #reversed bc display y-axis is flipped
        fractiontomove = 4
        diffmargin = 2#prevents being in between pixels with cursor from making trace head oscillate 1 pixel

        self.ysquarestravelled = self.ytravelled/self.gridsquaresize
        self.xsquarestravelled = self.xtravelled/self.gridsquaresize
        
        if abs(diffy) > abs(diffx):#primary axis is up/down
            
            if self.xsquarestravelled.is_integer(): #trace is on grid column, can move up/down
                if diffy > diffmargin:#up
                    self.tryMove(diffy/fractiontomove, up)
                elif diffy < -diffmargin:#down
                    self.tryMove(abs(diffy)/fractiontomove, down)
            elif self.ysquarestravelled.is_integer(): #can't move up/down, try left/right
                if diffx > diffmargin:#right
                    self.tryMove(diffx/fractiontomove, right)
                elif diffx < -diffmargin:#left
                    self.tryMove(abs(diffx)/fractiontomove, left)
                    
                elif abs(diffy) > self.mazesquaresize//4:#if cursor getting far away, check if can snap to intersection
                    disttoisect = int((self.pos[0] - self.xborder - self.width/2)%(self.mazesquaresize+self.width))
                    if disttoisect <= self.width:#trace is 1 linewidth right of intersection 
                        self.tryMove(disttoisect, left)
                    elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is 1 linewidth left of intersection
                        self.tryMove(self.mazesquaresize + self.width - disttoisect, right)
                        
                        
        else:#primary axis is left/right
            
            if self.ysquarestravelled.is_integer(): #trace is on grid row, can move up/down as long as no border in way
                if diffx > diffmargin:#right
                    self.tryMove(diffx/fractiontomove, right)
                elif diffx < -diffmargin:#left
                    self.tryMove(abs(diffx)/fractiontomove, left)
            elif self.xsquarestravelled.is_integer(): #can't move left/right, try up/down
                if diffy > diffmargin:#up
                    self.tryMove(diffy/fractiontomove, up)
                elif diffy < -diffmargin:#down
                    self.tryMove(abs(diffy)/fractiontomove, down)
                
                elif abs(diffx) > self.mazesquaresize//4:#if cursor getting far away, check if can snap to intersection
                    disttoisect = int((self.pos[1] - self.yborder - self.width/2)%(self.mazesquaresize+self.width))
                    if disttoisect <= self.width:#trace is 1 linewidth below intersection 
                        self.tryMove(disttoisect,up)
                    elif disttoisect >= (self.mazesquaresize+self.width) - self.width:#trace is one linewidth above intersection
                        self.tryMove(self.mazesquaresize+self.width - disttoisect, down)
                        
                        
    def tryMove(self,dist_to_move,direction):
        distance = math.ceil(dist_to_move) #always try to move at least 1 pixel
        
        if direction == up:
            for i in range(distance):
                if self.ysquarestravelled.is_integer():
                    if len(self.path) == 0:#line is beginning
                        pass
                    elif self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending and coords to be added are not redundant
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                    if len(self.path) > 1 and self.path[0][0]+self.ysquarestravelled > self.path[-2][1] and self.path[-1][0] == self.path[-2][0]: #line is retracting
                        self.path.pop()
                        self.pixelpath.pop()
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][1])][int(self.path[-1][0])][up]
                if self.pos[1] - self.radius != self.currentbarrier:
                    self.pos[1] -= 1
                    self.ytravelled -= 1
                    self.ysquarestravelled = self.ytravelled/self.gridsquaresize
                else:
                    return
                
        elif direction == down:
            for i in range(distance):
                if self.ysquarestravelled.is_integer():
                    if len(self.path) == 0:#line is beginning
                        pass
                    elif self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                    if len(self.path) > 1 and self.path[0][0]+self.ysquarestravelled < self.path[-2][1] and self.path[-1][0] == self.path[-2][0]: #line is retracting
                        self.path.pop()
                        self.pixelpath.pop()
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][1])][int(self.path[-1][0])][down]
                if self.pos[1] + self.radius != self.currentbarrier:
                    self.pos[1] += 1
                    self.ytravelled += 1
                    self.ysquarestravelled = self.ytravelled/self.gridsquaresize
                else:
                    return
                
                
        elif direction == right:
            for i in range(distance):
                if self.xsquarestravelled.is_integer():
                    if len(self.path) == 0:#line is beginning
                        pass
                    elif self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                    if len(self.path) > 1 and self.path[0][0]+self.xsquarestravelled < self.path[-2][0] and self.path[-1][1] == self.path[-2][1]: #line is retracting
                        self.path.pop()
                        self.pixelpath.pop()
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][1])][int(self.path[-1][0])][right]
                if self.pos[0] + self.radius != self.currentbarrier:
                    self.pos[0] += 1
                    self.xtravelled += 1
                    self.xsquarestravelled = self.xtravelled/self.gridsquaresize
                else:
                    return
                
        elif direction == left:
            for i in range(distance):
                if self.xsquarestravelled.is_integer():
                    if len(self.path) == 0:#line is beginning
                        pass
                    elif self.path[-1] != (self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled): #line is extending
                        self.path.append((self.path[0][0]+self.xsquarestravelled,self.path[0][1]+self.ysquarestravelled))
                        self.pixelpath.append(tuple(self.pos))
                    if len(self.path) > 1 and self.path[0][0]+self.xsquarestravelled > self.path[-2][0] and self.path[-1][1] == self.path[-2][1]: #line is retracting
                        self.path.pop()
                        self.pixelpath.pop()
                    self.currentbarrier = self.mazebarriers[int(self.path[-1][1])][int(self.path[-1][0])][left]
                if self.pos[0] - self.radius != self.currentbarrier:
                    self.pos[0] -= 1
                    self.xtravelled -= 1
                    self.xsquarestravelled = self.xtravelled/self.gridsquaresize
                else:
                    return
        
    def draw(self,display):
        pygame.draw.circle(display, self.color, self.startpos, self.currentradius)
        self.pixelpath.append(self.pos)
        for coord in range(len(self.pixelpath)-1):
            pygame.draw.line(display,self.color,(self.pixelpath[coord][0]-1,self.pixelpath[coord][1]-1),(self.pixelpath[coord+1][0]-1,self.pixelpath[coord+1][1]-1),self.width)
            pygame.draw.circle(display,self.color,self.pixelpath[coord],int(self.radius))
        pygame.draw.circle(display,self.color,self.pos,int(self.radius))
        self.pixelpath.pop()


class Wall():
    def __init__(self,startpos,endpos,color):
        self.color = color
        self.startpos = startpos
        self.width = endpos[0]-startpos[0]
        self.height = endpos[1]-startpos[1]
    def draw(self,display):
        pygame.draw.rect(display,self.color,(self.startpos,(self.width,self.height)))
        
class Maze():
    def __init__(self, display, size, nullzones,
                 symbols, starts, ends, hexagons,
                 linefrac, bgcolor, gridcolor, tracecolor):
        self.size = size #tuple with (x,y)
        self.symbols = symbols #tuple with (x,y), relative to squares, not intersections
        self.starts = starts #list of starting point positions
        self.sortEnds(ends) #generates 4 lists of end points, one for each maze side, needed later
        self.hexagons = hexagons #list of hexagon positions
        self.linefrac = linefrac #should be a fraction, i.e. 1/4 for 1/4 the size of squares
        self.bgcolor = bgcolor #color of squares and border
        self.gridcolor = gridcolor #color of grid lines
        self.tracecolor = tracecolor #color of trace
        self.grid = []

        self.tracedisplay = pygame.Surface((display.get_width(),display.get_height()))
        self.tracedisplay.set_colorkey(clear)#makes everything that's that color transparent
        
        for y in range(size[1]):
            self.grid.append([])
            for x in range(size[0]):
                self.grid[y].append(None)
                
        self.generateWalls(display)
        self.generateNullZones(nullzones)
        self.generateMazeImage(display)
        
    def printMaze(self):
        for i in self.grid:
            for j in i:
                print(j, end=" ")
            print()
            
    def sortEnds(self,ends):
        sortedends = sorted(ends, key=lambda end: end[2])#sorts all ends by direction value in third index
        self.upends = []
        self.rightends = []
        self.downends = []
        self.leftends = []
        for end in sortedends:
            if end[2] == up:
                self.upends.append(end[0]) #adds the positions of the ends along their respective sides
            elif end[2] == right:
                self.rightends.append(end[1])
            elif end[2] == down:
                self.downends.append(end[0])
            else:
                self.leftends.append(end[1])
        self.upends.sort()
        self.rightends.sort()
        self.downends.sort()
        self.leftends.sort()                
            
    def generateWalls(self,display):
        image = display.copy()
        self.screenrect = display.get_rect()
        #get largest possible square size (remember linefrac is fraction of square size, like 1/4)
        #includes space in between squares and 2x line width worth of buffer on both bounding edges
        self.squaresize = self.screenrect.w // (self.size[0] + (self.linefrac*self.size[0]) + 5*self.linefrac)
        #test if that self.squaresize is compatible with vertical dimension, if it bleeds over vertical is limiting
        if self.squaresize*(1+self.linefrac)*self.size[1] + 4*self.squaresize*self.linefrac > self.screenrect.h:
            self.squaresize = self.screenrect.h // (self.size[1] + (self.linefrac*self.size[1]) + 5*self.linefrac)
        self.squaresize = int(self.squaresize)
        self.linewidth = int(self.squaresize*self.linefrac)#I need the pixel value of self.linewidth more after this, so this will be useful
        while self.linewidth % 2 == 1:#make the line width always be even so that the trace head circle will fill it completely
            self.squaresize -= 1 #while loop because subtracting 1 from square size doesn't always make linewidth even
            self.linewidth = int(self.squaresize*self.linefrac)
        self.wspace = int(self.screenrect.w - ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth))
        self.hspace = int(self.screenrect.h - ((self.squaresize+self.linewidth)*self.size[1] + self.linewidth))
        self.walls = []

        #pixel values for the edges of the maze
        rightedge = self.wspace//2 + ((self.squaresize+self.linewidth)*self.size[0]) + self.linewidth
        botedge = self.hspace//2 + ((self.squaresize+self.linewidth)*self.size[1]) + self.linewidth
        leftedge = self.wspace//2
        topedge = self.hspace//2

        #create the 4 sides of the maze, leaving gaps for maze ends.     _ _|
        #without any gaps, the side borders form a pinwheel shape, i.e.   |_|_  for a square maze.
        #                                                                 |
        #top side:
        currentpos = (0,0)
        for endpos in self.upends:
            nextpos = (leftedge + ((self.squaresize+self.linewidth)*endpos), topedge)
            self.walls.append(Wall(currentpos,nextpos,self.bgcolor))
            currentpos = (nextpos[0]+self.linewidth,0)
        if currentpos[0] != rightedge:
            self.walls.append(Wall(currentpos,(rightedge,topedge),self.bgcolor))
        #right side:
        currentpos = (rightedge,0)
        for endpos in self.rightends:
            nextpos = (self.screenrect.w, topedge + (self.squaresize+self.linewidth)*endpos)
            self.walls.append(Wall(currentpos,nextpos,self.bgcolor))
            currentpos = (rightedge,nextpos[1]+self.linewidth)
        if currentpos[1] != botedge:
            self.walls.append(Wall(currentpos,(self.screenrect.w,botedge),self.bgcolor))
        #these next two have an extra if to make sure an extraneous, 0 area wall isn't created
        #bottom side:
        currentpos = (leftedge,botedge)
        for endpos in self.downends:
            nextpos = (leftedge + ((self.squaresize+self.linewidth)*endpos), self.screenrect.w)
            if nextpos[0]-currentpos[0] != 0:
                self.walls.append(Wall(currentpos,nextpos,self.bgcolor))
            currentpos = (nextpos[0]+self.linewidth,botedge)
        self.walls.append(Wall(currentpos,(self.screenrect.w,self.screenrect.h),self.bgcolor))
        #left side:
        currentpos = (0,topedge)
        for endpos in self.leftends:
            nextpos = (leftedge, topedge + (self.squaresize+self.linewidth)*endpos)
            if nextpos[1]-currentpos[1] != 0:
                self.walls.append(Wall(currentpos,nextpos,self.bgcolor))
            currentpos = (0, nextpos[1] + self.linewidth)
        self.walls.append(Wall(currentpos,(leftedge,self.screenrect.h),self.bgcolor))
        
        """       
        self.walls.append(Wall(0,0,self.wspace//2,
                            self.screenrect.h,self.bgcolor))#left boundary
        self.walls.append(Wall(((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,0,
                            self.screenrect.w,self.screenrect.h,self.bgcolor))#right boundary
        self.walls.append(Wall(self.wspace//2,0,
                            self.screenrect.w-self.wspace//2,self.hspace//2,self.bgcolor))#top boundary
        self.walls.append(Wall(self.wspace//2,((self.squaresize+self.linewidth)*self.size[1] + self.linewidth)+self.hspace//2,
                            ((self.squaresize+self.linewidth)*self.size[0] + self.linewidth)+ self.wspace//2,self.screenrect.h,self.bgcolor))#bottom boundary
        """
        
        for y in range(self.size[1]): #draw grid squares
            for x in range(self.size[0]):
                squarex = self.wspace//2+self.linewidth+(x*(self.squaresize+self.linewidth))
                squarey = self.hspace//2+self.linewidth+(y*(self.squaresize+self.linewidth))
                self.walls.append(Wall((squarex,squarey),(squarex + self.squaresize,squarey + self.squaresize),self.bgcolor))

    def generateNullZones(self,nullcoords):
        self.barriers = []
        for row in range(self.size[1]+1):#size + 1 because size describes the number of squares in the maze, not num of grid intersections
            self.barriers.append([])
            for column in range(self.size[0]+1):
                self.barriers[row].append([None,None,None,None])
        #self.barriers will store, for each intersection in the maze, the pixel position of the barriers, should they exist, in each of the 4 directions.
        #these will be used to calculate trace head nullzone collisions as well as represent the barriers graphically.
        for nullzone in nullcoords:
            if nullzone[1][0] - nullzone[0][0] == 1: #horizontal
                barrierleft = int(self.wspace/2 + nullzone[0][0]*(self.squaresize+self.linewidth) + self.linewidth + ((1-nullzone[2])/2)*self.squaresize)
                barrierright = int(self.wspace/2 + nullzone[0][0]*(self.squaresize+self.linewidth) + self.linewidth + ((1-nullzone[2])/2)*self.squaresize + nullzone[2]*self.squaresize)
                self.barriers[nullzone[0][1]][nullzone[0][0]][right] = barrierleft
                self.barriers[nullzone[1][1]][nullzone[1][0]][left] = barrierright
                self.walls.append(Wall((barrierleft,(self.hspace//2+(self.squaresize+self.linewidth)*nullzone[0][1])),
                                       (barrierright,self.hspace//2+(self.squaresize+self.linewidth)*nullzone[0][1]+self.linewidth),
                                        self.bgcolor))
            elif nullzone[1][1] - nullzone[0][1] == 1: #vertical
                barriertop = int(self.hspace/2 + nullzone[0][1]*(self.squaresize+self.linewidth) + self.linewidth + ((1-nullzone[2])/2)*self.squaresize)
                barrierbot = int(self.hspace/2 + nullzone[0][1]*(self.squaresize+self.linewidth) + self.linewidth + ((1-nullzone[2])/2)*self.squaresize + nullzone[2]*self.squaresize)
                self.barriers[nullzone[0][1]][nullzone[0][0]][down] = barriertop
                self.barriers[nullzone[1][1]][nullzone[1][0]][up] = barrierbot
                self.walls.append(Wall((self.wspace//2+(self.squaresize+self.linewidth)*nullzone[0][0],barriertop),(self.wspace//2+(self.squaresize+self.linewidth)*nullzone[0][0]+self.linewidth,barrierbot),self.bgcolor))
            
    def tryStart(self,mousepos):
        mgridpos = [(mousepos[0] - (self.wspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth),
                   (mousepos[1] - (self.hspace//2) - self.linewidth//2)/(self.squaresize+self.linewidth)]
        startradius = (self.linewidth*1.1)/(self.squaresize + self.linewidth)
        for start in self.starts:
            if abs(start[0] - mgridpos[0]) < startradius and abs(start[1] - mgridpos[1]) < startradius:
                self.makeTrace([self.wspace//2 + self.linewidth//2 + start[0]*(self.squaresize+self.linewidth),
                                self.hspace//2 + self.linewidth//2 + start[1]*(self.squaresize+self.linewidth)])
                return True
            
    def makeTrace(self,gridpos):
        #add tracebody in here later
        self.trace = Trace(self,gridpos)
        #list() makes temp copies of gridpos to pass
        #otherwise these will point to the same list in memory and create problems
        self.tracefade = 0
        
    def update(self,is_alive):
        if is_alive:
            #update maze flashing symbols when wrong
            self.trace.update()
        elif self.tracefade < 256:
            self.tracefade += 2
            
    def generateMazeImage(self,display):
        self.mazeimage = display.copy()
        self.mazeimage.fill(self.gridcolor)
        for wall in self.walls:
            wall.draw(self.mazeimage)
        self.drawStarts(self.mazeimage)
        
    def drawMaze(self, display):
        display.blit(self.mazeimage,(0,0))
        
    def drawStarts(self,display):
        self.startlist = []
        for startpos in self.starts:
            pygame.draw.circle(display,self.gridcolor,
                                (self.wspace//2 + self.linewidth//2 + startpos[0]*(self.squaresize+self.linewidth),
				self.hspace//2 + self.linewidth//2 + startpos[1]*(self.squaresize+self.linewidth)),
                                int(self.linewidth*1.15))
        
            
    def drawTrace(self,display,is_alive):
        if is_alive:
            self.tracedisplay.fill(clear)
            self.trace.draw(self.tracedisplay)
        #all the sections of the trace need to be faded as one image, otherwise
        #we get issues with transparent surfaces overlapping and being more opaque
        self.tracedisplay.set_alpha(256 - self.tracefade)
        display.blit(self.tracedisplay,(0,0))
        


pygame.init()
displaysize = [800,800]
screen = pygame.display.set_mode(displaysize)
clock = pygame.time.Clock()
m1prev = False
is_alive = False
startupdating = False
done = False

display = screen
size = (3,3)
nullzones = (((2,0),(2,1),2/5),)#(((1,1),(2,1),1/2),((3,3),(4,3),1),((0,4),(1,4),1/3),((1,1),(1,2),1/2),((2,2),(2,3),1)) #nullzone coordinate pairs must be left to right or up to down
symbols = ()
starts = ((3,3),)
#reminder: when only one tuple in another tuple, needs comma at end to tell python
#it's a tuple tuple, not just a tuple... lol   i.e. ((1,1),)
ends = ()#((0,0,up),(0,0,left),(2,0,up),(4,0,right),(4,4,right),(4,4,down),(0,4,down),(0,4,left))
hexagons = ()
linefrac = 1/5
bgcolor = (0,70,205,255)
gridcolor = (25,25,112,255)
tracecolor = white

testmaze = Maze(display,size,nullzones,symbols,starts,ends,hexagons,linefrac,bgcolor,gridcolor,tracecolor)

while not done:
    pygame.event.clear()#won't need to get events from event queue, chuck'em
    mousestates = pygame.mouse.get_pressed()
    if mousestates[0] != m1prev:
        if m1prev == False:#mouse being pressed
            mousepos = pygame.mouse.get_pos()
            if testmaze.tryStart(mousepos):
                is_alive = True
                startupdating = True
        else:#mouse being released
            is_alive = False
        m1prev = mousestates[0]
    if mousestates[1] == True:#close program upon middle mouse
        done = True
        
    screen.fill(testmaze.gridcolor)
    testmaze.drawMaze(screen)
    
    if startupdating:
        testmaze.update(is_alive)
        testmaze.drawTrace(screen, is_alive)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
