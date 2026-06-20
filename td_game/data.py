from .config import MAP_WIDTH


MAPS = [
    {
        "name": "Classic Road",
        "theme": "forest",
        "paths": [
            [(0, 297), (189, 297), (189, 135), (432, 135), (432, 432), (702, 432), (702, 216), (MAP_WIDTH, 216)],
        ],
    },
    {
        "name": "Split Road",
        "theme": "swamp",
        "paths": [
            [(0, 190), (210, 190), (210, 95), (520, 95), (520, 285), (MAP_WIDTH, 285)],
            [(0, 405), (250, 405), (250, 505), (610, 505), (610, 340), (MAP_WIDTH, 340)],
        ],
    },
    {
        "name": "Zigzag Road",
        "theme": "snow",
        "paths": [
            [(0, 135), (170, 135), (170, 465), (345, 465), (345, 180), (560, 180), (560, 430), (755, 430), (755, 245), (MAP_WIDTH, 245)],
        ],
    },
    {
        "name": "Spiral Road",
        "theme": "lava",
        "paths": [
            [(0, 300), (150, 300), (150, 120), (750, 120), (750, 480), (285, 480), (285, 240), (615, 240), (615, 360), (MAP_WIDTH, 360)],
        ],
    },
]

TOWER_UPGRADE_COSTS = {
    1: 75,
    2: 125,
    3: 175,
    4: 250,
}

SHOP_COSTS = {
    "archer": 50,
    "sniper": 90,
    "machine_gun": 70,
    "cannon": 90,
    "frost": 80,
    "tesla": 100,
    "poison": 85,
    "barracks": 85,
    "flame": 95,
    "mortar": 120,
    "support": 100,
    "gold": 110,
}

SHOP_TABS = {
    "Damage": ("archer", "sniper", "machine_gun", "cannon"),
    "Control": ("frost", "tesla", "poison"),
    "Military": ("barracks", "flame", "mortar"),
    "Utility": ("support", "gold"),
}

MASTERY_UPGRADE_COSTS = {
    5: 1000,
    6: 1800,
    7: 3000,
    8: 4500,
    9: 6500,
}

RESEARCH_UPGRADE_COSTS = {
    5: 10,
    6: 16,
    7: 24,
    8: 34,
    9: 46,
}

HIGH_TIER_MIN_TOWERS = {
    5: 2,
    6: 3,
    7: 4,
    8: 5,
    9: 6,
}

MUTATION_TRAITS = {
    "fast_hunter": {
        "label": "Fast Hunter",
        "short": "SPD",
        "description": "Bonus vs fast enemies; hits briefly slow them",
        "color": (235, 95, 190),
    },
    "armor_piercer": {
        "label": "Armor Piercer",
        "short": "AP",
        "description": "Bonus vs shields and armor; shield hits count as pierce",
        "color": (190, 195, 210),
    },
    "field_medic": {
        "label": "Field Medic",
        "short": "MED",
        "description": "Low-kill tower grants a small nearby damage/rate aura",
        "color": (150, 225, 145),
    },
    "corrupted": {
        "label": "Corrupted",
        "short": "COR",
        "description": "Earned in kill zones; bonus vs low-health enemies",
        "color": (170, 90, 210),
    },
    "swarm_reaper": {
        "label": "Swarm Reaper",
        "short": "SWM",
        "description": "Bonus vs swarm/split enemies with small cleave",
        "color": (240, 145, 85),
    },
    "sky_watcher": {
        "label": "Sky Watcher",
        "short": "AIR",
        "description": "Learns anti-air and deals bonus to flying enemies",
        "color": (165, 205, 255),
    },
}

TOWER_TYPES = {
    "archer": {
        "label": "Archer",
        "short": "A",
        "role": "Balanced single-target",
        "good_vs": "Normal waves and mixed pressure",
        "weakness": "No splash or special control",
        "color": (90, 180, 95),
        "range_color": (130, 220, 140),
        "projectile_color": (210, 160, 90),
        "tiers": {
            2: "Ranger Tower",
            3: "Longbow Tower",
            4: "Marksman Tower",
            5: "Elite Ranger",
        },
        "descriptions": {
            2: "Reliable arrows and balanced stats",
            3: "Longer range and stronger arrows",
            4: "Focused shots against priority targets",
            5: "Fast elite arrows with high range",
        },
        "paragon": "Windrunner Tower",
    },
    "sniper": {
        "label": "Sniper",
        "short": "S",
        "role": "Huge range, slow high damage",
        "good_vs": "Bosses, armor, and flying",
        "weakness": "Weak into large swarms",
        "color": (120, 150, 170),
        "range_color": (170, 205, 230),
        "projectile_color": (245, 245, 230),
        "tiers": {
            2: "Sniper Nest",
            3: "Armor Piercer",
            4: "Headshot Tower",
            5: "Deadeye Tower",
        },
        "descriptions": {
            2: "Very long range, slow heavy shots",
            3: "Pierces armor and shields better",
            4: "Headshots deal bonus damage",
            5: "Deadeye shots delete priority targets",
        },
        "paragon": "Rail Sniper",
    },
    "machine_gun": {
        "label": "Machine Gun",
        "short": "MG",
        "role": "Very fast, low damage",
        "good_vs": "Swarms and low-health enemies",
        "weakness": "Struggles against heavy armor",
        "color": (95, 115, 125),
        "range_color": (145, 165, 175),
        "projectile_color": (255, 225, 100),
        "tiers": {
            2: "Gatling Tower",
            3: "Twin Barrel",
            4: "Minigun Tower",
            5: "Bullet Storm",
        },
        "descriptions": {
            2: "Rapid shots, low damage per bullet",
            3: "Twin barrels increase fire rate",
            4: "Minigun fire shreds swarms",
            5: "Bullet Storm fires extremely fast",
        },
        "paragon": "Vulcan Tower",
    },
    "cannon": {
        "label": "Cannon",
        "short": "C",
        "role": "Slow splash damage",
        "good_vs": "Grouped enemies and tanks",
        "weakness": "Slow fire rate and no anti-air",
        "color": (150, 105, 70),
        "range_color": (200, 150, 95),
        "projectile_color": (80, 70, 60),
        "tiers": {
            2: "Cannon Tower",
            3: "Heavy Cannon",
            4: "Siege Cannon",
            5: "Earthshaker Cannon",
        },
        "descriptions": {
            2: "Explosive shots hit groups",
            3: "Bigger shells and wider splash",
            4: "Siege blasts weaken armor",
            5: "Huge area explosions",
        },
        "paragon": "Artillery Core",
    },
    "frost": {
        "label": "Frost",
        "short": "F",
        "role": "Slow and freeze control",
        "good_vs": "Fast enemies and boss control",
        "weakness": "Lower raw damage",
        "color": (90, 175, 225),
        "range_color": (150, 225, 255),
        "projectile_color": (175, 240, 255),
        "tiers": {
            2: "Frost Tower",
            3: "Ice Shard Tower",
            4: "Blizzard Tower",
            5: "Cryo Engine",
        },
        "descriptions": {
            2: "Slows enemies on hit",
            3: "Ice shards slow harder",
            4: "Blizzard slows nearby enemies",
            5: "Cryo hits briefly freeze targets",
        },
        "paragon": "Glacier Core",
    },
    "tesla": {
        "label": "Tesla",
        "short": "T",
        "role": "Chain lightning and anti-air",
        "good_vs": "Flying and clustered enemies",
        "weakness": "Higher cost, lower single hit",
        "color": (230, 210, 65),
        "range_color": (255, 235, 105),
        "projectile_color": (255, 245, 90),
        "tiers": {
            2: "Tesla Coil",
            3: "Chain Coil",
            4: "Storm Coil",
            5: "Thunder Engine",
        },
        "descriptions": {
            2: "Fast electric shots",
            3: "Chains to one extra enemy",
            4: "Chains to three and hits flying",
            5: "Extreme fire rate and stronger chain",
        },
        "paragon": "Storm Paragon",
    },
    "poison": {
        "label": "Poison",
        "short": "P",
        "role": "Damage over time",
        "good_vs": "Tanks, bosses, and long fights",
        "weakness": "Fast swarms can outrun the damage",
        "color": (105, 190, 85),
        "range_color": (150, 235, 125),
        "projectile_color": (125, 235, 95),
        "tiers": {
            2: "Venom Tower",
            3: "Toxic Spitter",
            4: "Plague Tower",
            5: "Bio Reactor",
        },
        "descriptions": {
            2: "Poisons enemies for damage over time",
            3: "Stronger poison lasts longer",
            4: "Poison spreads to nearby enemies",
            5: "Bio toxins melt high-health targets",
        },
        "paragon": "Venom Core",
    },
    "barracks": {
        "label": "Barracks",
        "short": "B",
        "role": "Guards slow enemies near path",
        "good_vs": "Ground lanes and slowing pushes",
        "weakness": "Cannot attack flying enemies",
        "color": (185, 145, 85),
        "range_color": (220, 185, 120),
        "projectile_color": (210, 180, 120),
        "tiers": {
            2: "Guard Post",
            3: "Veteran Guards",
            4: "Shield Wall",
            5: "Champion Barracks",
        },
        "descriptions": {
            2: "Guards slow nearby ground enemies",
            3: "Veterans hold enemies longer",
            4: "Shield wall weakens enemy damage taken",
            5: "Champions deal steady melee damage",
        },
        "paragon": "Fortress Gate",
    },
    "flame": {
        "label": "Flame",
        "short": "FL",
        "role": "Short-range burn damage",
        "good_vs": "Packed ground enemies",
        "weakness": "Short range and no anti-air",
        "color": (225, 95, 45),
        "range_color": (255, 145, 80),
        "projectile_color": (255, 120, 45),
        "tiers": {
            2: "Flame Tower",
            3: "Firestream",
            4: "Inferno Tower",
            5: "Dragon Furnace",
        },
        "descriptions": {
            2: "Burns enemies in close range",
            3: "Longer burn and hotter flame",
            4: "Inferno splash hits nearby ground",
            5: "Dragon fire leaves strong burn",
        },
        "paragon": "Sun Forge",
    },
    "mortar": {
        "label": "Mortar",
        "short": "MO",
        "role": "Huge range, slow splash",
        "good_vs": "Clustered enemies far away",
        "weakness": "Cannot hit close or flying enemies",
        "color": (115, 105, 90),
        "range_color": (195, 175, 135),
        "projectile_color": (105, 95, 80),
        "tiers": {
            2: "Mortar Pit",
            3: "Heavy Mortar",
            4: "Siege Mortar",
            5: "Bombardment Core",
        },
        "descriptions": {
            2: "Huge range with a minimum range",
            3: "Heavier shells and wider splash",
            4: "Siege blasts punish clusters",
            5: "Bombardment hits a large area",
        },
        "paragon": "Meteor Battery",
    },
    "support": {
        "label": "Support",
        "short": "SUP",
        "role": "Buffs nearby towers",
        "good_vs": "Dense tower clusters",
        "weakness": "Does not deal direct damage",
        "color": (200, 185, 105),
        "range_color": (245, 225, 145),
        "projectile_color": (245, 225, 145),
        "tiers": {
            2: "Banner Tower",
            3: "War Drum",
            4: "Command Post",
            5: "Battle Standard",
        },
        "descriptions": {
            2: "Nearby towers gain damage",
            3: "Adds fire-rate aura",
            4: "Adds range aura",
            5: "Stronger combined aura",
        },
        "paragon": "High Command",
    },
    "gold": {
        "label": "Gold",
        "short": "$",
        "role": "Weak damage plus bonus income",
        "good_vs": "Long games and early economy",
        "weakness": "Poor emergency damage",
        "color": (220, 180, 65),
        "range_color": (255, 220, 110),
        "projectile_color": (255, 220, 90),
        "tiers": {
            2: "Gold Tower",
            3: "Mint Tower",
            4: "Treasury Tower",
            5: "Royal Vault",
        },
        "descriptions": {
            2: "Weak shots and small income over time",
            3: "Minting improves income and range",
            4: "Treasury earns more during waves",
            5: "Royal Vault generates strong income",
        },
        "paragon": "Golden Engine",
    },
}


TARGET_MODES = ["first", "last", "strongest", "weakest", "closest", "flying"]
