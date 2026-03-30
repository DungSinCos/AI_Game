class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = state if state else tuple([0] * len(characters))
        self.cost = 0
        self.moves = 0  # dùng cho level 7

    def is_valid(self, state=None):
        if state is None:
            state = self.state

        # ===== LEVEL 1 =====
        if self.level == 1:
            p, w, s, c = state
            if w == s and p != w:
                return False
            if s == c and p != s:
                return False

        # ===== LEVEL 2 =====
        elif self.level == 2:
            idx = {c: i for i, c in enumerate(self.characters)}
            person_pos = state[idx["person"]]
            sheep_ages = {"sheep1": 1, "sheep2": 2, "sheep3": 3}

            for shore in [0, 1]:
                if person_pos == shore:
                    continue

                sheep = []
                for name, age in sheep_ages.items():
                    if name in idx and state[idx[name]] == shore:
                        sheep.append((name, age))

                for i in range(len(sheep)):
                    for j in range(i + 1, len(sheep)):
                        if abs(sheep[i][1] - sheep[j][1]) == 1:
                            return False

        # ===== LEVEL 3 =====
        elif self.level == 3:
            idx = {c: i for i, c in enumerate(self.characters)}
            if state[idx["bom"]] != state[idx["scientist"]]:
                return False

        # ===== LEVEL 4 =====
        elif self.level == 4:
            idx = {c: i for i, c in enumerate(self.characters)}
            person_pos = state[idx["person"]]

            for shore in [0, 1]:
                if person_pos == shore:
                    continue

                if state[idx["box_small"]] == shore and state[idx["box_medium"]] == shore:
                    return False

                if state[idx["box_small"]] == shore and state[idx["box_large"]] == shore:
                    return False

        # ===== LEVEL 5 =====
        elif self.level == 5:
            idx = {c: i for i, c in enumerate(self.characters)}
            person_pos = state[idx["person"]]
            tiger_times = self.level_data.get("tiger_times", {})

            for shore in [0, 1]:
                if person_pos == shore:
                    continue

                times = [
                    tiger_times[c]
                    for c in self.characters
                    if c.startswith("tiger") and state[idx[c]] == shore
                ]

                if any(t in [1, 3] for t in times) and any(t in [8, 12] for t in times) and 6 not in times:
                    return False

        # ===== LEVEL 6 =====
        elif self.level == 6:
            idx = {c: i for i, c in enumerate(self.characters)}

            p = state[idx["person"]]
            s = state[idx["scientist"]]
            r = state[idx["robot"]]
            t = state[idx["tiger"]]
            b1 = state[idx["bomb1"]]
            b2 = state[idx["bomb2"]]

            if b1 == b2:
                return False

            for b in [b1, b2]:
                if r == b and p != r:
                    return False

            for shore in [0, 1]:
                if t == shore:
                    if p == shore and s != shore and r != shore:
                        return False
                    if s == shore and p != shore and r != shore:
                        return False

        # ===== LEVEL 7 =====
        elif self.level == 7:
            idx = {c: i for i, c in enumerate(self.characters)}

            p = state[idx["person"]]
            w = state[idx["wolf"]]
            s = state[idx["sheep"]]
            b = state[idx["bomb"]]

            if w == s and p != w:
                return False

            limit = self.level_data.get("move_limit", 5)
            if b == 0 and self.moves >= limit:
                return False

        # ===== LEVEL 8 (FINAL - ĐÃ FIX) =====
        elif self.level == 8:
            idx = {c: i for i, c in enumerate(self.characters)}
            person_pos = state[idx["person"]]

            pairs = [
                ("sheep1", "cabbage1"),
                ("sheep2", "cabbage2"),
                ("sheep3", "cabbage3")
            ]

            for shore in [0, 1]:
                # có người → an toàn
                if person_pos == shore:
                    continue

                # danh sách cừu ở bờ
                sheep_on = [s for s, _ in pairs if state[idx[s]] == shore]

                for sheep, cabbage in pairs:
                    cabbage_pos = state[idx[cabbage]]
                    sheep_pos = state[idx[sheep]]

                    # bắp ở đây nhưng thiếu cừu của nó
                    if cabbage_pos == shore and sheep_pos != shore:
                        # nếu có bất kỳ cừu nào → nguy hiểm
                        if len(sheep_on) > 0:
                            return False

        return True

    def is_goal(self):
        return all(x == 1 for x in self.state)

    def get_weight(self, items):
        if self.level != 4:
            return 0
        weights = self.level_data.get("weights", {})
        return sum(weights.get(i, 0) for i in items if i != "person")

    def get_max_time(self, items):
        if self.level != 5:
            return 0
        times = self.level_data.get("tiger_times", {})
        return max([times.get(i, 1) for i in items if i != "person"], default=0)

    def move(self, move_indices):
        if len(move_indices) > self.boat_capacity:
            return None

        chars = self.characters

        # Level 2
        if self.level == 2:
            sheep_count = sum(1 for i in move_indices if i != 0 and chars[i].startswith("sheep"))
            if sheep_count > 2:
                return None

        # Level 4
        if self.level == 4:
            items = [chars[i] for i in move_indices]
            if self.get_weight(items) > self.level_data.get("weight_limit", 100):
                return None

        # Level 5
        if self.level == 5:
            items = [chars[i] for i in move_indices]
            time = self.get_max_time(items)
            if self.cost + time > self.level_data.get("time_limit", float('inf')):
                return None

        # Level 6
        if self.level == 6:
            moving = [chars[i] for i in move_indices]

            if "bomb1" in moving and "bomb2" in moving:
                return None

            for bomb in ["bomb1", "bomb2"]:
                if bomb in moving:
                    if "scientist" not in moving:
                        if "robot" in moving and "person" in moving:
                            continue
                        return None

            if "robot" in moving and ("bomb1" in moving or "bomb2" in moving):
                if "person" not in moving:
                    return None

        # tạo state mới
        new_state = list(self.state)
        new_state[0] = 1 - new_state[0]

        for i in move_indices:
            if i != 0:
                new_state[i] = 1 - new_state[i]

        new_state = tuple(new_state)

        if not self.is_valid(new_state):
            return None

        new_cost = self.cost
        if self.level == 5:
            items = [chars[i] for i in move_indices]
            new_cost += self.get_max_time(items)

        new_moves = self.moves
        if self.level == 7:
            new_moves += 1

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )

        new_state_obj.cost = new_cost
        new_state_obj.moves = new_moves

        return new_state_obj

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state