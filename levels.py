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
    "name": "Chuỗi nguy hiểm",
    "description": "Đưa tất cả qua sông. Sói ăn Cừu, Hổ ăn Sói nếu không có Người. Bom không được ở với Hổ nếu thiếu Nhà khoa học. Robot phải đi cùng Người.",

    "characters": ["person", "robot", "scientist", "wolf", "sheep", "tiger", "bomb"],

    "boat_capacity": 2,

    "rules": {
        "type": "level6_chain"
    },

    "display_names": {
        "person": "🧑 Người",
        "robot": "🤖 Robot",
        "scientist": "👨‍🔬 Nhà khoa học",
        "wolf": "🐺 Sói",
        "sheep": "🐑 Cừu",
        "tiger": "🐯 Hổ",
        "bomb": "💣 Bom"
    }
},
    7: {
    "name": "Bom hẹn giờ",
    "description": "Đưa Người, Sói, Cừu và Bom qua sông. Bom phải được đưa sang bờ bên kia trong tối đa 5 lượt. Sói không được ăn cừu khi không có người.",
    
    "characters": ["person", "wolf", "sheep", "bomb"],
    
    "boat_capacity": 2,

    # giống style level 5
    "move_limit": 5,

    "rules": {
        "type": "timed_bomb"
    },

    "display_names": {
        "person": "🧑 Người",
        "wolf": "🐺 Sói",
        "sheep": "🐑 Cừu",
        "bomb": "💣 Bom"
    }
},
    8: {
    "name": "Robot và vật nguy hiểm",
    "description": "Đưa Người, Robot, Sói, Cừu và Bom qua sông. Sói ăn Cừu nếu không có Người. Bom không được ở với Cừu nếu không có Người. Robot phải đi cùng Người.",
    
    "characters": [
        "person",
        "robot",
        "wolf",
        "sheep",
        "bomb"
    ],
    
    "boat_capacity": 2,

    "rules": {
        "type": "level8_medium_plus"
    },

    "display_names": {
        "person": "🧑 Người",
        "robot": "🤖 Robot",
        "wolf": "🐺 Sói",
        "sheep": "🐑 Cừu",
        "bomb": "💣 Bom"
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
    "bomb": "bom.png",
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
