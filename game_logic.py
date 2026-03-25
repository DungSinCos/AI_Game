# game_logic.py
import copy


class GameState:
    def __init__(self, level_data, state=None):
        """
        Khởi tạo trạng thái game
        level_data: dữ liệu level từ levels.py
        state: tuple trạng thái hiện tại (vị trí của các nhân vật)
        """
        self.level_data = level_data
        self.level = level_data["level"]
        self.characters = level_data["characters"]
        self.boat_config = level_data["boat"]
        self.rules = level_data["rules"]
        self.goal = level_data["goal"]
        self.extra = level_data.get("extra", {})

        # Khởi tạo trạng thái (0: bờ trái, 1: bờ phải)
        if state is None:
            self.state = tuple([0] * len(self.characters))
        else:
            self.state = state

        # Mapping tên nhân vật sang index
        self.name_to_idx = {name: idx for idx, name in enumerate(self.characters)}
        self.idx_to_name = {idx: name for name, idx in self.name_to_idx.items()}

        # Biến đặc biệt cho timer
        self.bomb_timer = self.extra.get("bomb_timer", None)
        self.steps = 0

    def is_valid(self, state):
        """Kiểm tra trạng thái có hợp lệ không (không vi phạm luật)"""
        # Chuyển state từ tuple sang dict để dễ xử lý
        state_dict = {self.characters[i]: state[i] for i in range(len(self.characters))}

        # Kiểm tra từng rule
        for rule in self.rules:
            # Rule dạng {"if_alone": ["wolf", "sheep"], "result": "sheep_eaten"}
            if "if_alone" in rule:
                alone_chars = rule["if_alone"]
                # Kiểm tra xem các nhân vật này có ở cùng bờ không
                if self._are_together(state_dict, alone_chars):
                    # Kiểm tra điều kiện unless_present
                    unless_present = rule.get("unless_present", [])
                    if unless_present:
                        # Nếu có nhân vật bảo vệ ở cùng bờ thì không vi phạm
                        if self._is_any_present(state_dict, unless_present, state_dict[alone_chars[0]]):
                            continue
                    return False

            # Rule dạng {"robot_behavior": "kills_animals_if_no_scientist"}
            elif "robot_behavior" in rule:
                if "kills_animals_if_no_scientist" in rule["robot_behavior"]:
                    # Kiểm tra robot và scientist
                    robot_side = state_dict.get("robot")
                    scientist_side = state_dict.get("scientist")
                    if robot_side is not None and scientist_side is not None:
                        if robot_side != scientist_side:
                            # Robot ở bờ không có scientist, kiểm tra có động vật không
                            for char in ["tiger", "wolf", "sheep"]:
                                if char in state_dict and state_dict[char] == robot_side:
                                    return False

            # Rule dạng {"if_transport": ["human", "tiger"], "require": ["scientist"]}
            elif "if_transport" in rule:
                # Rule này sẽ được kiểm tra trong hàm move
                pass

            # Rule dạng {"carry_rule": {"bomb": "only_scientist"}}
            elif "carry_rule" in rule:
                # Rule này sẽ được kiểm tra trong hàm move
                pass

            # Rule dạng {"robot_rule": "needs_human_to_carry_bomb"}
            elif "robot_rule" in rule:
                # Rule này sẽ được kiểm tra trong hàm move
                pass

        return True

    def _are_together(self, state_dict, characters):
        """Kiểm tra các nhân vật có ở cùng bờ không"""
        if not characters:
            return False
        first_side = state_dict.get(characters[0])
        if first_side is None:
            return False
        return all(state_dict.get(char, first_side) == first_side for char in characters)

    def _is_any_present(self, state_dict, characters, side):
        """Kiểm tra có bất kỳ nhân vật nào ở bờ side không"""
        return any(state_dict.get(char) == side for char in characters)

    def _check_transport_rules(self, move_indices, from_side):
        """Kiểm tra rule vận chuyển"""
        move_names = [self.idx_to_name[i] for i in move_indices]

        for rule in self.rules:
            if "if_transport" in rule:
                transport_chars = rule["if_transport"]
                require_chars = rule["require"]

                # Kiểm tra xem có vận chuyển cặp nhân vật này không
                if all(char in move_names for char in transport_chars):
                    # Kiểm tra xem có nhân vật yêu cầu ở cùng bờ không
                    state_dict = {self.characters[i]: self.state[i] for i in range(len(self.characters))}
                    if not any(state_dict.get(char) == from_side for char in require_chars):
                        return False
        return True

    def _check_carry_rules(self, move_indices, move_names):
        """Kiểm tra rule mang vác"""
        for rule in self.rules:
            if "carry_rule" in rule:
                carry_rule = rule["carry_rule"]
                for item, condition in carry_rule.items():
                    if item in move_names:
                        if condition == "only_scientist" and "scientist" not in move_names:
                            return False

        for rule in self.rules:
            if "robot_rule" in rule:
                if "needs_human_to_carry_bomb" in rule["robot_rule"]:
                    if "robot" in move_names and "bomb" in move_names:
                        if "human" not in move_names and "scientist" not in move_names:
                            return False
        return True

    def move(self, move_indices):
        """
        Thực hiện di chuyển
        move_indices: danh sách index các nhân vật lên thuyền
        """
        # Kiểm tra có người lái không
        driver_required = self.boat_config.get("requires_driver", False)
        drivers = self.boat_config.get("drivers", [])

        if driver_required:
            driver_names = [self.idx_to_name[i] for i in move_indices]
            if not any(driver in driver_names for driver in drivers):
                return None

        # Kiểm tra sức chứa thuyền
        capacity = self.boat_config.get("capacity", 2)
        if len(move_indices) > capacity:
            return None

        # Kiểm tra tất cả nhân vật di chuyển phải ở cùng bờ
        current_side = self.state[move_indices[0]]
        if not all(self.state[i] == current_side for i in move_indices):
            return None

        # Kiểm tra rule vận chuyển
        if not self._check_transport_rules(move_indices, current_side):
            return None

        # Tạo trạng thái mới
        new_state = list(self.state)
        move_names = [self.idx_to_name[i] for i in move_indices]

        # Kiểm tra rule mang vác
        if not self._check_carry_rules(move_indices, move_names):
            return None

        # Di chuyển các nhân vật
        for idx in move_indices:
            new_state[idx] = 1 - new_state[idx]

        new_state = tuple(new_state)

        # Kiểm tra tính hợp lệ
        if not self.is_valid(new_state):
            return None

        # Tạo GameState mới
        new_game = GameState(self.level_data, new_state)
        new_game.bomb_timer = self.bomb_timer
        new_game.steps = self.steps + 1

        # Cập nhật bomb timer nếu có
        if self.extra.get("bomb_timer") is not None:
            if "bomb" in self.name_to_idx:
                bomb_idx = self.name_to_idx["bomb"]
                if new_state[bomb_idx] == 1:  # Bomb đã qua sông
                    new_game.bomb_timer = None  # Vô hiệu hóa timer
                else:
                    new_game.bomb_timer = self.bomb_timer - 1
                    if new_game.bomb_timer <= 0:
                        return None  # Bomb nổ

        return new_game

    def is_goal(self):
        """Kiểm tra đã thắng chưa"""
        if self.goal == "move_all_safely":
            # Tất cả nhân vật ở bờ phải
            return all(side == 1 for side in self.state)

        # Thêm các điều kiện goal khác nếu cần
        return False

    def get_boat_side(self):
        """Lấy bờ hiện tại của thuyền (dựa vào vị trí người lái)"""
        drivers = self.boat_config.get("drivers", [])
        for driver in drivers:
            if driver in self.name_to_idx:
                return self.state[self.name_to_idx[driver]]
        return 0

    def get_characters_on_side(self, side):
        """Lấy danh sách nhân vật ở một bờ"""
        return [self.characters[i] for i in range(len(self.characters)) if self.state[i] == side]

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.state == other.state and self.level == other.level

    def __hash__(self):
        return hash((self.state, self.level))

    def __str__(self):
        return f"Level {self.level}: {self.state}"