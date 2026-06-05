import math
from pathlib import Path

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class OriginStory:
    """Cinematic intro shown after Start Game and before Level 1."""

    def __init__(self):
        self.options = ["Read Origin Story", "Skip Story"]
        self.sections = [
            {
                "title": "Before Ruin",
                "lines": [
                    "Before memory.",
                    "Before ruin.",
                    "Before the fall of Velaris...",
                    "There was only the Moon.",
                ],
            },
            {
                "title": "The Four Houses",
                "lines": [
                    "Its light illuminated a civilization unlike any other.",
                    "Beneath its glow stood four great Houses.",
                    "The warriors of Aegis.",
                    "The scholars of the Dawn Archive.",
                    "The watchers of the Veil.",
                    "And the architects who shaped the city itself.",
                ],
            },
            {
                "title": "Limitless",
                "lines": [
                    "Together, they transformed lunar energy into prosperity.",
                    "The city flourished.",
                    "Its towers pierced the heavens.",
                    "Its people believed their future was limitless.",
                ],
            },
            {
                "title": "Project Pale Crown",
                "lines": [
                    "But humanity desired more than it was given.",
                    "More power. More knowledge. More control.",
                    "Beneath the House of Science, a forbidden project began.",
                    "PROJECT PALE CROWN.",
                ],
            },
            {
                "title": "The Volunteer",
                "lines": [
                    "Its purpose was simple.",
                    "Create a human capable of wielding the full power of the Moon.",
                    "A single volunteer was chosen.",
                    "KAEL.",
                    "For a moment... success seemed within reach.",
                ],
            },
            {
                "title": "Containment Failed",
                "lines": [
                    "Then the containment failed.",
                    "The Moon answered with fury.",
                    "A wave of lunar energy erupted across Velaris.",
                    "The sky shattered with light.",
                    "The streets became graveyards.",
                    "The living became dead.",
                    "And the city fell in a single night.",
                ],
            },
            {
                "title": "Among the Dead",
                "lines": [
                    "Hours later... silence.",
                    "The laboratories of the Dawn Archive lay in ruins.",
                    "Bodies covered the floor.",
                    "Machines burned.",
                    "Among the dead... something stirred.",
                    "A lone survivor opened his eyes.",
                ],
            },
            {
                "title": "Wake, Kael",
                "lines": [
                    "No memory. No purpose.",
                    "Only a strange crystal floating beside him.",
                    "Its pale glow pierced the darkness.",
                    "And a voice whispered:",
                    "\"Wake, Kael.\"",
                    "\"The Lunar Core calls to you.\"",
                    "\"Rise. Destroy all who stand before you.\"",
                ],
            },
            {
                "title": "Borrowed Light",
                "lines": [
                    "Your journey is not yet over.",
                ],
                "final": True,
            },
        ]
        self.visible = False
        self.should_start_game = False
        self.selected_index = 0
        self.state = "choice"
        self.page_index = 0
        self.fade_alpha = 0.0
        self.black_alpha = 0.0
        self.time = 0.0
        self.particles = self._create_particles()

    def open(self):
        self.visible = True
        self.should_start_game = False
        self.selected_index = 0
        self.state = "choice"
        self.page_index = 0
        self.fade_alpha = 0.0
        self.black_alpha = 0.0
        self.time = 0.0
        self.particles = self._create_particles()

    def handle_event(self, event):
        if not self.visible:
            return

        if self.state == "choice":
            self._handle_choice_event(event)
            return

        if self.state == "story" and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.fade_alpha < 255:
                    self.fade_alpha = 255.0
                else:
                    self.state = "fade_out"

    def update(self, dt):
        if not self.visible:
            return

        self.time += dt
        self._update_particles(dt)

        if self.state == "story":
            self.fade_alpha = min(255.0, self.fade_alpha + 260.0 * dt)
        elif self.state == "fade_out":
            self.fade_alpha = max(0.0, self.fade_alpha - 380.0 * dt)
            if self.fade_alpha <= 0:
                self.page_index += 1
                self.fade_alpha = 0.0
                if self.page_index >= len(self.sections):
                    self.state = "fade_black"
                    self.black_alpha = 0.0
                else:
                    self.state = "story"
        elif self.state == "fade_black":
            self.black_alpha = min(255.0, self.black_alpha + 300.0 * dt)
            if self.black_alpha >= 255:
                self.visible = False
                self.should_start_game = True

    def draw(self, screen):
        if not self.visible:
            return

        screen.fill((3, 5, 13))
        self._draw_background(screen)

        if self.state == "choice":
            self._draw_choice(screen)
        else:
            self._draw_story_page(screen)

        if self.state == "fade_black":
            black = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            black.fill((0, 0, 0, int(self.black_alpha)))
            screen.blit(black, (0, 0))

    def _handle_choice_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirm_choice()

        elif event.type == pygame.MOUSEMOTION:
            for index, rect in enumerate(self._option_rects()):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self._option_rects()):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    self._confirm_choice()
                    break

    def _confirm_choice(self):
        if self.selected_index == 1:
            self.visible = False
            self.should_start_game = True
            return

        self.state = "story"
        self.page_index = 0
        self.fade_alpha = 0.0

    def _option_rects(self):
        width = 430
        height = 60
        gap = 18
        start_y = SCREEN_HEIGHT // 2 + 48
        return [
            pygame.Rect((SCREEN_WIDTH - width) // 2, start_y + index * (height + gap), width, height)
            for index in range(len(self.options))
        ]

    def _create_particles(self):
        particles = []
        for index in range(120):
            particles.append(
                {
                    "x": (index * 167 + 41) % SCREEN_WIDTH,
                    "y": (index * 91 + 29) % SCREEN_HEIGHT,
                    "speed": 8 + (index % 9) * 3,
                    "radius": 1 + (index % 3 == 0),
                    "phase": index * 0.37,
                    "alpha": 35 + (index * 17) % 105,
                    "drift": 0.4 + (index % 6) * 0.15,
                }
            )
        return particles

    def _update_particles(self, dt):
        for particle in self.particles:
            particle["y"] -= particle["speed"] * dt
            particle["x"] += math.sin(self.time * particle["drift"] + particle["phase"]) * 9 * dt
            if particle["y"] < -14:
                particle["y"] = SCREEN_HEIGHT + 14
                particle["x"] = (particle["x"] + 197) % SCREEN_WIDTH

    def _draw_background(self, screen):
        page = self.sections[min(self.page_index, len(self.sections) - 1)]
        section = self._section_key(page.get("title", ""))
        progress = max(0.0, min(1.0, self.fade_alpha / 255.0))
        cam_x = math.sin(self.time * 0.18 + self.page_index * 0.7) * 18
        cam_y = math.sin(self.time * 0.13 + self.page_index) * 7

        palettes = {
            "before": ((3, 5, 14), (8, 17, 35)),
            "houses": ((4, 6, 18), (10, 22, 40)),
            "limitless": ((5, 8, 20), (12, 29, 55)),
            "project": ((3, 7, 12), (11, 23, 28)),
            "volunteer": ((3, 6, 13), (11, 19, 34)),
            "failed": ((8, 3, 8), (27, 8, 15)),
            "dead": ((3, 4, 7), (14, 15, 19)),
            "wake": ((1, 2, 7), (3, 7, 15)),
            "borrowed": ((2, 4, 13), (8, 15, 31)),
        }
        top, bottom = palettes.get(section, palettes["before"])
        self._draw_gradient(screen, top, bottom)
        self._draw_starfield(screen, section, cam_x)

        if section == "before":
            self._scene_before_ruin(screen, cam_x, cam_y, progress)
        elif section == "houses":
            self._scene_four_houses(screen, cam_x, cam_y, progress)
        elif section == "limitless":
            self._scene_limitless(screen, cam_x, cam_y, progress)
        elif section == "project":
            self._scene_project_pale_crown(screen, cam_x, cam_y, progress)
        elif section == "volunteer":
            self._scene_volunteer(screen, cam_x, cam_y, progress)
        elif section == "failed":
            self._scene_containment_failed(screen, cam_x, cam_y, progress)
        elif section == "dead":
            self._scene_among_dead(screen, cam_x, cam_y, progress)
        elif section == "wake":
            self._scene_wake_kael(screen, cam_x, cam_y, progress)
        elif section == "borrowed":
            self._scene_borrowed_light(screen, cam_x, cam_y, progress)

        self._draw_lunar_particles(screen, section)
        self._draw_fog(screen, section)
        self._draw_vignette(screen, 150 if section in ("failed", "dead", "wake") else 120)

    def _section_key(self, title):
        title = title.lower()
        if "four houses" in title:
            return "houses"
        if "limitless" in title:
            return "limitless"
        if "pale crown" in title:
            return "project"
        if "volunteer" in title:
            return "volunteer"
        if "containment" in title:
            return "failed"
        if "dead" in title:
            return "dead"
        if "wake" in title:
            return "wake"
        if "borrowed" in title:
            return "borrowed"
        return "before"

    def _draw_gradient(self, screen, top, bottom):
        height = max(1, SCREEN_HEIGHT)
        for y in range(0, SCREEN_HEIGHT, 3):
            ratio = y / height
            color = (
                int(top[0] + (bottom[0] - top[0]) * ratio),
                int(top[1] + (bottom[1] - top[1]) * ratio),
                int(top[2] + (bottom[2] - top[2]) * ratio),
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 3))

    def _draw_starfield(self, screen, section, cam_x):
        if section in ("project", "volunteer", "dead", "wake"):
            return

        count = 70 if section != "failed" else 36
        tint = (135, 205, 255) if section != "failed" else (255, 90, 80)
        for index in range(count):
            speed = 0.14 + (index % 5) * 0.06
            x = ((index * 139 + self.time * 18 * speed - cam_x * speed) % (SCREEN_WIDTH + 90)) - 45
            y = (index * 83 + int(self.time * 7 * speed)) % (SCREEN_HEIGHT - 90)
            alpha = 35 + (index * 19) % 95
            size = 1 + (index % 17 == 0)
            surface = pygame.Surface((size + 3, size + 3), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*tint, alpha), (size + 1, size + 1), size)
            screen.blit(surface, (int(x), int(y)))

    def _draw_lunar_particles(self, screen, section):
        colors = {
            "failed": (255, 75, 72),
            "dead": (255, 150, 80),
            "wake": (120, 220, 255),
            "borrowed": (165, 230, 255),
        }
        color = colors.get(section, (120, 210, 255))
        for particle in self.particles:
            alpha = int(particle["alpha"] + math.sin(self.time * 1.7 + particle["phase"]) * 24)
            alpha = max(15, min(145, alpha))
            size = particle["radius"] * 2
            surface = pygame.Surface((size + 5, size + 5), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, alpha), (size // 2 + 2, size // 2 + 2), particle["radius"])
            screen.blit(surface, (int(particle["x"]), int(particle["y"])))

    def _draw_fog(self, screen, section):
        fog_color = (80, 150, 190) if section not in ("failed", "dead") else (110, 60, 70)
        base_alpha = 18 if section not in ("wake", "dead") else 28
        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for index in range(8):
            width = 360 + index * 58
            height = 56 + (index % 3) * 22
            x = int(((index * 251 + self.time * (12 + index * 2)) % (SCREEN_WIDTH + width)) - width)
            y = 92 + index * 66 + int(math.sin(self.time * 0.35 + index) * 9)
            pygame.draw.ellipse(fog, (*fog_color, base_alpha), (x, y, width, height))
        screen.blit(fog, (0, 0))

    def _draw_vignette(self, screen, strength):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for step in range(8):
            alpha = int(strength * (step + 1) / 22)
            rect = pygame.Rect(step * 24, step * 16, SCREEN_WIDTH - step * 48, SCREEN_HEIGHT - step * 32)
            pygame.draw.rect(overlay, (0, 0, 0, alpha), rect, 3)
        pygame.draw.rect(overlay, (0, 0, 0, 48), (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.rect(overlay, (0, 0, 0, 55), (0, SCREEN_HEIGHT - 78, SCREEN_WIDTH, 78))
        screen.blit(overlay, (0, 0))

    def _glow_circle(self, screen, center, radius, color, alpha):
        glow = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
        for step in range(4, 0, -1):
            r = int(radius * step / 4)
            a = int(alpha * (step / 4) * 0.35)
            pygame.draw.circle(glow, (*color, a), (radius + 4, radius + 4), r)
        pygame.draw.circle(glow, (*color, min(255, alpha)), (radius + 4, radius + 4), max(2, radius // 5))
        screen.blit(glow, (center[0] - radius - 4, center[1] - radius - 4))

    def _draw_moon(self, screen, x, y, radius, section, cracked=False):
        pulse = (math.sin(self.time * 1.1) + 1.0) * 0.5
        for glow_radius, alpha in ((radius * 4, 12), (radius * 3, 22), (radius * 2, 38)):
            self._glow_circle(screen, (int(x), int(y)), int(glow_radius + pulse * 5), (115, 190, 255), alpha)

        pygame.draw.circle(screen, (190, 208, 234), (int(x), int(y)), radius)
        pygame.draw.circle(screen, (143, 160, 190), (int(x + radius * 0.38), int(y - radius * 0.32)), max(4, radius // 7))
        pygame.draw.circle(screen, (150, 169, 196), (int(x - radius * 0.34), int(y + radius * 0.22)), max(5, radius // 5))
        pygame.draw.circle(screen, (132, 150, 182), (int(x + radius * 0.28), int(y + radius * 0.38)), max(3, radius // 9))

        if cracked:
            crack_color = (55, 70, 95)
            points = [
                (x - radius * 0.12, y - radius * 0.86),
                (x - radius * 0.04, y - radius * 0.42),
                (x - radius * 0.20, y - radius * 0.08),
                (x - radius * 0.03, y + radius * 0.32),
                (x - radius * 0.18, y + radius * 0.76),
            ]
            pygame.draw.lines(screen, crack_color, False, [(int(px), int(py)) for px, py in points], 3)
            pygame.draw.line(screen, crack_color, (int(x - radius * 0.04), int(y - radius * 0.42)), (int(x + radius * 0.24), int(y - radius * 0.62)), 2)
            pygame.draw.line(screen, crack_color, (int(x - radius * 0.20), int(y - radius * 0.08)), (int(x + radius * 0.18), int(y + radius * 0.02)), 2)

    def _scene_before_ruin(self, screen, cam_x, cam_y, progress):
        moon_x = SCREEN_WIDTH // 2 + cam_x * 0.08
        moon_y = 108 + cam_y * 0.08
        self._draw_moon(screen, moon_x, moon_y, 72, "before")
        self._draw_city_silhouette(screen, SCREEN_HEIGHT - 88, cam_x * 0.22, peaceful=True)
        self._draw_lunar_risers(screen, (105, 220, 255), 42)

    def _scene_four_houses(self, screen, cam_x, cam_y, progress):
        moon_x = SCREEN_WIDTH // 2 + cam_x * 0.05
        moon_y = 105 + cam_y * 0.06
        self._draw_moon(screen, moon_x, moon_y, 64, "houses")
        self._draw_city_silhouette(screen, SCREEN_HEIGHT - 84, cam_x * 0.25, peaceful=True)

        reveal = min(1.0, progress * 1.25)
        centers = [
            (SCREEN_WIDTH // 2 - 330, 140),
            (SCREEN_WIDTH // 2 + 330, 140),
            (SCREEN_WIDTH // 2 - 330, 470),
            (SCREEN_WIDTH // 2 + 330, 470),
        ]
        for index, center in enumerate(centers):
            local_alpha = int(max(0, min(255, (reveal * 4 - index) * 255)))
            if index == 0:
                self._draw_aegis_emblem(screen, center, local_alpha)
            elif index == 1:
                self._draw_archive_emblem(screen, center, local_alpha)
            elif index == 2:
                self._draw_veil_emblem(screen, center, local_alpha)
            else:
                self._draw_architecture_emblem(screen, center, local_alpha)

        if progress > 0.78:
            orbit_alpha = int((progress - 0.78) / 0.22 * 170)
            self._draw_orbiting_house_marks(screen, (moon_x, moon_y), orbit_alpha)

    def _scene_limitless(self, screen, cam_x, cam_y, progress):
        horizon = SCREEN_HEIGHT - 92
        self._draw_moon(screen, SCREEN_WIDTH - 235 + cam_x * 0.05, 112 + cam_y * 0.05, 54, "limitless")
        self._draw_city_silhouette(screen, horizon, cam_x * 0.45, peaceful=False)

        tower_h = int(190 + 180 * progress)
        tower_x = SCREEN_WIDTH // 2 - 44
        pygame.draw.rect(screen, (21, 42, 70), (tower_x, horizon - tower_h, 88, tower_h))
        pygame.draw.rect(screen, (73, 203, 240), (tower_x + 39, horizon - tower_h + 18, 10, tower_h - 24))
        self._glow_circle(screen, (tower_x + 44, horizon - tower_h + 22), 42, (70, 210, 255), 44)

        for index in range(14):
            x = int((index * 117 + self.time * (36 + index % 3 * 8) + cam_x) % (SCREEN_WIDTH + 80) - 40)
            y = 210 + (index * 37) % 220
            color = (74, 224, 255) if index % 2 else (170, 120, 255)
            pygame.draw.rect(screen, color, (x, y, 18, 3), border_radius=2)
            pygame.draw.rect(screen, (*color, 50), (x - 16, y + 1, 12, 1), border_radius=1)

        self._draw_energy_paths(screen, horizon)

    def _scene_project_pale_crown(self, screen, cam_x, cam_y, progress):
        self._draw_lab_walls(screen, cam_x)
        chamber = pygame.Rect(SCREEN_WIDTH // 2 - 86, 142, 172, 250)
        self._glow_circle(screen, chamber.center, 120, (80, 220, 255), 36)
        pygame.draw.rect(screen, (8, 20, 30), chamber, border_radius=8)
        pygame.draw.rect(screen, (90, 210, 245), chamber, 3, border_radius=8)
        pygame.draw.rect(screen, (62, 120, 165), (chamber.x + 30, chamber.y + 28, chamber.w - 60, chamber.h - 56), 2)
        pygame.draw.circle(screen, (150, 225, 255), chamber.center, 15)

        for x in (210, 300, SCREEN_WIDTH - 330, SCREEN_WIDTH - 240):
            self._draw_monitor(screen, x + cam_x * 0.12, 286 + math.sin(self.time + x) * 3)
        for x in (390, 438, SCREEN_WIDTH - 430, SCREEN_WIDTH - 382):
            self._draw_scientist(screen, x + cam_x * 0.08, 434)

        if progress > 0.72:
            flash_alpha = int(max(0, 135 - abs(progress - 0.78) * 900))
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((120, 230, 255, flash_alpha))
            screen.blit(flash, (0, 0))
            shake = math.sin(self.time * 45) * 3
            self._glow_circle(screen, (SCREEN_WIDTH // 2 + int(shake), 250), 190, (140, 235, 255), 60)

    def _scene_volunteer(self, screen, cam_x, cam_y, progress):
        self._draw_lab_walls(screen, cam_x * 0.5)
        pod = pygame.Rect(SCREEN_WIDTH // 2 - 72, 122, 144, 330)
        self._glow_circle(screen, pod.center, 150, (98, 188, 255), 48)
        pygame.draw.rect(screen, (8, 18, 32), pod, border_radius=28)
        pygame.draw.rect(screen, (102, 214, 252), pod, 4, border_radius=28)
        pygame.draw.rect(screen, (52, 93, 140), (pod.x + 26, pod.y + 22, pod.w - 52, pod.h - 44), 2, border_radius=20)

        cx = pod.centerx
        pygame.draw.circle(screen, (14, 20, 34), (cx, pod.y + 106), 22)
        pygame.draw.rect(screen, (14, 20, 34), (cx - 19, pod.y + 128, 38, 104), border_radius=16)
        for index in range(5):
            y = pod.y + 54 + index * 48 + math.sin(self.time * 1.8 + index) * 5
            pygame.draw.line(screen, (102, 210, 255), (pod.x + 12, y), (cx - 28, y + 24), 2)
            pygame.draw.line(screen, (154, 120, 255), (pod.right - 12, y + 10), (cx + 28, y + 30), 2)

        for x in (258, SCREEN_WIDTH - 338):
            pygame.draw.rect(screen, (10, 24, 38), (x, 272, 138, 84), border_radius=5)
            pygame.draw.rect(screen, (67, 124, 170), (x, 272, 138, 84), 2, border_radius=5)
            for row in range(3):
                yy = 295 + row * 19
                pygame.draw.line(screen, (90, 225, 255), (x + 18, yy), (x + 62, yy), 3)
                pygame.draw.line(screen, (105, 120, 162), (x + 80, yy), (x + 120, yy), 3)
        self._draw_scientist(screen, 430, 438)
        self._draw_scientist(screen, SCREEN_WIDTH - 450, 438)

    def _scene_containment_failed(self, screen, cam_x, cam_y, progress):
        shake = math.sin(self.time * 34) * 5 * progress
        self._draw_lab_walls(screen, cam_x + shake)
        self._draw_moon(screen, SCREEN_WIDTH // 2 + shake, 100 + cam_y, 58, "failed", cracked=True)

        alarm = int((math.sin(self.time * 10) + 1) * 65 + 35)
        for x in range(110, SCREEN_WIDTH, 220):
            pygame.draw.rect(screen, (70, 10, 16), (x + shake, 92, 52, 8), border_radius=2)
            self._glow_circle(screen, (int(x + 26 + shake), 96), 46, (255, 44, 44), alarm)

        chamber = pygame.Rect(SCREEN_WIDTH // 2 - 88 + int(shake), 165, 176, 245)
        pygame.draw.rect(screen, (12, 15, 24), chamber, border_radius=8)
        pygame.draw.rect(screen, (255, 80, 80), chamber, 4, border_radius=8)
        for index in range(7):
            x1 = chamber.x + 28 + index * 19
            y1 = chamber.y + 36
            pygame.draw.line(screen, (235, 90, 110), (x1, y1), (x1 + (-1) ** index * 34, y1 + 150), 2)

        radius = int(70 + progress * 430)
        pygame.draw.circle(screen, (150, 225, 255), (SCREEN_WIDTH // 2, 286), radius, 3)

        if 0.45 < progress < 0.58:
            flash_alpha = int(210 * (1 - abs(progress - 0.515) / 0.065))
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((245, 250, 255, max(0, flash_alpha)))
            screen.blit(flash, (0, 0))

        if progress > 0.72:
            self._draw_shadow_forms(screen, int((progress - 0.72) / 0.28 * 160))

    def _scene_among_dead(self, screen, cam_x, cam_y, progress):
        pan = math.sin(self.time * 0.2) * 24
        self._draw_destroyed_lab(screen, cam_x + pan)
        floor_y = SCREEN_HEIGHT - 92
        for index in range(18):
            x = int((index * 92 + pan) % (SCREEN_WIDTH + 140) - 70)
            y = floor_y - 18 - (index % 4) * 7
            pygame.draw.ellipse(screen, (11, 12, 17), (x, y, 64, 16))
            pygame.draw.circle(screen, (9, 10, 15), (x + 50, y + 4), 8)

        move = max(0, min(1, (progress - 0.58) / 0.22))
        hand_x = SCREEN_WIDTH // 2 - 92
        hand_y = floor_y - 34 - int(math.sin(move * math.pi) * 18)
        pygame.draw.line(screen, (38, 42, 52), (hand_x, hand_y + 35), (hand_x + 8, hand_y), 5)
        for finger in range(4):
            pygame.draw.line(screen, (45, 50, 62), (hand_x + 8, hand_y + 2), (hand_x + 2 + finger * 9, hand_y - 16 + finger % 2 * 4), 3)

        for index in range(16):
            x = (index * 79 + int(self.time * 40)) % SCREEN_WIDTH
            y = 95 + (index * 53) % 360
            pygame.draw.rect(screen, (255, 164, 67), (x, y, 3, 7))
            self._glow_circle(screen, (x, y), 12, (255, 120, 50), 28)

    def _scene_wake_kael(self, screen, cam_x, cam_y, progress):
        darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, 130))
        screen.blit(darkness, (0, 0))
        crystal_x = SCREEN_WIDTH // 2
        crystal_y = 265 + int(math.sin(self.time * 1.5) * 12)
        pulse = int((math.sin(self.time * 2.7) + 1) * 40 + 70)
        self._glow_circle(screen, (crystal_x, crystal_y), 108, (100, 220, 255), pulse)
        points = [
            (crystal_x, crystal_y - 38),
            (crystal_x + 28, crystal_y),
            (crystal_x, crystal_y + 38),
            (crystal_x - 28, crystal_y),
        ]
        pygame.draw.polygon(screen, (185, 238, 255), points)
        pygame.draw.polygon(screen, (70, 150, 220), points, 3)
        pygame.draw.line(screen, (255, 255, 255), (crystal_x, crystal_y - 28), (crystal_x, crystal_y + 28), 2)

    def _scene_borrowed_light(self, screen, cam_x, cam_y, progress):
        moon_x = SCREEN_WIDTH // 2
        moon_y = 220
        self._draw_moon(screen, moon_x, moon_y, 116, "borrowed")
        floor_y = SCREEN_HEIGHT - 110
        pygame.draw.rect(screen, (4, 7, 13), (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y))
        pygame.draw.line(screen, (48, 82, 112), (0, floor_y), (SCREEN_WIDTH, floor_y), 2)

        kael_x = SCREEN_WIDTH // 2 - 24
        self._draw_kael_finale_sprite(screen, (kael_x, floor_y + 2))

        crystal_x = kael_x + 102
        crystal_y = floor_y - 104 + int(math.sin(self.time * 1.8) * 8)
        self._glow_circle(screen, (crystal_x, crystal_y), 64, (115, 220, 255), 75)
        pygame.draw.polygon(
            screen,
            (190, 240, 255),
            [(crystal_x, crystal_y - 20), (crystal_x + 16, crystal_y), (crystal_x, crystal_y + 20), (crystal_x - 16, crystal_y)],
        )


    def _draw_kael_finale_sprite(self, screen, midbottom):
        sprite = self._get_kael_finale_sprite()
        if sprite is None:
            kael_x, floor_y = midbottom
            pygame.draw.circle(screen, (2, 4, 9), (kael_x, floor_y - 96), 24)
            pygame.draw.rect(screen, (2, 4, 9), (kael_x - 23, floor_y - 74, 46, 76), border_radius=14)
            pygame.draw.rect(screen, (72, 180, 240), (kael_x - 8, floor_y - 42, 16, 24))
            return

        shadow = pygame.Surface((sprite.get_width() + 46, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 110), shadow.get_rect())
        shadow_rect = shadow.get_rect(center=(midbottom[0], midbottom[1] - 4))
        screen.blit(shadow, shadow_rect)

        glow = pygame.Surface((sprite.get_width() + 74, sprite.get_height() + 74), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (85, 205, 255, 42), glow.get_rect())
        glow_rect = glow.get_rect(center=(midbottom[0], midbottom[1] - sprite.get_height() // 2))
        screen.blit(glow, glow_rect)

        sprite_rect = sprite.get_rect(midbottom=midbottom)
        screen.blit(sprite, sprite_rect)

    def _get_kael_finale_sprite(self):
        cached = getattr(self, "_kael_finale_sprite", None)
        if cached is False:
            return None
        if cached is not None:
            return cached

        asset_candidates = [
            Path(__file__).resolve().parents[2] / "assets" / "processed" / "animations" / "light_weapon_idle_clean.png",
            Path(__file__).resolve().parents[2] / "assets" / "animations" / "idle_withoutweapon.png",
        ]

        for asset_path in asset_candidates:
            if not asset_path.exists():
                continue

            try:
                loaded = pygame.image.load(str(asset_path))
                try:
                    sheet = loaded.convert_alpha()
                except pygame.error:
                    sheet = loaded
            except (OSError, pygame.error):
                continue

            frame_width = sheet.get_height()
            if sheet.get_width() >= frame_width:
                frame_rect = pygame.Rect(0, 0, frame_width, sheet.get_height())
            else:
                frame_rect = sheet.get_rect()

            frame = sheet.subsurface(frame_rect).copy()
            bounds = frame.get_bounding_rect()
            if bounds.width > 0 and bounds.height > 0:
                frame = frame.subsurface(bounds).copy()

            target_height = 142
            scale = target_height / max(1, frame.get_height())
            target_width = max(1, int(frame.get_width() * scale))
            self._kael_finale_sprite = pygame.transform.scale(frame, (target_width, target_height))
            return self._kael_finale_sprite

        self._kael_finale_sprite = False
        return None

    def _draw_city_silhouette(self, screen, horizon, offset, peaceful):
        for layer in range(3):
            color = (6 + layer * 5, 11 + layer * 8, 24 + layer * 12)
            step = 92 - layer * 9
            speed = 0.22 + layer * 0.18
            for index in range(-2, SCREEN_WIDTH // step + 4):
                x = int(index * step - (offset * speed) % step)
                height = 52 + ((index + layer * 3) % 6) * (18 + layer * 4)
                width = 58 + (index % 3) * 12
                pygame.draw.rect(screen, color, (x, horizon - height, width, height))
                if peaceful:
                    pygame.draw.rect(screen, (27, 74, 104), (x + 16, horizon - height + 18, 14, 4))
                else:
                    pygame.draw.rect(screen, (62, 205, 240), (x + 14, horizon - height + 18, 18, 4))
                    pygame.draw.rect(screen, (130, 84, 220), (x + width - 24, horizon - height + 44, 11, 20))

    def _draw_lunar_risers(self, screen, color, alpha):
        for index in range(26):
            x = (index * 53 + int(self.time * (10 + index % 4))) % SCREEN_WIDTH
            y = SCREEN_HEIGHT - 110 - (index * 37 + int(self.time * 22)) % 420
            pygame.draw.line(screen, (*color, alpha), (x, y + 18), (x, y), 2)

    def _draw_aegis_emblem(self, screen, center, alpha):
        if alpha <= 0:
            return
        surface = pygame.Surface((170, 150), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (95, 175, 225, alpha), [(85, 16), (128, 34), (118, 96), (85, 128), (52, 96), (42, 34)])
        pygame.draw.polygon(surface, (10, 25, 42, min(220, alpha)), [(85, 32), (110, 43), (103, 86), (85, 108), (67, 86), (60, 43)])
        for x in (38, 132):
            pygame.draw.circle(surface, (14, 17, 25, alpha), (x, 98), 10)
            pygame.draw.rect(surface, (14, 17, 25, alpha), (x - 7, 108, 14, 28))
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_archive_emblem(self, screen, center, alpha):
        if alpha <= 0:
            return
        surface = pygame.Surface((170, 150), pygame.SRCALPHA)
        c = (85, 74)
        pygame.draw.polygon(surface, (135, 230, 255, alpha), [(85, 18), (116, 74), (85, 130), (54, 74)])
        pygame.draw.polygon(surface, (70, 120, 200, min(210, alpha)), [(85, 18), (116, 74), (85, 74)])
        for radius in (45, 62):
            pygame.draw.ellipse(surface, (115, 210, 255, max(0, alpha - 60)), (c[0] - radius, c[1] - 18, radius * 2, 36), 2)
        for index in range(8):
            angle = self.time * 0.6 + index * math.pi / 4
            x = c[0] + math.cos(angle) * 70
            y = c[1] + math.sin(angle) * 32
            pygame.draw.circle(surface, (165, 235, 255, alpha), (int(x), int(y)), 2)
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_veil_emblem(self, screen, center, alpha):
        if alpha <= 0:
            return
        surface = pygame.Surface((170, 150), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (110, 220, 255, alpha), (35, 45, 100, 55), 3)
        pygame.draw.circle(surface, (115, 210, 255, alpha), (85, 72), 17)
        pygame.draw.circle(surface, (5, 12, 22, min(240, alpha)), (85, 72), 8)
        for index in range(7):
            x = 24 + index * 19
            y = 112 + math.sin(self.time * 2 + index) * 8
            pygame.draw.line(surface, (90, 190, 230, max(0, alpha - 40)), (x, y), (x + 12, y), 2)
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_architecture_emblem(self, screen, center, alpha):
        if alpha <= 0:
            return
        surface = pygame.Surface((170, 150), pygame.SRCALPHA)
        color = (145, 230, 255, alpha)
        for index, rect in enumerate(((34, 78, 30, 44), (72, 42, 34, 80), (114, 64, 28, 58))):
            pygame.draw.rect(surface, color, rect, 2)
            pygame.draw.line(surface, color, (rect[0], rect[1]), (rect[0] + 16, rect[1] - 18), 1)
            pygame.draw.line(surface, color, (rect[0] + rect[2], rect[1]), (rect[0] + rect[2] + 16, rect[1] - 18), 1)
        pygame.draw.line(surface, color, (28, 124), (146, 124), 2)
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_orbiting_house_marks(self, screen, center, alpha):
        if alpha <= 0:
            return
        colors = [(95, 175, 225), (135, 230, 255), (165, 120, 255), (110, 255, 190)]
        for index, color in enumerate(colors):
            angle = self.time * 0.45 + index * math.pi / 2
            x = int(center[0] + math.cos(angle) * 125)
            y = int(center[1] + math.sin(angle) * 62)
            self._glow_circle(screen, (x, y), 22, color, alpha)

    def _draw_energy_paths(self, screen, horizon):
        for index in range(8):
            x1 = index * 170 - 80
            y1 = horizon - 16 - (index % 3) * 28
            x2 = x1 + 150
            y2 = y1 - 22
            pygame.draw.line(screen, (65, 220, 255), (x1, y1), (x2, y2), 2)
            dot_x = x1 + int((self.time * 56 + index * 30) % 150)
            dot_y = y1 + int((dot_x - x1) / 150 * (y2 - y1))
            self._glow_circle(screen, (dot_x, dot_y), 10, (80, 230, 255), 58)

    def _draw_lab_walls(self, screen, offset):
        for x in range(-80, SCREEN_WIDTH + 120, 160):
            xx = int(x - offset * 0.16)
            pygame.draw.rect(screen, (8, 18, 28), (xx, 80, 74, SCREEN_HEIGHT - 150))
            pygame.draw.rect(screen, (18, 36, 52), (xx + 10, 108, 54, 90), 2)
            pygame.draw.rect(screen, (18, 36, 52), (xx + 10, 238, 54, 120), 2)
        pygame.draw.rect(screen, (8, 12, 18), (0, SCREEN_HEIGHT - 96, SCREEN_WIDTH, 96))
        pygame.draw.line(screen, (40, 56, 72), (0, SCREEN_HEIGHT - 96), (SCREEN_WIDTH, SCREEN_HEIGHT - 96), 3)

    def _draw_monitor(self, screen, x, y):
        rect = pygame.Rect(int(x), int(y), 94, 58)
        pygame.draw.rect(screen, (8, 17, 27), rect, border_radius=4)
        pygame.draw.rect(screen, (58, 111, 146), rect, 2, border_radius=4)
        for index in range(3):
            yy = rect.y + 15 + index * 14
            color = (90, 230, 255) if index % 2 == 0 else (110, 130, 162)
            pygame.draw.line(screen, color, (rect.x + 12, yy), (rect.x + 58 + index * 8, yy), 3)

    def _draw_scientist(self, screen, x, floor_y):
        x = int(x)
        pygame.draw.circle(screen, (17, 21, 30), (x, floor_y - 54), 10)
        pygame.draw.rect(screen, (22, 29, 42), (x - 7, floor_y - 45, 14, 36))
        pygame.draw.rect(screen, (120, 215, 235), (x - 3, floor_y - 36, 6, 14))

    def _draw_shadow_forms(self, screen, alpha):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for index in range(7):
            x = 140 + index * 165
            y = SCREEN_HEIGHT - 160 - (index % 3) * 30
            pygame.draw.circle(surface, (0, 0, 0, alpha), (x, y), 20 + (index % 2) * 8)
            pygame.draw.rect(surface, (0, 0, 0, alpha), (x - 18, y + 14, 36, 70), border_radius=16)
            pygame.draw.line(surface, (30, 90, 120, min(150, alpha)), (x - 26, y + 38), (x - 58, y + 8), 2)
            pygame.draw.line(surface, (30, 90, 120, min(150, alpha)), (x + 26, y + 38), (x + 58, y + 8), 2)
        screen.blit(surface, (0, 0))

    def _draw_destroyed_lab(self, screen, offset):
        self._draw_lab_walls(screen, offset)
        for index in range(9):
            x = int(index * 160 - (offset * 0.24 % 160))
            pygame.draw.line(screen, (34, 42, 54), (x, 96), (x + 80, 190 + (index % 3) * 44), 2)
            pygame.draw.rect(screen, (18, 22, 28), (x + 40, 360 + (index % 2) * 30, 90, 14))
        smoke = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for index in range(9):
            x = int((index * 151 + self.time * 18) % SCREEN_WIDTH)
            y = 315 - (index % 4) * 34
            pygame.draw.ellipse(smoke, (80, 88, 100, 22), (x, y, 180, 56))
        screen.blit(smoke, (0, 0))

    def _draw_choice(self, screen):
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 28)
        option_font = pygame.font.Font(None, 38)
        prompt_font = pygame.font.Font(None, 24)

        title = title_font.render("Origin Story", True, (232, 244, 255))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 260)))

        subtitle = subtitle_font.render("Before Kael wakes, choose how the journey begins.", True, (146, 184, 220))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 310)))

        for index, rect in enumerate(self._option_rects()):
            selected = index == self.selected_index
            fill = (29, 48, 74) if selected else (13, 21, 36)
            border = (186, 230, 255) if selected else (65, 110, 150)
            text_color = (255, 255, 255) if selected else (204, 222, 238)
            pygame.draw.rect(screen, fill, rect, border_radius=6)
            pygame.draw.rect(screen, border, rect, 2, border_radius=6)
            if selected:
                pygame.draw.rect(screen, (96, 210, 255), (rect.x + 16, rect.centery - 2, 34, 4), border_radius=2)
            label = option_font.render(self.options[index], True, text_color)
            screen.blit(label, label.get_rect(center=rect.center))

        prompt = prompt_font.render("Press Enter to Continue", True, (166, 198, 224))
        screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 58)))

    def _draw_story_page(self, screen):
        prompt_font = pygame.font.Font(None, 24)
        progress_font = pygame.font.Font(None, 22)
        page_alpha = int(self.fade_alpha)
        page = self.sections[min(self.page_index, len(self.sections) - 1)]
        section = self._section_key(page.get("title", ""))
        is_final = page.get("final", False)

        page_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._draw_text_readability_field(page_surface, section, is_final)

        if is_final:
            title_alpha = int(max(0, min(255, (self.fade_alpha - 18) * 1.8)))
            self._blit_centered_text(
                page_surface,
                page["title"].upper(),
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 48),
                72,
                38,
                (232, 247, 255),
                title_alpha,
                SCREEN_WIDTH - 150,
                glow_color=(112, 220, 255),
                glow_alpha=title_alpha,
            )
            self._blit_centered_text(
                page_surface,
                page["lines"][0],
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 44),
                31,
                22,
                (171, 219, 246),
                max(0, min(page_alpha, page_alpha - 65)),
                SCREEN_WIDTH - 190,
                glow_color=(70, 190, 255),
                glow_alpha=70,
            )
        else:
            self._blit_centered_text(
                page_surface,
                page["title"].upper(),
                (SCREEN_WIDTH // 2, 188),
                40,
                28,
                (235, 246, 255),
                page_alpha,
                SCREEN_WIDTH - 210,
                glow_color=(95, 195, 255),
                glow_alpha=65,
            )

            lines = page["lines"]
            available_top = 278
            available_bottom = SCREEN_HEIGHT - 122
            available_height = available_bottom - available_top
            line_height = max(29, min(38, available_height // max(1, len(lines))))
            block_height = (len(lines) - 1) * line_height
            start_y = available_top + (available_height - block_height) // 2
            base_size = 32 if len(lines) <= 5 else 28

            for index, text in enumerate(lines):
                line_alpha = int(max(0, min(255, (self.fade_alpha - index * 28) * 1.45)))
                size = base_size
                color = (229, 240, 250)
                glow_color = None
                glow_alpha = 0

                if section == "wake" and text.startswith("\""):
                    color = (175, 235, 255)
                    glow_color = (80, 205, 255)
                    glow_alpha = 95
                elif section == "project" and "PROJECT PALE CROWN" in text:
                    size = 35
                    color = (240, 252, 255)
                    glow_color = (120, 235, 255)
                    glow_alpha = 120
                elif section == "volunteer" and text == "KAEL.":
                    size = 44
                    color = (235, 248, 255)
                    glow_color = (110, 220, 255)
                    glow_alpha = 130
                elif section == "failed":
                    color = (255, 230, 230)
                    if "Moon answered" in text or "sky shattered" in text:
                        glow_color = (255, 90, 90)
                        glow_alpha = 95

                self._blit_centered_text(
                    page_surface,
                    text,
                    (SCREEN_WIDTH // 2, start_y + index * line_height),
                    size,
                    22,
                    color,
                    line_alpha,
                    SCREEN_WIDTH - 190,
                    glow_color=glow_color,
                    glow_alpha=glow_alpha,
                )

        prompt_ready = self.fade_alpha >= 255
        prompt_text = "Press Enter to Begin" if is_final else "Press Enter or Space to Continue"
        prompt_alpha = 68
        if prompt_ready:
            prompt_alpha = int((math.sin(self.time * 3.0) + 1.0) * 70 + 90)
        prompt = prompt_font.render(prompt_text, True, (166, 198, 224))
        prompt.set_alpha(min(page_alpha, prompt_alpha))
        page_surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 58)))

        progress = progress_font.render(f"{self.page_index + 1} / {len(self.sections)}", True, (100, 132, 165))
        progress.set_alpha(min(page_alpha, 145))
        page_surface.blit(progress, progress.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        screen.blit(page_surface, (0, 0))

    def _draw_text_readability_field(self, surface, section, is_final):
        field = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        if is_final:
            rect = pygame.Rect(120, 210, SCREEN_WIDTH - 240, 270)
            alpha = 118
        else:
            rect = pygame.Rect(90, 156, SCREEN_WIDTH - 180, SCREEN_HEIGHT - 250)
            alpha = 104 if section not in ("failed", "wake", "dead") else 130

        pygame.draw.rect(field, (0, 0, 0, alpha), rect, border_radius=18)
        pygame.draw.rect(field, (40, 78, 108, 26), rect, 1, border_radius=18)
        surface.blit(field, (0, 0))

    def _blit_centered_text(
        self,
        surface,
        text,
        center,
        base_size,
        min_size,
        color,
        alpha,
        max_width,
        glow_color=None,
        glow_alpha=0,
    ):
        if alpha <= 0:
            return

        rendered = self._render_fit(text, base_size, min_size, color, max_width)
        shadow = self._render_fit(text, base_size, min_size, (0, 0, 0), max_width)
        alpha = int(max(0, min(255, alpha)))

        shadow.set_alpha(min(210, alpha))
        surface.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 3)))

        if glow_color and glow_alpha > 0:
            glow = self._render_fit(text, base_size, min_size, glow_color, max_width)
            glow.set_alpha(min(alpha, glow_alpha))
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                surface.blit(glow, glow.get_rect(center=(center[0] + dx, center[1] + dy)))

        rendered.set_alpha(alpha)
        surface.blit(rendered, rendered.get_rect(center=center))

    def _render_fit(self, text, base_size, min_size, color, max_width):
        size = base_size
        font = pygame.font.Font(None, size)
        while size > min_size and font.size(text)[0] > max_width:
            size -= 2
            font = pygame.font.Font(None, size)
        return font.render(text, True, color)
