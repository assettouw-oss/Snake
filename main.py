"""Moto Bamako: an endless-runner game built with Pygame."""

import asyncio
import colorsys
import json
import math
import random
import sys
from array import array
from enum import Enum, auto
from pathlib import Path
from typing import List, Tuple

import pygame


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FPS = 60
ROAD_TOP = 430
GROUND_Y = ROAD_TOP
PLAYER_X = 150
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 64
PLAYER_MOVE_SPEED = 360.0
GRAVITY = 1500.0
JUMP_VELOCITY = -660.0
DOUBLE_JUMP_WINDOW_MS = 450
START_SPEED = 390.0
MAX_SPEED = 780.0
SAVE_PATH = Path(__file__).with_name("moto_bamako_save.json")
DIFFICULTIES = {
    "DECOUVERTE": {"start_speed": 330.0, "max_speed": 600.0, "spawn": (1.55, 2.05)},
    "NORMAL": {"start_speed": START_SPEED, "max_speed": MAX_SPEED, "spawn": (1.2, 1.75)},
    "EXPERT": {"start_speed": 470.0, "max_speed": 880.0, "spawn": (0.95, 1.4)},
}
MISSIONS = (
    ("coins", "Ramasse 6 pieces", 6),
    ("distance", "Parcours 1 200 m", 1200),
    ("dodges", "Evite 12 obstacles", 12),
)
MISSION_REWARD = 250
SECTORS = (
    ("CENTRE DE BAMAKO", (240, 175, 111), (160, 112, 82), (129, 91, 71)),
    ("ROUTE DU SAHEL", (248, 198, 131), (172, 126, 84), (143, 102, 70)),
    ("GRAND MARCHE", (226, 154, 112), (139, 90, 74), (107, 70, 62)),
)
ROUTES = (
    ("BAMAKO CENTRAL", (240, 175, 111), (188, 130, 84), (49, 54, 61), (248, 202, 66), (160, 112, 82), (129, 91, 71), "city"),
    ("PISTE DU SAHEL", (248, 198, 131), (200, 149, 94), (87, 69, 51), (240, 197, 100), (172, 126, 84), (143, 102, 70), "dirt"),
    ("GRAND MARCHE", (226, 154, 112), (174, 116, 84), (68, 54, 52), (240, 179, 80), (139, 90, 74), (107, 70, 62), "market"),
    ("BERGES DU NIGER", (137, 198, 207), (105, 163, 146), (48, 76, 76), (249, 216, 121), (106, 145, 125), (70, 109, 98), "river"),
    ("COLLINE KOULOUBA", (164, 177, 202), (132, 137, 157), (57, 64, 82), (241, 204, 108), (124, 120, 127), (83, 86, 105), "mountain"),
    ("ROUTE DE SEGOU", (242, 190, 133), (195, 145, 98), (81, 67, 55), (245, 218, 135), (164, 112, 75), (126, 82, 60), "highway"),
    ("PISTE ROUGE", (221, 147, 111), (183, 105, 76), (76, 52, 48), (240, 196, 102), (146, 86, 68), (107, 66, 58), "red_dirt"),
    ("NUIT DE BAMAKO", (71, 86, 126), (83, 95, 127), (39, 46, 68), (249, 206, 84), (90, 89, 119), (60, 62, 92), "night"),
    ("PLAINES DU MANDE", (184, 202, 143), (139, 162, 110), (59, 70, 52), (244, 211, 116), (139, 145, 91), (99, 108, 69), "plains"),
    ("ROUTE DES DUNES", (240, 210, 153), (211, 173, 118), (83, 67, 49), (255, 224, 124), (182, 139, 91), (143, 101, 66), "dunes"),
)
_ADDITIONAL_ROUTE_NAMES = (
    "FORET DE SIKASSO", "LAC DE SELINGUE", "FALAISES DE BANDIAGARA",
    "ROUTE DES BAOBABS", "VALLEE DU NIGER", "SAVANE DOREE",
    "PLUIE TROPICALE", "ROUTE DES COTONNIERS", "CANYON DE HOMBORI",
    "AUBE SUR BAMAKO", "OASIS DE TAOUDENI", "JARDINS DU SUD",
    "ROUTE DES ACACIAS", "DELTA DU NIGER", "CREPUSCULE ROUGE",
    "PLATEAU DE KITA", "ROUTE DES PALMIERS", "NUIT ETOILEE",
    "GRAND NORD", "CAMPAGNE DU MALI", "ROUTE DES MANGUIERS",
    "PONT DE KAYES", "HORIZON DU SAHEL",
)
_ROAD_STYLES = ("city", "dirt", "market", "river", "mountain", "highway", "red_dirt", "night", "plains", "dunes")


def _build_additional_routes() -> tuple[tuple, ...]:
    routes = []
    for offset, name in enumerate(_ADDITIONAL_ROUTE_NAMES):
        hue = (0.13 + offset * 0.61803398875) % 1.0
        sky = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb(hue, 0.76, 0.62))
        landscape = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb(hue, 0.55, 0.44))
        road = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb(hue, 0.24, 0.25))
        marking = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb((hue + 0.11) % 1.0, 0.67, 0.78))
        buildings = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb(hue, 0.46, 0.38))
        outlines = tuple(round(channel * 255) for channel in colorsys.hls_to_rgb(hue, 0.34, 0.27))
        style = _ROAD_STYLES[offset % len(_ROAD_STYLES)]
        routes.append((name, sky, landscape, road, marking, buildings, outlines, style))
    return tuple(routes)


ROUTES += _build_additional_routes()
ROUTE_UNLOCK_SCORES = tuple(index * 1000 for index in range(len(ROUTES)))

Color = Tuple[int, int, int]

SAND = (211, 169, 111)
WHITE = (255, 248, 232)
INK = (37, 34, 34)
RED = (195, 53, 44)
GREEN = (38, 137, 84)
SAMPLE_RATE = 22050
BAR_COUNT = 4


class Soundtrack:
    """Creates route-specific music and sound effects with synthesized instruments."""

    MODES = (
        (0, 2, 4, 5, 7, 9, 11),
        (0, 2, 3, 5, 7, 9, 10),
        (0, 1, 3, 5, 7, 8, 10),
        (0, 2, 4, 6, 7, 9, 11),
        (0, 2, 4, 5, 7, 9, 10),
        (0, 2, 3, 5, 7, 8, 11),
        (0, 1, 3, 5, 6, 8, 10),
    )
    INSTRUMENTS = (
        ((0.62, 0.24, 0.10, 0.04), (1.0, 2.01, 3.02, 4.05), 180, 5.5, 2.2, 0.68),
        ((0.55, 0.26, 0.14, 0.05), (1.0, 2.76, 5.4, 8.93), 300, 4.0, 1.2, 0.75),
        ((0.70, 0.20, 0.08, 0.02), (1.0, 3.9, 10.1, 14.2), 250, 10.0, 4.0, 0.85),
        ((0.65, 0.25, 0.08, 0.02), (1.0, 2.0, 3.0, 4.0), 30, 0.7, 0.35, 0.35),
        ((0.55, 0.30, 0.10, 0.05), (1.0, 2.01, 3.9, 6.1), 350, 9.0, 2.4, 0.85),
        ((0.45, 0.30, 0.18, 0.07), (1.0, 1.5, 2.0, 3.0), 55, 1.8, 0.35, 0.2),
    )

    def __init__(self) -> None:
        self.sound = None
        self.effects = {}
        self.enabled = False
        self.playing = False
        self.volume = 1.0
        self.route_index = 0
        try:
            mixer_settings = pygame.mixer.get_init()
            if mixer_settings is None:
                pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
                mixer_settings = pygame.mixer.get_init()
            if mixer_settings is None or mixer_settings[0] != SAMPLE_RATE or mixer_settings[1] != -16:
                raise pygame.error("Pygame audio must use 22050 Hz, signed 16-bit samples")

            self._build_route_audio()
            self.sound.play(loops=-1)
            self.enabled = True
            self.playing = True
        except pygame.error as error:
            print(f"Musique indisponible : {error}")

    def play_effect(self, name: str) -> None:
        effect = self.effects.get(name)
        if self.enabled and self.playing and effect is not None:
            effect.play()

    def set_route(self, route_index: int) -> None:
        if route_index == self.route_index or self.sound is None:
            return
        was_playing = self.playing
        self.sound.stop()
        for effect in self.effects.values():
            effect.stop()
        self.route_index = route_index
        try:
            self._build_route_audio()
        except pygame.error as error:
            self.sound = None
            self.effects = {}
            self.enabled = False
            self.playing = False
            print(f"Musique indisponible : {error}")
            return
        if was_playing:
            self.sound.play(loops=-1)
            self.playing = True

    def _build_route_audio(self) -> None:
        self.sound = pygame.mixer.Sound(buffer=self._create_loop(self.route_index))
        self.sound.set_volume(0.32 * self.volume)
        self.effects = {
            "jump": self._create_effect((69,), self.route_index),
            "coin": self._create_effect((84, 88), self.route_index),
            "hit": self._create_effect((52, 47), self.route_index),
            "shield": self._create_effect((76, 84), self.route_index),
        }
        for effect in self.effects.values():
            effect.set_volume(0.42 * self.volume)

    def set_volume(self, volume: float) -> None:
        self.volume = volume
        if self.sound is not None:
            self.sound.set_volume(0.32 * volume)
        for effect in self.effects.values():
            effect.set_volume(0.42 * volume)

    def stop(self) -> None:
        if self.sound is None:
            return
        self.sound.stop()
        for effect in self.effects.values():
            effect.stop()
        self.playing = False

    def resume(self) -> None:
        if self.sound is None or not self.enabled or self.playing:
            return
        self.sound.play(loops=-1)
        self.playing = True

    def toggle(self) -> None:
        if self.sound is None:
            return
        if self.enabled:
            self.enabled = False
            self.stop()
        else:
            self.enabled = True
            self.resume()

    @classmethod
    def _create_loop(cls, route_index: int = 0) -> bytes:
        tempo = 72 + (route_index * 7) % 49
        beat_duration = 60.0 / tempo
        duration = beat_duration * BAR_COUNT * 4
        samples = [0.0] * int(SAMPLE_RATE * duration)
        mode = cls.MODES[route_index % len(cls.MODES)]
        root = 48 + (route_index * 5) % 12
        instrument = route_index % len(cls.INSTRUMENTS)
        melody_degrees = (
            7, 9, 11, 14, 11, 9, 7, 4,
            6, 7, 9, 14, 9, 7, 6, 4,
            7, 9, 11, 14, 16, 14, 11, 9,
            6, 7, 9, 14, 9, 7, 6, 4,
        )
        melody = tuple(root + 12 + mode[degree % 7] + (degree // 7) * 12 for degree in melody_degrees)
        bass_degrees = (0, 4, 2, 4, 5, 2, 4, 2, 0, 4, 2, 4, 5, 2, 4, 2)
        bass = tuple(root - 12 + mode[degree] for degree in bass_degrees)

        for step, note in enumerate(melody):
            start = int(step * beat_duration / 2 * SAMPLE_RATE)
            cls._add_instrument(samples, start, note, beat_duration * 0.46, 0.27, instrument)

        for beat, note in enumerate(bass):
            start = int(beat * beat_duration * SAMPLE_RATE)
            cls._add_instrument(samples, start, note, beat_duration * 0.9, 0.2, instrument)

        pcm = array("h", (max(-32768, min(32767, int(value))) for value in samples))
        return pcm.tobytes()

    @classmethod
    def _create_effect(cls, notes: tuple[int, ...], route_index: int = 0) -> pygame.mixer.Sound:
        note_duration = 0.14 + route_index * 0.003
        samples = [0.0] * int(SAMPLE_RATE * (note_duration * len(notes) + 0.12))
        transposition = (route_index * 5) % 12
        for index, note in enumerate(notes):
            cls._add_instrument(
                samples,
                int(index * note_duration * SAMPLE_RATE),
                note + transposition,
                note_duration,
                0.36,
                route_index % len(cls.INSTRUMENTS),
            )
        pcm = array("h", (max(-32768, min(32767, int(value))) for value in samples))
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    @staticmethod
    def _add_instrument(
        samples: List[float],
        start: int,
        midi_note: int,
        duration: float,
        volume: float,
        instrument: int = 0,
    ) -> None:
        frequency = 440.0 * 2 ** ((midi_note - 69) / 12)
        harmonics, partials, attack_rate, transient_decay, sustain_decay, transient_mix = (
            Soundtrack.INSTRUMENTS[instrument]
        )
        end = min(len(samples), start + int(duration * SAMPLE_RATE))
        for index in range(start, end):
            elapsed = (index - start) / SAMPLE_RATE
            attack = 1 - math.exp(-elapsed * attack_rate)
            envelope = attack * (
                transient_mix * math.exp(-transient_decay * elapsed / duration)
                + (1 - transient_mix) * math.exp(-sustain_decay * elapsed / duration)
            )
            tone = (
                math.sin(2 * math.pi * frequency * partials[0] * elapsed) * harmonics[0]
                + math.sin(2 * math.pi * frequency * partials[1] * elapsed) * harmonics[1]
                + math.sin(2 * math.pi * frequency * partials[2] * elapsed) * harmonics[2]
                + math.sin(2 * math.pi * frequency * partials[3] * elapsed) * harmonics[3]
            )
            samples[index] += volume * envelope * tone * 32767


class GameState(Enum):
    MENU = auto()
    TUTORIAL = auto()
    SETTINGS = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class Mission:
    """A small run-specific objective that rewards deliberate play."""

    def __init__(self) -> None:
        self.kind, self.title, self.target = random.choice(MISSIONS)
        self.progress = 0
        self.completed = False

    def update(self, distance: float, coins: int, dodges: int) -> bool:
        if self.completed:
            return False
        if self.kind == "distance":
            self.progress = min(int(distance), self.target)
        elif self.kind == "coins":
            self.progress = min(coins, self.target)
        else:
            self.progress = min(dodges, self.target)
        if self.progress >= self.target:
            self.completed = True
            return True
        return False


class Obstacle:
    """A road hazard with its own hitbox and drawing behavior."""

    SIZES = {
        "trou": (72, 24),
        "dos_dane": (82, 24),
        "sotrama": (112, 70),
        "pierre": (66, 48),
        "barriere": (112, 58),
        "bidon": (46, 56),
    }

    def __init__(self, kind: str, x: float) -> None:
        self.kind = kind
        self.x = x
        self.width, self.height = self.SIZES[kind]
        self.y = GROUND_Y - self.height

    @property
    def hitbox(self) -> pygame.Rect:
        if self.kind == "trou":
            return pygame.Rect(int(self.x + 7), int(self.y + 8), self.width - 14, self.height - 8)
        if self.kind == "dos_dane":
            return pygame.Rect(int(self.x + 4), int(self.y + 5), self.width - 8, self.height - 5)
        if self.kind == "pierre":
            return pygame.Rect(int(self.x + 8), int(self.y + 13), self.width - 16, self.height - 13)
        if self.kind == "barriere":
            return pygame.Rect(int(self.x + 3), int(self.y + 10), self.width - 6, self.height - 10)
        if self.kind == "bidon":
            return pygame.Rect(int(self.x + 5), int(self.y + 5), self.width - 10, self.height - 5)
        return pygame.Rect(int(self.x + 5), int(self.y + 5), self.width - 10, self.height - 5)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        x = int(self.x)
        if self.kind == "trou":
            pygame.draw.ellipse(surface, (23, 24, 27), (x, int(self.y), self.width, self.height))
            pygame.draw.ellipse(surface, (111, 103, 88), (x - 3, int(self.y) - 2, self.width + 6, self.height + 4), 2)
        elif self.kind == "dos_dane":
            points = [
                (x, GROUND_Y),
                (x + 12, int(self.y + 8)),
                (x + self.width - 12, int(self.y + 8)),
                (x + self.width, GROUND_Y),
            ]
            pygame.draw.polygon(surface, (218, 177, 49), points)
            pygame.draw.line(surface, WHITE, (x + 25, int(self.y + 10)), (x + 55, int(self.y + 10)), 4)
        elif self.kind == "sotrama":
            bus = pygame.Rect(x, int(self.y), self.width, self.height)
            pygame.draw.rect(surface, GREEN, bus, border_radius=8)
            pygame.draw.rect(surface, (211, 234, 211), (x + 10, int(self.y + 10), 25, 20), border_radius=3)
            pygame.draw.rect(surface, (211, 234, 211), (x + 43, int(self.y + 10), 25, 20), border_radius=3)
            pygame.draw.rect(surface, (211, 234, 211), (x + 76, int(self.y + 10), 25, 20), border_radius=3)
            label = font.render("SOTRAMA", True, WHITE)
            surface.blit(label, label.get_rect(center=(x + self.width // 2, int(self.y + 48))))
            pygame.draw.circle(surface, INK, (x + 25, GROUND_Y - 2), 10)
            pygame.draw.circle(surface, INK, (x + 88, GROUND_Y - 2), 10)
        elif self.kind == "pierre":
            pygame.draw.ellipse(surface, (91, 82, 72), (x, int(self.y + 6), self.width, self.height - 6))
            pygame.draw.ellipse(surface, (137, 125, 108), (x + 10, int(self.y + 12), 25, 12))
            pygame.draw.line(surface, (64, 59, 54), (x + 13, int(self.y + 33)), (x + 27, int(self.y + 26)), 3)
            pygame.draw.line(surface, (64, 59, 54), (x + 42, int(self.y + 37)), (x + 52, int(self.y + 27)), 3)
        elif self.kind == "barriere":
            pygame.draw.rect(surface, (212, 199, 169), (x + 5, int(self.y + 8), self.width - 10, 22), border_radius=5)
            for stripe_x in range(x + 9, x + self.width - 8, 25):
                pygame.draw.polygon(
                    surface,
                    RED,
                    ((stripe_x, int(self.y + 9)), (stripe_x + 12, int(self.y + 9)),
                     (stripe_x + 5, int(self.y + 29)), (stripe_x - 7, int(self.y + 29))),
                )
            pygame.draw.rect(surface, (89, 74, 59), (x + 17, int(self.y + 29), 8, 25))
            pygame.draw.rect(surface, (89, 74, 59), (x + self.width - 25, int(self.y + 29), 8, 25))
        else:
            barrel = pygame.Rect(x + 4, int(self.y + 3), self.width - 8, self.height - 3)
            pygame.draw.rect(surface, (174, 71, 42), barrel, border_radius=7)
            pygame.draw.rect(surface, (218, 189, 129), (x + 5, int(self.y + 16), self.width - 10, 5))
            pygame.draw.rect(surface, (218, 189, 129), (x + 5, int(self.y + 37), self.width - 10, 5))
            pygame.draw.ellipse(surface, (121, 53, 36), (x + 5, int(self.y + 2), self.width - 10, 10))


class Pickup:
    """A collectible placed on the road."""

    def __init__(self, kind: str, x: float, y: int) -> None:
        self.kind = kind
        self.x = x
        self.y = y
        self.phase = random.random() * math.tau
        self.radius = 13 if kind == "coin" else 16

    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface: pygame.Surface, elapsed: float) -> None:
        bob = math.sin(elapsed * 5 + self.phase) * 4
        center = (int(self.x), int(self.y + bob))
        if self.kind == "coin":
            pygame.draw.circle(surface, (134, 86, 28), center, self.radius + 2)
            pygame.draw.circle(surface, (255, 202, 54), center, self.radius)
            pygame.draw.circle(surface, (255, 235, 148), center, self.radius - 5, 2)
            pygame.draw.line(surface, (255, 235, 148), (center[0], center[1] - 5), (center[0], center[1] + 5), 2)
        else:
            pygame.draw.circle(surface, (134, 86, 28), center, self.radius + 3)
            pygame.draw.circle(surface, (255, 202, 54), center, self.radius)
            pygame.draw.polygon(
                surface,
                (255, 239, 166),
                [
                    (center[0], center[1] - 10),
                    (center[0] + 9, center[1] - 5),
                    (center[0] + 7, center[1] + 6),
                    (center[0], center[1] + 11),
                    (center[0] - 7, center[1] + 6),
                    (center[0] - 9, center[1] - 5),
                ],
            )


class Particle:
    """A short-lived visual effect for jumps, pickups, and impacts."""

    def __init__(self, x: float, y: float, color: Color, velocity_x: float, velocity_y: float) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 0.55

    def update(self, delta_time: float) -> None:
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.velocity_y += 380 * delta_time
        self.life -= delta_time

    def draw(self, surface: pygame.Surface) -> None:
        radius = max(1, int(5 * self.life / 0.55))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class MotoBamakoGame:
    def __init__(self) -> None:
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Moto Bamako")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.title_font = pygame.font.Font(None, 82)
        self.heading_font = pygame.font.Font(None, 50)
        self.body_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)
        self.obstacle_font = pygame.font.Font(None, 17)
        self.soundtrack = Soundtrack()
        (
            self.high_score,
            self.tutorial_completed,
            self.difficulty_name,
            self.volume_percent,
            self.touch_controls_enabled,
        ) = self._load_save_data()
        self.soundtrack.set_volume(self.volume_percent / 100)
        self.route_index = 0
        self._make_buttons()
        self._make_cityscape()
        self.reset_round()
        self.elapsed_time = 0.0
        self.background_offset = 0.0

    def _make_buttons(self) -> None:
        center_x = SCREEN_WIDTH // 2
        self.play_button = pygame.Rect(center_x - 175, 382, 170, 54)
        self.settings_button = pygame.Rect(center_x + 5, 382, 170, 54)
        self.route_previous_button = pygame.Rect(center_x - 145, 265, 48, 48)
        self.route_button = pygame.Rect(center_x - 87, 265, 174, 48)
        self.route_next_button = pygame.Rect(center_x + 97, 265, 48, 48)
        self.settings_volume_down_button = pygame.Rect(center_x - 145, 245, 54, 48)
        self.settings_volume_up_button = pygame.Rect(center_x + 91, 245, 54, 48)
        self.settings_difficulty_button = pygame.Rect(center_x - 145, 323, 290, 48)
        self.settings_touch_button = pygame.Rect(center_x - 145, 395, 290, 48)
        self.settings_back_button = pygame.Rect(center_x - 115, 465, 230, 52)
        self.tutorial_start_button = pygame.Rect(center_x - 145, 420, 290, 54)
        self.resume_button = pygame.Rect(center_x - 115, 325, 230, 58)
        self.game_over_play_button = pygame.Rect(center_x - 115, 390, 230, 54)
        self.game_over_menu_button = pygame.Rect(center_x - 115, 452, 230, 48)
        self.menu_button = pygame.Rect(center_x - 115, 420, 230, 48)
        self.move_back_button = pygame.Rect(20, SCREEN_HEIGHT - 94, 116, 70)
        self.move_forward_button = pygame.Rect(144, SCREEN_HEIGHT - 94, 116, 70)
        self.jump_button = pygame.Rect(SCREEN_WIDTH - 166, SCREEN_HEIGHT - 106, 142, 82)
        self.touch_pause_button = pygame.Rect(SCREEN_WIDTH - 68, 136, 48, 48)

    def _make_cityscape(self) -> None:
        self.cityscapes: List[pygame.Surface] = []
        route = ROUTES[self.route_index]
        building_color, outline_color = route[5], route[6]
        for scene_index, _ in enumerate(SECTORS):
            scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            randomizer = random.Random(21 + scene_index)
            x = -10
            while x < SCREEN_WIDTH:
                width = randomizer.randint(56, 112)
                if scene_index == 0:
                    height = randomizer.randint(62, 126)
                    building = pygame.Rect(x, ROAD_TOP - height - 18, width, height)
                    pygame.draw.rect(scene, building_color, building)
                    pygame.draw.rect(scene, outline_color, building, 2)
                    for window_x in range(x + 9, x + width - 8, 18):
                        for window_y in range(building.y + 10, building.bottom - 8, 20):
                            pygame.draw.rect(scene, (238, 194, 122), (window_x, window_y, 7, 9))
                elif scene_index == 1:
                    height = randomizer.randint(36, 72)
                    building = pygame.Rect(x, ROAD_TOP - height - 18, width, height)
                    pygame.draw.rect(scene, building_color, building, border_radius=5)
                    pygame.draw.polygon(
                        scene,
                        outline_color,
                        ((x - 5, building.y + 5), (x + width // 2, building.y - 18),
                         (x + width + 5, building.y + 5)),
                    )
                    pygame.draw.rect(scene, (99, 70, 54), (x + width // 2 - 6, building.bottom - 25, 12, 25))
                    pygame.draw.circle(scene, (65, 110, 74), (x + width - 8, building.y + 4), 28)
                    pygame.draw.circle(scene, (78, 126, 78), (x + width - 24, building.y + 2), 22)
                else:
                    height = randomizer.randint(48, 84)
                    building = pygame.Rect(x, ROAD_TOP - height - 18, width, height)
                    pygame.draw.rect(scene, building_color, building)
                    pygame.draw.rect(scene, outline_color, building, 2)
                    awning_y = building.y + 12
                    for stripe_x in range(x + 4, x + width - 4, 16):
                        pygame.draw.polygon(
                            scene,
                            (236, 190, 100) if (stripe_x // 16) % 2 else (80, 139, 112),
                            ((stripe_x, awning_y), (stripe_x + 14, awning_y),
                             (stripe_x + 11, awning_y + 13), (stripe_x + 3, awning_y + 13)),
                        )
                x += width + randomizer.randint(12, 24)
            self.cityscapes.append(scene)

    def _load_save_data(self) -> Tuple[int, bool, str, int, bool]:
        try:
            data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return 0, False, "NORMAL", 100, True
        except (OSError, json.JSONDecodeError) as error:
            print(f"Impossible de lire la sauvegarde ({SAVE_PATH.name}) : {error}", file=sys.stderr)
            return 0, False, "NORMAL", 100, True

        if not isinstance(data, dict):
            return 0, False, "NORMAL", 100, True
        score = data.get("high_score", 0)
        high_score = score if isinstance(score, int) and score >= 0 else 0
        tutorial_completed = data.get("tutorial_completed", False)
        saved_difficulty = data.get("difficulty", "NORMAL")
        difficulty_name = (
            saved_difficulty
            if isinstance(saved_difficulty, str) and saved_difficulty in DIFFICULTIES
            else "NORMAL"
        )
        saved_volume = data.get("volume_percent", 100)
        volume_percent = (
            max(0, min(100, int(saved_volume)))
            if isinstance(saved_volume, (int, float)) and not isinstance(saved_volume, bool)
            else 100
        )
        touch_controls_enabled = data.get("touch_controls_enabled", True)
        return (
            high_score,
            tutorial_completed is True,
            difficulty_name,
            volume_percent,
            touch_controls_enabled is not False,
        )

    def _save_progress(self) -> None:
        try:
            SAVE_PATH.write_text(
                json.dumps(
                    {
                        "high_score": self.high_score,
                        "tutorial_completed": self.tutorial_completed,
                        "difficulty": self.difficulty_name,
                        "volume_percent": self.volume_percent,
                        "touch_controls_enabled": self.touch_controls_enabled,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            print(f"Impossible de sauvegarder la progression ({SAVE_PATH.name}) : {error}", file=sys.stderr)

    def reset_round(self) -> None:
        self.player_x = float(PLAYER_X)
        self.player_y = float(GROUND_Y - PLAYER_HEIGHT)
        self.vertical_velocity = 0.0
        self.is_jumping = False
        self.jump_started_at_ms = 0
        self.double_jump_used = False
        self.flip_active = False
        self.flip_angle = 0.0
        self.obstacles: List[Obstacle] = []
        self.pickups: List[Pickup] = []
        self.particles: List[Particle] = []
        self.distance = 0.0
        self.coins = 0
        self.dodges = 0
        self.mission = Mission()
        self.mission_bonus = 0
        self.mission_banner_timer = 0.0
        self.sector_index = 0
        self.sector_banner_timer = 0.0
        self.wheel_angle = 0.0
        settings = DIFFICULTIES[self.difficulty_name]
        self.health = 1
        self.pickup_bonus = 0
        self.new_record = False
        self.speed = settings["start_speed"]
        self.spawn_timer = 0.0
        self.next_spawn = 1.35
        self.pickup_timer = 0.0
        self.next_pickup = 2.4
        self.road_offset = 0.0
        self.mouse_direction = 0
        self.touch_direction = 0

    def start_game(self) -> None:
        self.reset_round()
        self.state = GameState.PLAYING
        self.soundtrack.resume()

    def _start_from_menu(self) -> None:
        if self.tutorial_completed:
            self.start_game()
        else:
            self.state = GameState.TUTORIAL

    def _complete_tutorial(self) -> None:
        self.tutorial_completed = True
        self._save_progress()
        self.start_game()

    def jump(self) -> None:
        if self.state != GameState.PLAYING:
            return
        if not self.is_jumping:
            self.vertical_velocity = JUMP_VELOCITY
            self.is_jumping = True
            self.jump_started_at_ms = pygame.time.get_ticks()
            self.double_jump_used = False
            self.soundtrack.play_effect("jump")
        elif (
            not self.double_jump_used
            and pygame.time.get_ticks() - self.jump_started_at_ms <= DOUBLE_JUMP_WINDOW_MS
        ):
            self.vertical_velocity = JUMP_VELOCITY
            self.double_jump_used = True
            self.flip_active = True
            self.flip_angle = 0.0
            self.soundtrack.play_effect("jump")
            self._emit_particles(self.player_x + 50, self.player_y + PLAYER_HEIGHT, (255, 211, 111), 12)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == GameState.PLAYING:
                if self.move_back_button.collidepoint(event.pos):
                    self.mouse_direction = -1
                elif self.move_forward_button.collidepoint(event.pos):
                    self.mouse_direction = 1
            return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_direction = 0
            if self.state == GameState.MENU:
                if self.play_button.collidepoint(event.pos):
                    self._start_from_menu()
                elif self.settings_button.collidepoint(event.pos):
                    self.state = GameState.SETTINGS
                elif self.route_previous_button.collidepoint(event.pos):
                    self._cycle_route(-1)
                elif self.route_button.collidepoint(event.pos) or self.route_next_button.collidepoint(event.pos):
                    self._cycle_route(1)
            elif self.state == GameState.TUTORIAL:
                if self.tutorial_start_button.collidepoint(event.pos):
                    self._complete_tutorial()
            elif self.state == GameState.SETTINGS:
                if self.settings_volume_down_button.collidepoint(event.pos):
                    self._change_volume(-10)
                elif self.settings_volume_up_button.collidepoint(event.pos):
                    self._change_volume(10)
                elif self.settings_difficulty_button.collidepoint(event.pos):
                    self._cycle_difficulty()
                elif self.settings_touch_button.collidepoint(event.pos):
                    self._toggle_touch_controls()
                elif self.settings_back_button.collidepoint(event.pos):
                    self.state = GameState.MENU
            elif self.state == GameState.PAUSED:
                if self.resume_button.collidepoint(event.pos):
                    self.state = GameState.PLAYING
                elif self.menu_button.collidepoint(event.pos):
                    self.state = GameState.MENU
            elif self.state == GameState.GAME_OVER:
                if self.game_over_play_button.collidepoint(event.pos):
                    self.start_game()
                elif self.game_over_menu_button.collidepoint(event.pos):
                    self.state = GameState.MENU
            elif self.state == GameState.PLAYING:
                if self.move_back_button.collidepoint(event.pos) or self.move_forward_button.collidepoint(event.pos):
                    pass
                elif self.touch_pause_button.collidepoint(event.pos):
                    self.state = GameState.PAUSED
                else:
                    self.jump()
            return True
        if event.type == pygame.FINGERDOWN:
            touch_position = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
            if self.state == GameState.PLAYING:
                if self.touch_controls_enabled and self.move_back_button.collidepoint(touch_position):
                    self.touch_direction = -1
                elif self.touch_controls_enabled and self.move_forward_button.collidepoint(touch_position):
                    self.touch_direction = 1
                elif self.touch_pause_button.collidepoint(touch_position):
                    self.state = GameState.PAUSED
                else:
                    self.jump()
                return True
            return self.handle_event(pygame.event.Event(
                pygame.MOUSEBUTTONUP,
                {"button": 1, "pos": touch_position},
            ))
        if event.type == pygame.FINGERUP:
            self.touch_direction = 0
            return True

        if event.type != pygame.KEYDOWN:
            return True

        if event.key == pygame.K_ESCAPE:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
            elif self.state == GameState.TUTORIAL:
                self.state = GameState.MENU
            elif self.state == GameState.SETTINGS:
                self.state = GameState.MENU
            elif self.state == GameState.MENU:
                return False
        elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.state == GameState.MENU:
                self._start_from_menu()
            elif self.state == GameState.TUTORIAL:
                self._complete_tutorial()
            elif self.state == GameState.SETTINGS:
                self.state = GameState.MENU
            elif self.state == GameState.GAME_OVER:
                self.start_game()
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
            else:
                self.jump()
        elif event.key in (pygame.K_UP, pygame.K_w) and self.state == GameState.PLAYING:
            self.jump()
        elif event.key in (pygame.K_LEFT, pygame.K_a) and self.state == GameState.PLAYING:
            self.player_x = max(20.0, self.player_x - 48.0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.state == GameState.PLAYING:
            self.player_x = min(SCREEN_WIDTH - PLAYER_WIDTH - 20.0, self.player_x + 48.0)
        elif event.key == pygame.K_p:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
        elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
            self.start_game()
        elif event.key == pygame.K_q and self.state == GameState.MENU:
            return False
        elif event.key == pygame.K_d and self.state == GameState.MENU:
            self._cycle_difficulty()
        elif event.key == pygame.K_d and self.state == GameState.SETTINGS:
            self._cycle_difficulty()
        elif event.key == pygame.K_t and self.state == GameState.SETTINGS:
            self._toggle_touch_controls()
        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS) and self.state == GameState.SETTINGS:
            self._change_volume(10)
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS) and self.state == GameState.SETTINGS:
            self._change_volume(-10)
        elif event.key == pygame.K_LEFT and self.state == GameState.MENU:
            self._cycle_route(-1)
        elif event.key == pygame.K_RIGHT and self.state == GameState.MENU:
            self._cycle_route(1)
        elif event.key == pygame.K_m:
            self.soundtrack.toggle()
        return True

    def _cycle_difficulty(self) -> None:
        options = list(DIFFICULTIES)
        index = (options.index(self.difficulty_name) + 1) % len(options)
        self.difficulty_name = options[index]
        self._save_progress()

    def _change_volume(self, amount: int) -> None:
        self.volume_percent = max(0, min(100, self.volume_percent + amount))
        self.soundtrack.set_volume(self.volume_percent / 100)
        self._save_progress()

    def _toggle_touch_controls(self) -> None:
        self.touch_controls_enabled = not self.touch_controls_enabled
        self.touch_direction = 0
        self._save_progress()

    def _cycle_route(self, direction: int) -> None:
        unlocked_count = self._unlocked_route_count()
        self.route_index = (self.route_index + direction) % unlocked_count
        self.soundtrack.set_route(self.route_index)
        self._make_cityscape()

    def _unlocked_route_count(self) -> int:
        return max(1, sum(self.high_score >= threshold for threshold in ROUTE_UNLOCK_SCORES))

    def update(self, delta_time: float) -> None:
        self.elapsed_time += delta_time
        self.particles = [particle for particle in self.particles if particle.life > 0]
        for particle in self.particles:
            particle.update(delta_time)
        self.mission_banner_timer = max(0.0, self.mission_banner_timer - delta_time)
        self.sector_banner_timer = max(0.0, self.sector_banner_timer - delta_time)
        if self.state != GameState.PLAYING:
            return

        keyboard = pygame.key.get_pressed()
        keyboard_direction = int(keyboard[pygame.K_RIGHT] or keyboard[pygame.K_d]) - int(
            keyboard[pygame.K_LEFT] or keyboard[pygame.K_a]
        )
        move_direction = max(-1, min(1, keyboard_direction + self.mouse_direction + self.touch_direction))
        self.player_x = max(
            20.0,
            min(
                SCREEN_WIDTH - PLAYER_WIDTH - 20.0,
                self.player_x + move_direction * PLAYER_MOVE_SPEED * delta_time,
            ),
        )

        self.distance += self.speed * delta_time / 10
        new_sector = int(self.distance // 700) % len(SECTORS)
        if new_sector != self.sector_index:
            self.sector_index = new_sector
            self.sector_banner_timer = 2.5
        settings = DIFFICULTIES[self.difficulty_name]
        self.speed = min(settings["max_speed"], settings["start_speed"] + self.distance * 0.55)
        self.wheel_angle = (self.wheel_angle + self.speed * delta_time / 14) % math.tau
        self.road_offset = (self.road_offset + self.speed * delta_time) % 88
        self.background_offset = (self.background_offset + self.speed * delta_time * 0.12) % SCREEN_WIDTH
        if self.flip_active:
            self.flip_angle += math.tau * delta_time / 0.55
            if self.flip_angle >= math.tau:
                self.flip_angle = 0.0
                self.flip_active = False
        if self.is_jumping:
            self.player_y += self.vertical_velocity * delta_time
            self.vertical_velocity += GRAVITY * delta_time
            if self.player_y >= GROUND_Y - PLAYER_HEIGHT:
                self.player_y = float(GROUND_Y - PLAYER_HEIGHT)
                self.vertical_velocity = 0.0
                self.is_jumping = False
                self.flip_active = False
                self.flip_angle = 0.0
                self._emit_particles(self.player_x + 48, GROUND_Y - 5, SAND, 7)

        self.spawn_timer += delta_time
        if self.spawn_timer >= self.next_spawn:
            self.obstacles.append(Obstacle(random.choices(
                ["trou", "dos_dane", "sotrama", "pierre", "barriere", "bidon"],
                weights=[3, 3, 2, 2, 2, 2],
                k=1,
            )[0], SCREEN_WIDTH + 30))
            self.spawn_timer = 0.0
            self.next_spawn = random.uniform(*settings["spawn"]) * (settings["start_speed"] / self.speed) ** 0.2

        self.pickup_timer += delta_time
        if self.pickup_timer >= self.next_pickup:
            kind = "bonus" if random.random() < 0.18 else "coin"
            self.pickups.append(Pickup(kind, SCREEN_WIDTH + 25, random.choice((GROUND_Y - 42, GROUND_Y - 150))))
            self.pickup_timer = 0.0
            self.next_pickup = random.uniform(2.5, 4.0)

        player_hitbox = pygame.Rect(
            int(self.player_x) + 17,
            int(self.player_y + 22),
            PLAYER_WIDTH - 34,
            PLAYER_HEIGHT - 28,
        )
        for obstacle in self.obstacles[:]:
            obstacle.x -= self.speed * delta_time
            if obstacle.hitbox.colliderect(player_hitbox):
                self.health = 0
                self.soundtrack.play_effect("hit")
                self._emit_particles(self.player_x + 55, GROUND_Y - 28, (255, 133, 91), 18)
                self._finish_round()
                return
            if obstacle.x + obstacle.width < 0:
                if obstacle in self.obstacles:
                    self.obstacles.remove(obstacle)
                    self.dodges += 1

        for pickup in self.pickups[:]:
            pickup.x -= self.speed * delta_time
            if pickup.hitbox.colliderect(player_hitbox):
                if pickup.kind == "coin":
                    self.coins += 1
                    self.soundtrack.play_effect("coin")
                    self._emit_particles(pickup.x, pickup.y, (255, 213, 82), 10)
                else:
                    self.pickup_bonus += 100
                    self.soundtrack.play_effect("coin")
                    self._emit_particles(pickup.x, pickup.y, (255, 213, 82), 12)
                self.pickups.remove(pickup)
            elif pickup.x + pickup.radius < 0:
                self.pickups.remove(pickup)

        if self.mission.update(self.distance, self.coins, self.dodges):
            self.mission_bonus = MISSION_REWARD
            self.mission_banner_timer = 3.0
            self.soundtrack.play_effect("coin")
            self._emit_particles(self.player_x + 50, GROUND_Y - 35, (255, 213, 82), 24)

    def _emit_particles(self, x: float, y: float, color: Color, count: int) -> None:
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(55, 210)
            self.particles.append(Particle(
                x,
                y,
                color,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 55,
            ))

    def _finish_round(self) -> None:
        self.state = GameState.GAME_OVER
        self.soundtrack.stop()
        final_score = self.score
        if final_score > self.high_score:
            self.high_score = final_score
            self.new_record = True
            self._save_progress()

    def draw(self) -> None:
        self._draw_world()
        self._draw_obstacles()
        self._draw_pickups()
        self._draw_particles()
        self._draw_motorcycle()
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.TUTORIAL:
            self._draw_tutorial()
        elif self.state == GameState.SETTINGS:
            self._draw_settings()
        elif self.state == GameState.PLAYING:
            self._draw_hud()
            self._draw_mission_card()
            if self.mission_banner_timer > 0:
                self._draw_mission_banner()
            elif self.sector_banner_timer > 0:
                self._draw_sector_banner()
        elif self.state == GameState.PAUSED:
            self._draw_hud()
            self._draw_mission_card()
            self._draw_pause()
        elif self.state == GameState.GAME_OVER:
            self._draw_hud()
            self._draw_game_over()
        self._draw_music_status()
        if self.state == GameState.PLAYING:
            self._draw_steering_buttons()
            self._draw_jump_button()
            self._draw_touch_pause_button()
        pygame.display.flip()

    def _draw_world(self) -> None:
        route = ROUTES[self.route_index]
        self.screen.fill(route[1])
        pygame.draw.circle(self.screen, (255, 220, 137), (790, 110), 58)
        pygame.draw.ellipse(self.screen, route[2], (-160, 275, 740, 270))
        pygame.draw.ellipse(self.screen, tuple(max(0, channel - 18) for channel in route[2]), (360, 298, 800, 255))
        cityscape = self.cityscapes[self.sector_index]
        self.screen.blit(cityscape, (-int(self.background_offset), 0))
        self.screen.blit(cityscape, (SCREEN_WIDTH - int(self.background_offset), 0))
        style = route[7]
        ground_color = route[2]
        road_color = route[3]
        marking_color = route[4]
        pygame.draw.rect(self.screen, ground_color, (0, ROAD_TOP - 18, SCREEN_WIDTH, 18))
        pygame.draw.rect(self.screen, road_color, (0, ROAD_TOP, SCREEN_WIDTH, SCREEN_HEIGHT - ROAD_TOP))
        pygame.draw.line(
            self.screen,
            tuple(min(255, channel + 24) for channel in road_color),
            (0, ROAD_TOP + 2),
            (SCREEN_WIDTH, ROAD_TOP + 2),
            3,
        )
        pygame.draw.rect(
            self.screen,
            tuple(max(0, channel - 20) for channel in road_color),
            (0, ROAD_TOP + 162, SCREEN_WIDTH, 8),
        )

        offset = int(self.road_offset)
        if style == "city":
            for x in range(-88, SCREEN_WIDTH + 88, 88):
                pygame.draw.rect(self.screen, marking_color, (x - offset, ROAD_TOP + 83, 46, 7), border_radius=3)
            pygame.draw.line(self.screen, (197, 190, 169), (0, ROAD_TOP + 8), (SCREEN_WIDTH, ROAD_TOP + 8), 2)
        elif style == "dirt":
            for index, x in enumerate(range(-72, SCREEN_WIDTH + 72, 72)):
                mark_x = x - offset
                pygame.draw.line(self.screen, (119, 91, 66), (mark_x, ROAD_TOP + 32 + (index % 3) * 42),
                                 (mark_x + 24, ROAD_TOP + 28 + (index % 3) * 42), 3)
                pygame.draw.circle(self.screen, marking_color, (mark_x + 48, ROAD_TOP + 120), 2)
        elif style == "market":
            for x in range(-132, SCREEN_WIDTH + 132, 132):
                mark_x = x - offset
                for stripe in range(6):
                    pygame.draw.polygon(
                        self.screen,
                        (232, 220, 193),
                        ((mark_x + stripe * 20, ROAD_TOP + 82), (mark_x + stripe * 20 + 13, ROAD_TOP + 82),
                         (mark_x + stripe * 20 + 21, ROAD_TOP + 110), (mark_x + stripe * 20 + 8, ROAD_TOP + 110)),
                    )
            pygame.draw.line(self.screen, marking_color, (0, ROAD_TOP + 28), (SCREEN_WIDTH, ROAD_TOP + 28), 3)
            pygame.draw.line(self.screen, marking_color, (0, ROAD_TOP + 145), (SCREEN_WIDTH, ROAD_TOP + 145), 3)
        elif style == "river":
            for y in (ROAD_TOP + 42, ROAD_TOP + 142):
                pygame.draw.line(self.screen, (229, 232, 216), (0, y), (SCREEN_WIDTH, y), 3)
            for x in range(-100, SCREEN_WIDTH + 100, 100):
                pygame.draw.circle(self.screen, marking_color, (x - offset, ROAD_TOP + 92), 4)
        elif style == "mountain":
            for x in range(-104, SCREEN_WIDTH + 104, 104):
                mark_x = x - offset
                pygame.draw.rect(self.screen, marking_color, (mark_x, ROAD_TOP + 82, 53, 6), border_radius=3)
                pygame.draw.line(self.screen, (205, 205, 192), (mark_x + 3, ROAD_TOP + 14),
                                 (mark_x + 20, ROAD_TOP + 32), 3)
                pygame.draw.line(self.screen, (205, 205, 192), (mark_x + 25, ROAD_TOP + 32),
                                 (mark_x + 46, ROAD_TOP + 10), 3)
            self._draw_roadside_blocks(offset, marking_color)
        elif style == "highway":
            for y in (ROAD_TOP + 12, ROAD_TOP + 112):
                pygame.draw.line(self.screen, (229, 225, 210), (0, y), (SCREEN_WIDTH, y), 3)
            for x in range(-96, SCREEN_WIDTH + 96, 96):
                mark_x = x - offset
                pygame.draw.rect(self.screen, marking_color, (mark_x, ROAD_TOP + 58, 52, 5), border_radius=2)
                pygame.draw.rect(self.screen, marking_color, (mark_x + 22, ROAD_TOP + 74, 52, 5), border_radius=2)
        elif style == "red_dirt":
            for x in range(-120, SCREEN_WIDTH + 120, 120):
                mark_x = x - offset
                pygame.draw.line(self.screen, (125, 76, 59), (mark_x, ROAD_TOP + 38),
                                 (mark_x + 64, ROAD_TOP + 63), 5)
                pygame.draw.line(self.screen, (125, 76, 59), (mark_x + 35, ROAD_TOP + 119),
                                 (mark_x + 94, ROAD_TOP + 92), 5)
        elif style == "night":
            for x in range(-64, SCREEN_WIDTH + 64, 64):
                mark_x = x - offset
                pygame.draw.circle(self.screen, (94, 204, 255), (mark_x, ROAD_TOP + 8), 4)
                pygame.draw.circle(self.screen, (94, 204, 255), (mark_x + 32, ROAD_TOP + 154), 4)
            for x in range(-92, SCREEN_WIDTH + 92, 92):
                pygame.draw.rect(self.screen, marking_color, (x - offset, ROAD_TOP + 82, 36, 5), border_radius=2)
        elif style == "plains":
            pygame.draw.line(self.screen, (177, 183, 150), (0, ROAD_TOP + 6), (SCREEN_WIDTH, ROAD_TOP + 6), 3)
            pygame.draw.line(self.screen, (177, 183, 150), (0, ROAD_TOP + 156), (SCREEN_WIDTH, ROAD_TOP + 156), 3)
            for x in range(-112, SCREEN_WIDTH + 112, 112):
                mark_x = x - offset
                pygame.draw.rect(self.screen, marking_color, (mark_x, ROAD_TOP + 80, 18, 5), border_radius=2)
                pygame.draw.rect(self.screen, marking_color, (mark_x + 45, ROAD_TOP + 80, 18, 5), border_radius=2)
                pygame.draw.rect(self.screen, marking_color, (mark_x + 90, ROAD_TOP + 80, 18, 5), border_radius=2)
        else:
            for x in range(-144, SCREEN_WIDTH + 144, 144):
                mark_x = x - offset
                pygame.draw.line(self.screen, (157, 127, 91), (mark_x, ROAD_TOP + 30),
                                 (mark_x + 45, ROAD_TOP + 44), 3)
                pygame.draw.line(self.screen, (157, 127, 91), (mark_x + 58, ROAD_TOP + 48),
                                 (mark_x + 116, ROAD_TOP + 29), 3)
                pygame.draw.line(self.screen, marking_color, (mark_x + 12, ROAD_TOP + 84),
                                 (mark_x + 45, ROAD_TOP + 84), 4)
                pygame.draw.line(self.screen, marking_color, (mark_x + 74, ROAD_TOP + 84),
                                 (mark_x + 107, ROAD_TOP + 84), 4)

    def _draw_roadside_blocks(self, offset: int, color: Color) -> None:
        for x in range(-96, SCREEN_WIDTH + 96, 96):
            block_x = x - offset
            pygame.draw.rect(self.screen, color, (block_x, ROAD_TOP - 18, 42, 14))
            pygame.draw.rect(self.screen, WHITE, (block_x + 42, ROAD_TOP - 18, 42, 14))

    def _draw_obstacles(self) -> None:
        for obstacle in self.obstacles:
            obstacle.draw(self.screen, self.obstacle_font)

    def _draw_pickups(self) -> None:
        for pickup in self.pickups:
            pickup.draw(self.screen, self.elapsed_time)

    def _draw_particles(self) -> None:
        for particle in self.particles:
            particle.draw(self.screen)

    def _draw_motorcycle(self) -> None:
        bike = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT + 8), pygame.SRCALPHA)
        x = int(self.player_x)
        suspension_bob = 0
        if self.state == GameState.PLAYING and not self.is_jumping:
            suspension_bob = round(math.sin(self.elapsed_time * 18) * 2)
        y = suspension_bob
        wheel_y = y + 54
        for wheel_x in (x + 25, x + 78):
            local_wheel_x = wheel_x - x
            pygame.draw.circle(bike, INK, (local_wheel_x, wheel_y), 14)
            pygame.draw.circle(bike, (176, 178, 177), (local_wheel_x, wheel_y), 7)
            for spoke in range(4):
                angle = self.wheel_angle + spoke * math.pi / 2
                spoke_end = (
                    round(local_wheel_x + math.cos(angle) * 11),
                    round(wheel_y + math.sin(angle) * 11),
                )
                pygame.draw.line(bike, (211, 215, 211), (local_wheel_x, wheel_y), spoke_end, 2)
            pygame.draw.circle(bike, (75, 75, 77), (local_wheel_x, wheel_y), 2)
        pygame.draw.line(bike, (207, 211, 205), (25, wheel_y), (49, y + 37), 5)
        pygame.draw.line(bike, (207, 211, 205), (49, y + 37), (78, wheel_y), 5)
        pygame.draw.line(bike, (207, 211, 205), (49, y + 37), (58, y + 51), 4)
        pygame.draw.ellipse(bike, RED, (37, y + 24, 39, 19))
        pygame.draw.rect(bike, (229, 189, 54), (68, y + 28, 14, 8), border_radius=3)
        pygame.draw.line(bike, INK, (70, y + 26), (85, y + 20), 4)
        pygame.draw.line(bike, INK, (42, y + 28), (34, y + 17), 4)
        pygame.draw.circle(bike, (43, 55, 69), (59, y + 12), 12)
        pygame.draw.arc(bike, (234, 192, 69), (48, y + 1, 23, 23), 3.2, 6.2, 4)
        pygame.draw.line(bike, WHITE, (48, y + 44), (57, y + 43), 3)
        if self.flip_active:
            bike = pygame.transform.rotate(bike, -math.degrees(self.flip_angle))
            bike_rect = bike.get_rect(
                center=(round(self.player_x + PLAYER_WIDTH / 2), round(self.player_y + PLAYER_HEIGHT / 2))
            )
            self.screen.blit(bike, bike_rect)
        else:
            self.screen.blit(bike, (round(self.player_x), round(self.player_y)))

    def _draw_hud(self) -> None:
        self._draw_panel(pygame.Rect(22, 20, 265, 106))
        self._draw_text(f"SCORE  {self.score:05d}", self.body_font, WHITE, (42, 32))
        self._draw_text(f"DISTANCE  {int(self.distance):04d} m", self.small_font, (236, 210, 159), (43, 62))
        self._draw_text(f"RECORD  {self.high_score:05d}", self.small_font, (236, 210, 159), (43, 87))
        for heart in range(1):
            center = (SCREEN_WIDTH - 208 + heart * 25, 94)
            color = (244, 83, 81) if heart < self.health else (104, 87, 84)
            self._draw_heart(center, color)
        self._draw_text("1 VIE", self.small_font, WHITE, (SCREEN_WIDTH - 177, 85))
        self._draw_panel(pygame.Rect(SCREEN_WIDTH - 208, 20, 186, 52))
        base_speed = DIFFICULTIES[self.difficulty_name]["start_speed"]
        displayed_speed = int(self.speed / base_speed * 60)
        self._draw_text(f"{displayed_speed} km/h", self.body_font, WHITE, (SCREEN_WIDTH - 189, 33))

    def _draw_mission_card(self) -> None:
        card = pygame.Rect(310, 20, 420, 92)
        self._draw_panel(card)
        title = "MISSION TERMINEE" if self.mission.completed else "OBJECTIF DE COURSE"
        self._draw_text(title, self.small_font, (255, 211, 111), (330, 31))
        self._draw_text(
            f"ROUTE {self.route_index + 1:02d}/{len(ROUTES)}",
            self.small_font,
            (255, 211, 111),
            (606, 31),
        )
        self._draw_text(self.mission.title, self.body_font, WHITE, (330, 53))
        progress = self.mission.progress / self.mission.target
        bar = pygame.Rect(330, 87, 378, 8)
        pygame.draw.rect(self.screen, (75, 68, 65), bar, border_radius=4)
        if progress > 0:
            fill = bar.copy()
            fill.width = max(8, int(bar.width * min(progress, 1.0)))
            pygame.draw.rect(self.screen, (255, 196, 72), fill, border_radius=4)
        amount = self.body_font.render(
            f"{self.mission.progress}/{self.mission.target}",
            True,
            WHITE,
        )
        self.screen.blit(amount, amount.get_rect(topright=(708, 55)))

    def _draw_mission_banner(self) -> None:
        self._draw_panel(pygame.Rect(300, 151, 360, 66), alpha=232)
        self._draw_text_center("OBJECTIF ACCOMPLI  +250", self.body_font, (255, 218, 119), 184)

    def _draw_sector_banner(self) -> None:
        self._draw_panel(pygame.Rect(330, 151, 300, 56), alpha=220)
        self._draw_text_center(SECTORS[self.sector_index][0], self.body_font, WHITE, 179)

    def _draw_menu(self) -> None:
        self._draw_panel(pygame.Rect(174, 70, SCREEN_WIDTH - 348, 485), alpha=216)
        title = self.title_font.render("MOTO BAMAKO", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 144)))
        subtitle = self.body_font.render("La route est longue. Garde l'equilibre.", True, (244, 211, 158))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 197)))
        self._draw_text_center(f"RECORD PERSONNEL  {self.high_score:05d} points", self.small_font, WHITE, 232)
        self._draw_button(self.route_previous_button, "<", subdued=True)
        self._draw_button(self.route_button, f"ROUTE {self.route_index + 1:02d} / {len(ROUTES)}", subdued=True)
        self._draw_button(self.route_next_button, ">", subdued=True)
        self._draw_button(self.play_button, "JOUER")
        self._draw_button(self.settings_button, "REGLAGES", subdued=True)
        self._draw_text_center(ROUTES[self.route_index][0], self.small_font, (255, 211, 111), 454)
        unlocked_count = self._unlocked_route_count()
        self._draw_text_center(f"ROUTES DEBLOQUEES : {unlocked_count}/{len(ROUTES)}", self.small_font, WHITE, 477)
        if unlocked_count < len(ROUTES):
            next_route = unlocked_count
            next_score = ROUTE_UNLOCK_SCORES[next_route]
            progress = max(0, next_score - self.high_score)
            route_status = f"Prochaine : {ROUTES[next_route][0]} dans {progress} points"
        else:
            route_status = "Toutes les routes sont debloquees !"
        self._draw_text_center(route_status, self.small_font, (255, 211, 111), 499)
        self._draw_text_center("Fleches gauche / droite pour choisir une route debloquee", self.small_font, WHITE, 521)
        self._draw_text_center("ESPACE / ENTREE pour jouer   •   M musique   •   Q quitter", self.small_font, WHITE, 543)

    def _draw_settings(self) -> None:
        self._draw_panel(pygame.Rect(174, 70, SCREEN_WIDTH - 348, 485), alpha=232)
        self._draw_text_center("REGLAGES", self.title_font, WHITE, 145)
        self._draw_text_center("VOLUME DE LA MUSIQUE ET DES EFFETS", self.body_font, (255, 211, 111), 197)
        self._draw_button(self.settings_volume_down_button, "-", subdued=True)
        self._draw_button(self.settings_volume_up_button, "+", subdued=True)
        volume_bar = pygame.Rect(SCREEN_WIDTH // 2 - 62, 264, 124, 10)
        pygame.draw.rect(self.screen, (75, 68, 65), volume_bar, border_radius=5)
        if self.volume_percent > 0:
            volume_fill = volume_bar.copy()
            volume_fill.width = max(1, int(volume_bar.width * self.volume_percent / 100))
            pygame.draw.rect(self.screen, (255, 196, 72), volume_fill, border_radius=5)
        self._draw_text_center(f"{self.volume_percent} %", self.body_font, WHITE, 285)
        self._draw_text_center("DIFFICULTE", self.body_font, (255, 211, 111), 319)
        self._draw_button(
            self.settings_difficulty_button,
            f"{self.difficulty_name}   (D)",
            subdued=True,
        )
        self._draw_text_center("COMMANDES DE DIRECTION SUR ECRAN TACTILE", self.body_font, (255, 211, 111), 380)
        touch_status = "DIRECTION TACTILE : ON" if self.touch_controls_enabled else "DIRECTION TACTILE : OFF"
        self._draw_button(self.settings_touch_button, touch_status, subdued=True)
        self._draw_text_center("Saut et pause tactiles restent toujours disponibles.", self.small_font, WHITE, 449)
        self._draw_button(self.settings_back_button, "RETOUR AU MENU")
        self._draw_text_center("- / + : volume   •   D : difficulte   •   T : commandes tactiles", self.small_font, WHITE, 532)

    def _draw_tutorial(self) -> None:
        self._draw_panel(pygame.Rect(174, 70, SCREEN_WIDTH - 348, 465), alpha=232)
        self._draw_text_center("BIENVENUE SUR LA ROUTE !", self.heading_font, WHITE, 139)
        self._draw_text_center("COMMANDES CLAVIER", self.body_font, (255, 211, 111), 204)
        self._draw_text_center("ESPACE ou FLECHE HAUT : sauter par-dessus les obstacles", self.small_font, WHITE, 239)
        self._draw_text_center("FLECHES GAUCHE / DROITE ou A / D : diriger la moto", self.small_font, WHITE, 270)
        self._draw_text_center("P ou ECHAP : mettre en pause", self.small_font, WHITE, 301)
        self._draw_text_center("COMMANDES TELEPHONE", self.body_font, (255, 211, 111), 344)
        self._draw_text_center("Maintiens RECULER ou AVANCER pour diriger", self.small_font, WHITE, 378)
        self._draw_text_center("Double saut : la moto fait un salto en l'air", self.small_font, WHITE, 405)
        self._draw_button(self.tutorial_start_button, "C'EST PARTI !")
        self._draw_text_center("Une collision termine la course. Les pieces rapportent des points.", self.small_font, WHITE, 496)
        self._draw_text_center("ENTREE / ESPACE pour jouer   •   ECHAP pour revenir au menu", self.small_font, WHITE, 520)

    def _draw_pause(self) -> None:
        self._draw_overlay()
        self._draw_text_center("PAUSE", self.title_font, WHITE, 240)
        self._draw_button(self.resume_button, "REPRENDRE")
        self._draw_button(self.menu_button, "MENU", subdued=True)
        self._draw_text_center("P / ECHAP pour reprendre", self.small_font, WHITE, 480)

    def _draw_game_over(self) -> None:
        self._draw_overlay()
        self._draw_text_center("FIN DE COURSE", self.title_font, (255, 222, 161), 230)
        self._draw_text_center(f"Score : {self.score} points", self.heading_font, WHITE, 294)
        mission_status = "Mission accomplie !" if self.mission.completed else f"Mission : {self.mission.progress}/{self.mission.target}"
        self._draw_text_center(mission_status, self.body_font, (255, 218, 119), 330)
        if self.new_record:
            self._draw_text_center("NOUVEAU RECORD !", self.body_font, (255, 220, 90), 363)
        self._draw_button(self.game_over_play_button, "REJOUER")
        self._draw_button(self.game_over_menu_button, "MENU", subdued=True)
        self._draw_text_center("ESPACE / R pour recommencer", self.small_font, WHITE, 529)

    @property
    def score(self) -> int:
        return int(self.distance) + self.coins * 25 + self.mission_bonus + self.pickup_bonus

    def _draw_heart(self, center: Tuple[int, int], color: Color) -> None:
        x, y = center
        pygame.draw.circle(self.screen, color, (x - 5, y - 3), 6)
        pygame.draw.circle(self.screen, color, (x + 5, y - 3), 6)
        pygame.draw.polygon(self.screen, color, ((x - 11, y), (x + 11, y), (x, y + 12)))

    def _draw_overlay(self) -> None:
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((20, 18, 18, 172))
        self.screen.blit(shade, (0, 0))

    def _draw_music_status(self) -> None:
        if self.soundtrack.sound is None:
            status = "MUSIQUE INDISPONIBLE"
        elif not self.soundtrack.enabled:
            status = "SON COUPE"
        elif not self.soundtrack.playing:
            status = "MUSIQUE ARRETEE"
        else:
            status = "MUSIQUE ACTIVE"
        position = (22, 136) if self.state == GameState.PLAYING else (22, SCREEN_HEIGHT - 30)
        self._draw_text(status, self.small_font, WHITE, position)

    def _draw_steering_buttons(self) -> None:
        if not self.touch_controls_enabled:
            return
        self._draw_button(self.move_back_button, "RECULER", subdued=True)
        self._draw_button(self.move_forward_button, "AVANCER")
        self._draw_text_center("MAINTENIR POUR DIRIGER", self.small_font, WHITE, SCREEN_HEIGHT - 112)

    def _draw_jump_button(self) -> None:
        pygame.draw.rect(self.screen, (50, 38, 32), self.jump_button.move(0, 4), border_radius=18)
        pygame.draw.rect(self.screen, (190, 58, 48), self.jump_button, border_radius=18)
        pygame.draw.rect(self.screen, (255, 226, 184), self.jump_button, width=2, border_radius=18)
        center_x = self.jump_button.centerx
        pygame.draw.polygon(
            self.screen,
            WHITE,
            ((center_x, self.jump_button.y + 13), (center_x - 13, self.jump_button.y + 31),
             (center_x - 5, self.jump_button.y + 31), (center_x - 5, self.jump_button.y + 41),
             (center_x + 5, self.jump_button.y + 41), (center_x + 5, self.jump_button.y + 31),
             (center_x + 13, self.jump_button.y + 31)),
        )
        label = self.small_font.render("SAUT X2 + SALTO", True, WHITE)
        self.screen.blit(label, label.get_rect(center=(center_x, self.jump_button.y + 61)))

    def _draw_touch_pause_button(self) -> None:
        pygame.draw.circle(self.screen, (39, 36, 36), self.touch_pause_button.center, 27)
        pygame.draw.circle(self.screen, (255, 238, 204), self.touch_pause_button.center, 27, 2)
        x, y = self.touch_pause_button.center
        pygame.draw.rect(self.screen, WHITE, (x - 7, y - 10, 5, 20), border_radius=2)
        pygame.draw.rect(self.screen, WHITE, (x + 2, y - 10, 5, 20), border_radius=2)

    def _draw_panel(self, rect: pygame.Rect, alpha: int = 205) -> None:
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (39, 36, 36, alpha), panel.get_rect(), border_radius=18)
        pygame.draw.rect(panel, (255, 238, 204, 45), panel.get_rect(), width=1, border_radius=18)
        self.screen.blit(panel, rect)

    def _draw_button(self, rect: pygame.Rect, label: str, subdued: bool = False) -> None:
        color = (108, 74, 49) if subdued else RED
        pygame.draw.rect(self.screen, (70, 45, 36), rect.move(0, 4), border_radius=12)
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 231, 195), rect, width=2, border_radius=12)
        text = self.body_font.render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw_text(self, text: str, font: pygame.font.Font, color: Color, position: Tuple[int, int]) -> None:
        self.screen.blit(font.render(text, True, color), position)

    def _draw_text_center(self, text: str, font: pygame.font.Font, color: Color, y: int) -> None:
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=(SCREEN_WIDTH // 2, y)))

    async def run(self) -> None:
        running = True
        while running:
            delta_time = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                running = self.handle_event(event) and running
            self.update(delta_time)
            self.draw()
            await asyncio.sleep(0)


async def main() -> None:
    game = MotoBamakoGame()
    try:
        await game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
