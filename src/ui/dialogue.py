from __future__ import annotations

import math
from pathlib import Path

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DialogueSystem:
    """Bottom-screen visual-novel dialogue UI.

    Portrait paths are optional and are only displayed as loaded surfaces.
    This class never edits, crops, scales, trims, exports, or rewrites artwork.
    """

    def __init__(self):
        self.speakers = {
            "CRYSTAL": {
                "name": "CRYSTAL",
                "color": (142, 231, 255),
                "portrait": None,
            },
            "KAEL": {
                "name": "KAEL",
                "color": (230, 238, 255),
                "portrait": str(PROJECT_ROOT / "assets" / "dialogue" / "kael_portrait.png"),
            },
            "LUNAR WARDEN": {
                "name": "LUNAR WARDEN",
                "color": (255, 112, 112),
                "portrait": None,
            },
        }
        self.sequences = self._build_sequences()
        self._portrait_cache = {}
        self._particles = [
            {
                "x": (i * 97) % SCREEN_WIDTH,
                "y": (i * 43) % 180,
                "speed": 9 + (i % 5) * 4,
                "phase": i * 0.7,
            }
            for i in range(28)
        ]
        self.time = 0.0
        self.reset_for_new_run()

    def reset_for_new_run(self):
        self.active = False
        self.sequence_id = None
        self.lines = []
        self.index = 0
        self.visible_chars = 0.0
        self.box_fade = 0.0
        self.line_fade = 0.0
        self.played = set()
        self.spawn_center_x = None
        self.largest_enemy_count_seen = 0

    def _build_sequences(self):
        return {
            "opening": [
                ("CRYSTAL", "Wake up."),
                ("CRYSTAL", "Can you hear me?"),
                ("KAEL", "..."),
                ("KAEL", "Where am I?"),
                ("CRYSTAL", "A question for another time."),
                ("CRYSTAL", "Stand."),
                ("CRYSTAL", "The Lunar Core is calling."),
                ("KAEL", "Lunar Core?"),
                ("CRYSTAL", "Move forward."),
                ("CRYSTAL", "The answers you seek lie ahead."),
            ],
            "first_movement": [
                ("CRYSTAL", "Good."),
                ("CRYSTAL", "Your body remembers what your mind has forgotten."),
            ],
            "first_enemy_encounter": [
                ("KAEL", "Who are those people?"),
                ("CRYSTAL", "Humans."),
                ("CRYSTAL", "They were attacking you."),
                ("KAEL", "..."),
                ("CRYSTAL", "Do not hesitate."),
                ("CRYSTAL", "Destroy them."),
            ],
            "first_enemy_defeat": [
                ("CRYSTAL", "You see?"),
                ("CRYSTAL", "They stand between you and the Core."),
            ],
            "ruined_laboratory": [
                ("KAEL", "This place..."),
                ("KAEL", "Why does it feel familiar?"),
                ("CRYSTAL", "Fragments of memory."),
                ("CRYSTAL", "They are irrelevant."),
                ("KAEL", "I've been here before."),
                ("CRYSTAL", "Keep moving."),
                ("CRYSTAL", "The Core awaits."),
            ],
            "before_boss_room": [
                ("KAEL", "This energy..."),
                ("KAEL", "I've felt it before."),
                ("CRYSTAL", "You are close."),
                ("CRYSTAL", "Beyond this door lies the Lunar Core."),
                ("KAEL", "Then why do I feel afraid?"),
                ("CRYSTAL", "..."),
                ("CRYSTAL", "Enter."),
            ],
            "boss_intro": [
                ("LUNAR WARDEN", "IDENTIFICATION CONFIRMED."),
                ("LUNAR WARDEN", "PROJECT PALE CROWN DETECTED."),
                ("KAEL", "Project... Pale Crown?"),
                ("LUNAR WARDEN", "PRIMARY SUBJECT: KAEL."),
                ("LUNAR WARDEN", "CONTAINMENT FAILURE ORIGIN CONFIRMED."),
                ("KAEL", "What are you talking about?"),
                ("CRYSTAL", "Do not listen."),
                ("CRYSTAL", "Destroy it."),
                ("LUNAR WARDEN", "WARNING."),
                ("LUNAR WARDEN", "SUBJECT MEMORY LOSS DETECTED."),
                ("LUNAR WARDEN", "YOU CAUSED THE FALL OF VELARIS."),
                ("KAEL", "..."),
                ("CRYSTAL", "Lies."),
                ("CRYSTAL", "Destroy the guardian."),
                ("CRYSTAL", "Claim the Core."),
            ],
        }

    def set_portrait(self, speaker, image_path):
        """Register an optional portrait path.

        The image will be displayed at its original loaded size. It is not
        resized, cropped, converted, saved, or modified.
        """
        self.speakers.setdefault(
            speaker,
            {"name": speaker, "color": (230, 238, 255), "portrait": None},
        )
        self.speakers[speaker]["portrait"] = str(image_path) if image_path else None

    def start(self, sequence_id):
        if self.active or sequence_id in self.played:
            return False
        lines = self.sequences.get(sequence_id)
        if not lines:
            return False

        self.sequence_id = sequence_id
        self.lines = list(lines)
        self.index = 0
        self.visible_chars = 0.0
        self.box_fade = 0.0
        self.line_fade = 0.0
        self.active = True
        self.played.add(sequence_id)
        return True

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return False

        if event.key not in (pygame.K_SPACE, pygame.K_RETURN):
            return False

        text = self._current_text()
        if self.visible_chars < len(text):
            self.visible_chars = len(text)
        else:
            self.index += 1
            if self.index >= len(self.lines):
                self.active = False
                return True
            self.visible_chars = 0.0
            self.line_fade = 0.0
        return True

    def update(self, dt):
        self.time += dt

        if not self.active:
            self.box_fade = max(0.0, self.box_fade - dt * 5.0)
            return

        self.box_fade = min(1.0, self.box_fade + dt * 4.5)
        self.line_fade = min(1.0, self.line_fade + dt * 5.0)
        self.visible_chars = min(len(self._current_text()), self.visible_chars + dt * 42.0)

        for particle in self._particles:
            particle["y"] -= particle["speed"] * dt
            particle["x"] += math.sin(self.time * 1.4 + particle["phase"]) * dt * 10
            if particle["y"] < -12:
                particle["y"] = SCREEN_HEIGHT + 12

    def check_triggers(self, player, current_map, enemies, archers, pale_core_boss):
        if self.active:
            return

        map_id = getattr(current_map, "map_id", 0)
        player_x = player.rect.centerx
        player_y = player.rect.centery

        if map_id == 0 and self.spawn_center_x is None:
            self.spawn_center_x = player_x

        alive_enemies = [
            enemy for enemy in list(enemies) + list(archers)
            if getattr(enemy, "alive", True)
        ]
        self.largest_enemy_count_seen = max(self.largest_enemy_count_seen, len(alive_enemies))

        if map_id == 0:
            if (
                "opening" in self.played
                and "first_movement" not in self.played
                and self.spawn_center_x is not None
                and abs(player_x - self.spawn_center_x) > 70
            ):
                self.start("first_movement")
                return

            enemy_nearby = any(
                abs(enemy.rect.centerx - player_x) < 360
                and abs(enemy.rect.centery - player_y) < 230
                for enemy in alive_enemies
            )
            if "first_enemy_encounter" not in self.played and enemy_nearby:
                self.start("first_enemy_encounter")
                return

            if (
                "first_enemy_encounter" in self.played
                and "first_enemy_defeat" not in self.played
                and self.largest_enemy_count_seen > 0
                and len(alive_enemies) < self.largest_enemy_count_seen
            ):
                self.start("first_enemy_defeat")
                return

            if "ruined_laboratory" not in self.played and player_x >= 7600:
                self.start("ruined_laboratory")
                return

            if "before_boss_room" not in self.played and player_x >= 10850:
                self.start("before_boss_room")
                return

        if getattr(pale_core_boss, "active", False) and "boss_intro" not in self.played:
            self.start("boss_intro")

    def draw(self, target):
        if self.box_fade <= 0:
            return

        alpha = int(255 * self.box_fade)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._draw_particles(overlay, alpha)

        box = pygame.Rect(54, SCREEN_HEIGHT - 190, SCREEN_WIDTH - 108, 162)
        for inflate, glow_alpha in ((18, 20), (10, 45), (4, 90)):
            glow_rect = box.inflate(inflate, inflate)
            pygame.draw.rect(
                overlay,
                (80, 221, 255, int(glow_alpha * self.box_fade)),
                glow_rect,
                2,
                border_radius=12,
            )
        pygame.draw.rect(overlay, (3, 7, 14, int(222 * self.box_fade)), box, border_radius=12)
        pygame.draw.rect(overlay, (95, 220, 255, int(215 * self.box_fade)), box, 2, border_radius=12)
        pygame.draw.line(
            overlay,
            (190, 244, 255, int(110 * self.box_fade)),
            (box.x + 18, box.y + 34),
            (box.right - 18, box.y + 34),
            1,
        )

        if self.active:
            speaker = self._current_speaker()
            other = self._other_speaker()
            left_slot_width = self._portrait_slot_width(speaker)
            right_slot_width = self._portrait_slot_width(other) if other is not None else 116
            left_slot = pygame.Rect(box.x + 18, box.y + 28, left_slot_width, 116)
            right_slot = pygame.Rect(box.right - 18 - right_slot_width, box.y + 28, right_slot_width, 116)
            self._draw_portrait_slot(overlay, left_slot, speaker, True)
            if other is not None:
                self._draw_portrait_slot(overlay, right_slot, other, False)

            text_width = max(220, right_slot.x - left_slot.right - 48)
            text_area = pygame.Rect(left_slot.right + 24, box.y + 48, text_width, 84)
            self._draw_name(overlay, speaker, text_area.x, box.y + 11, alpha)
            self._draw_dialogue_text(overlay, text_area, alpha)
            self._draw_prompt(overlay, box, alpha)

        target.blit(overlay, (0, 0))

    def _draw_particles(self, surface, alpha):
        for particle in self._particles:
            x = int(particle["x"] % SCREEN_WIDTH)
            y = int(particle["y"] % SCREEN_HEIGHT)
            pulse = 0.55 + 0.45 * math.sin(self.time * 2.0 + particle["phase"])
            particle_alpha = int(alpha * 0.18 * pulse)
            pygame.draw.circle(surface, (128, 226, 255, particle_alpha), (x, y), 2)

    def _current_speaker(self):
        return self.lines[self.index][0]

    def _current_text(self):
        return self.lines[self.index][1]

    def _speaker_info(self, speaker):
        return self.speakers.get(
            speaker,
            {"name": speaker, "color": (230, 238, 255), "portrait": None},
        )

    def _other_speaker(self):
        if not self.lines:
            return None
        speaker = self._current_speaker()
        sequence_speakers = []
        for candidate, _ in self.lines:
            if candidate not in sequence_speakers:
                sequence_speakers.append(candidate)

        preferred = ["KAEL", "CRYSTAL", "LUNAR WARDEN"]
        for candidate in preferred + sequence_speakers:
            if candidate != speaker and candidate in sequence_speakers:
                return candidate
        return None

    def _draw_name(self, surface, speaker, x, y, alpha):
        info = self._speaker_info(speaker)
        font = pygame.font.Font(None, 28)
        name = info["name"]
        color = info["color"]
        plate_width = max(150, font.size(name)[0] + 34)
        plate = pygame.Rect(x - 4, y - 6, plate_width, 30)
        pygame.draw.rect(surface, (7, 14, 26, int(225 * self.box_fade)), plate, border_radius=6)
        pygame.draw.rect(surface, (*color, int(180 * self.box_fade)), plate, 2, border_radius=6)
        label = font.render(name, True, color)
        label.set_alpha(alpha)
        surface.blit(label, (plate.x + 15, plate.y + 5))

    def _draw_dialogue_text(self, surface, text_area, alpha):
        font = pygame.font.Font(None, 30)
        visible = self._current_text()[: int(self.visible_chars)]
        text_alpha = int(alpha * self.line_fade)
        lines = self._wrap_text(font, visible, text_area.width)
        y = text_area.y
        for line in lines[:3]:
            shadow = font.render(line, True, (0, 0, 0))
            shadow.set_alpha(min(180, text_alpha))
            surface.blit(shadow, (text_area.x + 2, y + 2))

            rendered = font.render(line, True, (229, 238, 248))
            rendered.set_alpha(text_alpha)
            surface.blit(rendered, (text_area.x, y))
            y += 32

    def _draw_prompt(self, surface, box, alpha):
        font = pygame.font.Font(None, 22)
        pulse = 0.55 + 0.45 * math.sin(self.time * 4.0)
        prompt = "Press Space to Continue"
        rendered = font.render(prompt, True, (166, 224, 245))
        rendered.set_alpha(int(alpha * (0.45 + 0.4 * pulse)))
        surface.blit(rendered, (box.right - rendered.get_width() - 24, box.bottom - 29))

    def _wrap_text(self, font, text, max_width):
        if not text:
            return [""]
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = word if not current else f"{current} {word}"
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _portrait_slot_width(self, speaker):
        portrait = self._load_portrait(speaker) if speaker is not None else None
        if portrait is None:
            return 116
        return max(116, portrait.get_width())

    def _draw_portrait_slot(self, surface, rect, speaker, active):
        info = self._speaker_info(speaker)
        color = info["color"]
        fill_alpha = 126 if active else 70
        pygame.draw.rect(surface, (8, 15, 28, fill_alpha), rect, border_radius=8)
        pygame.draw.rect(surface, (*color, 165 if active else 85), rect, 2, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255, 24 if active else 12), rect.inflate(-10, -10), 1, border_radius=6)

        portrait = self._load_portrait(speaker)
        if portrait is not None:
            portrait_rect = portrait.get_rect(center=rect.center)
            surface.blit(portrait, portrait_rect)
            return

        self._draw_speaker_symbol(surface, rect, speaker, color, active)

    def _load_portrait(self, speaker):
        info = self._speaker_info(speaker)
        path = info.get("portrait")
        if not path:
            return None

        key = str(Path(path))
        if key in self._portrait_cache:
            return self._portrait_cache[key]

        try:
            image = pygame.image.load(key)
        except (FileNotFoundError, pygame.error):
            self._portrait_cache[key] = None
            return None

        self._portrait_cache[key] = image
        return image

    def _draw_speaker_symbol(self, surface, rect, speaker, color, active):
        center = rect.center
        glow_alpha = 90 if active else 38

        if speaker == "CRYSTAL":
            radius = 28 + int(math.sin(self.time * 3.0) * 3)
            pygame.draw.circle(surface, (*color, glow_alpha), center, radius + 20)
            points = [
                (center[0], center[1] - radius),
                (center[0] + radius - 7, center[1]),
                (center[0], center[1] + radius),
                (center[0] - radius + 7, center[1]),
            ]
            pygame.draw.polygon(surface, (214, 248, 255, 230), points)
            pygame.draw.polygon(surface, (*color, 240), points, 3)
            return

        if speaker == "LUNAR WARDEN":
            pygame.draw.circle(surface, (42, 15, 22, 190), center, 42)
            pygame.draw.circle(surface, (*color, glow_alpha), center, 52, 3)
            pygame.draw.circle(surface, (255, 224, 224, 240), center, 14)
            pygame.draw.line(surface, (*color, 210), (center[0] - 42, center[1]), (center[0] + 42, center[1]), 3)
            pygame.draw.line(surface, (*color, 210), (center[0], center[1] - 42), (center[0], center[1] + 42), 3)
            return

        pygame.draw.circle(surface, (13, 18, 30, 215), (center[0], center[1] - 20), 26)
        pygame.draw.rect(surface, (15, 21, 35, 230), (center[0] - 24, center[1] + 3, 48, 48), border_radius=12)
        pygame.draw.rect(surface, (*color, 220), (center[0] - 16, center[1] - 26, 32, 8), border_radius=3)
        pygame.draw.rect(surface, (92, 204, 255, 240), (center[0] - 9, center[1] + 17, 18, 24))
        pygame.draw.rect(surface, (*color, 150), (center[0] - 25, center[1] + 3, 50, 50), 2, border_radius=12)
