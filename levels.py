levels = {
    1: {
        "name": "Sói, Cừu và Bắp cải",
        "description": "Đưa sói, cừu và bắp cải qua sông.",
        "characters": ["person", "wolf", "sheep", "cabbage"],
        "boat_capacity": 2,
        "rules": {"type": "classic"}
    },

    2: {
        "name": "Người và đàn cừu",
        "description": "Cừu hơn kém 1 tuổi không được ở cùng nếu không có người.",
        "characters": ["person", "sheep1", "sheep2", "sheep3"],
        "boat_capacity": 3,
        "rules": {"type": "sheep"}
    },

    3: {
        "name": "Nhà khoa học và bom",
        "description": "Bom phải đi cùng nhà khoa học.",
        "characters": ["person", "scientist", "bom", "robot1", "robot2"],
        "boat_capacity": 2,
        "rules": {"type": "danger"}
    },

    4: {
        "name": "Những chiếc thùng",
        "description": "Thùng nhỏ không được ở với thùng vừa/lớn nếu không có người.",
        "characters": ["person", "box_small", "box_medium", "box_large"],
        "boat_capacity": 3,
        "weights": {
            "box_small": 30,
            "box_medium": 60,
            "box_large": 90
        },
        "weight_limit": 100,
        "rules": {"type": "weight"}
    },

    5: {
        "name": "Bầy hổ",
        "description": "Hổ nhanh và chậm không được ở cùng nếu thiếu hổ 6s.",
        "characters": ["person", "tiger1", "tiger2", "tiger3", "tiger4", "tiger5"],
        "boat_capacity": 2,
        "tiger_times": {
            "tiger1": 1,
            "tiger2": 3,
            "tiger3": 6,
            "tiger4": 8,
            "tiger5": 12
        },
        "time_limit": 30,
        "rules": {"type": "time"}
    },

    6: {
        "name": "Bom, Hổ và Nhà khoa học",
        "description": "Hai bom không được ở cùng nếu không có nhà khoa học. Hổ không ở với người nếu thiếu nhà khoa học.",
        "characters": ["person", "scientist", "robot", "tiger", "bomb1", "bomb2"],
        "boat_capacity": 3,
        "rules": {"type": "level6"}
    }
}

# 🔥 PHẢI TÁCH RA NGOÀI
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

    "bomb1": "bom.png",
    "bomb2": "bom.png",

    "robot": "robot.png",
    "robot1": "robot.png",
    "robot2": "robot.png",

    "box_small": "box.png",
    "box_medium": "box.png",
    "box_large": "box.png",

    "tiger": "tiger.png",
    "tiger1": "tiger.png",
    "tiger2": "tiger.png",
    "tiger3": "tiger.png",
    "tiger4": "tiger.png",
    "tiger5": "tiger.png"
}
