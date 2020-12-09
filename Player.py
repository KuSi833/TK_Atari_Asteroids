from random import random
from collections import deque
from Entity import Entity
from math import cos, sin, pi
from Bullet import Bullet

class Player(Entity):
    def __init__(self, orientation, canvas, match):
        super().__init__(orientation, canvas)
        self.match = match
        self.vel_x = 0
        self.vel_y = 0

        self.ammunition = 5
        self.bullets = [None] * self.ammunition

        self.respawn_timer = 0
        self.alive = True

        # self.points = [-18, -0, -15, -10, -6, -40, 0, -50, 6, -40, 18, -0, 15, -10, -15, -10] # used to make model
        self.points = [0, 60, 18, 0, 36, 60, 33, 50, 3, 50] # used to make model
        self.original_points = self.points.copy() # used to calculate rotation
        self.rotation_points = self.original_points.copy()

        # Centroid of original model position
        self.og_x = (self.original_points[0] + self.original_points[2] + self.original_points[4])/3
        self.og_y = (self.original_points[1] + self.original_points[3] + self.original_points[5])/3

        #Offseting to center
        self.go_to_center()
        self.rotate()

        for i in range(len(self.points)):
            if i % 2 == 0:
                self.points[i] = self.center_x + self.rotation_points[i]
            else:
                self.points[i] = self.center_y + self.rotation_points[i]

        self.model = self.canvas.create_polygon(self.points, outline="white", width=1)

    def go_to_center(self):
        self.center_x, self.center_y = 500, 500
        self.vel_x, self.vel_y = 0, 0

    def rotate_left(self, event):
        self.rotate("left")

    def rotate_right(self, event):
        self.rotate("right")

    def rotate(self, direction=None):
        if self.alive:
            angle = 0
            angle_val = pi*0.1
            if direction is not None:
                if direction == "left":
                    angle = - angle_val
                elif direction == "right":
                    angle = angle_val
                self.orientation += angle

            # Rotation points
            for i in range(0, len(self.points), 2):
                c = cos(self.orientation)
                s = sin(self.orientation)
                self.rotation_points[i] = c * (self.original_points[i]-self.og_x) - s * (self.original_points[i+1]-self.og_y)
                self.rotation_points[i+1] = s * (self.original_points[i]-self.og_x) + c * (self.original_points[i+1]-self.og_y)

    def boost(self, event):
        speed_val = -3
        self.vel_x = sin(self.orientation) * speed_val * -1
        self.vel_y = cos(self.orientation) * speed_val

    def jump(self, event):
        if self.alive:
            w = 1080
            h = 1080
            min_w = w*0.1
            max_w = w*0.9
            min_h = h*0.1
            max_h = h*0.9
            self.center_x = min_w + (max_w - min_w)*random()
            self.center_y = min_h + (max_h - min_h)*random()
            self.vel_x = 0
            self.vel_y = 0

    def shoot(self, event):
        if self.alive:
            if self.ammunition > 0:
                for i in range(len(self.bullets)):
                    if self.bullets[i] is None:
                        self.bullets[i] = Bullet(self.orientation, self.canvas, self.center_x, self.center_y, self, i, "green2")
                        break
                self.ammunition -= 1

    def reload(self):
        self.ammunition += 1

    def destroy(self):
        self.respawn_timer = 2000
        self.alive = False
        self.canvas.delete(self.model)
        # Call death animation

    def respawn(self):
        self.go_to_center()
        self.alive = True

    def test_respawn(self):
        if self.respawn_timer > 0:
            self.respawn_timer -= 10
        if self.respawn_timer == 0 and self.match.center_is_clear() and not self.match.perma_death:
            self.respawn()

    def update(self):
        if self.alive:
            self.move()
            self.test_bounds()
        else:
            self.test_respawn()

    def move(self):
        for i in range(len(self.points)):
            if i % 2 == 0:
                self.points[i] = self.center_x + self.rotation_points[i]
            else:
                self.points[i] = self.center_y + self.rotation_points[i]
        self.canvas.delete(self.model)
        self.model = self.canvas.create_polygon(self.points, outline="white", width=1)

        # Resistance
        resistance_val = 0.02
        if self.vel_x > resistance_val:
            self.vel_x -= resistance_val
        elif self.vel_x < -resistance_val:
            self.vel_x += resistance_val

        if self.vel_y > resistance_val:
            self.vel_y -= resistance_val
        elif self.vel_y < -resistance_val:
            self.vel_y += resistance_val

        self.center_x += self.vel_x
        self.center_y += self.vel_y

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