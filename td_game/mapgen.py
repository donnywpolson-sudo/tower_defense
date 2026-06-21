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


MIN_PATH_LENGTH = 1250
MAX_PATH_LENGTH = 2400
MIN_VERTICAL_STEP = 105
MAX_VERTICAL_STEP = 260
MIN_TURNS = 4
MAX_TURNS = 7
MIN_PARALLEL_LANE_SPACING = PATH_WIDTH + BUILD_TILE_SIZE + 18
MIN_BUILDABLE_SITES = 68
THEMES = ("forest", "swamp", "snow", "lava")
PATH_STYLES = ("Switchback", "Turnaround")


def path_length(path):
    total = 0
    for start, end in zip(path, path[1:]):
        total += math.hypot(end[0] - start[0], end[1] - start[1])
    return total


def generate_random_map(seed=None):
    if seed is None:
        seed = random.SystemRandom().randint(1000, 999999)

    rng = random.Random(seed)
    preferred_style = rng.choice(PATH_STYLES)
    style_order = [preferred_style] + [style for style in PATH_STYLES if style != preferred_style]
    for style in style_order:
        for _ in range(140):
            candidate = _generate_candidate_paths(rng, style)
            if candidate is None:
                continue

            paths, style_name = candidate
            if (
                paths_are_orthogonal(paths)
                and paths_have_overlap(paths)
                and _path_lengths_in_range(paths)
                and _paths_in_bounds(paths)
                and paths_have_open_build_corridors(paths)
                and count_buildable_sites_for_paths(paths) >= MIN_BUILDABLE_SITES
            ):
                return {
                    "name": f"Random {style_name}",
                    "theme": rng.choice(THEMES),
                    "seed": seed,
                    "paths": paths,
                }

    return _fallback_overlap_map(seed, rng)


def _generate_candidate_paths(rng, style):
    if style == "Turnaround":
        path = _generate_turnaround_path(rng)
        return ([path], style) if path is not None else None

    path = _generate_switchback_path(rng)
    return ([path], style) if path is not None else None


def _generate_switchback_path(rng):
    return _generate_overlap_loop_path(rng, first_lane="bottom")


def _generate_turnaround_path(rng):
    return _generate_overlap_loop_path(rng, first_lane="top")


def _generate_overlap_loop_path(rng, first_lane):
    min_y = _snap_y(BUILD_GRID_TOP + PATH_WIDTH + 30)
    max_y = _snap_y(HEIGHT - PATH_WIDTH - 20)
    min_gap = _snap_y(MIN_PARALLEL_LANE_SPACING)
    loop_height = rng.randrange(min_gap * 2, max_y - min_y + 1, BUILD_GRID_STEP)
    top_y = rng.randrange(min_y, max_y - loop_height + 1, BUILD_GRID_STEP)
    bottom_y = top_y + loop_height

    middle_candidates = [
        y
        for y in range(top_y + min_gap, bottom_y - min_gap + 1, BUILD_GRID_STEP)
        if top_y < y < bottom_y
    ]
    if len(middle_candidates) < 2:
        return None

    start_y = rng.choice(middle_candidates)
    inner_y = rng.choice(middle_candidates)
    exit_candidates = [y for y in middle_candidates if abs(y - inner_y) >= BUILD_GRID_STEP * 2]
    if not exit_candidates:
        return None
    exit_y = rng.choice(exit_candidates)

    left_x = _snap_x(rng.randint(120, 205))
    inner_left_x = _snap_x(rng.randint(285, 380))
    inner_right_x = _snap_x(rng.randint(525, 630))
    right_x = _snap_x(rng.randint(730, 810))
    if not (
        inner_left_x - left_x >= MIN_PARALLEL_LANE_SPACING
        and inner_right_x - inner_left_x >= MIN_PARALLEL_LANE_SPACING
        and right_x - inner_right_x >= MIN_PARALLEL_LANE_SPACING
    ):
        return None

    if first_lane == "bottom":
        outer_lane = bottom_y
        return_lane = top_y
    else:
        outer_lane = top_y
        return_lane = bottom_y

    return _dedupe_path(
        [
            (0, start_y),
            (left_x, start_y),
            (left_x, outer_lane),
            (right_x, outer_lane),
            (right_x, return_lane),
            (inner_left_x, return_lane),
            (inner_left_x, inner_y),
            (inner_right_x, inner_y),
            (inner_right_x, exit_y),
            (MAP_WIDTH, exit_y),
        ]
    )


def _fallback_overlap_map(seed, rng):
    return {
        "name": "Random Fallback Overlap",
        "theme": rng.choice(THEMES),
        "seed": seed,
        "paths": [
            [
                (0, 324),
                (135, 324),
                (135, 162),
                (756, 162),
                (756, 486),
                (378, 486),
                (378, 351),
                (567, 351),
                (567, 297),
                (MAP_WIDTH, 297),
            ]
        ],
    }


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


def _dedupe_path(path):
    result = []
    for point in path:
        if not result or result[-1] != point:
            result.append(point)
    return result


def _snap_x(value):
    return int(round(value / BUILD_GRID_STEP) * BUILD_GRID_STEP)


def _snap_y(value):
    return int(round(value / BUILD_GRID_STEP) * BUILD_GRID_STEP)


def _normalize_paths(paths_or_path):
    if not paths_or_path:
        return []
    first = paths_or_path[0]
    if isinstance(first, tuple):
        return [paths_or_path]
    return paths_or_path


def _path_lengths_in_range(paths):
    return all(MIN_PATH_LENGTH <= path_length(path) <= MAX_PATH_LENGTH for path in paths)


def paths_are_orthogonal(paths):
    return all(
        start[0] == end[0] or start[1] == end[1]
        for path in paths
        for start, end in zip(path, path[1:])
    )


def paths_have_overlap(paths):
    segments = []
    for path_index, path in enumerate(paths):
        for segment_index, (start, end) in enumerate(zip(path, path[1:])):
            segments.append((path_index, segment_index, start, end))

    for index, first in enumerate(segments):
        for second in segments[index + 1:]:
            if _segments_cross_interior(first[2], first[3], second[2], second[3]):
                return True
    return False


def path_has_overlap(path):
    return paths_have_overlap(_normalize_paths(path))


def _paths_in_bounds(paths):
    return all(_path_in_bounds(path) for path in paths)


def _path_in_bounds(path):
    min_y = BUILD_GRID_TOP + PATH_WIDTH // 2
    max_y = HEIGHT - PATH_WIDTH // 2
    return all(0 <= x <= MAP_WIDTH and min_y <= y <= max_y for x, y in path)


def paths_have_open_build_corridors(paths):
    """Reject tight snake lanes that leave no tower-sized space between roads."""

    vertical_segments = []
    horizontal_segments = []
    for path in paths:
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


def path_has_open_build_corridors(path):
    return paths_have_open_build_corridors(_normalize_paths(path))


def count_buildable_sites_for_paths(paths):
    count = 0
    half = BUILD_TILE_SIZE // 2
    blocked_distance = PATH_WIDTH / 2 + half

    for x in range(half, MAP_WIDTH, BUILD_TILE_SIZE):
        for y in range(BUILD_GRID_TOP + half, HEIGHT, BUILD_TILE_SIZE):
            if all(_point_has_path_clearance((x, y), path, blocked_distance) for path in paths):
                count += 1

    return count


def count_buildable_sites(path):
    return count_buildable_sites_for_paths(_normalize_paths(path))


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


def _segments_cross_interior(first_start, first_end, second_start, second_end):
    if first_start[1] == first_end[1] and second_start[0] == second_end[0]:
        return _horizontal_vertical_crosses(first_start, first_end, second_start, second_end)
    if first_start[0] == first_end[0] and second_start[1] == second_end[1]:
        return _horizontal_vertical_crosses(second_start, second_end, first_start, first_end)
    return False


def _horizontal_vertical_crosses(horizontal_start, horizontal_end, vertical_start, vertical_end):
    y = horizontal_start[1]
    x = vertical_start[0]
    h_min, h_max = sorted((horizontal_start[0], horizontal_end[0]))
    v_min, v_max = sorted((vertical_start[1], vertical_end[1]))
    return h_min < x < h_max and v_min < y < v_max


def _range_overlap(a_min, a_max, b_min, b_max):
    return max(0, min(a_max, b_max) - max(a_min, b_min))
