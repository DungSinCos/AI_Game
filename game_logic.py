class GameState:
    def __init__(self, state=(0,0,0,0)):
        self.state = state

    def is_valid(self):
        p, w, s, c = self.state
        if w == s and p != w:
            return False
        if s == c and p != s:
            return False
        return True

    def is_goal(self):
        return self.state == (1,1,1,1)

    def move(self, selected):
        p, w, s, c = self.state
        new = list(self.state)

        # đổi phía người
        new[0] = 1 - p

        # chở vật
        for item in selected:
            idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}[item]
            new[idx] = 1 - new[idx]

        new_state = GameState(tuple(new))
        return new_state if new_state.is_valid() else None