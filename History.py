import json
import os
from datetime import datetime
from typing import List, Dict


class HistoryManager:
    def __init__(self, history_file="algorithm_history.json"):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> List[Dict]:
        """Tải lịch sử từ file JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """Lưu lịch sử vào file JSON"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_record(self, level: int, algorithm: str, exec_time: float,
                   states_explored: int, solution_length: int = None,
                   cost: int = None):
        """Thêm một bản ghi mới vào lịch sử"""
        record = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "level_name": self.get_level_name(level),
            "algorithm": algorithm,
            "execution_time": round(exec_time, 6),
            "states_explored": states_explored,
            "solution_length": solution_length,
            "cost": cost
        }
        self.history.append(record)
        self.save_history()

    def get_level_name(self, level: int) -> str:
        """Lấy tên level từ levels.py"""
        from levels import levels
        return levels.get(level, {}).get("name", f"Level {level}")

    def get_history(self, level: int = None, algorithm: str = None) -> List[Dict]:
        """Lấy lịch sử với bộ lọc"""
        filtered = self.history
        if level is not None:
            filtered = [r for r in filtered if r["level"] == level]
        if algorithm is not None:
            filtered = [r for r in filtered if r["algorithm"] == algorithm]
        return filtered

    def clear_history(self):
        """Xóa toàn bộ lịch sử"""
        self.history = []
        self.save_history()

    def get_recent_history(self, level: int = None, limit: int = 5) -> List[Dict]:
        """Lấy lịch sử gần đây nhất"""
        filtered = self.get_history(level=level)
        return filtered[-limit:] if filtered else []

    def get_level_performance(self, level: int) -> Dict:
        """Lấy hiệu suất tổng hợp cho một level"""
        history = self.get_history(level=level)
        if not history:
            return {}

        result = {}
        for record in history:
            algo = record["algorithm"]
            if algo not in result:
                result[algo] = {
                    "count": 0,
                    "times": [],
                    "nodes": []
                }
            result[algo]["count"] += 1
            result[algo]["times"].append(record["execution_time"])
            result[algo]["nodes"].append(record["states_explored"])

        # Tính toán thống kê
        for algo in result:
            result[algo]["avg_time"] = sum(result[algo]["times"]) / len(result[algo]["times"])
            result[algo]["min_time"] = min(result[algo]["times"])
            result[algo]["max_time"] = max(result[algo]["times"])
            result[algo]["avg_nodes"] = sum(result[algo]["nodes"]) / len(result[algo]["nodes"])

        return result

    def get_statistics(self, level: int = None) -> Dict:
        """Thống kê hiệu suất các thuật toán"""
        filtered = self.get_history(level=level)
        stats = {}

        for record in filtered:
            algo = record["algorithm"]
            if algo not in stats:
                stats[algo] = {
                    "count": 0,
                    "avg_time": 0,
                    "min_time": float('inf'),
                    "max_time": 0,
                    "avg_states": 0,
                    "total_time": 0,
                    "total_states": 0
                }

            stats[algo]["count"] += 1
            stats[algo]["total_time"] += record["execution_time"]
            stats[algo]["total_states"] += record["states_explored"]
            stats[algo]["min_time"] = min(stats[algo]["min_time"], record["execution_time"])
            stats[algo]["max_time"] = max(stats[algo]["max_time"], record["execution_time"])

        # Tính trung bình
        for algo in stats:
            stats[algo]["avg_time"] = stats[algo]["total_time"] / stats[algo]["count"]
            stats[algo]["avg_states"] = stats[algo]["total_states"] / stats[algo]["count"]
            # Làm tròn
            stats[algo]["avg_time"] = round(stats[algo]["avg_time"], 6)
            stats[algo]["avg_states"] = round(stats[algo]["avg_states"], 2)
            stats[algo]["min_time"] = round(stats[algo]["min_time"], 6)
            stats[algo]["max_time"] = round(stats[algo]["max_time"], 6)

        return stats


# Tạo instance toàn cục
history_manager = HistoryManager()