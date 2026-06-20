import array
import math

import pygame


def make_tone(frequency, duration=0.08, volume=0.25):
    sample_rate = 22050
    sample_count = int(sample_rate * duration)
    samples = array.array("h")
    amplitude = int(32767 * volume)

    for index in range(sample_count):
        fade = 1 - index / max(1, sample_count)
        value = int(amplitude * fade * math.sin(2 * math.pi * frequency * index / sample_rate))
        samples.append(value)

    return pygame.mixer.Sound(buffer=samples.tobytes())
