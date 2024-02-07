import numpy as np
import pandas as pd
import pygame
import sys

# Constants
WIDTH, HEIGHT = 640, 360
DESIRED_SEPARATION = 25.0
NEIGHBOR_DISTANCE = 50
BOID_COUNT = 150

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Boid:
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)
        angle = np.random.uniform(0, 2 * np.pi)
        self.velocity = np.array([np.cos(angle), np.sin(angle)], dtype=float)
        self.acceleration = np.zeros(2, dtype=float)
        self.r = 2.0
        self.max_speed = 10
        self.max_force = 0.03

    def apply_force(self, force):
        self.acceleration += force

    def flock(self, boids):
        sep = self.separate(boids)
        ali = self.align(boids)
        coh = self.cohesion(boids)

        sep *= 1.5
        ali *= 1.0
        coh *= 1.0

        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

    def separate(self, boids):
        steer = np.zeros(2, dtype=float)
        count = 0

        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if 0 < d < DESIRED_SEPARATION:
                diff = self.position - other.position
                diff /= d  # Weight by distance
                steer += diff
                count += 1

        if count > 0:
            steer /= count

        if np.linalg.norm(steer) > 0:
            steer /= np.linalg.norm(steer)
            steer *= self.max_speed
            steer -= self.velocity
            steer = np.clip(steer, -self.max_force, self.max_force)

        return steer

    def align(self, boids):
        sum_vel = np.zeros(2, dtype=float)
        count = 0

        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if 0 < d < NEIGHBOR_DISTANCE:
                sum_vel += other.velocity
                count += 1

        if count > 0:
            avg_vel = sum_vel / count
            avg_vel /= np.linalg.norm(avg_vel)
            avg_vel *= self.max_speed
            steer = avg_vel - self.velocity
            steer = np.clip(steer, -self.max_force, self.max_force)
            return steer
        else:
            return np.zeros(2, dtype=float)

    def cohesion(self, boids):
        sum_pos = np.zeros(2, dtype=float)
        count = 0

        for other in boids:
            d = np.linalg.norm(self.position - other.position)
            if 0 < d < NEIGHBOR_DISTANCE:
                sum_pos += other.position
                count += 1

        if count > 0:
            avg_pos = sum_pos / count
            return self.seek(avg_pos)
        else:
            return np.zeros(2, dtype=float)

    def seek(self, target):
        desired = target - self.position
        desired /= np.linalg.norm(desired)
        desired *= self.max_speed
        steer = desired - self.velocity
        steer = np.clip(steer, -self.max_force, self.max_force)
        return steer

    def update(self):
        self.velocity += self.acceleration
        self.velocity = np.clip(self.velocity, -self.max_speed, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def borders(self):
        if self.position[0] < -self.r:
            self.position[0] = WIDTH + self.r
        if self.position[1] < -self.r:
            self.position[1] = HEIGHT + self.r
        if self.position[0] > WIDTH + self.r:
            self.position[0] = -self.r
        if self.position[1] > HEIGHT + self.r:
            self.position[1] = -self.r

    def render(self, screen):
        theta = np.arctan2(self.velocity[1], self.velocity[0]) + np.radians(90)
        pygame.draw.polygon(screen, RED, self.triangle(theta))

    def triangle(self, theta):
        return [
            (self.position[0] + np.cos(theta) * self.r * 2, self.position[1] + np.sin(theta) * self.r * 2),
            (self.position[0] + np.cos(theta - 2 * np.pi / 3) * self.r, self.position[1] + np.sin(theta - 2 * np.pi / 3) * self.r),
            (self.position[0] + np.cos(theta + 2 * np.pi / 3) * self.r, self.position[1] + np.sin(theta + 2 * np.pi / 3) * self.r)
        ]

class Flock:
    def __init__(self):
        self.boids = []

    def run(self):
        for boid in self.boids:
            boid.flock(self.boids)
            boid.update()
            boid.borders()
            boid.render(screen)

    def add_boid(self, boid):
        self.boids.append(boid)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flocking Simulation")

clock = pygame.time.Clock()

# Create flock and add initial boids
flock = Flock()
for _ in range(BOID_COUNT):
    flock.add_boid(Boid(WIDTH / 2, HEIGHT / 2))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)
    flock.run()

    pygame.display.flip()
    clock.tick(10000)
