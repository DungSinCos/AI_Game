class GameState:
    def __init__(self, characters, state=None, level=1, boat_capacity=2, rules=None, level_data=None):
        self.characters = characters
        self.level = level
        self.level_data = level_data or {}
        self.boat_capacity = boat_capacity
        self.rules = rules or {}
        self.state = state if state else tuple([0] * len(characters))
        self.cost = 0

    def is_valid(self, state=None):
        if state is None:
            state = self.state

        chars = self.characters
        idx = {c: i for i, c in enumerate(chars)}

        # LEVEL 1
        if self.level == 1:
            p, w, s, c = state
            if w == s and p != w:
                return False
            if s == c and p != s:
                return False

        # LEVEL 2
        elif self.level == 2:
            p = state[idx["person"]]
            sheep = ["sheep1", "sheep2", "sheep3"]

            for shore in [0, 1]:
                if p == shore:
                    continue

                ages = []
                for s in sheep:
                    if state[idx[s]] == shore:
                        ages.append(int(s[-1]))

                for i in range(len(ages)):
                    for j in range(i+1, len(ages)):
                        if abs(ages[i] - ages[j]) == 1:
                            return False

        # LEVEL 3
        elif self.level == 3:
            if state[idx["bom"]] != state[idx["scientist"]]:
                return False

        # LEVEL 4
        elif self.level == 4:
            p = state[idx["person"]]
            small = state[idx["box_small"]]
            medium = state[idx["box_medium"]]
            large = state[idx["box_large"]]

            for shore in [0, 1]:
                if p == shore:
                    continue
                if small == shore and medium == shore:
                    return False
                if small == shore and large == shore:
                    return False

        # LEVEL 5
        elif self.level == 5:
            p = state[idx["person"]]
            times = self.level_data["tiger_times"]

            for shore in [0, 1]:
                if p == shore:
                    continue

                fast = []
                slow = []
                has_mid = False

                for t, time in times.items():
                    if state[idx[t]] == shore:
                        if time in [1, 3]:
                            fast.append(t)
                        elif time in [8, 12]:
                            slow.append(t)
                        elif time == 6:
                            has_mid = True

                if fast and slow and not has_mid:
                    return False

        # 🔥 LEVEL 6 (FIXED)
        elif self.level == 6:
            p = state[idx["person"]]
            s = state[idx["scientist"]]
            t = state[idx["tiger"]]
            b1 = state[idx["bomb1"]]
            b2 = state[idx["bomb2"]]

            for shore in [0, 1]:
                has_p = (p == shore)
                has_s = (s == shore)
                has_t = (t == shore)
                has_b1 = (b1 == shore)
                has_b2 = (b2 == shore)

                if has_b1 and has_b2 and not has_s:
                    return False

                if has_t and has_p and not has_s:
                    return False

        return True

    def is_goal(self):
        return all(x == 1 for x in self.state)

    def move(self, move_indices):
        # 🔥 MUST HAVE PERSON
        if 0 not in move_indices:
            return None

        if len(move_indices) > self.boat_capacity:
            return None

        new_state = list(self.state)

        for i in move_indices:
            new_state[i] = 1 - new_state[i]

        new_state = tuple(new_state)

        if not self.is_valid(new_state):
            return None

        return GameState(
            self.characters,
            new_state,
            self.level,
            self.boat_capacity,
            self.rules,
            self.level_data
        )

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state
