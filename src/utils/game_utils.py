import random
import numpy as np
from typing import List, Dict

class GameUtils:
    @staticmethod
    def generate_player_name() -> str:
        first_names = ['James', 'Michael', 'Kevin', 'Stephen', 'LeBron', 'Kobe', 'Tim', 'Shaquille', 
                      'Magic', 'Larry', 'John', 'Wilt', 'Bill', 'Kareem', 'Hakeem']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def generate_player_stats() -> Dict:
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        position = random.choice(positions)
        
        # 根据位置生成基础能力值
        base_stats = {
            'PG': {'speed': 85, 'shooting': 80, 'passing': 85, 'defense': 70, 'rebounding': 60},
            'SG': {'speed': 80, 'shooting': 85, 'passing': 75, 'defense': 75, 'rebounding': 65},
            'SF': {'speed': 75, 'shooting': 80, 'passing': 70, 'defense': 80, 'rebounding': 75},
            'PF': {'speed': 70, 'shooting': 75, 'passing': 65, 'defense': 80, 'rebounding': 85},
            'C': {'speed': 65, 'shooting': 70, 'passing': 60, 'defense': 85, 'rebounding': 90}
        }

        # 添加随机波动
        stats = base_stats[position].copy()
        for stat in stats:
            stats[stat] += random.randint(-10, 10)
            stats[stat] = max(40, min(99, stats[stat]))  # 确保能力值在40-99之间

        # 计算总评
        overall = int(np.mean(list(stats.values())))

        return {
            'name': GameUtils.generate_player_name(),
            'position': position,
            'overall': overall,
            'stats': stats,
            'age': random.randint(19, 22),  # 新秀年龄
            'salary': random.randint(800000, 2000000)  # 新秀合同
        }

    @staticmethod
    def simulate_game(team1_players: List[Dict], team2_players: List[Dict]) -> Dict:
        # 计算两队平均能力值
        team1_avg = np.mean([p['overall'] for p in team1_players])
        team2_avg = np.mean([p['overall'] for p in team2_players])

        # 添加随机因素
        team1_score = int(team1_avg * 0.8 + random.randint(60, 120))
        team2_score = int(team2_avg * 0.8 + random.randint(60, 120))

        return {
            'team1_score': team1_score,
            'team2_score': team2_score,
            'winner': 1 if team1_score > team2_score else 2
        }

    @staticmethod
    def calculate_standings(teams: List[Dict]) -> List[Dict]:
        # 按胜率排序
        sorted_teams = sorted(teams, key=lambda x: (x['wins'] / (x['wins'] + x['losses'])), reverse=True)
        return sorted_teams 