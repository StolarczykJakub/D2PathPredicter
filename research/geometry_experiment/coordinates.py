"""Bearings in the registered automap plane."""

import math

Point = tuple[int, int]
SECTORS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
ORIENTATIONS = (*SECTORS, "NS", "NE_SW", "EW", "NW_SE")


def sector(angle: float) -> str:
    return SECTORS[int((angle + 22.5) // 45) % len(SECTORS)]


def angular_error(direction: str, angle: float) -> float:
    centre = SECTORS.index(direction) * 45
    return abs((angle - centre + 180) % 360 - 180)


def bearing(origin: Point, target: Point, uncertainty: float = 0) -> float | None:
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    distance = math.hypot(dx, dy)
    if distance <= uncertainty:
        return None
    angle = math.degrees(math.atan2(dx, -dy)) % 360
    if uncertainty:
        deviation = math.degrees(math.asin(uncertainty / distance))
        if deviation >= 22.5 - angular_error(sector(angle), angle):
            return None
    return angle
