from dataclasses import dataclass
import math
import random

import pygame


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple
    alpha: float
    size: float
    lifetime: float
    age: float = 0

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 18 * dt
        return self.age < self.lifetime

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        fade = max(0, 1 - self.age / self.lifetime)
        radius = max(1, int(self.size * fade))
        color = tuple(max(0, min(255, int(channel * fade * self.alpha))) for channel in self.color)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)


class ParticleManager:
    def __init__(self, max_particles=450):
        self.max_particles = max_particles
        self.particles = []

    def emit(self, x, y, color, count=6, speed=70, size=4, lifetime=0.45, alpha=1.0):
        if self.max_particles <= 0:
            return

        alpha = max(0.0, min(1.0, alpha))
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                self.particles.pop(0)
            angle = random.uniform(0, math.tau)
            velocity = random.uniform(speed * 0.25, speed)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * velocity,
                    vy=math.sin(angle) * velocity,
                    color=color,
                    alpha=alpha,
                    size=random.uniform(size * 0.55, size * 1.2),
                    lifetime=random.uniform(lifetime * 0.65, lifetime * 1.2),
                )
            )

    def update(self, dt):
        self.particles = [particle for particle in self.particles if particle.update(dt)]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

    def clear(self):
        self.particles.clear()
