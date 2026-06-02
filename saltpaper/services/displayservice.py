import pygame
import sys
from statistics import mean
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saltpaper import InputService
    from saltpaper import Layer

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DisplayService():

    def __init__(
            self,
            dimensions,
            inputservice,
            target_frame_rate:int=120,
            caption="saltpaper engine display",
            vsync=True, # for testing
            iconpath=None,
            fullscreen=False
    ):
        self.dimensions = dimensions
        self._caption = caption
        self.inputservice:'InputService' = inputservice
        self.target_frame_rate = target_frame_rate
        self.fullscreen=fullscreen

        self.layers = []

        self.refresh_sorting()

        pygame.init()

        self.funcs = []
        if iconpath is not None:
            iconsurf = pygame.image.load(iconpath)
            pygame.display.set_icon(iconsurf)
        flags = pygame.SCALED | pygame.FULLSCREEN if fullscreen else pygame.SCALED
        self.display = pygame.display.set_mode(dimensions, flags, vsync=vsync)

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.delta = 1
        self.deltas = []

        self.running = True
        self.dirty = True

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value
        pygame.display.set_caption(value)

    def mount(self, func=None):
        if not func: return
        self.funcs.append(func)

    def refresh_sorting(self):
        self.layers_by_tick = sorted(self.layers, key=lambda l: l.tick_priority)
        self.layers_by_render = sorted(self.layers, key=lambda l: l.render_priority)

    def add_layer(self, layer):
        self.layers.append(layer)
        self.refresh_sorting()

    def add_many_layers(self, layers:list):
        self.layers.extend(layers)
        self.refresh_sorting()

    def remove_layer(self, layer):
        for i, item in enumerate(self.layers):
            if item is layer:
                self.layers.pop(i)
                self.refresh_sorting()
                return True
        return False

    def get_layers(self):
        return self.layers

    def tick(self):
        if len(self.layers) == 0:
            raise ValueError("the display service has no layers to display. make sure they are added with displayservice.add_layer(layer)")

        self.events = pygame.event.get()
        self.inputservice.tick(self.events)
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return self.delta

        for layer in self.layers_by_tick:
            if layer.ticking:
                layer.tick(self.delta)

        for layer in self.layers_by_render:
            if not layer.visible:
                continue
            surf = layer.render()
            ox, oy = layer.offset
            d_width, d_height = self.display.get_size()
            
            src_x = max(0, -ox)
            src_y = max(0, -oy)
            src_w = min(d_width, surf.get_width() - src_x)
            src_h = min(d_height, surf.get_height() - src_y)
            
            if src_w <= 0 or src_h <= 0:  # layer is completely off screen
                continue
            
            dest_x = max(0, ox)
            dest_y = max(0, oy)
            
            self.display.blit(surf, (dest_x, dest_y), pygame.Rect(src_x, src_y, src_w, src_h))
            
        for func in self.funcs:
            func(self, self.delta)

        pygame.display.flip() 
        delta_entry = self.clock.tick(self.target_frame_rate) / 1000
        self.deltas.append(delta_entry)
        if len(self.deltas) > 10:
            self.deltas.pop(0)
        self.delta = mean(self.deltas)

        return self.delta