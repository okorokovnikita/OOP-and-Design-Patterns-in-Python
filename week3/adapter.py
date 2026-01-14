class MappingAdapter:
    def __init__(self, adaptee):
        # adaptee - это объект класса Light
        self.adaptee = adaptee
    
    def lighten(self, grid):
        # Определяем размеры карты (высота, ширина)
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        
        # Устанавливаем размеры в адаптируемом объекте
        self.adaptee.set_dim((width, height))
        
        # Собираем координаты источников света и препятствий
        lights = []
        obstacles = []
        
        # Проходим по всем клеткам карты
        for y in range(height):
            for x in range(width):
                if grid[y][x] == 1:  # Источник света
                    lights.append((x, y))
                elif grid[y][x] == -1:  # Препятствие
                    obstacles.append((x, y))
        
        # Устанавливаем источники света и препятствия
        self.adaptee.set_lights(lights)
        self.adaptee.set_obstacles(obstacles)
        
        # Возвращаем освещенную карту
        return self.adaptee.generate_lights()
