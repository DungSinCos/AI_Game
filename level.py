# --- Cấu hình 10 level Qua sông IQ ---
levels = {
    1: {"max_moves": None, "description": "Cơ bản, không giới hạn lượt"},
    2: {"max_moves": 7, "description": "Giới hạn 7 lượt"},
    3: {"max_moves": None, "description": "Thuyền không thể chở Cừu 1 lượt bất kỳ"},
    4: {"max_moves": None, "description": "Không được đưa Bắp cải trước Cừu"},
    5: {"max_moves": 6, "description": "Giới hạn lượt chặt chẽ"},
    6: {"max_moves": None, "description": "Thuyền không thể chở Cừu và Sói cùng lúc"},
    7: {"max_moves": None, "description": "Sói ăn Cừu nếu ở cùng bờ >1 lượt"},
    8: {"max_moves": None, "description": "Thuyền phải quay lại ngay sau khi chở vật"},
    9: {"max_moves": None, "description": "Có 2 thuyền, mỗi thuyền chỉ chở 1 vật"},
    10: {"max_moves": 5, "description": "Level tổng hợp, cực khó"}
}
