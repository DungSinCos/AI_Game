levels = {
    1: {
        "name": "Sói, Cừu và Bắp cải",
        "description": "Đưa sói, cừu và bắp cải qua sông. Sói ăn cừu, cừu ăn bắp cải nếu không có người. Thuyền chở được 2 người/vật.",
        "characters": ["person", "wolf", "sheep", "cabbage"],
        "boat_capacity": 2,
        "rules": {
            "type": "classic",
        }
    },

    2: {
        "name": "Người và đàn cừu non",
        "description": "Đưa 3 chú cừu (1, 2, 3 tuổi) qua sông. Thuyền chở tối đa 2 cừu. Cừu hơn kém 1 tuổi không được ở cùng nhau nếu không có người.",
        "characters": ["person", "sheep1", "sheep2", "sheep3"],
        "boat_capacity": 3,  # 1 người + tối đa 2 cừu
        "rules": {
            "type": "sheep_age_constraint",
        },
        "display_names": {
            "sheep1": "🐑 Cừu 1 tuổi",
            "sheep2": "🐏 Cừu 2 tuổi",
            "sheep3": "🐑 Cừu 3 tuổi"
        }
    },

    3: {
        "name": "Nhà nghiên cứu và Robot",
        "description": "Đưa nhà nghiên cứu, bom và 2 robot qua sông. Bom phải luôn có nhà nghiên cứu giám sát. Thời gian 60 giây.",
        "characters": ["scientist", "bom", "robot1", "robot2"],
        "boat_capacity": 2,
        "time_limit": 60,  # 60 giây
        "rules": {
            "type": "dangerous",
        }
    },

    4: {
        "name": "Những chiếc thùng",
        "description": "Đưa các thùng qua sông. Thuyền chịu tải tối đa 100kg. Thùng nhỏ và thùng vừa không được ở cùng nhau. Thùng lớn và thùng nhỏ không được ở cùng nhau nếu không có người.",
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
        },
        "display_names": {
            "box_small": "📦 Thùng nhỏ (30kg)",
            "box_medium": "📦 Thùng trung (60kg)",
            "box_large": "📦 Thùng lớn (90kg)"
        }
    },

    5: {
        "name": "Bầy hổ",
        "description": "Đưa 5 con hổ qua sông (1s, 3s, 6s, 8s, 12s). Thuyền chở 2 hổ. Hổ nhanh (1s,3s) và hổ chậm (8s,12s) không được ở cùng nhau nếu không có hổ 6s. Tổng thời gian ≤ 30s.",
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
        },
        "display_names": {
            "tiger1": "🐯 Hổ nhanh (1s)",
            "tiger2": "🐯 Hổ TB1 (3s)",
            "tiger3": "🐯 Hổ TB2 (6s)",
            "tiger4": "🐯 Hổ chậm (8s)",
            "tiger5": "🐯 Hổ rất chậm (12s)"
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