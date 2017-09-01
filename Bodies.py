from random import randint
import pygame as pg
from pygame.math import Vector2 as V2
from math import hypot
from copy import copy

from Constants import *


class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None, name=None):
        self.mass = mass
        self.radius = int((mass/density)**(1/3))

        self.position = V2(position)
        self.velocity = V2(velocity)
        self.acceleration = V2(0, 0)

        self.density = density

        self.color = tuple(randint(0, 255) for _ in '111') if color is None else color

        self.name = name

    def copy(self):
        return Body(self.mass, self.position, self.velocity, self.density, self.color, None if self.name is None else self.name + " copy")     # inheritance of 'name' for debugging purposes only

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), int(self.radius), 0)

    def click_collision(self, mouse_pos):
        mouse_pos = V2(mouse_pos)
        return self.position.distance_to(mouse_pos) < self.radius

    def force_of(self, other, G):
        x,y = (other.position[a]-self.position[a] for a in (0,1))
        r = hypot(x,y)
        acc = G/r**3
        return V2(acc * x, acc * y)

    def test_collision(self, other):
        return other.position.distance_to(self.position) < self.radius + other.radius # Zero-tolerance collision

    def collide(self, other, COR, prop_wins):
        # Special case: perfectly inelastic collision results in merging of the two bodies
        if COR == 0:
            total_mass = self.mass + other.mass
            self.position = (self.position*self.mass + other.position*other.mass) / total_mass
            self.velocity = (self.velocity*self.mass + other.velocity*other.mass) / total_mass

            avg_density = (self.density * self.mass + other.density * other.mass) / total_mass
            self.radius = int((total_mass/avg_density)**(1/3))

            self.color = tuple(((self.color[x]*self.mass + other.color[x]*other.mass)/total_mass) for _ in '111')

            self.mass = total_mass

            # Check to see if the deleted body belongs to a properties window; If so, set win.body to the combined body
            for win in prop_wins:
                if win.body is other:
                    win.body = self
                    win.original = self.copy()
        else:
            # TODO: fix this! this is the equation for one dimension (from COR wikipedia page), which i thought would work but it doesnt seem to lol
            m, m2, v, v2 = self.mass, other.mass, self.velocity, other.velocity
            self.velocity = (m*v + m2*v2 + m2*COR*(v2-v)) / (m+m2)
            other.velocity = (m*v + m2*v2 + m*COR*(v-v2)) / (m+m2)
            d = self.position.distance_to(other.position)
            n = (other.position - self.position) / d
            p = 2 * (self.velocity.dot(n) - other.velocity.dot(n)) / (self.mass + other.mass)
            # TODO: properly incorperate COR.  This is currently incorrect, and is only a proof of concept
            self.velocity = (self.velocity - p * self.mass * n) * COR
            other.velocity = (other.velocity + p * other.mass * n) * COR

    def update_radius(self):
        self.radius = int((self.mass / self.density) ** (1 / 3))

    def apply_acceleration(self, time_factor):
        self.velocity += self.acceleration * time_factor

    def apply_velocity(self, time_factor):
        self.position += self.velocity * time_factor
