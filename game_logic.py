class GameState:
    def __init__(self, state=(0,0,0,0), level=1, description=""):
        self.state = state
        self.level = level
        self.description = description

    def is_valid(self, state):
        p, w, s, c = state
        if w == s and p != w:
            return False
        if s == c and p != s:
            return False
        return True

    def is_goal(self):
        return self.state == (1,1,1,1)

    def move(self, move_idx):
        new_state = list(self.state)
        # người luôn đi
        new_state[0] = 1 - new_state[0]
        # vật đi cùng
        for idx in move_idx:
            if idx != 0:
                new_state[idx] = 1 - new_state[idx]
        if not self.is_valid(new_state):
            return None
        return GameState(tuple(new_state), self.level, self.description)