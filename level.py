# level.py
"""
Cấu hình các level cho game River Crossing
Mỗi level có các thuộc tính:
- level: số thứ tự level
- name: tên level
- characters: danh sách các nhân vật
- boat: cấu hình thuyền (sức chứa, yêu cầu người lái, ai có thể lái)
- rules: các luật chơi
- goal: mục tiêu của level
- extra: các điều kiện đặc biệt (time pressure, bomb timer...)
"""

levels = [
    # Level 1: Classic Wolf - Sheep - Cabbage
    {
        "level": 1,
        "name": "Wolf - Sheep - Cabbage",
        "characters": ["person", "wolf", "sheep", "cabbage"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["person"]
        },
        "rules": [
            {"if_alone": ["wolf", "sheep"], "result": "sheep_eaten"},
            {"if_alone": ["sheep", "cabbage"], "result": "cabbage_eaten"}
        ],
        "goal": "move_all_safely"
    },

    # Level 2: Tiger replaces Wolf (có thêm time pressure)
    {
        "level": 2,
        "name": "Tiger replaces Wolf",
        "characters": ["human", "tiger", "sheep", "cabbage"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["human"]
        },
        "rules": [
            {"if_alone": ["tiger", "sheep"], "result": "sheep_eaten"},
            {"if_alone": ["sheep", "cabbage"], "result": "cabbage_eaten"}
        ],
        "goal": "move_all_safely",
        "extra": {"time_pressure": True}
    },

    # Level 3: Food Chain Extended (thêm tiger - wolf relationship)
    {
        "level": 3,
        "name": "Food Chain Extended",
        "characters": ["person", "tiger", "wolf", "sheep", "cabbage"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["person"]
        },
        "rules": [
            {"if_alone": ["tiger", "wolf"], "result": "wolf_eaten"},
            {"if_alone": ["wolf", "sheep"], "result": "sheep_eaten"},
            {"if_alone": ["sheep", "cabbage"], "result": "cabbage_eaten"}
        ],
        "goal": "move_all_safely"
    },

    # Level 4: Scientist & Robot (robot có thể lái thuyền)
    {
        "level": 4,
        "name": "Scientist & Robot",
        "characters": ["scientist", "robot", "sheep", "cabbage"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["scientist", "robot"]
        },
        "rules": [
            {"if_alone": ["robot", "cabbage"], "result": "cabbage_destroyed", "unless_present": ["scientist"]}
        ],
        "goal": "move_all_safely"
    },

    # Level 5: Protect the Humans (bảo vệ con người khỏi thú dữ)
    {
        "level": 5,
        "name": "Protect the Humans",
        "characters": ["scientist", "human", "tiger", "wolf"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["scientist", "human"]
        },
        "rules": [
            {"if_alone": ["tiger", "wolf", "human"], "result": "human_attacked", "unless_present": ["scientist"]},
            {"if_alone": ["tiger", "wolf", "scientist"], "result": "equipment_destroyed", "unless_present": ["human"]}
        ],
        "goal": "move_all_safely"
    },

    # Level 6: Bomb Timer (có bom hẹn giờ)
    {
        "level": 6,
        "name": "Bomb Timer",
        "characters": ["human", "wolf", "sheep", "bomb"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["human"]
        },
        "rules": [
            {"if_alone": ["wolf", "sheep"], "result": "sheep_eaten"}
        ],
        "goal": "move_all_safely",
        "extra": {
            "bomb_timer": 5,
            "fail_condition": "bomb_explodes"
        }
    },

    # Level 7: Robot Defense System (robot có thể tự động tiêu diệt thú)
    {
        "level": 7,
        "name": "Robot Defense System",
        "characters": ["scientist", "robot", "tiger", "wolf", "sheep"],
        "boat": {
            "capacity": 3,
            "requires_driver": True,
            "drivers": ["scientist"]
        },
        "rules": [
            {"if_alone": ["tiger", "wolf"], "result": "fight"},
            {"robot_behavior": "kills_animals_if_no_scientist"}
        ],
        "goal": "move_all_safely"
    },

    # Level 8: Strong Current Constraint (có điều kiện vận chuyển đặc biệt)
    {
        "level": 8,
        "name": "Strong Current Constraint",
        "characters": ["scientist", "human", "tiger", "wolf", "sheep", "cabbage"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["scientist", "human"]
        },
        "rules": [
            {"if_alone": ["tiger", "sheep"], "result": "sheep_eaten"},
            {"if_alone": ["wolf", "sheep"], "result": "sheep_eaten"},
            {"if_transport": ["human", "tiger"], "require": ["scientist"]}
        ],
        "goal": "move_all_safely"
    },

    # Level 9: Double Bomb Problem (hai quả bom, cần xử lý cẩn thận)
    {
        "level": 9,
        "name": "Double Bomb Problem",
        "characters": ["scientist", "robot", "human", "tiger", "bomb1", "bomb2"],
        "boat": {
            "capacity": 2,
            "requires_driver": True,
            "drivers": ["scientist", "human"]
        },
        "rules": [
            {"if_alone": ["bomb1", "bomb2"], "result": "explosion"},
            {"carry_rule": {"bomb": "only_scientist"}},
            {"robot_rule": "needs_human_to_carry_bomb"}
        ],
        "goal": "move_all_safely"
    },

    # Level 10: Ultimate Challenge (kết hợp tất cả các yếu tố)
    {
        "level": 10,
        "name": "Ultimate Challenge",
        "characters": [
            "scientist", "human", "robot",
            "tiger", "wolf", "sheep",
            "cabbage", "bomb"
        ],
        "boat": {
            "capacity": 3,
            "requires_driver": True,
            "drivers": ["scientist", "human"],
            "alternate_driver": True
        },
        "rules": [
            {"if_alone": ["tiger", "wolf"], "result": "fight"},
            {"robot_first_move": True},
            {"bomb_last_move": True},
            {"alternating_driver": ["scientist", "human"]}
        ],
        "goal": "move_all_safely"
    }
]

# Hàm helper để lấy level data
def get_level(level_num):
    """Lấy thông tin level theo số thứ tự (1-10)"""
    if 1 <= level_num <= len(levels):
        return levels[level_num - 1]
    return None

def get_all_levels():
    """Lấy tất cả các level"""
    return levels

def get_level_count():
    """Lấy số lượng level"""
    return len(levels)

def get_level_names():
    """Lấy tên của tất cả các level"""
    return [level["name"] for level in levels]

# Thông tin mô tả cho từng level (dùng cho hướng dẫn)
level_descriptions = {
    1: "Classic puzzle: Transport wolf, sheep, and cabbage across the river without anything being eaten.",
    2: "Similar to level 1 but with a tiger instead of wolf. Time pressure adds challenge.",
    3: "Extended food chain: tiger eats wolf, wolf eats sheep, sheep eats cabbage.",
    4: "Robot can drive the boat but may destroy cabbage if left alone without scientist.",
    5: "Protect humans and equipment from wild animals.",
    6: "Bomb with timer! Transport everything before it explodes.",
    7: "Robot defense system: Robot can protect against animals but needs scientist.",
    8: "Strong current: Special transport rules apply.",
    9: "Two bombs! Handle with care, only scientist can carry bombs.",
    10: "Ultimate challenge: Combine all previous rules for the hardest puzzle!"
}

def get_level_description(level_num):
    """Lấy mô tả cho level"""
    return level_descriptions.get(level_num, "No description available")