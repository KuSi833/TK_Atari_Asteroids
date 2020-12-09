from Entity import Entity
from math import sin, cos, sqrt


class Bullet(Entity):
    def __init__(self, orientation, canvas, center_x, center_y, player, mag, colour):
        super().__init__(orientation, canvas)

        bullet_speed = 6
        self.vel_x = sin(orientation) * bullet_speed
        self.vel_y = cos(orientation) * bullet_speed * -1
        self.player = player
        self.mag = mag
        self.colour = colour

        self.center_x, self.center_y = center_x, center_y
        self.distance_traveled = 0
        self.distanced_limit = 800
        self.radius = 3

        self.model = self.canvas.create_oval(self.center_x-self.radius, self.center_y-self.radius,
                                             self.center_x+self.radius, self.center_y+self.radius,
                                             fill=self.colour, width="1")
        
    def move(self):
        self.canvas.delete(self.model)
        self.model = self.canvas.create_oval(self.center_x-self.radius, self.center_y-self.radius,
                                             self.center_x+self.radius, self.center_y+self.radius,
                                             fill=self.colour, width="1")

        self.center_x += self.vel_x
        self.center_y += self.vel_y
        self.distance_traveled += abs(self.vel_x) + abs(self.vel_y)

        if abs(self.distance_traveled) > self.distanced_limit:
            self.remove()

        self.test_bounds()

    def remove(self):
        self.canvas.delete(self.model)
        self.player.bullets[self.mag] = None
        self.player.reload()

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
