#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
import math

SCREEN_DIM = (800, 600)


class Vec2d:
    """
    2D вектор с базовыми операциями.
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Сложение векторов."""
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Вычитание векторов."""
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, k: float):
        """Умножение вектора на скаляр."""
        return Vec2d(self.x * k, self.y * k)

    def __rmul__(self, k: float):
        """Умножение скаляра на вектор (для симметрии)."""
        return self.__mul__(k)

    def __len__(self):
        """Длина вектора (евклидова норма)."""
        return math.sqrt(self.x**2 + self.y**2)

    def int_pair(self):
        """Возвращает кортеж из целых координат вектора."""
        return int(self.x), int(self.y)

    def __getitem__(self, index):
        """Позволяет обращаться к координатам как к кортежу: v[0], v[1]."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vec2d index out of range")

    def __iter__(self):
        """Позволяет итерироваться по координатам вектора."""
        yield self.x
        yield self.y


class Polyline:
    """
    Класс замкнутой ломаной, состоящей из точек Vec2d и скоростей.
    """
    def __init__(self):
        self.points = []
        self.speeds = []

    def add_point(self, point: Vec2d, speed: Vec2d):
        """Добавляет точку и её скорость."""
        self.points.append(point)
        self.speeds.append(speed)

    def set_points(self):
        """Пересчитывает координаты точек."""
        for i in range(len(self.points)):
            self.points[i] = self.points[i] + self.speeds[i]

            # Отражение от границ экрана
            if self.points[i].x > SCREEN_DIM[0] or self.points[i].x < 0:
                self.speeds[i] = Vec2d(-self.speeds[i].x, self.speeds[i].y)
            if self.points[i].y > SCREEN_DIM[1] or self.points[i].y < 0:
                self.speeds[i] = Vec2d(self.speeds[i].x, -self.speeds[i].y)

    def draw_points(self, display, style="points", width=3, color=(255, 255, 255)):
        """Отрисовывает точки или линии."""
        if style == "line":
            if len(self.points) < 2:
                return
            points = [p.int_pair() for p in self.points]
            pygame.draw.lines(display, color, True, points, width)
        elif style == "points":
            for p in self.points:
                pygame.draw.circle(display, color, p.int_pair(), width)


class Knot(Polyline):
    """
    Класс кривой, наследующий Polyline.
    Вычисляет сглаженные точки с помощью алгоритма де Кастельжо.
    """
    def __init__(self, steps=35):
        super().__init__()
        self.steps = steps

    def get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        return points[deg] * alpha + self.get_point(points, alpha, deg - 1) * (1 - alpha)

    def get_points(self, base_points, count):
        alpha = 1 / count
        res = []
        for i in range(count):
            res.append(self.get_point(base_points, i * alpha))
        return res

    def get_knot(self):
        """Вычисляет точки кривой по опорным точкам."""
        if len(self.points) < 3:
            return []
        res = []
        for i in range(-2, len(self.points) - 2):
            ptn = []
            ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
            ptn.append(self.points[i + 1])
            ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)

            res.extend(self.get_points(ptn, self.steps))
        return res

    def draw_points(self, display, style="line", width=3, color=(255, 255, 255)):
        """Отрисовывает сглаженную кривую."""
        if style == "line":
            knot_points = self.get_knot()
            if len(knot_points) < 2:
                return
            points = [p.int_pair() for p in knot_points]
            pygame.draw.lines(display, color, False, points, width)
        else:
            super().draw_points(display, style, width, color)


def draw_help(display, steps):
    """Функция отрисовки экрана справки."""
    display.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = [
        ["F1", "Show Help"],
        ["R", "Restart"],
        ["P", "Pause/Play"],
        ["Num+", "More points"],
        ["Num-", "Less points"],
        ["", ""],
        [str(steps), "Current points"]
    ]

    pygame.draw.lines(display, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        display.blit(font1.render(text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        display.blit(font2.render(text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


# =======================================================================================
# Основная программа
# =======================================================================================
if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    steps = 35
    working = True
    show_help = False
    pause = True

    hue = 0
    color = pygame.Color(0)

    # Создаём кривую
    knot = Knot(steps)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    knot = Knot(steps)
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    steps += 1
                    knot.steps = steps
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    steps = max(1, steps - 1)
                    knot.steps = steps

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = Vec2d(*event.pos)
                speed = Vec2d(random.random() * 2, random.random() * 2)
                knot.add_point(pos, speed)

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)

        knot.draw_points(gameDisplay, "points")
        knot.draw_points(gameDisplay, "line", 3, color)

        if not pause:
            knot.set_points()

        if show_help:
            draw_help(gameDisplay, steps)

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
