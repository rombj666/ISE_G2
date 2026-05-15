import math

import pygame


class MoonShard:
    """
    A glowing crystalline moon shard that floats beside the player at all times.
    Pulses softly, sways gently, and emits a layered halo + drifting particles.
    Pure decoration — no collision, no gameplay impact.
    """

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.time = 0.0
        # How tightly the shard tracks the target position (0..1; higher = snappier).
        self.smoothing = 0.22
        # How fast the shard arcs from one side to the other when player turns (0..1).
        self.side_swap_speed = 0.05
        # Base distance from the player's center on whichever side it's on.
        self.side_distance = 70
        self.offset_y = -30
        # Current horizontal offset — animates smoothly toward target_offset_x.
        # Negative = on the player's LEFT, positive = on the player's RIGHT.
        # Default to the right side (player spawns facing right).
        self.offset_x = -self.side_distance
        self.target_offset_x = -self.side_distance
        # Particle ring — orbits around the shard.
        self.particle_count = 5

    def reset_to(self, player_rect, player_facing=1):
        """Snap the shard to the player's TRAILING side immediately (use on map change)."""
        # Trail on the side OPPOSITE the facing direction so it doesn't block forward view.
        self.target_offset_x = -self.side_distance * player_facing
        self.offset_x = self.target_offset_x
        self.x = float(player_rect.centerx + self.offset_x)
        self.y = float(player_rect.top + self.offset_y)

    def update(self, dt, player_rect, player_facing=1):
        self.time += dt

        # Pick the trailing side based on the player's facing direction:
        # facing right (+1)  -> shard on LEFT  (offset_x = -70)
        # facing left  (-1)  -> shard on RIGHT (offset_x = +70)
        self.target_offset_x = -self.side_distance * player_facing

        # Smoothly arc the offset toward the new side when the player turns around.
        self.offset_x += (self.target_offset_x - self.offset_x) * self.side_swap_speed

        # Gentle bob + sway so the shard feels alive even when player stands still.
        bob = math.sin(self.time * 2.4) * 7
        sway = math.sin(self.time * 1.5) * 5

        target_x = player_rect.centerx + self.offset_x + sway
        target_y = player_rect.top + self.offset_y + bob

        # Smooth lerp toward the target — gives a tiny lag like a tethered spirit.
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing

    def draw(self, screen, camera=None):
        sx, sy = int(self.x), int(self.y)
        if camera is not None:
            sx, sy = camera.apply_pos((sx, sy))

        # Pulse value (0..1) modulates halo size + glow intensity.
        pulse = (math.sin(self.time * 3.2) + 1.0) * 0.5

        # ─── Outer halo (large, very transparent) ────────────────────────
        halo_radius = int(28 + pulse * 10)
        halo_alpha = int(28 + pulse * 22)
        halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            halo_surf,
            (140, 200, 250, halo_alpha),
            (halo_radius, halo_radius),
            halo_radius,
        )
        screen.blit(halo_surf, (sx - halo_radius, sy - halo_radius))

        # ─── Mid glow (smaller, brighter) ────────────────────────────────
        mid_radius = int(16 + pulse * 5)
        mid_alpha = int(70 + pulse * 60)
        mid_surf = pygame.Surface((mid_radius * 2, mid_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            mid_surf,
            (180, 220, 255, mid_alpha),
            (mid_radius, mid_radius),
            mid_radius,
        )
        screen.blit(mid_surf, (sx - mid_radius, sy - mid_radius))

        # ─── Inner glow tight around the shard ───────────────────────────
        inner_radius = int(10 + pulse * 3)
        inner_alpha = int(140 + pulse * 60)
        inner_surf = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            inner_surf,
            (220, 240, 255, inner_alpha),
            (inner_radius, inner_radius),
            inner_radius,
        )
        screen.blit(inner_surf, (sx - inner_radius, sy - inner_radius))

        # ─── Crystal core (diamond shape) ────────────────────────────────
        size = int(7 + pulse * 2)
        # Outer crystal facets — slightly larger
        outer_pts = [
            (sx, sy - size - 5),
            (sx + size + 1, sy),
            (sx, sy + size + 5),
            (sx - size - 1, sy),
        ]
        pygame.draw.polygon(screen, (90, 140, 200), outer_pts)
        # Inner crystal — bright core
        inner_pts = [
            (sx, sy - size - 2),
            (sx + size - 1, sy),
            (sx, sy + size + 2),
            (sx - size + 1, sy),
        ]
        pygame.draw.polygon(screen, (220, 240, 255), inner_pts)
        # Bright facet highlight (left edge)
        highlight_pts = [
            (sx, sy - size - 2),
            (sx - 1, sy - 1),
            (sx - size + 1, sy),
        ]
        pygame.draw.polygon(screen, (255, 255, 255), highlight_pts)
        # Tiny center sparkle
        pygame.draw.rect(screen, (255, 255, 255), (sx - 1, sy - 1, 2, 2))

        # ─── Drifting particles orbiting the shard ───────────────────────
        for i in range(self.particle_count):
            angle = self.time * 1.8 + i * (math.tau / self.particle_count)
            radius_x = 18 + pulse * 5
            radius_y = 14 + pulse * 4
            px = sx + int(math.cos(angle) * radius_x)
            py = sy + int(math.sin(angle) * radius_y)
            # Particle alpha varies with its angle for twinkle effect
            twinkle = (math.sin(self.time * 4.0 + i) + 1.0) * 0.5
            p_alpha = int(120 + twinkle * 100)
            p_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.rect(p_surf, (200, 230, 250, p_alpha), (0, 0, 4, 4))
            screen.blit(p_surf, (px - 2, py - 2))
