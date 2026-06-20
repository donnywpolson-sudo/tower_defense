from dataclasses import dataclass, field

from .config import STARTING_LIVES, STARTING_MONEY


@dataclass
class GameState:
    money: int = STARTING_MONEY
    lives: int = STARTING_LIVES
    score: int = 0
    research_points: int = 0
    wave: int = 1
    game_over: bool = False
    victory: bool = False
    paused: bool = False
    game_speed: float = 1.0
    current_map_index: int = 0
    spawn_path_index: int = 0
    spawn_timer: float = 0
    spawned_this_wave: int = 0
    wave_active: bool = False
    selected_build_type: str | None = None
    endless_mode: bool = False
    stars: int = 0
    starting_money_bonus_level: int = 0
    tower_damage_bonus_level: int = 0
    run_stars_awarded: bool = False
    screen_shake_timer: float = 0
    screen_shake_strength: float = 0
    boss_warning_timer: float = 0
    enemies: list = field(default_factory=list)
    towers: list = field(default_factory=list)
    projectiles: list = field(default_factory=list)
    effects: list = field(default_factory=list)

    def reset_run(self):
        self.money = STARTING_MONEY + self.starting_money_bonus_level * 25
        self.lives = STARTING_LIVES
        self.score = 0
        self.research_points = 0
        self.wave = 1
        self.game_over = False
        self.victory = False
        self.paused = False
        self.game_speed = 1.0
        self.spawn_path_index = 0
        self.spawn_timer = 0
        self.spawned_this_wave = 0
        self.wave_active = False
        self.selected_build_type = None
        self.endless_mode = False
        self.run_stars_awarded = False
        self.screen_shake_timer = 0
        self.screen_shake_strength = 0
        self.boss_warning_timer = 0
        self.enemies.clear()
        self.towers.clear()
        self.projectiles.clear()
        self.effects.clear()
