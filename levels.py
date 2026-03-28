# levels.py
levels = {
    1: {
        "name": "Sói, Cừu và Bắp cải",
        "description": "Đưa sói, cừu và bắp cải qua sông mà không để sói ăn cừu hoặc cừu ăn bắp cải",
        "characters": ["person", "wolf", "sheep", "cabbage"],
        "boat_capacity": 2,
        "rules": {
            "type": "classic",
            "constraints": [
                {"predator": "wolf", "prey": "sheep"},
                {"predator": "sheep", "prey": "cabbage"}
            ]
        }
    },

    2: {
        "name": "Ba chú cừu non",
        "description": "Đưa 3 chú cừu qua sông, thuyền chở được 3 người/vật",
        "characters": ["person", "sheep1", "sheep2", "sheep3"],
        "boat_capacity": 3,
        "rules": {
            "type": "no_constraint",
        }
    },

    3: {
        "name": "Nhà nghiên cứu và Robot",
        "description": "Đưa nhà nghiên cứu, bom và 2 robot qua sông. Không để bom và robot ở cùng bờ không có người",
        "characters": ["scientist", "bom", "robot1", "robot2"],
        "boat_capacity": 2,
        "rules": {
            "type": "dangerous",
            "dangerous_items": ["bom"],
            "protected_by": "scientist"
        }
    },

    4: {
        "name": "Những chiếc thùng",
        "description": "Đưa các thùng qua sông. Thuyền chịu tải tối đa 100kg",
        "characters": ["person", "box_small", "box_medium", "box_large"],
        "boat_capacity": 3,
        "weight_limit": 100,
        "weights": {
            "box_small": 30,
            "box_medium": 60,
            "box_large": 90
        },
        "rules": {
            "type": "weight_limit"
        }
    },

    5: {
        "name": "Bầy hổ",
        "description": "Đưa 5 con hổ qua sông. Mỗi con hổ có tốc độ khác nhau. Tối ưu thời gian",
        "characters": ["person", "tiger1", "tiger2", "tiger3", "tiger4", "tiger5"],
        "boat_capacity": 2,
        "time_limit": 30,
        "tiger_times": {
            "tiger1": 1,
            "tiger2": 3,
            "tiger3": 6,
            "tiger4": 8,
            "tiger5": 12
        },
        "rules": {
            "type": "time_cost"
        }
    }
}

# Map nhân vật với ảnh
IMAGE_MAP = {
    "person": "person.png",
    "scientist": "scientist.png",
    "wolf": "wolf.png",
    "sheep": "sheep.png",
    "sheep1": "sheep.png",
    "sheep2": "sheep.png",
    "sheep3": "sheep.png",
    "cabbage": "cabbage.png",
    "bom": "bom.png",
    "robot1": "robot.png",
    "robot2": "robot.png",
    "box_small": "box.png",
    "box_medium": "box.png",
    "box_large": "box.png",
    "tiger1": "tiger.png",
    "tiger2": "tiger.png",
    "tiger3": "tiger.png",
    "tiger4": "tiger.png",
    "tiger5": "tiger.png"
}