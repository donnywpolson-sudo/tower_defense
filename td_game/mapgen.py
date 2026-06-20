import math
import random

from .config import (
    BUILD_GRID_TOP,
    BUILD_GRID_STEP,
    BUILD_TILE_SIZE,
    HEIGHT,
    MAP_WIDTH,
    PATH_WIDTH,
)
from .data import MAPS


MIN_PATH_LENGTH = 1450
MAX_PATH_LENGTH = 1850
MIN_VERTICAL_STEP = 115
MAX_VERTICAL_STEP = 235
MIN_TURNS = 4
MAX_TURNS = 5
MIN_PARALLEL_LANE_SPACING = PATH_WIDTH + BUILD_TILE_SIZE + 18
MIN_BUILDABLE_SITES = 78
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
        if path is None:
            continue

        length = path_length(path)
        if (
            MIN_PATH_LENGTH <= length <= MAX_PATH_LENGTH
            and _path_in_bounds(path)
            and path_has_open_build_corridors(path)
            and count_buildable_sites(path) >= MIN_BUILDABLE_SITES
        ):
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
    if x_turns is None:
        return None

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
        jitter = rng.randint(-24, 24)
        lower = previous + MIN_PARALLEL_LANE_SPACING
        upper = MAP_WIDTH - MIN_PARALLEL_LANE_SPACING
        if lower > upper:
            return None

        x = max(lower, min(upper, base + jitter))
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


def path_has_open_build_corridors(path):
    """Reject tight snake lanes that leave no tower-sized space between roads."""

    vertical_segments = []
    horizontal_segments = []
    for start, end in zip(path, path[1:]):
        if start[0] == end[0]:
            y1, y2 = sorted((start[1], end[1]))
            vertical_segments.append((start[0], y1, y2))
        elif start[1] == end[1]:
            x1, x2 = sorted((start[0], end[0]))
            horizontal_segments.append((start[1], x1, x2))

    for index, first in enumerate(vertical_segments):
        x1, y1_min, y1_max = first
        for x2, y2_min, y2_max in vertical_segments[index + 1:]:
            if _range_overlap(y1_min, y1_max, y2_min, y2_max) > PATH_WIDTH:
                if abs(x1 - x2) < MIN_PARALLEL_LANE_SPACING:
                    return False

    for index, first in enumerate(horizontal_segments):
        y1, x1_min, x1_max = first
        for y2, x2_min, x2_max in horizontal_segments[index + 1:]:
            if _range_overlap(x1_min, x1_max, x2_min, x2_max) > PATH_WIDTH:
                if abs(y1 - y2) < MIN_PARALLEL_LANE_SPACING:
                    return False

    return True


def count_buildable_sites(path):
    count = 0
    half = BUILD_TILE_SIZE // 2
    blocked_distance = PATH_WIDTH / 2 + half

    for x in range(half, MAP_WIDTH, BUILD_TILE_SIZE):
        for y in range(BUILD_GRID_TOP + half, HEIGHT, BUILD_TILE_SIZE):
            if _point_has_path_clearance((x, y), path, blocked_distance):
                count += 1

    return count


def _point_has_path_clearance(point, path, blocked_distance):
    return all(
        _distance_point_to_segment(point, start, end) >= blocked_distance
        for start, end in zip(path, path[1:])
    )


def _distance_point_to_segment(point, start, end):
    px, py = point
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)

    t = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)


def _range_overlap(a_min, a_max, b_min, b_max):
    return max(0, min(a_max, b_max) - max(a_min, b_min))
