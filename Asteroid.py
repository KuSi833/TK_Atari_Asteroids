from Entity import Entity
from math import pi, cos, sin
from random import random

class Asteroid(Entity):
    def __init__(self, orientation, canvas, size_class, asteroid_id, pos_x=0, pos_y=0):
        super().__init__(orientation, canvas)
        self.size_class = size_class
        self.size = size_class * 25
        self.vel_x = self.rand_speed()
        self.vel_y = self.rand_speed()
        self.bounty = self.assign_bounty()
        self.original_points = self.genereate_model()
        self.points = self.original_points.copy()
        self.id = asteroid_id

        if pos_x == 0 and pos_y == 0: # Random or same as destoyed asteroid
            self.center_x, self.center_y = self.rand_coords()
        else:
            self.center_x, self.center_y = pos_x, pos_y

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
        speed = 0.2 + speed_constant*random()*(50/self.size)
        if random() < 0.5:
            return -speed
        else:
            return speed

    def genereate_model(self):
        points = []
        for i in range(14):
            angle = (i/14)*(pi*2)
            r = self.size*0.7 + self.size*0.3 * random()
            points.append(r * cos(angle))
            points.append(r * sin(angle))
        return points

    def assign_bounty(self):
        if self.size_class == 1:
            return 100
        elif self.size_class == 2:
            return 50
        elif self.size_class == 3:
            return 20
        return 10

    def explode(self, asteroid_id):
        self.canvas.delete(self.model)
        new_asteroids = []
        if self.size_class != 1:
            for i in range(2):
                new_asteroids.append(Asteroid(0, self.canvas, self.size_class-1, asteroid_id, self.center_x, self.center_y))
                asteroid_id += 1
        return new_asteroids, asteroid_id

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