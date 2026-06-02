import pygame
import math

from saltpaper.services.layer import Layer
from saltpaper.services.assetservice import AssetService
from saltpaper.worldsystem.components.sprite import Sprite
from saltpaper.worldsystem.components.position import Position

class RenderService():
    def __init__(self, world, assetservice: AssetService):
        self.world = world
        self.assetservice = assetservice
        self.render_queue:dict[Layer, list] = {}
        self.zoom = 1
        
    def _queue(self, layer:Layer, pos:tuple[int,int], surface:pygame.Surface):
        item = (surface, pos)
        if not self.render_queue.get(layer, None):
            self.render_queue[layer] = []
        self.render_queue[layer].append(item)

    def _process_queue(self):
        for layer, items in self.render_queue.items():
            layer.surface.blits(items)
        self.render_queue.clear()

    def render(self, layer:Layer, pos:tuple[int,int], asset_id:str):
        surf = self.assetservice.get_asset(asset_id)
        self._queue(layer, pos, surf)

    def _render_renderables(self, renderables):
        for renderable in renderables:
            if not renderable.visible: continue
            if not renderable.has(Position): continue
            
            surf = self.assetservice.get_asset(renderable.asset_id)
            if self.zoom != 1:
                new_size = (math.ceil(surf.get_width() * self.zoom), math.ceil(surf.get_height() * self.zoom))
                surf = pygame.transform.scale(surf, new_size)
            
            pos = (int(renderable.position[0]), int(renderable.position[1]))

            layer_rect = renderable.layer.surface.get_rect()
            sw, sh = surf.get_size()
            if pos[0] + sw < 0 or pos[1] + sh < 0 or pos[0] > layer_rect.width or pos[1] > layer_rect.height:
                continue

            self._queue(renderable.layer, pos, surf)

    def tick(self):
        self._render_renderables(self.world.collect_component_type(Sprite))
        self._process_queue()
