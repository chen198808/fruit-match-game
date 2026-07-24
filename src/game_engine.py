"""
水果消消乐 - 核心游戏引擎
匹配3个及以上相同水果即可消除
"""

import random
from typing import List, Tuple, Set

# 水果类型
FRUITS = ['🍎', '🍊', '🍋', '🍇', '🍓', '🍑', '🍒', '🥝']
FRUIT_COLORS = {
    '🍎': '#FF0000',  # 红苹果
    '🍊': '#FF8C00',  # 橙子
    '🍋': '#FFD700',  # 柠檬
    '🍇': '#8B008B',  # 葡萄
    '🍓': '#FF1493',  # 草莓
    '🍑': '#FFB6C1',  # 桃子
    '🍒': '#DC143C',  # 樱桃
    '🥝': '#228B22',  # 猕猴桃
}

# 消除得分
MATCH_SCORE = {
    3: 10,   # 3连消
    4: 25,   # 4连消
    5: 50,   # 5连消
    6: 100,  # 6连消以上
}


class FruitGrid:
    """水果网格 - 游戏主棋盘"""
    
    def __init__(self, rows: int = 8, cols: int = 8):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.selected = None  # (row, col)
        self.score = 0
        self.combo_count = 0
        self.initialize()
    
    def initialize(self):
        """初始化棋盘，保证没有初始匹配"""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = random.choice(FRUITS)
        # 消除初始匹配并填补
        while True:
            matches = self.find_all_matches()
            if not matches:
                break
            for (r, c) in matches:
                self.grid[r][c] = random.choice(FRUITS)
    
    def get_fruit(self, row: int, col: int) -> str:
        """获取指定位置的水果"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None
    
    def swap(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """交换两个水果，如果有匹配返回True"""
        if not (0 <= r1 < self.rows and 0 <= c1 < self.cols and
                0 <= r2 < self.rows and 0 <= c2 < self.cols):
            return False
        
        # 检查是否相邻
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
        
        # 交换
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        
        # 检查是否有匹配
        if self.find_all_matches():
            return True
        else:
            # 没有匹配，换回来
            self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
            return False
    
    def find_matches_at(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """查找某个位置参与的匹配"""
        matched = set()
        fruit = self.grid[row][col]
        if fruit is None:
            return matched
        
        # 水平方向检查
        horizontal = [(row, c) for c in range(self.cols) if self.grid[row][c] == fruit]
        if len(horizontal) >= 3:
            matched.update(horizontal)
        
        # 垂直方向检查
        vertical = [(r, col) for r in range(self.rows) if self.grid[r][col] == fruit]
        if len(vertical) >= 3:
            matched.update(vertical)
        
        return matched
    
    def find_all_matches(self) -> Set[Tuple[int, int]]:
        """查找棋盘上所有匹配"""
        all_matched = set()
        
        # 水平匹配
        for r in range(self.rows):
            c = 0
            while c < self.cols:
                fruit = self.grid[r][c]
                if fruit is None:
                    c += 1
                    continue
                # 找连续相同水果
                end = c
                while end < self.cols and self.grid[r][end] == fruit:
                    end += 1
                if end - c >= 3:
                    for cc in range(c, end):
                        all_matched.add((r, cc))
                c = end
        
        # 垂直匹配
        for c in range(self.cols):
            r = 0
            while r < self.rows:
                fruit = self.grid[r][c]
                if fruit is None:
                    r += 1
                    continue
                end = r
                while end < self.rows and self.grid[end][c] == fruit:
                    end += 1
                if end - r >= 3:
                    for rr in range(r, end):
                        all_matched.add((rr, c))
                r = end
        
        return all_matched
    
    def calculate_score(self, matched_count: int) -> int:
        """计算消除得分"""
        if matched_count <= 2:
            return 0
        elif matched_count <= 3:
            return MATCH_SCORE[3]
        elif matched_count <= 4:
            return MATCH_SCORE[4]
        elif matched_count <= 5:
            return MATCH_SCORE[5]
        else:
            return MATCH_SCORE[6]
    
    def remove_matches(self, matches: Set[Tuple[int, int]]) -> int:
        """消除匹配的水果，返回消除数量"""
        # 计算得分
        count = len(matches)
        self.combo_count += 1
        combo_bonus = int(self.calculate_score(count) * (1 + (self.combo_count - 1) * 0.5))
        self.score += combo_bonus
        
        # 消除
        for (r, c) in matches:
            self.grid[r][c] = None
        
        return count
    
    def drop_fruits(self):
        """让水果下落填补空缺"""
        drops = []
        for c in range(self.cols):
            empty_row = self.rows - 1
            for r in range(self.rows - 1, -1, -1):
                if self.grid[r][c] is not None:
                    if r != empty_row:
                        self.grid[empty_row][c] = self.grid[r][c]
                        self.grid[r][c] = None
                        drops.append((r, c, empty_row, c))
                    empty_row -= 1
            # 填充顶部空缺
            for r in range(empty_row, -1, -1):
                self.grid[r][c] = random.choice(FRUITS)
                drops.append((-1, c, r, c))
        return drops
    
    def process_turn(self, r1: int, c1: int, r2: int, c2: int) -> dict:
        """处理一次完整的游戏回合"""
        result = {
            'success': False,
            'swapped': False,
            'matches': [],
            'score_gained': 0,
            'combo': 0,
            'chain': 0,
        }
        
        if not self.swap(r1, c1, r2, c2):
            return result
        
        result['success'] = True
        result['swapped'] = True
        
        # 连锁消除
        chain = 0
        total_score = 0
        while True:
            matches = self.find_all_matches()
            if not matches:
                self.combo_count = 0
                break
            
            chain += 1
            count = self.remove_matches(matches)
            total_score += self.calculate_score(count) * (1 + (chain - 1) * 0.5)
            
            result['matches'].append(list(matches))
            result['chain'] = chain
            
            # 下落填补
            self.drop_fruits()
        
        result['score_gained'] = total_score
        result['combo'] = self.combo_count
        
        return result
    
    def has_valid_moves(self) -> bool:
        """检查是否还有可行的移动"""
        for r in range(self.rows):
            for c in range(self.cols):
                # 尝试向右交换
                if c + 1 < self.cols:
                    self.grid[r][c], self.grid[r][c+1] = self.grid[r][c+1], self.grid[r][c]
                    if self.find_all_matches():
                        self.grid[r][c], self.grid[r][c+1] = self.grid[r][c+1], self.grid[r][c]
                        return True
                    self.grid[r][c], self.grid[r][c+1] = self.grid[r][c+1], self.grid[r][c]
                
                # 尝试向下交换
                if r + 1 < self.rows:
                    self.grid[r][c], self.grid[r+1][c] = self.grid[r+1][c], self.grid[r][c]
                    if self.find_all_matches():
                        self.grid[r][c], self.grid[r+1][c] = self.grid[r+1][c], self.grid[r][c]
                        return True
                    self.grid[r][c], self.grid[r+1][c] = self.grid[r+1][c], self.grid[r][c]
        
        return False
    
    def shuffle(self):
        """重新洗牌"""
        fruits = []
        for r in range(self.rows):
            for c in range(self.cols):
                fruits.append(self.grid[r][c])
        random.shuffle(fruits)
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = fruits[idx]
                idx += 1
        
        # 确保没有初始匹配
        while True:
            matches = self.find_all_matches()
            if not matches:
                break
            for (r, c) in matches:
                self.grid[r][c] = random.choice(FRUITS)


class GameState:
    """游戏状态管理"""
    
    def __init__(self):
        self.grid = FruitGrid(8, 8)
        self.level = 1
        self.target_score = 500
        self.moves_left = 30
        self.time_left = 120  # 秒
        self.is_paused = False
        self.is_game_over = False
        self.is_won = False
        self.total_score = 0
        self.coins = 0  # 游戏币（积分）
    
    def add_score(self, points: int):
        """添加分数并同步积分"""
        self.total_score += points
        # 游戏币=分数//10
        self.coins = self.total_score // 10
    
    def check_level_up(self) -> bool:
        """检查是否升级"""
        if self.total_score >= self.target_score:
            self.level += 1
            self.target_score = self.level * 500
            self.moves_left += 5
            return True
        return False


if __name__ == '__main__':
    # 测试游戏引擎
    game = GameState()
    print(f'棋盘初始状态: {game.grid.rows}x{game.grid.cols}')
    print(f'水果类型: {FRUITS}')
    print(f'是否有可行移动: {game.grid.has_valid_moves()}')
    
    # 模拟一次交换
    result = game.grid.process_turn(3, 3, 3, 4)
    print(f'交换结果: {result}')
    print(f'当前分数: {game.grid.score}')
