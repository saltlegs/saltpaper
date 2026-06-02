import pygame
import os
from pathlib import Path

cwd = Path.cwd()
filetypes = {
    "image":    [".png", ".jpg", ".bmp", ".gif"],
    "anim":     [".png", ".jpg", ".bmp", ".gif"],
    "music":    [".wav", ".ogg", ".mp3"],
    "sound":    [".wav", ".ogg", ".mp3"],
    "tilemap":  [".png", ".jpg", ".bmp", ".gif"],
    "font":     [".ttf", ".otf"],
}

class FontMaker:
    def __init__(self, path:Path):
        self.path = path
        self._cache = {}

    def get_size(self, size) -> pygame.Font:
        cached = self._cache.get(size)
        if cached: return cached

        this_font = pygame.Font(self.path, size)
        self._cache[size] = this_font
        return this_font

class Tilemap():
    def __init__(self, surface, tile_size=(16, 16)):
        self.surface = surface
        self.tile_size = tile_size
        self._cache = {}
        self._multitile_cache = {}

    def get_tile(self, id):
        if id in self._cache:
            return self._cache[id]

        width, height = self.tile_size
        columns = self.surface.get_width() // width
        if columns <= 0:
            raise ValueError("invalid tile size for this tilemap surface")

        row = id // columns
        col = id % columns
        x = col * width
        y = row * height

        if x + width > self.surface.get_width() or y + height > self.surface.get_height():
            raise IndexError(f"tile index out of range: {id}")

        rect = pygame.Rect(x, y, width, height)
        tile = self.surface.subsurface(rect).copy()
        self._cache[id] = tile
        return tile

    def get_multi_tile(self, id, width, height):
        if (id, width, height) in self._multitile_cache:
            return self._multitile_cache[(id, width, height)]
        
        twidth, theight = self.tile_size
        columns = self.surface.get_width() // twidth
        if columns <= 0:
            raise ValueError("invalid tile size for this tilemap surface")

        row = id // columns
        col = id % columns
        x = col * twidth
        y = row * theight

        multitile_width = twidth * width
        multitile_height = theight * height

        rect = pygame.Rect(x, y, multitile_width, multitile_height)
        multitile = self.surface.subsurface(rect).copy()
        self._multitile_cache[(id, width, height)] = multitile
        return multitile


class AssetService():
    def __init__(self, assets_folder_path):
        self.cache = {}
        self.roots = []

        self.set_assets_folder(assets_folder_path)

    def set_assets_folder(self, path):
        path = Path(path)
        self.roots.append(path)

    def get_kind(self, asset_id):
        kind, name = asset_id.split("_", 1)
        return kind

    def get_asset(self, id, frame=0):
        asset = self.cache.get(id)

        kind, name = id.split("_", 1)


        if asset is not None:
            return asset if kind != "anim" else asset[frame]
        
        extensions = filetypes.get(kind)

        if extensions is None:
            raise ValueError(f"unknown asset type: {kind}")

        searched = []
        folder = kind + "s"
        for root in self.roots:
            for ext in extensions:
                if kind == "anim":
                    i = 0
                    self.cache[id] = []
                    while i >= 0:
                        path = root / folder / name / f"{name}_{i}{ext}"
                        searched.append(str(path))
                        if path.exists():
                            asset = self._load_asset(kind, path)
                            self.cache[id].append(asset)
                        else:
                            i = -1
                    if len(self.cache[id]) <= 1: raise ValueError("animated asset must have more than one frame")
                    return self.cache[id][frame]
                else:
                    path = root / folder / f"{name}{ext}"
                    searched.append(str(path))
                    if path.exists():
                        asset = self._load_asset(kind, path)
                        self.cache[id] = asset
                        return asset

        if id == "image_missing":
            raise FileNotFoundError(f"No /image/missing.png is set")

        print(
            f"asset not found: '{id}' (type='{kind}', name='{name}'). "
            f"tried locations:" + '\n'.join(searched) + "\n",
            f"ensure the asset exists in 'game/assets' or 'engine/assets' and that the id is formatted as '<type>_<name>'."
        )

        try:
            return self.get_asset("image_missing")
        except FileNotFoundError:
            raise FileNotFoundError(f"No /image/missing.png is set")

    def _load_asset(self, kind, path: Path):
        if kind == "image":
            return pygame.image.load(path).convert_alpha()

        if kind == "tilemap":
            surface = pygame.image.load(path).convert_alpha()
            return Tilemap(surface)

        if kind == "music":
            pygame.mixer.music.load(path)
            return path  # music is streamed so just return path

        if kind == "sound":
            return pygame.mixer.Sound(path)

        if kind == "font":
            return FontMaker(path)

        # tilesheet etc later
        return path
    
    def submit_surface(self, id, surface):
        self.cache[id] = surface

