import pygame
import collections

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        self.engine = engine
        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):

    def connect_engine(self, engine):
        # FIXME save engine and send it to next in chain
        self.game_engine = engine
        super().connect_engine(engine)

    def draw_hero(self):
        self.game_engine.hero.draw(self)

    def draw_map(self):

        screen_width = self.get_width() // self.game_engine.sprite_size
        screen_height = self.get_height() // self.game_engine.sprite_size
        
        hero_x, hero_y = self.game_engine.hero.position
        
        # Center on hero
        min_x = max(0, hero_x - screen_width // 2)
        min_y = max(0, hero_y - screen_height // 2)
        
        # Adjust if near edge
        if min_x + screen_width > len(self.game_engine.map[0]):
            min_x = len(self.game_engine.map[0]) - screen_width
        if min_y + screen_height > len(self.game_engine.map):
            min_y = len(self.game_engine.map) - screen_height
        
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        
        self.min_x = min_x
        self.min_y = min_y

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    self.blit(self.game_engine.map[min_y + j][min_x + i][
                              0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        size = self.game_engine.sprite_size
        self.blit(sprite, ((coord[0] - self.min_x) * size,
                          (coord[1] - self.min_y) * size))

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        
        if not hasattr(self, 'min_x'):
            self.min_x = 0
            self.min_y = 0
            
        self.draw_map()
        
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0], 
                     ((obj.position[0] - self.min_x) * size,
                      (obj.position[1] - self.min_y) * size))
        
        self.draw_hero()
        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))

        # draw next surface in chain
        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))

        # FIXME
        # draw next surface in chain
        super().draw(canvas)

    def connect_engine(self, engine):
        # FIXME set this class as Observer to engine and send it to next in
        # chain
        self.engine = engine
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])
        # FIXME You can add some help information
        self.data.append([" M ", "Show/Hide Minimap"])
        self.data.append(["", ""])
        self.data.append(["Collect gold and XP"])
        self.data.append(["Avoid enemies or fight"])
        self.data.append(["Find exit to next level"])

    def connect_engine(self, engine):
        # FIXME save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))
        # FIXME
        # draw next surface in chain
        super().draw(canvas)


class MinimapWindow(ScreenHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_minimap = True

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        if self.engine.show_minimap and self.engine.map:
            self.fill((0, 0, 0, 150))
            
            # Draw minimap border
            pygame.draw.rect(self, (255, 255, 255), (5, 5, 152, 152), 2)
            
            # Calculate minimap scale
            map_width = len(self.engine.map[0])
            map_height = len(self.engine.map)
            
            if map_width > 0 and map_height > 0:
                cell_size = min(150 // map_width, 150 // map_height)
                
                # Draw map tiles
                for y in range(min(map_height, 150 // cell_size)):
                    for x in range(min(map_width, 150 // cell_size)):
                        tile = self.engine.map[y][x][0]
                        color = (100, 100, 100)
                        if tile == wall[0]:
                            color = (50, 50, 50)
                        
                        pygame.draw.rect(self, color, 
                                        (5 + x * cell_size, 5 + y * cell_size, 
                                         cell_size, cell_size))
                
                # Draw hero position
                hero_x, hero_y = self.engine.hero.position
                if hero_x < map_width and hero_y < map_height:
                    pygame.draw.rect(self, (255, 0, 0),
                                   (5 + hero_x * cell_size, 5 + hero_y * cell_size,
                                    cell_size, cell_size))
                
                # Draw enemies
                for obj in self.engine.objects:
                    if isinstance(obj, Objects.Enemy):
                        obj_x, obj_y = obj.position
                        pygame.draw.rect(self, (0, 0, 255),
                                       (5 + obj_x * cell_size, 5 + obj_y * cell_size,
                                        cell_size, cell_size))
        
        super().draw(canvas)
