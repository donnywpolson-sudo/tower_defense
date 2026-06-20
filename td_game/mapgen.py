import random

from .config import BUILD_GRID_TOP, BUILD_GRID_STEP, HEIGHT, MAP_WIDTH, PATH_WIDTH
from .data import MAPS


MIN_PATH_LENGTH = 1850
MAX_PATH_LENGTH = 2250
MIN_VERTICAL_STEP = 85
MAX_VERTICAL_STEP = 210
MIN_TURNS = 6
MAX_TURNS = 8
THEMES = ("forest", "swamp", "snow", "lava")


def path_length(path):
    total = 0
    for start, end in zip(path, path[1:]):
        total += abs(end[0] - start[0]) + abs(end[1] - start[1])
    return total


def generate_random_map(seed=None):
    if seed is None:
        seed = random.SystemRandom().randint(1000, 999999)

    rng = random.Random(seed)
    for _ in range(160):
        path = _generate_candidate_path(rng)
        length = path_length(path)
        if MIN_PATH_LENGTH <= length <= MAX_PATH_LENGTH and _path_in_bounds(path):
            return {
                "name": "Random Road",
                "theme": rng.choice(THEMES),
                "seed": seed,
                "paths": [path],
            }

    fallback = dict(MAPS[0])
    fallback["name"] = "Random Fallback"
    fallback["seed"] = seed
    return fallback


def _generate_candidate_path(rng):
    vertical_count = rng.randint(MIN_TURNS, MAX_TURNS)
    x_turns = _x_turns(rng, vertical_count)
    y_values = _y_values(rng, vertical_count + 1)

    path = [(0, y_values[0])]
    current_y = y_values[0]
    for x, next_y in zip(x_turns, y_values[1:]):
        path.append((x, current_y))
        path.append((x, next_y))
        current_y = next_y
    path.append((MAP_WIDTH, current_y))
    return path


def _x_turns(rng, count):
    section = MAP_WIDTH / (count + 1)
    turns = []
    previous = 0
    for index in range(count):
        base = int(section * (index + 1))
        jitter = rng.randint(-28, 28)
        x = max(previous + 82, min(MAP_WIDTH - 82, base + jitter))
        turns.append(x)
        previous = x
    return turns


def _y_values(rng, count):
    min_y = _snap_y(BUILD_GRID_TOP + PATH_WIDTH + 30)
    max_y = _snap_y(HEIGHT - PATH_WIDTH - 20)
    current = rng.randrange(min_y, max_y + 1, BUILD_GRID_STEP)
    values = [current]
    direction = rng.choice((-1, 1))

    for _ in range(count - 1):
        for _ in range(20):
            step = rng.randrange(MIN_VERTICAL_STEP, MAX_VERTICAL_STEP + 1, BUILD_GRID_STEP)
            candidate = _snap_y(current + direction * step)
            if min_y <= candidate <= max_y and abs(candidate - current) >= MIN_VERTICAL_STEP:
                break
            direction *= -1
        else:
            candidates = [
                y for y in range(min_y, max_y + 1, BUILD_GRID_STEP)
                if abs(y - current) >= MIN_VERTICAL_STEP
            ]
            candidate = rng.choice(candidates)

        values.append(candidate)
        current = candidate
        if rng.random() < 0.72:
            direction *= -1

    return values


def _snap_y(value):
    return int(round(value / BUILD_GRID_STEP) * BUILD_GRID_STEP)


def _path_in_bounds(path):
    min_y = BUILD_GRID_TOP + PATH_WIDTH // 2
    max_y = HEIGHT - PATH_WIDTH // 2
    return all(0 <= x <= MAP_WIDTH and min_y <= y <= max_y for x, y in path)
