import os
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, Union, Sequence

import pygame

from surface import Surface


Asset = Union[Sequence[pygame.Surface], bytes]

img_formats = [
    "bmp", "jpeg", "jpg",
    "png", "svg", "webp"
]


class Assets:
    _abs_path: Path = None
    _meta_data: Dict[Path, dict] = {}
    _assets: Dict[Path, Asset] = {}


    @classmethod
    def _read_all_files(cls, prefix: Path) -> None:
        # this will only map all files into a list and load json files
        for sub_path in os.listdir(prefix):
            curr_path = Path(prefix, sub_path)
            relative_path = curr_path.relative_to(cls._abs_path)

            # if the path leads to a file read it's byte contents
            if curr_path.is_file():
                with open(curr_path, "rb") as file:

                    # the metadata must be preloaded before handling
                    # images due the order of which files are handled
                    if curr_path.name == "meta.json":
                        cls._meta_data[relative_path] = json.load(file)
                    else:
                        cls._assets[relative_path] = file.read()
            
            # if it's a directory loop through it
            elif curr_path.is_dir():
                cls._read_all_files(curr_path)
            
            else:
                raise OSError(f"{relative_path} is not a valid path")


    @classmethod
    def _load_surface(cls, data: bytes, meta: dict = None) -> Sequence[Surface]: 
        surface = pygame.image.load(BytesIO(data)).convert_alpha()

        frame_count = meta.get("frames", 1)

        if frame_count == 1:
            return [surface]
        
        frames: Sequence[Surface] = []

        w, h = meta.get("frame_res", surface.get_size())
        surface_width = surface.get_size()[0]
        
        for i in range(1, frame_count):
            new_surface = surface.copy()
            x = (w*i) % surface_width
            y = int((w*i) / surface_width)
            
            new_surface = pygame.Surface((w, h))
            new_surface.blit(surface, (0, 0), (x, y, x+w, y+h))
            
            new_surface.convert_alpha()
            frames.append(new_surface)

        return frames
    

    @classmethod
    def load_all(cls, prefix_path: Path) -> None:
        if not prefix_path.is_dir():
            raise ValueError("unable to locate directory: %s" % prefix_path)

        # set abs_path for root of folder
        cls._abs_path = prefix_path
        
        # read all files inside prefix_path
        cls._read_all_files(cls._abs_path)

        # convert all files with image format extensions to pygame surfaces
        for path, data in cls._assets.items():
            if path.suffix[1:] in img_formats:
                logging.debug(f"loading image {path}")
                meta = cls._meta_data.get(Path(path.parent, "meta.json"), {})
                cls._assets[path] = cls._load_surface(data, meta)


    @classmethod
    def get(cls, path: Path) -> Asset:
        if isinstance(path, str):
            path = Path(path)

        if path not in cls._assets:
            raise ValueError("no asset with path: %s" % path)
        return cls._assets.get(path)