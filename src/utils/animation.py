import pygame
import json
import os

class SpriteSheet:
    """Load and cut the sprite sheet"""
    def __init__(self, image_path):
        self.sheet = pygame.image.load(image_path).convert_alpha()
    
    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image

class Animation:
    """Manage an animation (multiple frames, playback speed, loop)"""
    def __init__(self, frames, duration_per_frame=0.1, loop=False):
        self.frames = frames      # list of pygame.Surface
        self.duration_per_frame = duration_per_frame  # Display time per frame (seconds)
        self.loop = loop
        self.current_frame = 0
        self.timer = 0
        self.playing = True
        self.finished = False
    
    def update(self, dt):
        if not self.playing or self.finished:
            return
        
        self.timer += dt
        if self.timer >= self.duration_per_frame:
            self.timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
                    self.finished = True
    
    def get_frame(self):
        if self.frames and self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def reset(self):
        self.current_frame = 0
        self.timer = 0
        self.playing = True
        self.finished = False

def load_libresprite_animation(json_path, png_path, scale=1):
    """Load animation from JSON + PNG exported by Aseprite / libresprite"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Determine the PNG path (if the path in the JSON is wrong, use the png_path passed in)
    if os.path.exists(png_path):
        image_path = png_path
    else:
        #Try to extract path from JSON
        image_path = data.get("meta", {}).get("image", png_path)
        if not os.path.exists(image_path):
            image_path = png_path
    
    sprite_sheet = SpriteSheet(image_path)
    frames = []

    # Support both list format and dictionary format
    frames_data = data.get("frames", {})
    
    if isinstance(frames_data, list):
        # Format A: list of frames
        frame_items = [(i, frame) for i, frame in enumerate(frames_data)]
    else:
        # Format B: dictionary with frame names as keys
        frame_items = sorted(frames_data.items(), key=lambda x: x[0])  # Sort by name
    
    for name, frame_data in frame_items:
        frame_rect = frame_data.get("frame", {})
        x = frame_rect.get("x", 0)
        y = frame_rect.get("y", 0)
        w = frame_rect.get("w", 32)
        h = frame_rect.get("h", 48)
        
        duration_ms = frame_data.get("duration", 100)
        duration_sec = duration_ms / 1000.0
        
        image = sprite_sheet.get_image(x, y, w, h)
        if scale != 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = pygame.transform.scale(image, (new_w, new_h))
        frames.append(image)
    
    if frames:
        return Animation(frames, duration_sec, loop=False)
    
    return None