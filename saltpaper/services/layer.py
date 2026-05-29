import pygame
import numpy as np

class Layer:
    def __init__(
            self,
            dimensions:tuple[int,int],
            render_priority:int=0,
            tick_priority:int=0,
            opacity_percent:int=100,
            surface:pygame.Surface=None,
            offset:tuple[int,int]=(0,0)
    ):
        self.dimensions = dimensions
        self.surface = surface if surface else pygame.Surface(dimensions, pygame.HWSURFACE | pygame.SRCALPHA)
        self.visible = True
        self.ticking = True
        self.opacity_percent = opacity_percent
        self.offset:tuple[int,int] = offset
        
        self.render_priority = render_priority
        self.tick_priority = tick_priority
        
        self.funcs = []

        # loopscroll()
        self._loopscroll_accum_x = 0.0
        self._loopscroll_accum_y = 0.0

    def mount(self, func=None):
        """mount a function to be called when this layer ticks. gives the layer and delta as arguments (i.e. `main(layer, delta)`)"""
        if not func: return
        self.funcs.append(func)

    def tick(self, delta):
        for func in self.funcs:
            func(self, delta)
    
    def render(self):
        if self.opacity_percent >= 100:
            return self.surface
        
        surf = self.surface.copy()
        surf.set_alpha(int(self.opacity_percent * 2.55))
        return surf
    
    def relative_coords(self, coords):
        """takes a screen coordinate and converts it to local coordinates on the layer"""
        x, y = coords
        newcoords = (x - self.offset[0], y - self.offset[1])
        return newcoords
    

    def loopscroll(self, dx, dy, dt=1.0):
        self._loopscroll_accum_x += dx * dt
        self._loopscroll_accum_y += dy * dt

        scroll_x = int(self._loopscroll_accum_x)
        scroll_y = int(self._loopscroll_accum_y)

        self._loopscroll_accum_x -= scroll_x
        self._loopscroll_accum_y -= scroll_y

        if scroll_x == 0 and scroll_y == 0:
            return

        surf = self.surface
        scroll_area_x = (abs(scroll_x), surf.get_height())
        scroll_area_y = (surf.get_width(), abs(scroll_y))
        if scroll_x != 0:
            tempx = pygame.Surface(scroll_area_x, pygame.SRCALPHA)
        if scroll_y != 0:
            tempy = pygame.Surface(scroll_area_y, pygame.SRCALPHA)

        top = 0
        left = 0
        right = surf.get_width()
        bottom = surf.get_height()

        if scroll_x > 0: # image is moving right, copy rightmost chunk to left
            tempx.blit(surf, (0,0), ((right-scroll_x, top), (scroll_x, bottom)))
            surf.scroll(scroll_x, 0)
            surf.blit(tempx, (left,top))
        elif scroll_x < 0: # image is moving left, copy leftmost chunk to right
            tempx.blit(surf, (0,0), ((0, top), (-scroll_x, bottom)))
            surf.scroll(scroll_x, 0)
            surf.blit(tempx, (right+scroll_x,top))
        
        if scroll_y > 0: # image is moving down, copy bottom chunk to top
            tempy.blit(surf, (0,0), ((left, bottom-scroll_y), (right, scroll_y)))
            surf.scroll(0, scroll_y)
            surf.blit(tempy, (left, top))
        elif scroll_y < 0: # image is moving up, copy top chunk to bottom
            tempy.blit(surf, (0,0), ((left, 0), (right, -scroll_y)))
            surf.scroll(0, scroll_y)
            surf.blit(tempy, (left, bottom+scroll_y))

        self.surface = surf
