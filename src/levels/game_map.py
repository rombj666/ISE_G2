class GameMap:
    def __init__(
        self,
        map_id,
        name,
        width,
        height,
        platforms,
        player_spawn,
        doors,
        enemy_spawns=None,
        boss_spawn=None,
        fulcrums=None,
        shop_rect=None,
        shop_slots=None,
        moving_platforms=None,
        checkpoints=None,
        interactables=None,
        hazards=None,
        map_type="normal_stage",
    ):
        self.map_id = map_id
        self.name = name
        self.width = width
        self.height = height
        self.platforms = platforms
        self.player_spawn = player_spawn
        self.doors = doors
        self.enemy_spawns = enemy_spawns or []
        self.boss_spawn = boss_spawn
        self.fulcrums = fulcrums or []
        self.shop_rect = shop_rect
        self.shop_slots = shop_slots or []
        self.moving_platforms = moving_platforms or []
        self.checkpoints = checkpoints or []
        self.interactables = interactables or []
        self.hazards = hazards or []
        self.map_type = map_type
