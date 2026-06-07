from pathlib import Path

import pygame


class MusicManager:
    def __init__(self, audio_dir=None, volume=0.55):
        self.audio_dir = Path(audio_dir) if audio_dir is not None else Path(__file__).resolve().parent
        self.volume = volume
        self.current_track = None
        self.enabled = True
        self.tracks = {
            "menu": self.audio_dir / "BorrowLight OST.mp3",
            "gameplay": self.audio_dir / "Gameplay BGM.mp3",
            "boss": self._first_existing("BOSS OST.mp3", "BOSS OST .mp3"),
        }
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error as error:
            self.enabled = False
            print(f"Music disabled: {error}")

    def _first_existing(self, *names):
        for name in names:
            path = self.audio_dir / name
            if path.exists():
                return path
        return self.audio_dir / names[0]

    def play(self, track_name):
        if not self.enabled:
            return

        if self.current_track == track_name:
            return

        path = self.tracks.get(track_name)
        if path is None or not path.exists():
            print(f"Missing music track: {path}")
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
            self.current_track = track_name
        except pygame.error as error:
            print(f"Could not play music track {path}: {error}")

    def update_for_game(self, game_state, map_id, boss_map_id):
        if game_state in ("menu", "origin_story"):
            self.play("menu")
        elif map_id == boss_map_id:
            self.play("boss")
        else:
            self.play("gameplay")
