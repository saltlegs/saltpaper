import math

class VectorTools:
    """I HATE MATHEMATICS"""
    def __init__(self):
        pass

    @staticmethod
    def distance_between(a:tuple[float, float], b:tuple[float, float]) -> float:
        ax, ay = a
        bx, by = b

        xdiff = bx - ax
        ydiff = by - ay

        return math.sqrt((xdiff**2 + ydiff**2))
        # i was worried that this would crash if given a negative number
        # but both components are exponentiated so it can never be negative

    @staticmethod
    def lerp(a: tuple[float, float], b: tuple[float, float], progress: float = 0.5) -> tuple[float, float]:
        ax, ay = a
        bx, by = b

        return (
            ax + (bx - ax) * progress,
            ay + (by - ay) * progress
        )
    
    @staticmethod
    def smoothstep(a: tuple[float, float], b: tuple[float, float], progress: float = 0.5) -> tuple[float, float]:
        ax, ay = a
        bx, by = b

        t = progress ** 2 * (3 - 2 * progress)

        return (
            ax + (bx - ax) * t,
            ay + (by - ay) * t
        )
    
    @staticmethod
    def is_point_inside(point:tuple[int,int], x:int, y:int, width:int, height:int) -> bool:
        px, py = point
        return (x <= px < x + width) and (y <= py < y + height)
        