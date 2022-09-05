# We want to create a GUI class that will be used to create the GUI.
# The GUI will have components that will be drawn on the screen.
# The components will have events that will be listened to.
# The event handling of the components will be modifiable by the user using the GUI library.

import pygame


class GUI:
    def __init__(self, fullscreen=False, background=None, icon=None, title="window") -> None:
        # Initialize the pygame library.
        pygame.init()
        # Initialize the screen.
        self.background = None

        if background:
            self.background = pygame.image.load(background)
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.background = pygame.transform.scale(
                self.background, (self.screen.get_width(), self.screen.get_height()))
        else:
            self.screen = pygame.display.set_mode((1366, 768))
            self.background = pygame.transform.scale(
                self.background, (1366, 768))
        if icon:
            pygame.display.set_icon(pygame.image.load(icon))
        # Set title.
        pygame.display.set_caption(title)
        # Initialize the components dictionary. It is indexed by the component name.
        self.components = {}
        # Initialize component by Z index lookup table.
        self.componentsByZIndex = []
        # We will invalidate the z index lookup table when we add or remove a component, as well as when we change the z index of a component.
        self.zOrder = True
        # Initialize the fonts dictionary. It is indexed by the font name.
        self.fonts = {}

    # The registerFont function will register a font.

    def registerFont(self, name, fontName, fontSize):
        if name in self.fonts:
            raise Exception("Font already registered.")
        self.fonts[name] = pygame.font.SysFont(fontName, fontSize)

    # The getFont function will return a font.
    def getFont(self, name):
        if name in self.fonts:
            return self.fonts[name]
        # If the font is not found, exception.
        raise Exception("Font not found.")

    # The preUpdate function will get informations from pygame.
    def preUpdate(self):
        pygameInfo = {}
        pygameInfo["mouse"] = pygame.mouse.get_pos()
        pygameInfo["mouseClick"] = pygame.mouse.get_pressed()
        pygameInfo["keys"] = pygame.key.get_pressed()
        pygameInfo["events"] = pygame.event.get()
        self.events = {}
        return pygameInfo

    # The checkExit function will check if the user wants to exit the program.
    def checkExit(self, pyInfo):
        for event in pyInfo["events"]:
            if event.type == pygame.QUIT:
                self.close()
        return pyInfo

    # The draw function will draw all components on the screen.
    def draw(self):
        # draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        # else draw a black background
        else:
            self.screen.fill((0, 0, 0))
        if not self.zOrder:
            self.componentsByZIndex.sort(key=lambda x: x.zIndex)
            self.zOrder = True
        for component in self.componentsByZIndex:
            component.draw(self.screen)

    # The update function will update all components on the screen.
    def update(self, pyInfo):
        for component in self.componentsByZIndex:
            component.step(component)
            component.events(pyInfo["events"], pyInfo)

    # The addComponent function will add a component to the GUI.
    def addComponent(self, component):
        self.components[component.name] = component
        self.componentsByZIndex.append(component)
        component.setGUI(self)
        self.zOrder = False

    # The removeComponent function will remove a component from the GUI.
    def removeComponent(self, component):
        del self.components[component.name]
        self.componentsByZIndex.remove(component)
        self.zOrder = False

    # The getComponent function will return a component.
    def getComponent(self, name):
        if name in self.components:
            return self.components[name]
        # If the component is not found, exception.
        raise Exception("Component not found.")

    # The run function will run the GUI.
    def run(self):
        while True:
            pyInfo = self.preUpdate()
            pyInfo = self.checkExit(pyInfo)
            self.update(pyInfo)
            self.draw()
            pygame.display.update()
            pygame.time.delay(10)

    # The close function will close the GUI.
    def close(self):
        self.screen.close()
        pygame.quit()
        quit()

# The Component class will be the base class for all components.


class Component:
    def __init__(self, gui=None):
        self.gui = gui
        self.zIndex = 0
        self.step = lambda: None
        pass

    def events(self, events, pyInfo):
        pass

    def draw(self, screen):
        pass

    def setGUI(self, gui):
        self.gui = gui


class Drawable (Component):
    def __init__(self, name, surface, position, zIndex=0, gui=None, setup=None, step=None):
        self.name = name
        self.surface = surface
        self.position = position
        self.size = surface.get_size()
        self.zIndex = zIndex
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup()
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None

    def draw(self, screen):
        screen.blit(self.surface, self.position)

    def setZ(self, gui, zIndex):
        self.zIndex = zIndex
        gui.zOrder = False


class TextComponent (Component):
    def __init__(self, name, text, font, position, zIndex=0, color=(255, 255, 255), gui=None, setup=None, step=None):
        self.name = name
        self.text = text
        self.font = font
        self.position = position
        self.zIndex = zIndex
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup()
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None
        self.color = color

    def draw(self, screen):
        screen.blit(self.font.render(
            self.text, True, self.color), self.position)

    def setZ(self, gui, zIndex):
        self.zIndex = zIndex
        gui.zOrder = False

    def setText(self, text):
        self.text = text


class Button (Drawable):

    def __init__(self, name, position, size, colours, text, font, action, gui=None, zIndex=0, setup=None, step=None):
        self.name = name
        self.position = position
        self.size = size
        self.zIndex = zIndex
        self.colours = colours
        self.text = text
        self.font = font
        self.action = action
        self.pressed = False
        self.hover = False
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup(self)
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None

    def events(self, events, pyInfo):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.position[0] < pyInfo["mouse"][0] < self.position[0] + self.size[0] and self.position[1] < pyInfo["mouse"][1] < self.position[1] + self.size[1]:
                    self.pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if self.pressed:
                    if self.action:
                        self.action(self)
                    self.pressed = False
            if event.type == pygame.MOUSEMOTION:
                if self.position[0] < pyInfo["mouse"][0] < self.position[0] + self.size[0] and self.position[1] < pyInfo["mouse"][1] < self.position[1] + self.size[1]:
                    self.hover = True
                else:
                    self.hover = False

    def draw(self, screen):
        surf = self.preRender()
        screen.blit(surf, self.position)

    def preRender(self):
        surf = pygame.Surface(self.size)
        # Colours contains:
        # 0: border colour
        # 1: background colour (hover)
        # 2: background colour (not hover)
        # 3: text colour

        if self.hover:
            surf.fill(self.colours[1])
        else:
            surf.fill(self.colours[2])
        pygame.draw.rect(
            surf, self.colours[0], (0, 0, self.size[0], self.size[1]), 1)
        textSurf = self.font.render(self.text, True, self.colours[3])
        textRect = textSurf.get_rect()
        textRect.center = (self.size[0] / 2, self.size[1] / 2)
        surf.blit(textSurf, textRect)
        return surf

    def step(self):
        pass


class listComponent (Drawable):
    def __init__(self, name, position, size, colours, font, gui=None, zIndex=0, shownRows=15, setup=None, step=None, action=None):
        self.name = name
        self.position = position
        self.size = size
        self.zIndex = zIndex
        self.colours = colours
        self.font = font
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup(self)
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None
        self.action = action
        self.items = []
        self.scroll = 0
        self.shownRows = shownRows

    def clear(self):
        self.items = []

    def addItem(self, item):
        # See if an item with the same barcode already exists.
        for i in self.items:
            if i.barcode == item.barcode:
                # only modify the fields
                i.name = item.name
                i.price += item.price
                i.quantity += item.quantity
                i.points += item.points
                # round the price to 2 decimal places
                i.price = round(i.price, 2)
                print("Quantity: " + str(i.quantity))
                if i.quantity == 0:
                    self.items.remove(i)
                    if self.scroll > len(self.items) - self.shownRows + 1:
                        self.scroll = max(len(self.items) -
                                          self.shownRows + 1, 0)
                else:
                    # Scroll to the item
                    self.scroll = max(self.items.index(i) -
                                      self.shownRows + 2, 0)
                return
        # Scroll to the bottom of the list
        self.scroll = max(len(self.items) - self.shownRows + 2, 0)
        self.items.append(item)

    def getItems(self):
        return self.items

    def events(self, events, pyInfo):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                scroll = -event.y
                self.scroll += scroll
                # +1 because the last row is the total
                if self.scroll > len(self.items) - self.shownRows + 1:
                    self.scroll = len(self.items) - self.shownRows + 1
                if self.scroll < 0:
                    self.scroll = 0

    def preRender(self):

        # The colours contains:
        # 0: border colour
        # 1: background colour
        # 2: secondary background colour
        # 3: text colour

        surf = pygame.Surface(self.size)
        surf.fill(self.colours[1])
        pygame.draw.rect(
            surf, self.colours[0], (0, 0, self.size[0], self.size[1]), 1)
        totals = [0, 0, 0]
        i = None
        actualScroll = int(self.scroll)
        for item in self.items:
            totals[0] += item.quantity
            totals[1] += item.price
            totals[2] += item.points
        for i in range(self.shownRows-1):

            if (i+actualScroll) % 2 == 0:
                pygame.draw.rect(
                    surf, self.colours[2], (1, 1 + i * 25, self.size[0] - 2, 25))
            if i + actualScroll >= len(self.items) or i + actualScroll < 0:
                continue

            item = self.items[i + actualScroll]

            currText = item.name
            textSurf = self.font.render(currText, True, self.colours[3])
            textRect = textSurf.get_rect()
            drawPos = (self.position[0] + 0, self.position[1] - 58 + i * 25)
            surf.blit(textSurf, drawPos)
            currText = str(item.price)
            textSurf = self.font.render(currText, True, self.colours[3])
            textRect = textSurf.get_rect()
            drawPos = (self.position[0] + 625, self.position[1] - 58 + i * 25)
            surf.blit(textSurf, drawPos)
            currText = str(item.quantity)
            textSurf = self.font.render(currText, True, self.colours[3])
            textRect = textSurf.get_rect()
            drawPos = (self.position[0] + 520, self.position[1] - 58 + i * 25)
            surf.blit(textSurf, drawPos)
            currText = str(item.points)
            textSurf = self.font.render(currText, True, self.colours[3])
            textRect = textSurf.get_rect()
            drawPos = (self.position[0] + 720, self.position[1] - 58 + i * 25)
            surf.blit(textSurf, drawPos)

        ######
        # Draw a 2px line to separate the totals from the items
        pygame.draw.rect(
            surf, self.colours[0], (0, self.size[1] - 25, self.size[0], 4))
        i += 1
        currText = "TOTALE"
        textSurf = self.font.render(currText, True, self.colours[3])
        textRect = textSurf.get_rect()
        drawPos = (self.position[0] + 0, self.position[1] - 58 + i * 25)
        surf.blit(textSurf, drawPos)

        currText = str(round(totals[0], 2))
        textSurf = self.font.render(currText, True, self.colours[3])
        textRect = textSurf.get_rect()
        drawPos = (self.position[0] + 515, self.position[1] - 58 + i * 25)
        surf.blit(textSurf, drawPos)

        currText = str(round(totals[1], 2))
        # If currText is an integer, add a .00 to the end
        if totals[1] == int(totals[1]):
            currText += ".00"
        elif totals[1] * 10 == int(totals[1] * 10):
            currText += "0"
        textSurf = self.font.render(currText, True, self.colours[3])
        textRect = textSurf.get_rect()
        drawPos = (self.position[0] + 620, self.position[1] - 58 + i * 25)
        surf.blit(textSurf, drawPos)

        currText = str(totals[2])
        textSurf = self.font.render(currText, True, self.colours[3])
        textRect = textSurf.get_rect()
        drawPos = (self.position[0] + 715, self.position[1] - 58 + i * 25)
        surf.blit(textSurf, drawPos)
        ######
        return surf

    def draw(self, screen):
        screen.blit(self.preRender(), self.position)


class ToggleButton (Drawable):
    def __init__(self, name, position, size, colours, text, font, gui=None, zIndex=0, setup=None, step=None, action=None):
        self.name = name
        self.position = position
        self.size = size
        self.zIndex = zIndex
        self.colours = colours
        self.text = text
        self.font = font
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup(self)
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None
        if action != None:
            self.action = action
        else:
            self.action = lambda _: None
        self.toggled = False

    def events(self, events, pyInfo):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.position[0] <= event.pos[0] <= self.position[0] + self.size[0] and self.position[1] <= event.pos[1] <= self.position[1] + self.size[1]:
                        self.toggled = not self.toggled
                        self.action(self)

    def preRender(self):
        surf = pygame.Surface(self.size)
        surf.fill(self.colours[1] if self.toggled else self.colours[2])
        pygame.draw.rect(
            surf, self.colours[0], (0, 0, self.size[0], self.size[1]), 1)
        textSurf = self.font.render(self.text, True, self.colours[3])
        textRect = textSurf.get_rect()
        textRect.center = (self.size[0] / 2, self.size[1] / 2)
        surf.blit(textSurf, textRect)
        return surf

    def draw(self, screen):
        screen.blit(self.preRender(), self.position)

    def getChecked(self):
        return self.toggled


class InputBox (Drawable):
    def __init__(self, name, position, size, colours, font, gui=None, zIndex=0, setup=None, step=None, action=None, unselectedString="inputBox"):
        self.name = name
        self.position = position
        self.size = size
        self.zIndex = zIndex
        self.colours = colours
        self.font = font
        self.text = ""
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup(self)
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None
        self.action = action
        if self.action == None:
            self.action = lambda _: None
        self.active = False
        self.sstring = ""
        self.cursor = 0
        self.unselectedString = unselectedString

    def clear(self):
        self.text = ""
        self.sstring = ""
        self.cursor = 0

    def getString(self, clear=True):
        cpy = self.sstring
        if clear:
            self.sstring = ""
        return cpy

    def events(self, events, pyInfo):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the mouse is pressed and the mouse is over the input box, the input box is active.
                if self.position[0] < pyInfo["mouse"][0] < self.position[0] + self.size[0] and self.position[1] < pyInfo["mouse"][1] < self.position[1] + self.size[1]:
                    self.active = True
            if event.type == pygame.MOUSEBUTTONUP:
                # If the mouse is released and the mouse is not over the input box
                # the input box is not active.
                if not (self.position[0] < pyInfo["mouse"][0] < self.position[0] + self.size[0] and self.position[1] < pyInfo["mouse"][1] < self.position[1] + self.size[1]):
                    self.active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and self.active:
                    self.sstring = self.sstring[:-1]
                    if self.cursor >= len(self.sstring):
                        self.cursor = len(self.sstring) - 1
                elif event.key == pygame.K_RETURN:
                    self.action(self)
                    self.active = False
                elif event.key == pygame.K_LEFT:
                    if self.cursor > 0:
                        self.cursor -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor < len(self.sstring):
                        self.cursor += 1
                else:
                    if self.active:
                        self.sstring += event.unicode

    def preRender(self):
        # The colours are
        # 0: border colour
        # 1: background colour (active and not active)
        # 2: Text colour (active)
        # 3: Text colour (not active)
        surf = pygame.Surface(self.size)
        text = self.font.render(self.sstring if self.active or len(
            self.sstring) else self.unselectedString, True, self.colours[2] if self.active else self.colours[3])
        textRect = text.get_rect()
        PADX = 20
        renderPos = (
            PADX,
            (self.size[1] - textRect.height) / 2
        )
        surf.fill(self.colours[1])
        pygame.draw.rect(
            surf, self.colours[0], (0, 0, self.size[0], self.size[1]), 1)
        surf.blit(text, renderPos)
        return surf

    def draw(self, screen):
        surf = self.preRender()
        screen.blit(surf, self.position)


class Group (Component):
    def __init__(self, name, components, gui=None, setup=None, step=None):
        self.name = name
        self.components = components
        self.gui = gui
        self.setup = setup
        if self.setup != None:
            self.setup()
        self.step = step
        if self.step != None:
            self.step(self)
        else:
            self.step = lambda _: None

    def events(self, events, pyInfo):
        for component in self.components:
            component.events(events, pyInfo)

    def draw(self, screen):
        for component in self.components:
            component.draw(screen)
