import pygame
import random
from pygame.locals import *

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Boid class
class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = pygame.Vector2(0, 0)
        self.r = 2.0
        self.maxspeed = 2
        self.maxforce = 0.03

    def run(self, boids):
        self.flock(boids)
        self.update()
        self.borders()
        self.render()

    def applyForce(self, force):
        self.acceleration += force

    def flock(self, boids):
        sep = self.separate(boids)
        ali = self.align(boids)
        coh = self.cohesion(boids)

        # Check if sep vector has non-zero length before scaling
        if sep.length() > 0:
            sep.scale_to_length(1.5)
        
        ali.scale_to_length(1.0)
        coh.scale_to_length(1.0)

        self.applyForce(sep)
        self.applyForce(ali)
        self.applyForce(coh)

    def update(self):
        self.velocity += self.acceleration
        self.velocity.scale_to_length(self.maxspeed)
        self.position += self.velocity
        self.acceleration *= 0

    def seek(self, target):
        desired = target - self.position
        desired.normalize_ip()
        desired *= self.maxspeed
        steer = desired - self.velocity
        steer.scale_to_length(self.maxforce)
        return steer

    def render(self):
        theta = self.velocity.angle_to(pygame.Vector2(0, 1)) + 90
        pygame.draw.polygon(screen, WHITE, [
            self.position + pygame.Vector2(0, -self.r*2),
            self.position + pygame.Vector2(-self.r, self.r*2),
            self.position + pygame.Vector2(self.r, self.r*2)
        ])

    def borders(self):
        if self.position.x < -self.r:
            self.position.x = SCREEN_WIDTH + self.r
        if self.position.y < -self.r:
            self.position.y = SCREEN_HEIGHT + self.r
        if self.position.x > SCREEN_WIDTH + self.r:
            self.position.x = -self.r
        if self.position.y > SCREEN_HEIGHT + self.r:
            self.position.y = -self.r

    def separate(self, boids):
        desiredseparation = 25.0
        steer = pygame.Vector2(0, 0)
        count = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if 0 < d < desiredseparation:
                diff = self.position - other.position
                diff.normalize_ip()
                diff /= d
                steer += diff
                count += 1
        if count > 0:
            steer /= count
        if steer.length() > 0:
            steer.normalize_ip()
            steer *= self.maxspeed
            steer -= self.velocity
            steer.scale_to_length(self.maxforce)
        return steer

    def align(self, boids):
        neighbordist = 50
        sum_vel = pygame.Vector2(0, 0)
        count = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if 0 < d < neighbordist:
                sum_vel += other.velocity
                count += 1
        if count > 0:
            sum_vel /= count
            sum_vel.normalize_ip()
            sum_vel *= self.maxspeed
            steer = sum_vel - self.velocity
            steer.scale_to_length(self.maxforce)
            return steer
        else:
            return pygame.Vector2(0, 0)

    def cohesion(self, boids):
        neighbordist = 50
        sum_pos = pygame.Vector2(0, 0)
        count = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if 0 < d < neighbordist:
                sum_pos += other.position
                count += 1
        if count > 0:
            sum_pos /= count
            return self.seek(sum_pos)
        else:
            return pygame.Vector2(0, 0)


# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flocking Simulation")

# Create a flock
flock = []

# Add boids to the flock
for _ in range(150):
    flock.append(Boid(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            flock.append(Boid(event.pos[0], event.pos[1]))

    screen.fill(BLACK)

    # Run the flock
    for boid in flock:
        boid.run(flock)

    pygame.display.flip()

pygame.quit()
