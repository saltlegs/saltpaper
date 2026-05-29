import math

class Position():
    def __init__(
            self,
            layer:int=0,
            position:tuple[int,int]=(0,0),
            width:int=0,
            height:int=0,
    ):
        self.layer = layer
        self.position = position
        self.width = width
        self.height = height

    @property
    def x(self):
        return self.position[0]
    
    @property
    def y(self):
        return self.position[1]

    def set_layer(self, layer):
        self.layer = layer

    def move(self, dx, dy):
        x, y = self.position
        self.position = (x + dx, y + dy)

    def move_toward(self, tx, ty, distance):
        x, y = self.position
        dx = tx - x
        dy = ty - y
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
        nx = dx / length
        ny = dy / length
        self.position = (x + nx * distance, y + ny * distance)

    def move_away(self, tx, ty, distance):
        self.move_toward(tx, ty, -distance)

    def is_point_inside(self, point):
        x, y  = point