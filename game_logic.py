class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {"type": "classic"}
        self.state = state if state else tuple([0] * len(characters))
        self.cost = 0
        self.moves = 0

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

        # ===== LEVEL 6 (CHAIN LOGIC) =====
        elif self.level == 6:
            idx = {c: i for i, c in enumerate(self.characters)}

            p = state[idx["person"]]
            r = state[idx["robot"]]
            s = state[idx["scientist"]]
            w = state[idx["wolf"]]
            sh = state[idx["sheep"]]
            t = state[idx["tiger"]]
            b = state[idx["bomb"]]

            for shore in [0, 1]:

                # 🐺 Sói ăn cừu
                if w == shore and sh == shore and p != shore:
                    return False

                # 🐯 Hổ ăn sói
                if t == shore and w == shore and p != shore:
                    return False

                # 💣 Bom + Hổ cần scientist
                if b == shore and t == shore and s != shore:
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

        # ===== LEVEL 8 =====
        elif self.level == 8:
            idx = {c: i for i, c in enumerate(self.characters)}

            p = state[idx["person"]]
            w = state[idx["wolf"]]
            s = state[idx["sheep"]]
            b = state[idx["bomb"]]

            if w == s and p != w:
                return False

            if b == s and p != b:
                return False

        return True

    def is_goal(self):
        return all(x == 1 for x in self.state)

    def move(self, move_indices):
        if len(move_indices) > self.boat_capacity:
            return None

        chars = self.characters

        # ===== LEVEL 6 =====
        if self.level == 6:
            moving = [chars[i] for i in move_indices]

            # 🤖 Robot phải đi cùng người
            if "robot" in moving and "person" not in moving:
                return None

        # ===== LEVEL 8 =====
        if self.level == 8:
            moving = [chars[i] for i in move_indices]

            if "robot" in moving and "person" not in moving:
                return None

        # ===== tạo state mới =====
        new_state = list(self.state)
        new_state[0] = 1 - new_state[0]

        for i in move_indices:
            if i != 0:
                new_state[i] = 1 - new_state[i]

        new_state = tuple(new_state)

        if not self.is_valid(new_state):
            return None

        new_state_obj = GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )

        return new_state_obj

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state
