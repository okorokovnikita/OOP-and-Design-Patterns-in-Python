from abc import ABC, abstractmethod
import pygame
import random


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass

class AbstractObject(ABC):

    def __init__(self):
        pass
    
    def draw(self, display):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats["strength"] += 5
        self.stats["endurance"] += 5
        self.base.calc_max_HP()
        self.base.hp = self.base.max_hp


class Blessing(Effect):
    def apply_effect(self):
        self.stats["strength"] += 3
        self.stats["endurance"] += 3
        self.stats["luck"] += 3
        self.base.calc_max_HP()
        self.base.hp = self.base.max_hp


class Weakness(Effect):
    def apply_effect(self):
        self.stats["strength"] = max(1, self.stats["strength"] - 3)
        self.stats["endurance"] = max(1, self.stats["endurance"] - 3)

class Power(Effect):
    def apply_effect(self):
        # Просто увеличиваем силу на 7
        self.stats["strength"] += 7

class Enemy(Creature, Interactive):
    def __init__(self, icon, stats, experience, position):
        super().__init__(icon, stats, position)
        self.experience = experience
        
    def interact(self, engine, hero):
        hero.exp += self.experience
        engine.notify(f"Got {self.experience} experience")
        
        # Calculate damage
        damage = max(0, self.stats["strength"] - hero.stats["endurance"])
        hero.hp = max(0, hero.hp - damage)
        
        if hero.hp <= 0:
            hero.position = [1, 1]
            hero.hp = hero.max_hp
            engine.notify("You died! Restarting level...")
        else:
            engine.objects.remove(self)
            engine.notify(f"Enemy defeated! Lost {damage} HP")