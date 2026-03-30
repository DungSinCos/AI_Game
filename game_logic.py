class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = state if state else tuple([0] * len(characters))
        self.cost = 0  # for UCS and A*

    def is_valid(self, state=None):
        if state is None:
            state = self.state

        # Level 1: Classic wolf-sheep-cabbage
        if self.level == 1:
            p, w, s, c = state
            # Sói ăn cừu nếu không có người
            if w == s and p != w:
                return False
            # Cừu ăn bắp cải nếu không có người
            if s == c and p != s:
                return False

        # Level 2: Sheep age constraint - Cừu hơn kém 1 tuổi không được ở cùng nhau nếu không có người
        elif self.level == 2:
            chars = self.characters
            idx = {c: i for i, c in enumerate(chars)}
            person_pos = state[idx["person"]]

            # Lấy vị trí và tuổi của từng con cừu
            sheep_ages = {
                "sheep1": 1,
                "sheep2": 2,
                "sheep3": 3
            }

            # Kiểm tra từng bờ
            for shore in [0, 1]:
                # Nếu người ở bờ này, không cần kiểm tra
                if person_pos == shore:
                    continue

                # Lấy danh sách cừu ở bờ này
                sheep_on_shore = []
                for sheep_name, age in sheep_ages.items():
                    if sheep_name in idx and state[idx[sheep_name]] == shore:
                        sheep_on_shore.append((sheep_name, age))

                # Kiểm tra các cặp cừu có chênh lệch tuổi = 1
                for i in range(len(sheep_on_shore)):
                    for j in range(i + 1, len(sheep_on_shore)):
                        age_diff = abs(sheep_on_shore[i][1] - sheep_on_shore[j][1])
                        # Nếu chênh lệch = 1, chúng đánh nhau
                        if age_diff == 1:
                            return False

        # Level 3: Scientist and bomb - Bom phải có nhà nghiên cứu giám sát
        elif self.level == 3:
            chars = self.characters
            idx = {c: i for i, c in enumerate(chars)}
            scientist_pos = state[idx["scientist"]]
            bom_pos = state[idx["bom"]]

            # Bom không được ở một mình hoặc đi cùng người hỗ trợ mà thiếu nhà nghiên cứu
            if bom_pos != scientist_pos:
                return False

        # Level 4: Box constraints - Thùng không được ở cùng nhau nếu không có người
        elif self.level == 4:
            chars = self.characters
            idx = {c: i for i, c in enumerate(chars)}
            person_pos = state[idx["person"]]

            # Lấy vị trí các thùng
            box_small_pos = state[idx.get("box_small", -1)] if "box_small" in idx else None
            box_medium_pos = state[idx.get("box_medium", -1)] if "box_medium" in idx else None
            box_large_pos = state[idx.get("box_large", -1)] if "box_large" in idx else None

            # Kiểm tra từng bờ
            for shore in [0, 1]:
                # Nếu người ở bờ này, không cần kiểm tra
                if person_pos == shore:
                    continue

                # Kiểm tra thùng nhỏ và thùng vừa ở cùng nhau
                if box_small_pos is not None and box_medium_pos is not None:
                    if box_small_pos == shore and box_medium_pos == shore:
                        return False

                # Kiểm tra thùng lớn và thùng nhỏ ở cùng nhau
                if box_large_pos is not None and box_small_pos is not None:
                    if box_large_pos == shore and box_small_pos == shore:
                        return False

        # Level 5: Tiger constraints - Hổ nhanh và hổ chậm không được ở cùng nhau nếu không có hổ trung gian
        elif self.level == 5:
            chars = self.characters
            idx = {c: i for i, c in enumerate(chars)}
            person_pos = state[idx["person"]]

            # Lấy vị trí và thời gian của từng con hổ
            tiger_times = self.level_data.get("tiger_times", {})
            tiger_data = {}
            for i, char in enumerate(chars):
                if char.startswith("tiger"):
                    tiger_data[char] = {
                        "pos": state[i],
                        "time": tiger_times.get(char, 1)
                    }

            # Kiểm tra từng bờ
            for shore in [0, 1]:
                # Nếu người ở bờ này, không cần kiểm tra
                if person_pos == shore:
                    continue

                # Lấy danh sách hổ ở bờ này
                tigers_on_shore = []
                for name, data in tiger_data.items():
                    if data["pos"] == shore:
                        tigers_on_shore.append((name, data["time"]))

                # Kiểm tra: hổ nhanh (1s, 3s) và hổ chậm (8s, 12s) không được ở cùng nhau nếu không có hổ 6s
                fast_tigers = [t for t in tigers_on_shore if t[1] in [1, 3]]
                slow_tigers = [t for t in tigers_on_shore if t[1] in [8, 12]]
                has_medium = any(t[1] == 6 for t in tigers_on_shore)

                if fast_tigers and slow_tigers and not has_medium:
                    return False

        return True

    def is_goal(self):
        return all(x == 1 for x in self.state)

    def get_weight(self, items):
        """Tính tổng trọng lượng của các vật được chọn (Level 4)"""
        if self.level != 4:
            return 0

        weights = self.level_data.get("weights", {})
        total = 0
        for item in items:
            if item != "person":  # person không tính trọng lượng
                total += weights.get(item, 0)
        return total

    def get_max_time(self, items):
        """Tính thời gian di chuyển dựa trên vật chậm nhất (Level 5)"""
        if self.level != 5:
            return 0

        tiger_times = self.level_data.get("tiger_times", {})
        max_time = 0
        for item in items:
            if item != "person":  # person không tính thời gian
                max_time = max(max_time, tiger_times.get(item, 1))
        return max_time

    def move(self, move_indices):
        """
        move_indices: list of indices to move (includes person)
        """
        # Kiểm tra sức chứa thuyền
        if len(move_indices) > self.boat_capacity:
            return None

        # Level 2: Kiểm tra không được chở quá 2 cừu
        if self.level == 2:
            chars = self.characters
            sheep_count = sum(1 for idx in move_indices if idx != 0 and chars[idx].startswith("sheep"))
            if sheep_count > 2:
                return None

        # Level 4: Kiểm tra trọng lượng
        if self.level == 4:
            item_names = [self.characters[i] for i in move_indices]
            total_weight = self.get_weight(item_names)
            weight_limit = self.level_data.get("weight_limit", 100)
            if total_weight > weight_limit:
                return None

        # Level 5: Kiểm tra thời gian không vượt quá giới hạn
        if self.level == 5:
            item_names = [self.characters[i] for i in move_indices]
            move_time = self.get_max_time(item_names)
            time_limit = self.level_data.get("time_limit", float('inf'))
            if self.cost + move_time > time_limit:
                return None

        new_state = list(self.state)
        # Đảo vị trí người và các vật được chọn
        new_state[0] = 1 - new_state[0]  # person always moves

        for idx in move_indices:
            if idx != 0:  # không đảo person lần nữa
                new_state[idx] = 1 - new_state[idx]

        new_state = tuple(new_state)

        if not self.is_valid(new_state):
            return None

        # Tính cost cho Level 5 (thời gian)
        new_cost = self.cost
        if self.level == 5:
            item_names = [self.characters[i] for i in move_indices]
            max_time = self.get_max_time(item_names)
            new_cost = self.cost + max_time

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )
        new_state_obj.cost = new_cost
        return new_state_obj

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state