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

ROOT_TOWER_IDS = (
    "archer",
    "sniper",
    "machine_gun",
    "cannon",
    "frost",
    "tesla",
    "poison",
    "barracks",
    "support",
)

SHOP_TOWER_ORDER = (
    "machine_gun",
    "cannon",
    "frost",
    "poison",
    "support",
    "sniper",
    "tesla",
    "barracks",
)

BRANCH_UNLOCK_LEVEL = 3

LEGACY_TOWER_ALIASES = {
    "flame": ("cannon", "terraformer"),
    "mortar": ("cannon", "artillery"),
    "gold": ("support", "research_lab"),
}

FAMILY_INFO = {
    "archer": ("Ranger Family", "Flexible precision, traps, pets"),
    "sniper": ("Marksman Family", "Long-range deletion and target painting"),
    "machine_gun": ("Ballistics Family", "Fire-rate, ammo types, suppression"),
    "cannon": ("Siege Family", "Splash, armor break, terrain denial"),
    "frost": ("Cryo Family", "Slow, freeze, shatter, time control"),
    "tesla": ("Storm Family", "Chain lightning, energy, anti-air"),
    "poison": ("Venom Family", "Poison, burn, and spreading debuffs"),
    "barracks": ("Garrison Family", "Guards, engineers, mercenaries"),
    "support": ("Channeler Family", "Mana casts, buffs, and priority debuffs"),
}

BRANCH_DEFINITIONS = {
    "archer": {
        "deadeye": {
            "name": "Deadeye Rangers",
            "short": "DE",
            "role": "Marks enemies and pressures bosses",
            "effect_preview": "Marks targets; crits marked/boss enemies.",
            "mechanics": ("mark", "crit", "boss_pressure"),
            "tags": ("damage", "mark", "boss"),
            "color": (120, 230, 120),
            "tiers": {3: "Deadeye Rangers", 4: "Critline Patrol", 5: "Boss Stalkers"},
            "descriptions": {
                3: "Arrows mark enemies and focus priority targets",
                4: "Marked enemies take stronger critical hits",
                5: "Boss pressure and mark duration improve",
            },
        },
        "trapline": {
            "name": "Trapline Rangers",
            "short": "TR",
            "role": "Snares, nets, venom road traps",
            "effect_preview": "Poisons and slows enemies with trap shots.",
            "mechanics": ("trap", "poison", "slow", "anti_regen"),
            "tags": ("control", "poison", "trap"),
            "color": (125, 220, 95),
            "tiers": {3: "Trapline Rangers", 4: "Venom Netters", 5: "Wildwood Snareline"},
            "descriptions": {
                3: "Shots slow and poison enemies briefly",
                4: "Venom snares weaken swarms and regen enemies",
                5: "Trapline effects spread to nearby enemies",
            },
        },
        "beastmaster": {
            "name": "Beastmaster Rangers",
            "short": "BM",
            "role": "Pet-style extra hits and holds",
            "effect_preview": "Falcon/wolf strikes add periodic damage.",
            "mechanics": ("pet_hit", "hold", "assist"),
            "tags": ("weird", "pet", "assist"),
            "color": (175, 210, 105),
            "tiers": {3: "Beastmaster Rangers", 4: "Wolf Pack", 5: "Bearwarden Patrol"},
            "descriptions": {
                3: "Pet strikes add extra physical hits",
                4: "Wolf attacks briefly hold wounded enemies",
                5: "Bearwarden hits punish elites near the path",
            },
        },
    },
    "sniper": {
        "railgun": {
            "name": "Railgun Sniper",
            "short": "RG",
            "role": "Armor pierce and boss beams",
            "effect_preview": "Pierces armor and strips shields.",
            "mechanics": ("pierce", "shield_break", "boss_pressure"),
            "tags": ("damage", "pierce", "boss"),
            "color": (205, 230, 245),
            "tiers": {3: "Railgun Sniper", 4: "Coil Piercer", 5: "Rail Executor"},
            "descriptions": {
                3: "Shots pierce armor and shields better",
                4: "Rail beams expose damaged enemies",
                5: "Boss and shield damage increase sharply",
            },
        },
        "spotter": {
            "name": "Spotter Sniper",
            "short": "SP",
            "role": "Target paint and shared priority",
            "effect_preview": "Paints enemies for nearby towers.",
            "mechanics": ("paint", "shared_targeting", "marked_reward"),
            "tags": ("utility", "mark", "targeting"),
            "color": (170, 210, 245),
            "tiers": {3: "Spotter Sniper", 4: "Weak Point Team", 5: "Forward Observer"},
            "descriptions": {
                3: "Painted enemies are preferred by nearby towers",
                4: "Weak points increase allied damage",
                5: "Marked kills can grant tactical rewards",
            },
        },
        "time_lag": {
            "name": "Time-Lag Sniper",
            "short": "TL",
            "role": "Delayed damage and echo bullets",
            "effect_preview": "Stores bonus damage, then detonates.",
            "mechanics": ("delayed_damage", "echo", "detonate"),
            "tags": ("weird", "time", "burst"),
            "color": (190, 170, 245),
            "tiers": {3: "Time-Lag Sniper", 4: "Echo Bullet", 5: "Chrono Detonator"},
            "descriptions": {
                3: "Shots leave delayed echo damage",
                4: "Echo bullets detonate harder on marked enemies",
                5: "Stored damage bursts against priority enemies",
            },
        },
    },
    "machine_gun": {
        "vulcan": {
            "name": "Vulcan",
            "short": "VU",
            "role": "Spin-up fire-rate DPS",
            "effect_preview": "Continuous fire increases attack speed.",
            "mechanics": ("spin_up", "fire_rate", "dps"),
            "tags": ("damage", "rapid", "swarm"),
            "color": (255, 225, 90),
            "tiers": {3: "Vulcan", 4: "Rotary Engine", 5: "Bullet Tempest"},
            "descriptions": {
                3: "Sustained fire spins up attack speed",
                4: "Rotary fire shreds swarms",
                5: "Tempest rate peaks during long waves",
            },
        },
        "suppression": {
            "name": "Suppression",
            "short": "SU",
            "role": "Slows, pins, panic effects",
            "effect_preview": "Rapid hits briefly suppress enemies.",
            "mechanics": ("slow", "pin", "panic"),
            "tags": ("control", "rapid", "slow"),
            "color": (220, 205, 120),
            "tiers": {3: "Suppression Team", 4: "Pinning Fire", 5: "Panic Zone"},
            "descriptions": {
                3: "Bullets briefly slow fast enemies",
                4: "Pinning fire improves control duration",
                5: "Panic zones disrupt clustered pushes",
            },
        },
        "ammo_fabricator": {
            "name": "Ammo Fabricator",
            "short": "AF",
            "role": "Adaptive AP/toxic/incendiary rounds",
            "effect_preview": "Rounds adapt to armor, swarms, and regen.",
            "mechanics": ("adaptive_ammo", "poison", "burn", "pierce"),
            "tags": ("weird", "ammo", "poison", "burn"),
            "color": (185, 220, 135),
            "tiers": {3: "Ammo Fabricator", 4: "Tracer Foundry", 5: "Adaptive Arsenal"},
            "descriptions": {
                3: "Ammo adapts against armor and swarms",
                4: "Tracer rounds mark and weaken targets",
                5: "Toxic and incendiary rounds rotate in",
            },
        },
    },
    "cannon": {
        "artillery": {
            "name": "Artillery",
            "short": "AR",
            "role": "Mortar splash and bombardment",
            "effect_preview": "Long-range splash with cluster shells.",
            "mechanics": ("splash", "mortar", "cluster"),
            "tags": ("damage", "splash", "mortar"),
            "color": (205, 155, 95),
            "tiers": {3: "Artillery Battery", 4: "Cluster Shells", 5: "Map Bombardment"},
            "descriptions": {
                3: "Mortar-style splash and longer range",
                4: "Cluster shells hit wider groups",
                5: "Bombardment punishes dense waves",
            },
        },
        "demolition": {
            "name": "Demolition",
            "short": "DM",
            "role": "Armor crack and shield break",
            "effect_preview": "Explosions expose armored enemies.",
            "mechanics": ("armor_break", "shield_break", "vulnerable"),
            "tags": ("utility", "armor", "splash"),
            "color": (225, 125, 90),
            "tiers": {3: "Demolition Crew", 4: "Shield Cracker", 5: "Exposed Core"},
            "descriptions": {
                3: "Blast damage cracks armor",
                4: "Shield cracking improves splash damage",
                5: "Exposed enemies take more burst damage",
            },
        },
        "terraformer": {
            "name": "Terraformer",
            "short": "TF",
            "role": "Rubble, craters, fire/lava zones",
            "effect_preview": "Leaves slowing hazard zones.",
            "mechanics": ("hazard", "burn", "slow", "crater"),
            "tags": ("weird", "hazard", "burn"),
            "color": (235, 95, 55),
            "tiers": {3: "Terraformer", 4: "Lava Craters", 5: "Molten Kill Zone"},
            "descriptions": {
                3: "Shells leave short-lived rubble slow zones",
                4: "Lava craters burn enemies in the area",
                5: "Molten zones punish clustered ground waves",
            },
        },
    },
    "frost": {
        "glacier": {
            "name": "Glacier",
            "short": "GL",
            "role": "Stronger slows and freezes",
            "effect_preview": "Slows harder and freezes longer.",
            "mechanics": ("slow", "freeze", "cryo_prison"),
            "tags": ("control", "freeze", "slow"),
            "color": (155, 235, 255),
            "tiers": {3: "Glacier Tower", 4: "Cryo Prison", 5: "Deep Freeze"},
            "descriptions": {
                3: "Stronger slow on hit",
                4: "Cryo prison briefly stops priority enemies",
                5: "Deep freeze improves control uptime",
            },
        },
        "shatter": {
            "name": "Shatter",
            "short": "SH",
            "role": "Frozen burst damage",
            "effect_preview": "Frozen enemies burst on heavy hits/death.",
            "mechanics": ("freeze", "shatter", "burst"),
            "tags": ("damage", "freeze", "burst"),
            "color": (205, 250, 255),
            "tiers": {3: "Shatter Tower", 4: "Ice Fracture", 5: "Crystal Detonation"},
            "descriptions": {
                3: "Frozen enemies take bonus burst damage",
                4: "Fractured enemies splash on death",
                5: "Crystal detonation improves shatter bursts",
            },
        },
        "time_control": {
            "name": "Time Control",
            "short": "TC",
            "role": "Stasis and slow-motion effects",
            "effect_preview": "Briefly stops enemies in stasis.",
            "mechanics": ("stasis", "slow_motion", "rewind"),
            "tags": ("weird", "time", "control"),
            "color": (170, 210, 255),
            "tiers": {3: "Time Control", 4: "Stasis Field", 5: "Rewind Engine"},
            "descriptions": {
                3: "Hits briefly stasis slowed enemies",
                4: "Stasis fields hold groups longer",
                5: "Rewind engine gives strong wave control",
            },
        },
    },
    "tesla": {
        "chain_lightning": {
            "name": "Chain Lightning",
            "short": "CL",
            "role": "Jumps, anti-air, storm pulses",
            "effect_preview": "Lightning jumps to extra enemies.",
            "mechanics": ("chain", "anti_air", "storm_pulse"),
            "tags": ("damage", "chain", "anti_air"),
            "color": (255, 240, 95),
            "tiers": {3: "Chain Lightning", 4: "Storm Pulse", 5: "Thunder Web"},
            "descriptions": {
                3: "Lightning chains to nearby enemies",
                4: "Storm pulses improve anti-air control",
                5: "Thunder web increases chain coverage",
            },
        },
        "battery_grid": {
            "name": "Battery Grid",
            "short": "BG",
            "role": "Overclock nearby towers",
            "effect_preview": "Stores charge and boosts nearby towers.",
            "mechanics": ("overclock", "charge", "aura"),
            "tags": ("utility", "energy", "aura"),
            "color": (245, 225, 130),
            "tiers": {3: "Battery Grid", 4: "Charge Relay", 5: "Power Network"},
            "descriptions": {
                3: "Stores charge to overclock nearby towers",
                4: "Charge relay improves buff uptime",
                5: "Power network boosts linked defenses",
            },
        },
        "magnet_tech": {
            "name": "Magnet Tech",
            "short": "MT",
            "role": "Pulls enemies and EMPs shields",
            "effect_preview": "Clusters enemies and disrupts shields/haste.",
            "mechanics": ("pull", "emp", "cluster"),
            "tags": ("weird", "magnet", "emp"),
            "color": (210, 190, 255),
            "tiers": {3: "Magnet Tech", 4: "EMP Coil", 5: "Gravity Storm"},
            "descriptions": {
                3: "Magnet hits cluster nearby enemies",
                4: "EMP strips shields and haste effects",
                5: "Gravity storm improves clustering control",
            },
        },
    },
    "poison": {
        "venom_cask": {
            "name": "Venom Cask",
            "short": "VC",
            "role": "Long poison for tanks and bosses",
            "effect_preview": "Poisons linger and suppress regeneration.",
            "mechanics": ("poison", "anti_regen", "boss_pressure"),
            "tags": ("damage", "poison", "boss"),
            "color": (120, 225, 95),
            "tiers": {3: "Venom Cask", 4: "Toxin Still", 5: "Manticore Flask"},
            "descriptions": {
                3: "Poison lasts longer on high-health enemies",
                4: "Toxins hit regenerating enemies harder",
                5: "Bosses melt under stacked venom",
            },
        },
        "wildfire": {
            "name": "Wildfire",
            "short": "WF",
            "role": "Burning clouds for clustered lanes",
            "effect_preview": "Adds burn and small hazard bursts.",
            "mechanics": ("burn", "hazard", "splash"),
            "tags": ("damage", "hazard", "splash"),
            "color": (245, 135, 65),
            "tiers": {3: "Wildfire", 4: "Caustic Flame", 5: "Scorch Bloom"},
            "descriptions": {
                3: "Toxins ignite into short burn effects",
                4: "Burning clouds punish grouped enemies",
                5: "Scorch blooms widen the kill zone",
            },
        },
        "plague_mist": {
            "name": "Plague Mist",
            "short": "PM",
            "role": "Spreading debuffs and slows",
            "effect_preview": "Spreads poison and snares nearby enemies.",
            "mechanics": ("poison", "slow", "trap"),
            "tags": ("control", "poison", "slow"),
            "color": (150, 215, 95),
            "tiers": {3: "Plague Mist", 4: "Spore Net", 5: "Contagion Engine"},
            "descriptions": {
                3: "Poison clouds slow infected targets",
                4: "Spore nets spread control to nearby enemies",
                5: "Contagion keeps waves weakened longer",
            },
        },
    },
    "barracks": {
        "champions": {
            "name": "Champions",
            "short": "CH",
            "role": "Melee hold and elite duels",
            "effect_preview": "Guards hold enemies and damage elites.",
            "mechanics": ("hold", "melee", "elite_duel"),
            "tags": ("control", "hold", "melee"),
            "color": (220, 170, 95),
            "tiers": {3: "Champion Guard", 4: "Fortress Duelists", 5: "Elite Garrison"},
            "descriptions": {
                3: "Guards hold ground enemies longer",
                4: "Duelists damage elites and bosses",
                5: "Shield wall creates a strong kill zone",
            },
        },
        "engineers": {
            "name": "Engineers",
            "short": "EN",
            "role": "Barricades, spike strips, mines",
            "effect_preview": "Places periodic road traps.",
            "mechanics": ("trap", "mine", "repair", "barricade"),
            "tags": ("utility", "trap", "mine"),
            "color": (200, 160, 110),
            "tiers": {3: "Engineer Crew", 4: "Spike Strip", 5: "Minefield Crew"},
            "descriptions": {
                3: "Engineers add slowing road traps",
                4: "Spike strips damage held enemies",
                5: "Minefield crews improve trap bursts",
            },
        },
        "mercenary_guild": {
            "name": "Mercenary Guild",
            "short": "MG",
            "role": "Bounty, contracts, danger pay",
            "effect_preview": "Held kills can earn bonus money.",
            "mechanics": ("bounty", "contract", "danger_pay"),
            "tags": ("weird", "economy", "hold"),
            "color": (235, 195, 95),
            "tiers": {3: "Mercenary Guild", 4: "Contract Board", 5: "Danger Pay Office"},
            "descriptions": {
                3: "Held kills can grant bounty money",
                4: "Contracts improve reward consistency",
                5: "Danger pay scales during hard waves",
            },
        },
    },
    "support": {
        "war_banner": {
            "name": "War Banner",
            "short": "WB",
            "role": "Damage, rate, and range aura",
            "effect_preview": "Strong direct aura buffs.",
            "mechanics": ("aura", "damage_buff", "rate_buff", "range_buff"),
            "tags": ("utility", "aura", "buff"),
            "color": (245, 225, 145),
            "tiers": {3: "War Banner", 4: "Command Post", 5: "Battle Standard"},
            "descriptions": {
                3: "Aura adds damage and fire-rate buffs",
                4: "Command post extends range support",
                5: "Battle standard strengthens all aura stats",
            },
        },
        "research_lab": {
            "name": "Tech Lab",
            "short": "RL",
            "role": "Tech gain and upgrade discounts",
            "effect_preview": "Generates tech and discounts upgrades.",
            "mechanics": ("research", "discount", "prototype", "gold"),
            "tags": ("weird", "economy", "research"),
            "color": (210, 220, 120),
            "tiers": {3: "Tech Lab", 4: "Prototype Desk", 5: "Adaptive Institute"},
            "descriptions": {
                3: "Assists grant small tech progress",
                4: "Prototype discounts help nearby upgrades",
                5: "Adaptive tech improves long-term scaling",
            },
        },
        "signal_tower": {
            "name": "Signal Tower",
            "short": "ST",
            "role": "Shared targeting and threat scan",
            "effect_preview": "Paints priority enemies for nearby towers.",
            "mechanics": ("paint", "shared_targeting", "threat_scan"),
            "tags": ("control", "targeting", "mark"),
            "color": (180, 215, 245),
            "tiers": {3: "Signal Tower", 4: "Threat Scanner", 5: "Tactical Grid"},
            "descriptions": {
                3: "Signals paint priority enemies",
                4: "Threat scanner improves shared targeting",
                5: "Tactical grid improves battlefield control",
            },
        },
    },
}

BRANCH_IDENTITY = {
    "archer": {
        "deadeye": {
            "signature": "priority_mark_crit",
            "primary_mechanic": "priority mark",
            "late_descriptions": {
                6: "Paragon arrows extend marks and punish bosses harder",
                7: "Marked priority targets take stronger critical hits",
                8: "Boss pressure ramps faster during long fights",
                9: "Marks persist longer through crowded waves",
                10: "Critline mastery deletes weakened marked enemies",
            },
            "upgrade_effects": {
                3: "Mark duration +2.0s",
                4: "Crit damage +35%",
                5: "Boss mark duration +0.7s",
                6: "Mark uptime +25%",
                7: "Marked damage +6%",
                8: "Boss ramp +8%",
                9: "Mark duration +0.5s",
                10: "Execute threshold +8%",
            },
        },
        "trapline": {
            "signature": "venom_snareline",
            "primary_mechanic": "snare trap",
            "late_descriptions": {
                6: "Paragon snares spread farther along the lane",
                7: "Venom traps last longer on fast enemies",
                8: "Snared enemies carry weaker poison to nearby packs",
                9: "Trapline uptime improves during dense waves",
                10: "Wildwood mastery keeps priority targets trapped",
            },
            "upgrade_effects": {
                3: "Snare slow +0.9s",
                4: "Anti-regen +25%",
                5: "Trap spread +1 target",
                6: "Trap spread radius +18",
                7: "Snare duration +0.4s",
                8: "Poison spread +1 target",
                9: "Trap uptime +10%",
                10: "Priority snare +0.6s",
            },
        },
        "beastmaster": {
            "signature": "companion_strikes",
            "primary_mechanic": "pet strike",
            "late_descriptions": {
                6: "Paragon companions strike priority enemies more often",
                7: "Wolf holds last longer on wounded enemies",
                8: "Companion assists hit elites harder",
                9: "Bearwarden strikes splash to nearby ground enemies",
                10: "Beastmaster mastery doubles down on companion assists",
            },
            "upgrade_effects": {
                3: "Pet hit +16%",
                4: "Wounded hold +0.3s",
                5: "Elite pet damage +25%",
                6: "Assist rate +20%",
                7: "Hold duration +0.3s",
                8: "Elite damage +8%",
                9: "Assist cleave +1 target",
                10: "Pet hit +12%",
            },
        },
    },
    "machine_gun": {
        "vulcan": {
            "signature": "spin_up_heat",
            "primary_mechanic": "heat ramp",
            "late_descriptions": {
                6: "Vulcan paragon raises heat capacity and burst damage",
                7: "Sustained fire ramps attack speed faster",
                8: "High heat shots burst into extra swarm damage",
                9: "Heat decays slower between targets",
                10: "Maximum heat triggers stronger overheat bursts",
            },
            "upgrade_effects": {
                3: "Heat rate +12%",
                4: "Spin cap +1 stage",
                5: "Overheat burst unlocks",
                6: "Heat cap +20%",
                7: "Rate ramp +4%",
                8: "Burst damage +10%",
                9: "Heat decay -15%",
                10: "Max-heat burst +1",
            },
        },
        "suppression": {
            "signature": "pin_stack_panic",
            "primary_mechanic": "pin stacks",
            "late_descriptions": {
                6: "Suppression paragon raises pin stacks and panic duration",
                7: "Rapid hits pin fast and hasted enemies harder",
                8: "Pinned enemies briefly panic when stacks peak",
                9: "Suppression stacks last longer between bullets",
                10: "Panic zones disrupt dense fast pushes",
            },
            "upgrade_effects": {
                3: "Pin stacks +2 max",
                4: "Pin duration +0.4s",
                5: "Panic trigger unlocks",
                6: "Pin stacks +1 max",
                7: "Fast slow +6%",
                8: "Panic freeze +0.08s",
                9: "Stack decay -20%",
                10: "Panic radius +20",
            },
        },
        "ammo_fabricator": {
            "signature": "adaptive_round_cycle",
            "primary_mechanic": "adaptive ammo",
            "late_descriptions": {
                6: "Ammo paragon improves AP, frangible, and tracer rounds",
                7: "AP rounds strip shields and armor more reliably",
                8: "Frangible rounds cleave swarm targets harder",
                9: "Tracer rounds expose priority targets longer",
                10: "Adaptive arsenal rotates stronger counters per hit",
            },
            "upgrade_effects": {
                3: "Adaptive check +1 tag",
                4: "Tracer expose +0.5s",
                5: "Counter bonus +12%",
                6: "Ammo bonus +15%",
                7: "AP strip +1 shield",
                8: "Frangible cleave +1",
                9: "Tracer mark +0.5s",
                10: "Counter bonus +8%",
            },
        },
    },
    "cannon": {
        "artillery": {
            "signature": "bombardment_clusters",
            "primary_mechanic": "bombardment",
            "late_descriptions": {
                6: "Artillery paragon adds wider bombardment clusters",
                7: "Cluster shells gain a larger secondary blast",
                8: "Bombardment hits more grouped enemies per shell",
                9: "Long-range shells retain more splash damage",
                10: "Map bombardment punishes dense waves with extra bursts",
            },
            "upgrade_effects": {
                3: "Splash radius +18",
                4: "Cluster targets +2",
                5: "Splash damage +18%",
                6: "Blast radius +24",
                7: "Cluster radius +12",
                8: "Cluster targets +1",
                9: "Splash falloff -10%",
                10: "Extra burst +1",
            },
        },
        "demolition": {
            "signature": "breach_stack_exposure",
            "primary_mechanic": "breach stacks",
            "late_descriptions": {
                6: "Demolition paragon raises breach vulnerability",
                7: "Breach stacks strip shields faster",
                8: "Exposed armor takes more burst damage",
                9: "Breach duration improves against tanks and bosses",
                10: "Exposed core mastery spikes damage on cracked targets",
            },
            "upgrade_effects": {
                3: "Breach expose +1.8s",
                4: "Shield strip +1",
                5: "Vulnerability +15%",
                6: "Breach cap +1",
                7: "Shield strip chance +20%",
                8: "Vulnerability +4%",
                9: "Breach duration +0.4s",
                10: "Cracked burst +12%",
            },
        },
        "terraformer": {
            "signature": "crater_zone_control",
            "primary_mechanic": "crater zone",
            "late_descriptions": {
                6: "Terraformer paragon leaves larger molten crater zones",
                7: "Crater slows last longer on ground enemies",
                8: "Molten zones burn clustered enemies harder",
                9: "Repeated crater hits stack stronger terrain denial",
                10: "Kill-zone mastery widens persistent ground control",
            },
            "upgrade_effects": {
                3: "Crater slow +1.0s",
                4: "Crater burn unlocks",
                5: "Crater radius +16",
                6: "Crater radius +20",
                7: "Ground slow +0.4s",
                8: "Molten burn +10%",
                9: "Zone uptime +12%",
                10: "Kill-zone radius +18",
            },
        },
    },
    "frost": {
        "glacier": {
            "signature": "glacier_lockdown",
            "primary_mechanic": "lockdown freeze",
            "late_descriptions": {
                6: "Glacier paragon improves slow strength and freeze uptime",
                7: "Priority enemies stay frozen longer",
                8: "Slow fields cover more nearby targets",
                9: "Control uptime improves against bosses and fast waves",
                10: "Deep freeze mastery keeps dangerous pushes locked down",
            },
            "upgrade_effects": {
                3: "Slow strength +10%",
                4: "Freeze window +0.25s",
                5: "Lockdown uptime +15%",
                6: "Freeze +0.25s",
                7: "Priority freeze +0.15s",
                8: "Slow radius +18",
                9: "Boss control +10%",
                10: "Lockdown uptime +12%",
            },
        },
        "shatter": {
            "signature": "frozen_shatter_burst",
            "primary_mechanic": "shatter burst",
            "late_descriptions": {
                6: "Shatter paragon converts frozen targets into stronger bursts",
                7: "Frozen hits deal more bonus damage",
                8: "Fractured enemies splash damage on death more often",
                9: "Crystal detonation radius improves",
                10: "Shatter mastery detonates frozen packs harder",
            },
            "upgrade_effects": {
                3: "Frozen burst +18%",
                4: "Death splash unlocks",
                5: "Detonation radius +18",
                6: "Shatter damage +20%",
                7: "Frozen bonus +8%",
                8: "Death splash +1 target",
                9: "Detonation radius +12",
                10: "Pack burst +15%",
            },
        },
        "time_control": {
            "signature": "rewind_stasis",
            "primary_mechanic": "rewind stasis",
            "late_descriptions": {
                6: "Time paragon rewinds dangerous ground enemies farther",
                7: "Stasis pulses last longer on slowed enemies",
                8: "Rewind effects trigger on more priority targets",
                9: "Slow-motion fields improve wave control uptime",
                10: "Rewind engine mastery pushes back dangerous leaks",
            },
            "upgrade_effects": {
                3: "Stasis +0.18s",
                4: "Rewind nudge +8%",
                5: "Priority rewind unlocks",
                6: "Rewind nudge +5%",
                7: "Stasis +0.08s",
                8: "Priority targets +1",
                9: "Slow-motion +0.3s",
                10: "Leak rewind +8%",
            },
        },
    },
    "tesla": {
        "chain_lightning": {
            "signature": "chain_web",
            "primary_mechanic": "chain web",
            "late_descriptions": {
                6: "Chain paragon increases lightning jump range",
                7: "Chain web jumps to one more clustered target",
                8: "Storm pulses hit flying enemies harder",
                9: "Lightning retains more damage after each jump",
                10: "Thunder web mastery covers wider packed waves",
            },
            "upgrade_effects": {
                3: "Chain targets +1",
                4: "Chain targets +2",
                5: "Chain damage +25%",
                6: "Jump range +20",
                7: "Chain targets +1",
                8: "Anti-air damage +10%",
                9: "Chain damage +8%",
                10: "Web radius +18",
            },
        },
        "battery_grid": {
            "signature": "charge_overclock_pulse",
            "primary_mechanic": "charge pulse",
            "late_descriptions": {
                6: "Battery paragon sends stronger overclock pulses",
                7: "Charge pulses happen more often",
                8: "Linked towers gain more fire-rate overclock",
                9: "Charge relay also adds damage to nearby defenses",
                10: "Power network mastery keeps clustered towers overclocked",
            },
            "upgrade_effects": {
                3: "Pulse rate +15%",
                4: "Overclock uptime +0.6s",
                5: "Network radius +20",
                6: "Pulse strength +12%",
                7: "Pulse interval -0.3s",
                8: "Rate overclock +4%",
                9: "Damage overclock +4%",
                10: "Network uptime +1.0s",
            },
        },
        "magnet_tech": {
            "signature": "gravity_emp",
            "primary_mechanic": "gravity EMP",
            "late_descriptions": {
                6: "Magnet paragon strengthens pull and EMP disruption",
                7: "Gravity pulses cluster more enemies",
                8: "EMP strips shields and haste effects more reliably",
                9: "Pulled enemies remain slowed longer",
                10: "Gravity storm mastery sets up splash kill zones",
            },
            "upgrade_effects": {
                3: "Pull radius +70",
                4: "EMP strip +1 shield",
                5: "Gravity targets +2",
                6: "Pull strength +20%",
                7: "Pull targets +1",
                8: "EMP duration +0.4s",
                9: "Gravity slow +0.3s",
                10: "Storm radius +18",
            },
        },
    },
    "poison": {
        "venom_cask": {
            "signature": "long_toxin_stack",
            "primary_mechanic": "long toxin",
            "late_descriptions": {
                6: "Venom paragon extends toxin duration and boss ramp",
                7: "Long toxin suppresses regeneration harder",
                8: "Stacked venom deals more damage to high-health enemies",
                9: "Boss toxins last longer through long fights",
                10: "Manticore mastery melts priority targets with stacked venom",
            },
            "upgrade_effects": {
                3: "Poison duration +0.7s",
                4: "Anti-regen +25%",
                5: "Boss toxin +18%",
                6: "Poison duration +0.8s",
                7: "Regen cut +10%",
                8: "High-HP damage +8%",
                9: "Boss duration +0.5s",
                10: "Stacked toxin +12%",
            },
        },
        "wildfire": {
            "signature": "volatile_toxin_bloom",
            "primary_mechanic": "volatile bloom",
            "late_descriptions": {
                6: "Wildfire paragon makes poisoned targets ignite in bursts",
                7: "Volatile burns tick harder on clustered enemies",
                8: "Scorch blooms reach more nearby targets",
                9: "Burning clouds last longer after poison hits",
                10: "Wildfire mastery detonates infected packs harder",
            },
            "upgrade_effects": {
                3: "Ignition burn +1.4s",
                4: "Bloom radius +18",
                5: "Bloom targets +2",
                6: "Ignition damage +18%",
                7: "Burn DPS +8%",
                8: "Bloom targets +1",
                9: "Cloud duration +0.4s",
                10: "Detonation damage +12%",
            },
        },
        "plague_mist": {
            "signature": "contagion_mist",
            "primary_mechanic": "contagion",
            "late_descriptions": {
                6: "Plague paragon spreads contagion to more nearby enemies",
                7: "Contagion weakens infected targets longer",
                8: "Spore nets apply stronger control in poison clouds",
                9: "Mist coverage improves against dense waves",
                10: "Contagion mastery keeps whole packs weakened",
            },
            "upgrade_effects": {
                3: "Contagion spread +1",
                4: "Weakening +8%",
                5: "Mist duration +0.5s",
                6: "Spread targets +1",
                7: "Weakening +3%",
                8: "Spore slow +6%",
                9: "Mist radius +16",
                10: "Pack duration +0.6s",
            },
        },
    },
    "barracks": {
        "champions": {
            "signature": "duel_hold",
            "primary_mechanic": "duel hold",
            "late_descriptions": {
                6: "Champion paragon improves melee lockdown and duel damage",
                7: "Held elites and bosses take more champion damage",
                8: "Duel holds last longer on priority enemies",
                9: "Champion zones expose held targets more reliably",
                10: "Elite garrison mastery anchors a stronger kill zone",
            },
            "upgrade_effects": {
                3: "Hold strength +8%",
                4: "Elite duel +20%",
                5: "Melee damage +25%",
                6: "Hold duration +0.4s",
                7: "Elite damage +10%",
                8: "Priority hold +0.3s",
                9: "Expose +4%",
                10: "Kill-zone damage +12%",
            },
        },
        "engineers": {
            "signature": "barricade_minefield",
            "primary_mechanic": "barricade traps",
            "late_descriptions": {
                6: "Engineer paragon improves minefield damage and trap uptime",
                7: "Spike strips hit held enemies harder",
                8: "Barricades slow ground lanes longer",
                9: "Mine bursts cover more enemies in the hold zone",
                10: "Minefield mastery turns holds into burst kill zones",
            },
            "upgrade_effects": {
                3: "Trap slow +0.3s",
                4: "Mine damage +18%",
                5: "Mine radius +18",
                6: "Mine damage +15%",
                7: "Held damage +8%",
                8: "Barricade slow +0.3s",
                9: "Mine targets +1",
                10: "Burst damage +12%",
            },
        },
        "mercenary_guild": {
            "signature": "contract_bounty",
            "primary_mechanic": "contracts",
            "late_descriptions": {
                6: "Mercenary paragon increases bounty consistency",
                7: "Contracts pay more from held kills",
                8: "Danger pay scales during hard waves",
                9: "Boss and elite contracts grant stronger rewards",
                10: "Guild mastery converts kill zones into reliable economy",
            },
            "upgrade_effects": {
                3: "Bounty chance +1",
                4: "Contract payout +1",
                5: "Danger pay unlocks",
                6: "Bounty cap +2",
                7: "Held payout +1",
                8: "Hard-wave pay +1",
                9: "Boss contract +2",
                10: "Economy uptime +15%",
            },
        },
    },
    "support": {
        "war_banner": {
            "signature": "steady_war_aura",
            "primary_mechanic": "war aura",
            "late_descriptions": {
                6: "War Banner paragon strengthens direct cluster buffs",
                7: "Aura buffs last longer on nearby towers",
                8: "Damage and fire-rate buffs improve together",
                9: "Command range support reaches more clustered towers",
                10: "Battle standard mastery keeps dense defenses empowered",
            },
            "upgrade_effects": {
                3: "Aura damage +4%",
                4: "Aura range +0.8s",
                5: "Aura strength +6%",
                6: "Buff strength +10%",
                7: "Buff duration +0.6s",
                8: "Damage/rate +3%",
                9: "Range buff +5%",
                10: "Aura uptime +1.0s",
            },
        },
        "research_lab": {
            "signature": "prototype_research",
            "primary_mechanic": "prototype tech",
            "late_descriptions": {
                6: "Tech Lab paragon improves research and prototype tempo",
                7: "Assists generate tech more consistently",
                8: "Prototype buffs reduce nearby upgrade pressure",
                9: "Research casts recover mana faster",
                10: "Adaptive institute mastery accelerates late upgrades",
            },
            "upgrade_effects": {
                3: "Tech every 3 casts",
                4: "Prototype discount +5%",
                5: "Research tempo +12%",
                6: "Tech chance +20%",
                7: "Assist tech +1",
                8: "Prototype buff +6%",
                9: "Mana recovery +3/s",
                10: "Late tech +1",
            },
        },
        "signal_tower": {
            "signature": "tactical_scan_grid",
            "primary_mechanic": "tactical scan",
            "late_descriptions": {
                6: "Signal paragon scans more priority enemies per cast",
                7: "Threat scans last longer on dangerous targets",
                8: "Tactical grid improves shared targeting damage",
                9: "Scans slow priority enemies more reliably",
                10: "Signal mastery keeps the battlefield painted",
            },
            "upgrade_effects": {
                3: "Scan mark +2.8s",
                4: "Shared targeting +8%",
                5: "Grid targets +1",
                6: "Scan targets +1",
                7: "Scan duration +0.5s",
                8: "Marked damage +4%",
                9: "Priority slow +5%",
                10: "Grid uptime +0.8s",
            },
        },
    },
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
        "label": "Gunner",
        "short": "GUN",
        "role": "Fast single-target DPS",
        "good_vs": "Swarms and low-health enemies",
        "weakness": "Heavy armor and shields",
        "color": (95, 115, 125),
        "range_color": (145, 165, 175),
        "projectile_color": (255, 225, 100),
        "tiers": {
            2: "Gunner Nest",
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
        "label": "Artillery",
        "short": "ART",
        "role": "Slow massive AoE",
        "good_vs": "Grouped enemies and tanks",
        "weakness": "Fast leaks and flying enemies",
        "color": (150, 105, 70),
        "range_color": (200, 150, 95),
        "projectile_color": (80, 70, 60),
        "tiers": {
            2: "Artillery Tower",
            3: "Heavy Battery",
            4: "Siege Platform",
            5: "Earthshaker",
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
        "label": "Venom",
        "short": "VEN",
        "role": "Burn and poison DoT",
        "good_vs": "Tanks, bosses, and regeneration",
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
        "label": "Garrison",
        "short": "GAR",
        "role": "Holds ground enemies",
        "good_vs": "Ground lanes and slowing pushes",
        "weakness": "Cannot attack flying enemies",
        "color": (185, 145, 85),
        "range_color": (220, 185, 120),
        "projectile_color": (210, 180, 120),
        "tiers": {
            2: "Guard Post",
            3: "Veteran Guards",
            4: "Shield Wall",
            5: "Champion Garrison",
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
        "label": "Channeler",
        "short": "CHN",
        "role": "Casts buffs and debuffs",
        "good_vs": "Dense tower clusters",
        "weakness": "Does not deal direct damage",
        "color": (200, 185, 105),
        "range_color": (245, 225, 145),
        "projectile_color": (245, 225, 145),
        "tiers": {
            2: "Channeler Tower",
            3: "Mana Relay",
            4: "Command Focus",
            5: "Battle Conduit",
        },
        "descriptions": {
            2: "Builds mana and casts tower buffs",
            3: "Casts faster and marks priority enemies",
            4: "Buffs last longer",
            5: "Stronger targeted support casts",
        },
        "paragon": "High Conduit",
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


REQUIRED_TOWER_KEYS = (
    "label",
    "short",
    "role",
    "good_vs",
    "weakness",
    "color",
    "range_color",
    "projectile_color",
    "tiers",
    "descriptions",
    "paragon",
)

REQUIRED_BRANCH_KEYS = (
    "name",
    "short",
    "role",
    "effect_preview",
    "mechanics",
    "tags",
    "color",
    "tiers",
    "descriptions",
    "signature",
    "primary_mechanic",
    "late_descriptions",
    "upgrade_effects",
    "focus",
    "keystone",
    "synergy",
    "mastery",
    "milestones",
)


FOCUS_LABELS = {
    "damage": "Damage",
    "control": "Control",
    "utility": "Utility",
    "weird": "Specialist",
}

MECHANIC_KEYSTONES = (
    (("boss_pressure",), "Boss pressure scales during long fights"),
    (("crit",), "Critical hits spike against marked targets"),
    (("mark", "paint"), "Marked enemies become shared priority targets"),
    (("trap",), "Road traps add control between tower shots"),
    (("poison",), "Venom keeps damaging high-health enemies"),
    (("pet_hit",), "Companion strikes add periodic extra hits"),
    (("hold",), "Holds create a stable kill zone"),
    (("pierce", "armor_break", "shield_break"), "Piercing hits expose armor and shields"),
    (("shared_targeting",), "Nearby towers coordinate target focus"),
    (("delayed_damage", "echo"), "Stored damage detonates after setup"),
    (("spin_up",), "Sustained fire ramps into higher DPS"),
    (("slow", "pin"), "Suppression keeps fast enemies in range"),
    (("adaptive_ammo",), "Ammo adapts to the wave's main threat"),
    (("splash", "cluster", "mortar"), "Explosions punish clustered lanes"),
    (("hazard", "crater", "burn"), "Hazards leave damaging road zones"),
    (("freeze", "cryo_prison"), "Freeze windows set up burst damage"),
    (("shatter",), "Frozen enemies burst when finished"),
    (("stasis", "slow_motion"), "Time effects pause dangerous pushes"),
    (("chain", "storm_pulse"), "Lightning jumps through packed targets"),
    (("overclock", "charge"), "Stored charge boosts nearby towers"),
    (("pull", "emp"), "Magnet pulses group enemies and disrupt shields"),
    (("mine", "barricade"), "Engineers seed the lane with traps"),
    (("bounty", "contract"), "Contracts convert held kills into money"),
    (("aura", "damage_buff", "rate_buff"), "Aura buffs reward tight tower clusters"),
    (("research", "prototype"), "Assists convert into tech tempo"),
    (("threat_scan",), "Scans steer damage into priority targets"),
)

TAG_SYNERGIES = {
    "boss": "Pairs with marks, armor break, and long lanes",
    "mark": "Pairs with Archer, Sniper, and Signal targeting",
    "trap": "Pairs with Artillery splash and Garrison holds",
    "poison": "Pairs with slows that keep enemies in the cloud",
    "pet": "Pairs with rapid marks and wounded targets",
    "pierce": "Pairs with shield and armored waves",
    "targeting": "Pairs with any high-damage tower nearby",
    "rapid": "Pairs with Frost, armor pierce, and on-hit traits",
    "splash": "Pairs with slows, pulls, and held enemies",
    "mortar": "Pairs with grouped lanes and long sight lines",
    "armor": "Pairs with Sniper or Demolition exposure",
    "hazard": "Pairs with slows, pulls, and repeated path crossings",
    "freeze": "Pairs with Shatter, Artillery, and Tesla chains",
    "chain": "Pairs with Frost slow and clustered waves",
    "anti_air": "Pairs with flying-heavy waves",
    "energy": "Pairs with rapid-fire towers",
    "magnet": "Pairs with splash and hazard paths",
    "melee": "Pairs with Artillery, Frost, and Channeler buffs",
    "mine": "Pairs with Garrison holds and slow lanes",
    "economy": "Pairs with safe early defenses and long waves",
    "aura": "Pairs with dense tower clusters",
    "research": "Tech helps expensive late mastery upgrades",
}


def branch_focus(branch):
    tags = set(branch["tags"])
    for focus in ("damage", "control", "utility", "weird"):
        if focus in tags:
            return focus
    return "utility"


def branch_keystone(branch):
    mechanics = set(branch["mechanics"])
    for candidates, text in MECHANIC_KEYSTONES:
        if mechanics.intersection(candidates):
            return text
    return branch["effect_preview"]


def branch_synergy(branch):
    for tag in branch["tags"]:
        if tag in TAG_SYNERGIES:
            return TAG_SYNERGIES[tag]
    return "Pairs with towers that cover its weak spots"


def branch_mastery(branch):
    focus = branch.get("focus") or branch_focus(branch)
    if focus == "damage":
        return "Mastery adds higher priority-target damage"
    if focus == "control":
        return "Mastery improves uptime and control coverage"
    if focus == "utility":
        return "Mastery improves team support and consistency"
    return "Mastery strengthens the branch's special mechanic"


def branch_milestones(branch):
    return (
        f"T3 {branch['tiers'][3]}: {branch['descriptions'][3]}",
        f"T4 {branch['tiers'][4]}: {branch['descriptions'][4]}",
        f"T5 {branch['tiers'][5]}: {branch['descriptions'][5]}",
        f"T6 Keystone: {branch['keystone']}",
        f"M Mastery: {branch['mastery']}",
    )


def normalize_tower_type(tower_type):
    return LEGACY_TOWER_ALIASES.get(tower_type, (tower_type, None))


def branch_data(tower_type, branch_key):
    root_type, legacy_branch = normalize_tower_type(tower_type)
    selected = branch_key or legacy_branch
    if selected is None:
        return None
    return BRANCH_DEFINITIONS.get(root_type, {}).get(selected)


def tower_tier_name(tower_type, level, branch_key=None):
    branch = branch_data(tower_type, branch_key)
    if branch and level in branch["tiers"]:
        return branch["tiers"][level]
    root_type, _ = normalize_tower_type(tower_type)
    return TOWER_TYPES[root_type]["tiers"].get(level, TOWER_TYPES[root_type]["label"])


def tower_tier_description(tower_type, level, branch_key=None):
    branch = branch_data(tower_type, branch_key)
    if branch and level in branch["descriptions"]:
        return branch["descriptions"][level]
    if branch and level in branch["late_descriptions"]:
        return branch["late_descriptions"][level]
    root_type, _ = normalize_tower_type(tower_type)
    return TOWER_TYPES[root_type]["descriptions"].get(level, TOWER_TYPES[root_type]["role"])


def _apply_family_metadata():
    for tower_type in ROOT_TOWER_IDS:
        family, theme = FAMILY_INFO[tower_type]
        branches = BRANCH_DEFINITIONS[tower_type]
        tower = TOWER_TYPES[tower_type]
        for branch_key, branch in branches.items():
            identity = BRANCH_IDENTITY.get(tower_type, {}).get(branch_key, {})
            branch.update(identity)
            branch.setdefault("signature", f"{tower_type}_{branch_key}")
            branch.setdefault("primary_mechanic", branch["mechanics"][0])
            branch.setdefault(
                "late_descriptions",
                {
                    6: f"{branch['name']} paragon strengthens its signature mechanic",
                    7: f"{branch['name']} mastery improves uptime",
                    8: f"{branch['name']} mastery improves coverage",
                    9: f"{branch['name']} mastery improves consistency",
                    10: f"{branch['name']} mastery reaches maximum scaling",
                },
            )
            branch.setdefault(
                "upgrade_effects",
                {
                    3: branch["descriptions"][3],
                    4: branch["descriptions"][4],
                    5: branch["descriptions"][5],
                    6: branch["late_descriptions"][6],
                    7: branch["late_descriptions"][7],
                    8: branch["late_descriptions"][8],
                    9: branch["late_descriptions"][9],
                    10: branch["late_descriptions"][10],
                },
            )
            branch["focus"] = branch_focus(branch)
            branch["keystone"] = branch_keystone(branch)
            branch["synergy"] = branch_synergy(branch)
            branch["mastery"] = branch_mastery(branch)
            branch["milestones"] = branch_milestones(branch)
        tower["family"] = family
        tower["family_theme"] = theme
        tower["branch_options"] = tuple(branches.keys())
        tower["branch_tiers"] = {key: value["tiers"] for key, value in branches.items()}
        tower["branch_mechanics"] = {key: value["mechanics"] for key, value in branches.items()}
        tower["synergies"] = tuple(sorted({tag for branch in branches.values() for tag in branch["tags"]}))
        tower["tags"] = tuple(sorted({tag for branch in branches.values() for tag in branch["tags"]}))

    for legacy_id, (root_type, branch_key) in LEGACY_TOWER_ALIASES.items():
        if legacy_id in TOWER_TYPES:
            TOWER_TYPES[legacy_id]["legacy_alias_for"] = root_type
            TOWER_TYPES[legacy_id]["legacy_branch"] = branch_key


def validate_tower_family_data():
    errors = []
    shop_roots = tuple(SHOP_TOWER_ORDER)

    for tower_type in shop_roots:
        if tower_type not in ROOT_TOWER_IDS:
            errors.append(f"Shop tower {tower_type} must be a root tower")
        if tower_type not in SHOP_COSTS:
            errors.append(f"Shop tower {tower_type} missing shop cost")

    for legacy_id in LEGACY_TOWER_ALIASES:
        if legacy_id in shop_roots:
            errors.append(f"Legacy tower {legacy_id} must not appear in the root shop")

    for tower_type in ROOT_TOWER_IDS:
        tower = TOWER_TYPES.get(tower_type)
        if tower is None:
            errors.append(f"Missing root tower {tower_type}")
            continue
        for key in REQUIRED_TOWER_KEYS:
            if key not in tower:
                errors.append(f"{tower_type} missing required key {key}")

        branches = BRANCH_DEFINITIONS.get(tower_type, {})
        if len(branches) != 3:
            errors.append(f"{tower_type} must have exactly 3 branches")
        for branch_key, branch in branches.items():
            for key in REQUIRED_BRANCH_KEYS:
                if key not in branch:
                    errors.append(f"{tower_type}.{branch_key} missing branch key {key}")
            for level in range(BRANCH_UNLOCK_LEVEL, 6):
                if level not in branch.get("tiers", {}):
                    errors.append(f"{tower_type}.{branch_key} missing tier name for level {level}")
                if level not in branch.get("descriptions", {}):
                    errors.append(f"{tower_type}.{branch_key} missing description for level {level}")
            for level in range(6, 11):
                if level not in branch.get("late_descriptions", {}):
                    errors.append(f"{tower_type}.{branch_key} missing late description for level {level}")
                if level not in branch.get("upgrade_effects", {}):
                    errors.append(f"{tower_type}.{branch_key} missing upgrade effect for level {level}")

    visible_signatures = []
    visible_primary_mechanics = []
    for tower_type in SHOP_TOWER_ORDER:
        for branch_key, branch in BRANCH_DEFINITIONS[tower_type].items():
            visible_signatures.append((branch["signature"], tower_type, branch_key))
            visible_primary_mechanics.append((branch["primary_mechanic"], tower_type, branch_key))

    for label, values in (("signature", visible_signatures), ("primary mechanic", visible_primary_mechanics)):
        seen = {}
        for value, tower_type, branch_key in values:
            if value in seen:
                other_tower, other_branch = seen[value]
                errors.append(
                    f"Visible branch {tower_type}.{branch_key} duplicates {label} with {other_tower}.{other_branch}: {value}"
                )
            seen[value] = (tower_type, branch_key)

    for legacy_id, (root_type, branch_key) in LEGACY_TOWER_ALIASES.items():
        if root_type not in ROOT_TOWER_IDS:
            errors.append(f"Legacy {legacy_id} maps to unknown root {root_type}")
        if branch_key not in BRANCH_DEFINITIONS.get(root_type, {}):
            errors.append(f"Legacy {legacy_id} maps to unknown branch {root_type}.{branch_key}")

    return errors


_apply_family_metadata()
