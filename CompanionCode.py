#   Last edit: Eddie Lowe 28/12/2016
#   Works with Python 3.4.2 and Pygame 1.9.2

import sys, pygame, os, time, math, random
from pygame.locals import *


green =     (  0, 255,   0)
red =       (255,   0,   0)
white =     (255, 255, 255)
grey =      (200, 200, 200)
yellow =    (255, 255,   0)
black =     ( 52,  52,  52)
parchment = (241, 241, 212)
violet =    (125,   0, 255)

def createText(text, font, colour):
    surf = font.render(text, True, colour)
    return surf, surf.get_rect()

def createScrollBar(font, textColour, bgColour, surface, rect, outlineBar):
    scrollBarHeight = font.size(' ')[1] * 3/2

    # outline bar determines whether the 'scroll' text is written onto the background or a different colour
    if outlineBar == True:
        rectColour = bgColour
        scrollBarTextColour = textColour
    else:
        rectColour = textColour
        scrollBarTextColour = bgColour
    
    scrollDownText, scrollDownRect = createText('Scroll Down To Continue', font, scrollBarTextColour)
    scrollBar = pygame.draw.rect(surface, rectColour, (0, rect.height - scrollBarHeight,
                                                        rect.width, scrollBarHeight))

    if outlineBar == True:
        outlineScrollBar = pygame.draw.rect(surface, scrollBarTextColour, (scrollBar), 1)
        
    scrollDownRect.center = scrollBar.center
    surface.blit(scrollDownText, scrollDownRect)
    
    #draw a triangle either side of the text pointing down
    arrowTextGap = font.size(' ')[0]
    triangleWidth = arrowTextGap
    matrix1 = (scrollDownRect.x - arrowTextGap, scrollDownRect.y + scrollDownRect.height/4)
    matrix2 = (matrix1[0] - triangleWidth, matrix1[1])
    matrix3 = (matrix1[0] - (triangleWidth / 2), matrix1[1] + scrollDownRect.height/2)

    pygame.draw.polygon(surface, scrollBarTextColour, ((matrix1), (matrix2), (matrix3)))

    matrix4 = (scrollDownRect.x + scrollDownRect.width + arrowTextGap, matrix1[1])
    matrix5 = (matrix4[0] + triangleWidth, matrix1[1])
    matrix6 = (matrix4[0] + (triangleWidth / 2), matrix3[1])

    pygame.draw.polygon(surface, scrollBarTextColour, ((matrix4), (matrix5), (matrix6)))
    
def lineVar(axis):
    '''Used when creating a hand drawn box to slightly vary the start and end of each line
to create a messier effect'''
    if axis == 'x':
        return random.randint(-5, 5)
    elif axis == 'y':
        return random.randint(-3, 3)

def handDrawnBox(rect, numOfLines):
    ''' creates a hand drawn effect around a rect '''
    r = rect
    listOfLines = []
                 
    for i in range(numOfLines):
        listOfLines.append([[r.x + lineVar('x'), r.y + lineVar('y')],
                            [r.x + lineVar('x'), r.y + r.height + lineVar('y')]])

        listOfLines.append([[r.x + lineVar('x'), r.y + lineVar('y')],
                            [r.x + r.width + lineVar('x'), r.y + lineVar('y')]])

        listOfLines.append([[r.x + r.width + lineVar('x'), r.y + lineVar('y')],
                            [r.x + r.width + lineVar('x'), r.y + r.height + lineVar('y')]])

        listOfLines.append([[r.x + lineVar('x'), r.y + r.height + lineVar('y')],
                            [r.x + r.width + lineVar('x'), r.y + r.height + lineVar('y')]])

    return listOfLines
    
def createWrappedText(text, textColour, bgColour, surf, rect, font, startLine, scrollBarOutline = False):
    text = ''.join(text)
    lines = []
    
    while text:
        i = 1
        leaveExtraLine = False
        
        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
            
        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text) or i >= len(text):
            if '\\' in text[:i]:
                leaveExtraLine = True
                j = text.find('\\', 0, i)
                text = text[:j] + text[j+1:]
                i = j
            else:
                i = text.rfind(" ", 0, i) + 1
 
        textLine = text[:i]
        lines.append(textLine)
        if leaveExtraLine:
            lines.append('')

        # remove the text we just appended to the lines list
        text = text[i:]

    #we blit each line to the surface
    textHeight = font.size(' ')[1]
    
    for line in lines[startLine:]:
        image = font.render(line, True, textColour)
        imageRect = image.get_rect()
        imageRect.midtop = (rect.width/2, textHeight)
        surf.blit(image, imageRect)
        textHeight += font.size(line)[1] * 3/2

    #checks if the text is longer than the info panel
    if textHeight >= surf.get_height():
        canScrollDown = True
        createScrollBar(UIFont, textColour, bgColour, surf, rect, scrollBarOutline)
        
    else:
        canScrollDown = False
               
    return canScrollDown

def checkForScroll(startDisplacement, canScrollDown, event, scrollFactor = 1):
    displacement = 0
   
    if event.type == KEYDOWN:
        
        if event.key == K_DOWN:
            if canScrollDown == True:
                displacement += scrollFactor * 3
            
        if event.key == K_UP and startDisplacement > 0:
            
            displacement -= scrollFactor * 3
            
            if startDisplacement + displacement < 0:
                displacement = 0 - startDisplacement
            
    if event.type == MOUSEBUTTONDOWN:
        
        #mouse button 5 is scroll down
        if event.button == 5:
            if canScrollDown == True:
                displacement += scrollFactor
                
        #mouse button 4 is scroll up
        if event.button == 4 and startDisplacement > 0:
            displacement -= scrollFactor                
                
    return displacement

def main():
    global backgroundSurf, FPSClock, screenWidth, screenHeight, tileWidth, tileHeight, displaySurf, displayRect, mountainImg,\
           grassImg, waterImg, forestImg, dirtImg, infoPanelBodyFont, titleFont, wMountainImg,\
           backgroundImg, clickableTiles, worldMap, UIFont, bgTileX, bgTileY, displayTileX, displayTileY,\
           linkFont, handwrittenBodyFont, sandImg, sMountainImg, snowImg, redForestImg, pavedImg, marshImg
    
    pygame.init()
    modes = pygame.display.list_modes()
    backgroundSurf = pygame.display.set_mode((modes[4]))
    screenWidth, screenHeight = backgroundSurf.get_width(), backgroundSurf.get_height()

    #read the map file
    clickableTiles = []
    worldMap = readMapFile('TextDocs/world_map.txt')
    
    #creates the map surface, which is used to display the world map
    displaySurf = pygame.Surface((tileWidth * mapWidth, tileHeight * mapHeight))
    displayRect = displaySurf.get_rect()
    displayRect.center = (screenWidth/2, screenHeight/2)

    #fonts
    #font factor is used to scale the font size to be a similar relative size for whatever size display is used
    fontFactor = screenWidth/1600
    
    linkFont = [pygame.font.SysFont('gabriola', int(60 * fontFactor)),
                pygame.font.SysFont('gabriola', int(40 * fontFactor)),
                pygame.font.SysFont('gabriola', int(30 * fontFactor)),
                pygame.font.SysFont('gabriola', int(25 * fontFactor)),
                pygame.font.SysFont('gabriola', int(20 * fontFactor))]

    titleFont = [pygame.font.SysFont('andalus', int(40 * fontFactor)),
                 pygame.font.SysFont('andalus', int(30 * fontFactor)),
                 pygame.font.SysFont('andalus', int(25 * fontFactor)),
                 pygame.font.SysFont('andalus', int(20 * fontFactor))]
    
    for font in titleFont:
        font.set_underline(True)

    handwrittenBodyFont = [pygame.font.SysFont('andalus', int(30 * fontFactor)),
                           pygame.font.SysFont('andalus', int(25 * fontFactor)),
                           pygame.font.SysFont('andalus', int(20 * fontFactor)),
                           pygame.font.SysFont('andalus', int(15 * fontFactor))]
    
    infoPanelBodyFont = pygame.font.SysFont('narkisim', int(20 * fontFactor))
    
    UIFont = pygame.font.SysFont('couriernew', int(15 * fontFactor))

    #load our images
    mountainImg = pygame.transform.scale(pygame.image.load('Images/Tiles/mountain_grass.png'), (tileWidth, tileHeight))
    wMountainImg = pygame.transform.scale(pygame.image.load('Images/Tiles/mountain_water.png'), (tileWidth, tileHeight))
    sMountainImg = pygame.transform.scale(pygame.image.load('Images/Tiles/mountain_snow.png'), (tileWidth, tileHeight))
    
    grassImg = pygame.transform.scale(pygame.image.load('Images/Tiles/grass.png'), (tileWidth, tileHeight))
    waterImg = pygame.transform.scale(pygame.image.load('Images/Tiles/water.png'), (tileWidth, tileHeight))
    forestImg = pygame.transform.scale(pygame.image.load('Images/Tiles/forest.png'), (tileWidth, tileHeight))
    redForestImg = pygame.transform.scale(pygame.image.load('Images/Tiles/red_leaf_forest.png'), (tileWidth, tileHeight))
    dirtImg = pygame.transform.scale(pygame.image.load('Images/Tiles/dirt.png'), (tileWidth, tileHeight))
    sandImg = pygame.transform.scale(pygame.image.load('Images/Tiles/sand.png'), (tileWidth, tileHeight))
    snowImg = pygame.transform.scale(pygame.image.load('Images/Tiles/snow.png'), (tileWidth, tileHeight))
    pavedImg = pygame.transform.scale(pygame.image.load('Images/Tiles/paving.png'), (tileWidth, tileHeight))
    marshImg = pygame.transform.scale(pygame.image.load('Images/Tiles/marsh.png'), (tileWidth, tileHeight))
    
    bgTileX, bgTileY = 8, 10
    backgroundImg = pygame.transform.scale(pygame.image.load('Images/background.png'), (math.ceil(screenWidth/bgTileX), math.ceil(screenHeight/bgTileY)))

    FPSClock = pygame.time.Clock()

    while True:
        menuScreen()

def menuScreen():
    buttons = ['World Map', 'History', 'Encyclopedia', 'Exit']
    buttonRects = []
    
    #The background image of the main menu is tiled, decided by tileX and tileY values
    for i in range(bgTileY):
        for j in range(bgTileX):
            backgroundRect = pygame.Rect(screenWidth * j/bgTileX, screenHeight * i/bgTileY, screenWidth/bgTileX, screenHeight/bgTileY)
            backgroundSurf.blit(backgroundImg, backgroundRect)

    for button in buttons:
        buttonRect = pygame.Rect(0, 0, screenWidth/3, (screenHeight/len(buttons))/2)
            
        buttonRect.midleft = (screenWidth*3/5, screenHeight * ((buttons.index(button) + 1)/(len(buttons) + 1)))
            
        buttonRects.append(buttonRect)

    gapSize = screenWidth - (buttonRects[0].x + buttonRects[0].width)

    titleRect = pygame.Rect(gapSize, buttonRects[0].y, screenWidth - gapSize * 3 - buttonRects[0].width,
                           (buttonRects[len(buttonRects) - 1].y + buttonRects[len(buttonRects) - 1].height) - buttonRects[0].y)

    readMeFile = readInfoFile('Read Me.txt')

    posterHeadingText = readMeFile[0][1]
    campaignTitle = readMeFile[0][0]

    posterHeading = linkFont[3].render(posterHeadingText, True, black)
    posterHeadingRect = posterHeading.get_rect()
    posterHeadingRect.center = (titleRect.centerx, titleRect.y + (titleRect.height * 2/10))

    posterCampaignTitle = titleFont[0].render(campaignTitle, True, black)
    posterCampaignTitleRect = posterCampaignTitle.get_rect()
    posterCampaignTitleRect.center = (titleRect.centerx, titleRect.y + (titleRect.height * 1/10))

    posterImageList = os.listdir('Images\menu_image')
    randomImage = random.choice(posterImageList)
    
    posterImageRect = pygame.Rect(titleRect.x + gapSize/2, posterHeadingRect.y + gapSize/2, titleRect.width - gapSize,
                                  titleRect.height - posterHeadingRect.y + posterHeadingRect.height)

    posterImage = pygame.transform.scale(pygame.image.load('Images\menu_image\\' + randomImage), (posterImageRect.width, posterImageRect.height))

    imageFadeScreen = pygame.Surface((posterImageRect.width, posterImageRect.height))
    imageFadeScreen.fill(parchment)
    imageFadeScreen.set_alpha(150)
        
    while True:
               
        mouseX, mouseY = pygame.mouse.get_pos()

        #we draw the buttons on the screen and check if they're highlighted
        for rect in buttonRects:
            pygame.draw.rect(backgroundSurf, parchment, (rect))
            
            if rect.collidepoint(mouseX, mouseY):
                rectColour = violet
            else:
                rectColour = black
            pygame.draw.rect(backgroundSurf, rectColour, (rect), 1)
            
            text = linkFont[1].render(buttons[buttonRects.index(rect)], True, rectColour)
            textRect = text.get_rect()
            textRect.center = rect.center
            backgroundSurf.blit(text, textRect)

        pygame.draw.rect(backgroundSurf, parchment, (titleRect))
        pygame.draw.rect(backgroundSurf, black, (titleRect), 1)      

        backgroundSurf.blit(posterHeading, posterHeadingRect)
        backgroundSurf.blit(posterCampaignTitle, posterCampaignTitleRect)
        backgroundSurf.blit(posterImage, posterImageRect)
        backgroundSurf.blit(imageFadeScreen, posterImageRect)

        pygame.draw.rect(backgroundSurf, black, (posterImageRect), 1)

        #checks for button selection or quit
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONUP:
                for button in buttonRects:
                    if button.collidepoint(mouseX, mouseY):
                        backgroundSurf.fill(parchment)
                        if buttons[buttonRects.index(button)] == 'World Map':
                            displayMap()
                        if buttons[buttonRects.index(button)] == 'Encyclopedia':
                            encyclopedia()
                        if buttons[buttonRects.index(button)] == 'History':
                            chronology()
                        if buttons[buttonRects.index(button)] == 'Exit':
                            pygame.quit()
                            sys.exit()
                            
        pygame.display.update()

def displayMap():
    global worldMap, selectedTile, infoPanelSurf, infoPanelRect, clickableTiles
    POIInfo = readInfoFile('TextDocs/map_points_of_interest.txt')
    selectedTile = None
    unreadPOITiles = clickableTiles[:]

    #info panel appears at the side of the map screen when a point of interest is selected
    infoPanelSurf = pygame.Surface(((mapWidth*tileWidth) * (1/4), mapHeight*tileHeight))
    infoPanelSurf.set_alpha(200)
    infoPanelRect = infoPanelSurf.get_rect()
    infoPanelRect.topleft = (0, 0)
    infoScrollStartHeight = infoPanelRect.x + titleFont[1].size(' ')[1]

    #upon launch (or pressing h) a help panel appears in the middle of the screen, telling the user how to use the map
    helpText = ['Press H to open and close this help window.',
                'Press G to toggle the grid overlay.',
                'Click on a City or Flag to open the information panel.',
                'Press ESC to close an information panel,',
                'or return to the main menu']

    #Here we calculate how large the help panel should be (the width of the longest text line)    
    #checks each line of text and finds the longest
    longestLine = helpText[0]
    for i in helpText:
        if len(i) > len(longestLine):
            longestLine = i

    helpPanelWidth = infoPanelBodyFont.size(longestLine)[0] + 2*(infoPanelBodyFont.size('  ')[0])

    #create the help panel
    helpPanelSurf = pygame.Surface((helpPanelWidth, (mapHeight*tileHeight)/4))
    helpPanelSurf.set_alpha(200)
    helpPanelRect = pygame.Rect(((mapWidth * tileWidth) / 2) - ((helpPanelSurf.get_width()) / 2),
                                (((mapHeight * tileHeight) / 2) - ((helpPanelSurf.get_height()) / 2)),
                                helpPanelSurf.get_width(), helpPanelSurf.get_height())
    
    #blit text to the help panel
    for line in range(len(helpText)):
        text, rect = createText(helpText[line], infoPanelBodyFont, white)
        rect.center = (helpPanelRect.width/2, helpPanelRect.height * (line + 1)/(len(helpText) + 1))
        helpPanelSurf.blit(text, rect)

    #we convert our coordinates into pixel sizes, then find which images should be used for each tile
    mapTiles = []
    drawMap(mapTiles, clickableTiles)
    
    #keep track of whether the grid or help panel should be open or closed
    mapGridOn = False
    mapHelpWindow = True
    
    #just used for FPS testing purposes
    frameCount = 0
    start = time.time()


    #main map loop
    while True:
        displaySurf.fill(grey)

        #actually draws the map onto the map surface
        for i in mapTiles:
            displaySurf.blit(i['surf'], i['rect'])
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if selectedTile != None:
                infoPanelStartLine += checkForScroll(infoPanelStartLine, canScrollDown, event)                    
                        
            if event.type == MOUSEBUTTONUP:
                mouseX, mouseY = pygame.mouse.get_pos()
                mouseX -= displayRect.x
                mouseY -= displayRect.y
                for i in clickableTiles:
                    if i[1].collidepoint(mouseX, mouseY):
                        if i[1].x <= (mapWidth*tileWidth)/2:
                            infoPanelRect.topright = (displaySurf.get_width(), 0)
                        else:
                            infoPanelRect.topleft = (0, 0)
                        infoPanelStartLine = 0
                        selectedTile = i
                        infoPanelSurf.fill(black)
                        canScrollDown = False
                        if selectedTile in unreadPOITiles:
                            unreadPOITiles.remove(i)
                        
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if selectedTile != None:
                        selectedTile = None
                    else:
                        menuScreen()
                if event.key == K_g:
                    if mapGridOn == False:
                        mapGridOn = True
                    elif mapGridOn == True:
                        mapGridOn = False
                if event.key == K_h:
                    if mapHelpWindow == False:
                        mapHelpWindow = True
                    elif mapHelpWindow == True:
                        mapHelpWindow = False

        if mapGridOn == True:
            for i in mapTiles:
                pygame.draw.rect(displaySurf, grey, (i['rect']), 1)

        #draw a yellow outline around each POI tile that the user hasn't clicked on yet
        for tile in unreadPOITiles:
            pygame.draw.rect(displaySurf, yellow, (tile[1]), 1)

        #Checks whether the info panel should be on, and what information should be displayed
        if selectedTile != None:
            pygame.draw.rect(displaySurf, violet, (selectedTile[1]), 2)
            displaySurf.blit(infoPanelSurf, infoPanelRect)
            pygame.draw.rect(displaySurf, white, (infoPanelRect), 3)
            
            for i in POIInfo:
                #info file adds a space to the end of each line, so we have to do that here as well when comparing
                if str(selectedTile[0]) + ' ' == i[0]:

                    infoPanelSurf.fill(black)
                    
                    #Creates the main body of text on the info panel
                    textRect = pygame.Rect(0, infoScrollStartHeight, infoPanelRect.width,
                                           infoPanelRect.height - infoScrollStartHeight)
                    textSurf = pygame.Surface((textRect.width, textRect.height))
                    textSurf.fill(black)

                    #blits the text to the info panel, and tells us if the user will be able to scroll down or not
                    canScrollDown = createWrappedText(i[2:], white, black, textSurf, textRect, infoPanelBodyFont, infoPanelStartLine)
                    infoPanelSurf.blit(textSurf, textRect)

                    #Creates the title on the info panel
                    titleSurf = pygame.Surface((infoPanelRect.width, infoScrollStartHeight))
                    titleSurf.fill(black)
                    titleSurf, titleRect = createText(i[1], titleFont[1], white)
                    titleRect.center = (infoPanelRect.width / 2, infoPanelRect.y + infoScrollStartHeight/2)
                    infoPanelSurf.blit(titleSurf, titleRect)

        #displays help window
        if mapHelpWindow:
            displaySurf.blit(helpPanelSurf, helpPanelRect)
            pygame.draw.rect(displaySurf, white, (helpPanelRect), 3)

        #draws the map surface onto our screen
        backgroundSurf.blit(displaySurf, displayRect)

        pygame.display.update()
        FPSClock.tick(30)


def chronology():
    ''' code that displays the screen when the user is in the chronology section of the program'''
    pygame.event.clear()
    
    chronoInfo = readInfoFile('textDocs/history.txt')

    gapSize = displayRect.height/30 # 'gap' is the size between nodes
    numberOfEntries = len(chronoInfo)
    
    nodeSize = displayRect.height/30 # a node is one entry on the timeline
    timelineThickness = 6
    
    entryWidth = displayRect.width * 3/4
    entryHeight = (displayRect.height/2) - (nodeSize/2) - (gapSize * 2)

    #all entries will be displayed horizontally, and the user will be able to scroll sideways
    #camera X variable keeps track of the scroll bar
    cameraX = 0

    scrollFactor = 60 # determines how much one scroll of the mouse wheel does
    maxCameraValue = (len(chronoInfo) + 1) * (displayRect.width / 2) - displayRect.width

    boxesToDraw = []
    timeline = []
    entries = []
    nodes = []
    
    for i in range(len(chronoInfo)):
        entryRectX = ((i+1) * (displayRect.width / 2))
        
        node = pygame.Rect(entryRectX - (nodeSize/2) + lineVar('x'),
                            displayRect.height / 2 - nodeSize/2 + lineVar('y'), nodeSize, nodeSize)

        if i % 2 == 0: # diplays entries above and below the timeline alternatively
            entry = pygame.Rect(entryRectX - entryWidth/2,
                                node.y + node.height + gapSize, entryWidth, entryHeight)
        else:
            entry = pygame.Rect(entryRectX - entryWidth/2,
                                node.y - gapSize - entryHeight, entryWidth, entryHeight)

        currentNodeCoords = [node.centerx, node.centery + lineVar('y')]
        
        if i > 0:
            timeline.append([lastNodeCoords, currentNodeCoords])

        lastNodeCoords = currentNodeCoords[:]
                
        boxesToDraw.append(handDrawnBox(entry, 4))

        #entry = rect, whether it has a scroll option, scroll start line
        entries.append([entry, False, 0])
        nodes.append(currentNodeCoords)

    titleRect = pygame.Rect(0, 0, displayRect.width / 3, entryHeight / 3)

    startTitleRect = pygame.Rect(100, 0, titleRect.width, titleRect.height)
    startTitleRect.center = (displayRect.width * 5/16, displayRect.height * 1/4)

    # displays end title on opposite side of line to last entry
    if len(entries) % 2 == 0: 
        endTitleRect = pygame.Rect(maxCameraValue + displayRect.width - startTitleRect.x - startTitleRect.width, displayRect.height / 2 + startTitleRect.y,
                                   titleRect.width, titleRect.height)
        
    else:
        endTitleRect = pygame.Rect(maxCameraValue + displayRect.width - startTitleRect.x - startTitleRect.width, startTitleRect.y,
                                   titleRect.width, titleRect.height)

    titleText = linkFont[0].render('World History', True, black)
    titleTextRect = titleText.get_rect()        

    boxesToDraw.append(handDrawnBox(startTitleRect, 3))
    boxesToDraw.append(handDrawnBox(endTitleRect, 3))

    # right arrow and left arrow used to scroll timeline
    rightArrowRect = pygame.Rect(displayRect.width - nodeSize * 2, (displayRect.height / 2) - nodeSize / 2, nodeSize * 2, nodeSize)
    rightArrowBox = handDrawnBox(rightArrowRect, 2)
    
    rightArrow = [[[rightArrowRect.x + nodeSize/2, rightArrowRect.centery + (lineVar('y') / 2)],
                   [rightArrowRect.x + (nodeSize * 3/2), rightArrowRect.centery + (lineVar('y') / 2)]]]
    
    rightArrow.append([[rightArrow[0][1][0] - nodeSize/3, rightArrow[0][1][1] - nodeSize/3], rightArrow[0][1]])
    rightArrow.append([[rightArrow[0][1][0] - nodeSize/3, rightArrow[0][1][1] + nodeSize/3], rightArrow[0][1]])
   

    leftArrowRect = pygame.Rect(0, (displayRect.height / 2) - nodeSize / 2, nodeSize * 2, nodeSize)
    leftArrowBox = handDrawnBox(leftArrowRect, 2)

    leftArrow = [[[nodeSize/2, leftArrowRect.centery + (lineVar('y') / 2)],
                  [nodeSize * 3/2, leftArrowRect.centery + lineVar('y') / 2]]]

    leftArrow.append([[leftArrow[0][0][0] + nodeSize/3, leftArrow[0][0][1] - nodeSize/3], leftArrow[0][0]])
    leftArrow.append([[leftArrow[0][0][0] + nodeSize/3, leftArrow[0][0][1] + nodeSize/3], leftArrow[0][0]])   

    # exitX button returns to main menu
    exitX = handwrittenBodyFont[0].render('X', True, black)
    exitXRect = exitX.get_rect()
    
    exitButton = pygame.Rect(screenWidth * 1/40, screenHeight * 1/40, exitX.get_height(), exitX.get_height())

    exitXRect.center = exitButton.center

    exitBox = handDrawnBox(exitButton, 3)
                   
    while True:
        displaySurf.fill(parchment)

        cameraChange = 0
        
        if cameraX >= maxCameraValue:
            canScroll = False
        else:
            canScroll = True

        mouseX, mouseY = pygame.mouse.get_pos()
        mouseX -= displayRect.x
        mouseY -= displayRect.y
        mouseOverEntry = False
        
        for event in pygame.event.get():

            for entry in entries:
                rect = pygame.Rect(entry[0].x - cameraX, entry[0].y, entry[0].width, entry[0].height)
                if rect.collidepoint((mouseX, mouseY)): #if user scrolls while hovering over entry, entry will scroll instead of timeline
                    mouseOverEntry = True
                    
                    entry[2] += checkForScroll(entry[2], entry[1], event) # changes y position of entry after scroll

                    if entry[1] == False and entry[2] == 0:
                        mouseOverEntry = False

            if mouseOverEntry == False:
                cameraChange = checkForScroll(cameraX, canScroll, event, scrollFactor)
                cameraX += cameraChange
                if cameraX > maxCameraValue:
                    cameraX = maxCameraValue
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    menuScreen()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if cameraX < maxCameraValue and rightArrowRect.collidepoint((mouseX, mouseY)):
                        cameraX += scrollFactor * 3
                    if cameraX > 0 and leftArrowRect.collidepoint((mouseX, mouseY)):
                        cameraX -= scrollFactor * 3
                    if exitButton.collidepoint((mouseX, mouseY)):
                        menuScreen()

            if cameraX > maxCameraValue:
                cameraX = maxCameraValue
            if cameraX < 0:
                cameraX = 0

        # connects nodes
        for line in timeline:
            lastNode = line[0]
            nextNode = line[1]
            
            pygame.draw.line(displaySurf, black, (lastNode[0] - cameraX, lastNode[1]), (nextNode[0] - cameraX, nextNode[1]), timelineThickness)

        # create each entry
        for i in range(len(entries)):
            entry = entries[i][0]
            node = nodes[i]

            yearLoc = pygame.Rect(entry.x - cameraX + (nodeSize/2), entry.y + nodeSize/3, nodeSize, nodeSize)

            entryTextRect = pygame.Rect(entry.x + nodeSize/4 - cameraX, entry.y + nodeSize, entry.width - nodeSize/2, entry.height - nodeSize)
            entrySurf = pygame.Surface((entryTextRect.width, entryTextRect.height))
            entrySurf.fill(parchment)
            
            if i % 2 == 0:
                c = 0
            else:
                c = entry.height
                        
            pygame.draw.line(displaySurf, black, (entry.centerx - cameraX, entry.y + c),
                             (node[0] - cameraX, node[1]), timelineThickness)


            entryText = chronoInfo[i]

            year, yearRect = createText(entryText[0]+' - '+entryText[1], titleFont[1], black)
            yearRect.midleft = yearLoc.midleft
            
            entries[i][1] = createWrappedText(entryText[2:], black, parchment, entrySurf, entryTextRect, handwrittenBodyFont[2], entries[i][2], True)

            blitRect = pygame.Rect(entryTextRect.x - cameraX, entryTextRect.y, entryTextRect.width, entryTextRect.height)

            displaySurf.blit(entrySurf, entryTextRect)
            displaySurf.blit(year, yearRect)

        for rect in boxesToDraw:
            for line in rect:

                pygame.draw.line(displaySurf, black, (line[0][0] - cameraX, line[0][1]),
                                (line[1][0] - cameraX, line[1][1]))


        for titleArea in [startTitleRect, endTitleRect]:
            titleTextRect.center = titleArea.center
            titleTextRect.x -= cameraX
            displaySurf.blit(titleText, titleTextRect)
            
       
        if cameraX < maxCameraValue:
            pygame.draw.rect(displaySurf, parchment, (rightArrowRect))

            if rightArrowRect.collidepoint((mouseX, mouseY)):
                colour = violet
            else:
                colour = black
            
            for line in rightArrowBox:
                pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line[1][1]))
                
            for line in rightArrow:
                pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line[1][1]))

        if cameraX > 0:
            pygame.draw.rect(displaySurf, parchment, (leftArrowRect))

            # set colour of arrow depending on whether mouse over or not
            if leftArrowRect.collidepoint((mouseX, mouseY)):
                colour = violet
            else:
                colour = black
            
            for line in leftArrowBox:
                pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line[1][1]))

            for line in leftArrow:
                pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line [1][1]))

        pygame.draw.rect(displaySurf, parchment, (exitButton))
        for line in exitBox:
            if exitButton.collidepoint((mouseX, mouseY)):
                colour = red #red if mouseover
            else:
                colour = black
                
            pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line[1][1]))
        exitX = handwrittenBodyFont[0].render('X', True, colour)
        
        displaySurf.blit(exitX, exitXRect)

        backgroundSurf.blit(displaySurf, displayRect)        
        pygame.display.update()
        FPSClock.tick(30)
        
def encyclopedia():
    encycloInfo = readInfoFile('TextDocs/encyclopedia.txt')

    #define constants
    gapSize = displayRect.height/30
    entriesPerPage = 8
    numberOfPages = math.ceil(len(encycloInfo) / entriesPerPage)

    if numberOfPages > 10:
        numberOfPages = 10

    lockedEntry = '- Locked -'

    #variables
    currentPage = 0
    selectedEntry = None
    
    #draw background
    displaySurf.fill(parchment)

    #create rects for title
    titleRect = pygame.Rect((displayRect.width / 2) - ((displayRect.width / 4)/2), gapSize,
                            displayRect.width / 4, displayRect.height / 10)
        
    titleRect.center = (displayRect.width / 2, gapSize + titleRect.height / 2)

    #add entry and description panels
    entryPanelRect = pygame.Rect(gapSize, titleRect.y + titleRect.height + gapSize,
                                titleRect.width, displayRect.height - (3 * gapSize) - titleRect.height)

    descriptionRect = pygame.Rect(entryPanelRect.x + entryPanelRect.width + gapSize, entryPanelRect.y,
                                displayRect.width - (3 * gapSize) - entryPanelRect.width, entryPanelRect.height)
    
    descriptionSurf = pygame.Surface((descriptionRect.width, descriptionRect.height))

    entryBox = handDrawnBox(entryPanelRect, 4)
    descriptionBox = handDrawnBox(descriptionRect, 4)
    titleBox = handDrawnBox(titleRect, 3)

    exitX = handwrittenBodyFont[0].render('X', True, black)
    exitXRect = exitX.get_rect()
    
    exitButton = pygame.Rect(screenWidth * 1/40, screenHeight * 1/40, exitX.get_height(), exitX.get_height())

    exitXRect.center = exitButton.center

    exitBox = handDrawnBox(exitButton, 3)

    #main loop        
    while True:
        #this will store the clickable entries (stores rects)
        entries = []
        pageSelect = []
        
        displaySurf.fill(parchment)
        descriptionSurf.fill(parchment)

        #add title       
        tSurf, tRect = createText('Encyclopedia', titleFont[1], black)
        tRect.center = (displayRect.width / 2, gapSize + titleRect.height / 2)
        displaySurf.blit(tSurf, tRect)

        mouseX, mouseY = pygame.mouse.get_pos()
        mouseX -= displayRect.x
        mouseY -= displayRect.y

        #create entries
        for i in range(numberOfPages):
            if i == currentPage:
                colour = violet
            else:
                colour = black
            pageNumberSurf, pageNumberRect = createText(str(i+1), linkFont[1], colour)
            pageNumberRect.midbottom = (entryPanelRect.width * ((i+1) / 10), entryPanelRect.y + (entryPanelRect.height * 99/100))
            displaySurf.blit(pageNumberSurf, pageNumberRect)

            if pageNumberRect.collidepoint(mouseX, mouseY) and i != currentPage:
                pygame.draw.line(displaySurf, colour, (pageNumberRect.x, pageNumberRect.y + pageNumberRect.height),
                                    (pageNumberRect.x + pageNumberRect.width, pageNumberRect.y + pageNumberRect.height))

            pageSelect.append({'pageNumber': i,
                               'rect': pageNumberRect})
        
        firstEntry = currentPage * 8
        mouseLeeway = linkFont[1].size(' ')[0] * 3
        
        for i in range(0, entriesPerPage):
            
            #If condition stops the loop once we've blitted the last entry in the encyclopedia
            if firstEntry + i < len(encycloInfo):
                #looks at the first letter of the title
                #if it's a '!', that means it should be hidden at the moment
                if encycloInfo[firstEntry + i][0][0] == '!':
                    entryName = lockedEntry
                else:
                    entryName = encycloInfo[firstEntry + i][0]
                    
                if entryName == selectedEntry:
                    textColour = violet
                else:
                    textColour = black

                #entryPanelSegment refers to a section of the panel where it is split into parts of equal size
                #1 for each entry to be displayed
                entryPanelSegment = pygame.Rect(0, 0, entryPanelRect.width,
                                                (entryPanelRect.height - pageNumberRect.height) / entriesPerPage)
                
                entryPanelSegment.center = (entryPanelRect.x + entryPanelRect.width / 2,
                                        #find top of the entry panel, take away page number area from entry panel height to find workable area
                                        #divide workable area into 8 parts, and put an entry in the middle of each one
                                        entryPanelRect.y + ( (( (i+1)*2-1) /(entriesPerPage*2)) * (entryPanelRect.height - pageNumberRect.height)))

                entryNameSurf, entryNameRect = createText(entryName, linkFont[1], textColour)
                entryNameRect.center = entryPanelSegment.center

                entryHighlightRect = pygame.Rect(entryNameRect.x - mouseLeeway, entryNameRect.y - entryNameRect.height/4,
                                entryNameRect.width + (mouseLeeway * 2), entryNameRect.height * (6/4))
                
                entries.append({'entryName': entryName,
                                'entryRect': entryHighlightRect})

                if entryHighlightRect.collidepoint(mouseX, mouseY) and entryPanelRect.collidepoint(mouseX, mouseY)\
                   and encycloInfo[firstEntry + i][0][0] != '!' and entryName != selectedEntry:
                    pygame.draw.line(displaySurf, black, (entryNameRect.x, entryNameRect.y + entryNameRect.height),
                                    (entryNameRect.x + entryNameRect.width, entryNameRect.y + entryNameRect.height))
                
                displaySurf.blit(entryNameSurf, entryNameRect)

        if selectedEntry:
            for i in encycloInfo:
                if i[0] == selectedEntry:                    
                    canScrollDown = createWrappedText(i[1:], black, parchment, descriptionSurf, descriptionRect,\
                                                      handwrittenBodyFont[1], descriptionTextStartLine, True)
                    
                    displaySurf.blit(descriptionSurf, descriptionRect)
           
        #event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if selectedEntry:
                descriptionTextStartLine += checkForScroll(descriptionTextStartLine, canScrollDown, event)
                
            if event.type == MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                mouseX -= displayRect.x
                mouseY -= displayRect.y

                if event.button == 1:
                    for i in entries:
                        if i['entryRect'].collidepoint(mouseX, mouseY) and i['entryName'] != lockedEntry:
                            selectedEntry = i['entryName']
                            descriptionTextStartLine = 0
                            canScrollDown = False
                                    
                    for i in pageSelect:
                        if i['rect'].collidepoint(mouseX, mouseY):
                            currentPage = i['pageNumber']

                    if exitButton.collidepoint((mouseX, mouseY)):
                        menuScreen()
                        
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if selectedEntry != None:
                        selectedEntry = None
                    else:
                        menuScreen()

        #draw panels
        for box in [entryBox, descriptionBox, titleBox]:
            for i in box:
                pygame.draw.line(displaySurf, black, (i[0]), (i[1]))

        pygame.draw.rect(displaySurf, parchment, (exitButton))
        for line in exitBox:
            if exitButton.collidepoint((mouseX, mouseY)):
                colour = red
            else:
                colour = black
                
            pygame.draw.line(displaySurf, colour, (line[0][0], line[0][1]), (line[1][0], line[1][1]))
        exitX = handwrittenBodyFont[0].render('X', True, colour)
        
        displaySurf.blit(exitX, exitXRect)
            
        backgroundSurf.blit(displaySurf, displayRect)
        pygame.display.update()
        FPSClock.tick(30)


def drawMap(mapTiles, clickableTiles):
    imgPath = 'Images/points_of_interest'
    POIImgList = os.listdir(imgPath)

    #We search the OS for the images used for each point of interest
    #If an index error pops up here, there isn't an image for every point of interest in the tiles folder
    for i in range(len(clickableTiles)):
        clickableTiles[i].append(pygame.transform.scale(pygame.image.load(imgPath+'/'+POIImgList[i]), (tileWidth, tileHeight)))

    #Creates a dictionary of each tile, including it's coordinates (stored as x and y)
    for i in range(mapWidth):
        for j in range(mapHeight):
            rect = pygame.Rect(i*tileWidth, j*tileHeight, tileWidth, tileHeight)
            mapTiles.append({'rect': rect,
                            'x': i,
                            'y': j})

    #goes through the dictionary above and finds out which image it should display from the map file
    for i in mapTiles:
        tile = (i['x'], i['y'])
        if tile in worldMap['grass']:
            i['surf'] = grassImg
            
        if tile in worldMap['dirt']:
            i['surf'] = dirtImg

        if tile in worldMap['sand']:
            i['surf'] = sandImg

        if tile in worldMap['snow']:
            i['surf'] = snowImg

        if tile in worldMap['paved']:
            i['surf'] = pavedImg

        if tile in worldMap['marsh']:
            i['surf'] = marshImg
            
        if tile in worldMap['water']:
            i['surf'] = waterImg
            
        if tile in worldMap['mountains']:
            i['surf'] = mountainImg
            
        if tile in worldMap['wMountains']:
            i['surf'] = wMountainImg
            
        if tile in worldMap['sMountains']:
            i['surf'] = sMountainImg
            
        if tile in worldMap['forest']:
            i['surf'] = forestImg

        if tile in worldMap['redForest']:
            i['surf'] = redForestImg
            
        if tile in worldMap['pointsOfInterest']:
            for j in clickableTiles:
                if j[1] == i['rect']:
                    i['surf'] = j[2]
                    
        if tile in worldMap['allRivers']:
            i['surf'] = calcRiverImg(i, tile)

    return mapTiles
                
def calcRiverImg(i, tile):
    #This variable is run when a tile needs a river image
    #It looks at the tiles above, below, left, and right of the argument and determines what the river image should look like
    global worldMap

    if tile in worldMap['riversDirt']:
        imagePath = 'Images/Tiles/Water/dirt/river_'
        
    elif tile in worldMap['riversGrass']:
        imagePath = 'Images/Tiles/Water/grass/river_'
        
    elif tile in worldMap['riversSand']:
        imagePath = 'Images/Tiles/Water/sand/river_'
        
    elif tile in worldMap['riversSnow']:
        imagePath = 'Images/Tiles/Water/snow/river_'
        
    elif tile in worldMap['riversPaved']:
        imagePath = 'Images/Tiles/Water/paved/river_'
        
    else:
        return waterImg
    
    r = worldMap['allRivers']
    w = worldMap['water']
    m = worldMap['marsh']
    left = (i['x']-1, i['y'])
    right = (i['x']+1, i['y'])
    up = (i['x'], i['y']-1)
    down = (i['x'], i['y']+1)
    
    if (right in r or right in w or right in m) and (left in r or left in w or left in m) and\
       (up in r or up in w or up in m) and (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'urdl.png'), (tileWidth, tileHeight))
    
    elif (right in r or right in w or right in m) and (left in r or left in w or left in m) and (up in r or up in w or up in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'url.png'), (tileWidth, tileHeight))
    
    elif (right in r or right in w or right in m) and (left in r or left in w or left in m) and (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'rdl.png'), (tileWidth, tileHeight))
    
    elif (right in r or right in w or right in m) and (up in r or up in w or up in m) and (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'urd.png'), (tileWidth, tileHeight))
    
    elif (left in r or left in w or left in m) and (up in r or up in w or up in m) and (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'udl.png'), (tileWidth, tileHeight))
    
    elif (up in r or up in w or up in m) and (right in r or right in w or right in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'ur.png'), (tileWidth, tileHeight))
    
    elif (right in r or right in w or right in m) and (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'rd.png'), (tileWidth, tileHeight))
    
    elif (down in r or down in w or down in m) and (left in r or left in w or left in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'dl.png'), (tileWidth, tileHeight))
    
    elif (left in r or left in w or left in m) and (up in r or up in w or up in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'ul.png'), (tileWidth, tileHeight))
    
    elif (left in r or left in w or left in m) or (right in r or right in w or right in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'rl.png'), (tileWidth, tileHeight))
    
    elif (up in r or up in w or up in m) or (down in r or down in w or down in m):
        return pygame.transform.scale(pygame.image.load(imagePath + 'ud.png'), (tileWidth, tileHeight))
    
    else:
        #if we reach this step then the river tile isn't connected to another river tile
        #so we use a lake tile instead
        return waterImg

def readMapFile(mapfilename):
    #Reads the map text file and appends each character to a list showing what image it should use
    assert os.path.exists(mapfilename), 'cannot find the map file'
    global clickableTiles, mapWidth, mapHeight, tileWidth, tileHeight
    
    mapFile = open(mapfilename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    mapTextLines = []
    mapObj = []
    worldMap = []

    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')
        #doesn't read lines which a semi colon in them
        if ';' in line:
            continue
        if line != '':
            #mapWidth is the amount of tiles, not pixel coords
            mapWidth = len(line)
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(mapWidth):
                    mapObj[x].append(mapTextLines[y][x])

    #mapHeight is the amount of tiles, not pixel coords
    mapHeight = len(mapTextLines)
    
    #calculate the pixel size of a map tile based on the mapsize and screensize
    tileWidth = math.floor(screenWidth/mapWidth)
    tileHeight = math.floor(screenHeight/mapHeight)
    
    grass = []
    dirt = []
    sand = []
    snow = []
    paved = []
    marsh = []
    water = []
    mountains = []
    wMountains = []
    sMountains = []
    pointsOfInterest = []
    forest = []
    redForest = []

    allRivers = []
    riversGrass = []
    riversSand = []
    riversSnow = []
    riversPaved = []
    riversDirt = []

    #for each character in the map file we check which list it should be appended to (based on the character read)
    #then we at the x, y coordinates to that list
    for x in range(mapWidth):
        for y in range(len(mapObj[x])):
            if mapObj[x][y] == '-':
                grass.append((x, y))
            elif mapObj[x][y] == '_':
                dirt.append((x, y))
            elif mapObj[x][y] == '~':
                sand.append((x, y))
            elif mapObj[x][y] == '*':
                snow.append((x, y))
            elif mapObj[x][y] == 'x':
                paved.append((x, y))
            elif mapObj[x][y] == 'm':
                marsh.append((x, y))
                
            elif mapObj[x][y] == '^':
                mountains.append((x, y))
            elif mapObj[x][y] == 'n':
                wMountains.append((x, y))
            elif mapObj[x][y] == 'h':
                sMountains.append((x, y))
                
            elif mapObj[x][y] == '|':
                water.append((x, y))

            elif mapObj[x][y] == 'r' or mapObj[x][y] == 'i' or mapObj[x][y] == 'v'or mapObj[x][y] == 'e' or mapObj[x][y] == 'c':
                allRivers.append((x, y))
                if mapObj[x][y] == 'r':
                    riversGrass.append((x, y))
                elif mapObj[x][y] == 'i':
                    riversDirt.append((x, y))
                elif mapObj[x][y] == 'v':
                    riversSand.append((x, y))
                elif mapObj[x][y] == 'e':
                    riversSnow.append((x, y))
                elif mapObj[x][y] == 'c':
                    riversPaved.append((x, y))
                
            elif mapObj[x][y] == 'T':
                forest.append((x, y))
            elif mapObj[x][y] == 'P':
                redForest.append((x, y))
            else:
                pointsOfInterest.append((x, y))
                clickableTiles.append([mapObj[x][y], pygame.Rect(x*tileWidth, y*tileHeight, tileWidth, tileHeight)])
                
    #in the clickablesTiles list, the first element stored is the ASCII character used in the map file
    #for the points of interest the character used will always be a unique number
    #when we use clickableTiles.sort(), they are arranged in numerical order using that element.
    #since they're now in order, we can order the image files in the same order and it's easier to match them up
    clickableTiles.sort()

    #add all of our coordinates lists to a worldMap object which is what is returned from this function
    worldMap = {'grass': grass,
                'dirt': dirt,
                'sand': sand,
                'snow': snow,
                'paved': paved,
                'marsh': marsh,
                'water': water,
                'mountains': mountains,
                'wMountains': wMountains,
                'sMountains': sMountains,
                'pointsOfInterest': pointsOfInterest,
                'forest': forest,
                'redForest': redForest,

                'allRivers': allRivers,
                'riversDirt': riversDirt,
                'riversGrass': riversGrass,
                'riversSand': riversSand,
                'riversSnow': riversSnow,
                'riversPaved': riversPaved}

    return worldMap

def readInfoFile(file):
    infoFile = open(file, 'r')
    content = infoFile.readlines()
    infoFile.close()

    #this variable stores all of the data from the file, each element of this list is one entry
    infoText = []
    
    #this variable is a list that stores each line of text seperately until it reads a '#', then it appends this variable
    #to the POIInfoText variable
    thisEntry = []

    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')
        if line == '':
            continue
        elif line[0] == ';':
            continue
        elif line[0] == '#':
            infoText.append(thisEntry)
            thisEntry = []
            continue
        else:
            if line[-1] != ' ':
                line = line + ' '
            thisEntry.append(line)

    return infoText
        

if __name__ == '__main__':
    main()
