from Entity import Entity
from math import pi, cos, sin
from random import random
from Bullet import Bullet

class Enemy(Entity):
    def __init__(self, orientation, canvas, size_class, enemy_id):
        super().__init__(orientation, canvas)
        self.size_class = size_class
        self.size = size_class * 5
        self.vel_x = self.rand_speed()
        self.vel_y = self.rand_speed()
        self.bounty = self.assign_bounty()
        self.original_points = self.genereate_model()
        self.points = self.original_points.copy()
        self.id = enemy_id

        self.center_x, self.center_y = self.rand_coords()

        self.ammunition = 5
        self.bullets = [None] * self.ammunition

        # Offset
        for i in range(len(self.points)):
            if i % 2 == 0:
                self.points[i] = self.center_x + self.original_points[i]
            else:
                self.points[i] = self.center_y + self.original_points[i]

        self.model = self.canvas.create_polygon(self.points, outline="white", width=1)

    def rand_coords(self):
        w = 1080
        h = 1080
        min_w = w*0.05
        max_w = w*0.95
        min_h = h*0.05
        max_h = h*0.95
        if random() < 0.5:
            if random() < 0.5:
                x = min_w
            else:
                x = max_w
            y = min_h + max_h*random()
        else:
            if random() < 0.5:
                y = min_h
            else:
                y = max_h
            x = min_w + max_w*random()

        return x, y

    def rand_speed(self):
        speed_constant = 1
        speed = 0.6 + speed_constant*random()*(5/self.size)
        if random() < 0.5:
            return -speed
        else:
            return speed

    def genereate_model(self):
        points = [-5, 0, -2, -2, -1, -4, 1, -4, 2, -2,
                  -2, -2, 2, -2, 5, 0, -5, 0, -3, 2, 3, 2, 5, 0]
        points = [i * self.size_class * 2 for i in points]
        return points

    def assign_bounty(self):
        if self.size_class == 1:
            return 100
        elif self.size_class == 2:
            return 50
        elif self.size_class == 3:
            return 20
        return 10

    def explode(self):
        for bullet in self.bullets:
            if bullet is not None:
                self.canvas.delete(bullet.model)
        self.canvas.delete(self.model)
        return

    def shoot(self):
        if random() < 0.005:
            for i in range(len(self.bullets)):
                if self.bullets[i] is None:
                    orientation = 2 * pi * random()
                    self.bullets[i] = Bullet(orientation, self.canvas, self.center_x, self.center_y, self, i, "red")
                    break

    def update(self):
        self.move()
        self.test_bounds()
        self.shoot()

    def reload(self):
        pass

    def move(self):
        for i in range(len(self.points)):
            if i % 2 == 0:
                self.points[i] = self.vel_x + self.center_x + self.original_points[i]
            else:
                self.points[i] = self.vel_y + self.center_y + self.original_points[i]
        self.canvas.delete(self.model)
        self.model = self.canvas.create_polygon(self.points, outline="white", width=1)

        self.center_x += self.vel_x
        self.center_y += self.vel_y

        self.test_bounds()

    def test_bounds(self):
        w = 1080
        h = 1080
        min_w = 0 - w*0.05
        max_w = w + w*0.05
        min_h = 0 - h*0.05
        max_h = h + h*0.05
        if self.center_x > max_w:
            self.center_x = min_w + w * 0.05
        if self.center_x < min_w:
            self.center_x = max_w - w * 0.05
        if self.center_y > max_h:
            self.center_y = min_h + h * 0.05
        if self.center_y < min_h:
            self.center_y = max_h - h * 0.05