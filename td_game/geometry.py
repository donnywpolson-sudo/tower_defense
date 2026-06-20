import math


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distance_to_segment(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b

    dx = bx - ax
    dy = by - ay

    if dx == 0 and dy == 0:
        return dist(p, a)

    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))

    closest = (ax + t * dx, ay + t * dy)
    return dist(p, closest)


def distance_point_to_rect(point, rect):
    px, py = point
    closest_x = max(rect.left, min(px, rect.right))
    closest_y = max(rect.top, min(py, rect.bottom))
    return dist((px, py), (closest_x, closest_y))


def segment_intersects_rect(a, b, rect):
    if rect.collidepoint(a) or rect.collidepoint(b):
        return True
    return rect.clipline(a, b)


def distance_segment_to_rect(a, b, rect):
    if segment_intersects_rect(a, b, rect):
        return 0

    distances = [
        distance_point_to_rect(a, rect),
        distance_point_to_rect(b, rect),
    ]

    for corner in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
        distances.append(distance_to_segment(corner, a, b))

    return min(distances)

