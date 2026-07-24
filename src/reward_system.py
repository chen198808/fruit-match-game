"""
水果消消乐 - 积分兑换人民币系统
积分(金币) -> 人民币 提现（即将上线）
"""

import json
import os
import time
from typing import Optional

# 兑换比例：100积分 = 1元人民币
EXCHANGE_RATE = 100  # 积分:人民币比例
MIN_WITHDRAW = 1.0   # 最低提现1元
MAX_WITHDRAW = 100.0 # 单次最高提现100元

# 提现方式
WITHDRAW_METHODS = {
    'alipay': '支付宝',
    'wechat': '微信',
    'bank': '银行卡',
}


class RewardSystem:
    """积分奖励与提现系统"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'reward_data.json')
        self._ensure_data_dir()
        self.data = self._load_data()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_data(self) -> dict:
        """加载积分数据"""
        default_data = {
            'coins': 0,           # 当前积分（游戏币）
            'total_coins': 0,     # 历史获得总积分
            'withdrawn_rmb': 0.0, # 已提现人民币总额
            'withdraw_history': [], # 提现记录
            'daily_bonus': {},    # 每日签到奖励
            'watch_ad_bonus': 0,  # 看广告获得的奖励次数
            'last_login': None,
        }
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return {**default_data, **json.load(f)}
            except:
                pass
        return default_data
    
    def _save_data(self):
        """保存积分数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # ========== 积分操作 ==========
    
    def add_coins(self, amount: int) -> int:
        """添加积分"""
        if amount <= 0:
            return self.data['coins']
        self.data['coins'] += amount
        self.data['total_coins'] += amount
        self._save_data()
        return self.data['coins']
    
    def deduct_coins(self, amount: int) -> bool:
        """扣除积分（暂未开放提现，此功能保留）"""
        if amount <= 0 or self.data['coins'] < amount:
            return False
        self.data['coins'] -= amount
        self._save_data()
        return True
    
    def get_coins(self) -> int:
        """获取当前积分"""
        return self.data['coins']
    
    def get_total_coins(self) -> int:
        """获取历史总积分"""
        return self.data['total_coins']
    
    # ========== 积分转人民币 ==========
    
    def coins_to_rmb(self, coins: int) -> float:
        """积分转人民币（按比例计算）"""
        return coins / EXCHANGE_RATE
    
    def rmb_to_coins(self, rmb: float) -> int:
        """人民币转积分"""
        return int(rmb * EXCHANGE_RATE)
    
    def can_withdraw(self, coins: int) -> tuple:
        """
        检查是否可以提现（功能待上线）
        返回: (can_withdraw: bool, message: str)
        """
        return False, '提现功能即将上线，敬请期待！'
    
    def request_withdraw(self, coins: int, method: str = 'alipay', 
                        account: str = '') -> dict:
        """
        发起提现申请（功能待上线）
        返回: {'success': bool, 'message': str, 'data': dict}
        """
        return {
            'success': False,
            'message': '🔄 提现功能即将上线，敬请期待！\n   积分照常累计，开放提现后可直接兑换 💰',
            'data': None,
        }
    
    def get_withdraw_history(self, limit: int = 20) -> list:
        """获取提现记录"""
        return list(reversed(self.data['withdraw_history'][-limit:]))
    
    def get_total_withdrawn(self) -> float:
        """获取总提现金额"""
        return self.data['withdrawn_rmb']
    
    # ========== 每日签到 ==========
    
    def daily_sign_in(self) -> dict:
        """
        每日签到
        返回: {'bonus': int, 'streak': int, 'message': str}
        """
        today = time.strftime('%Y-%m-%d')
        yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
        
        # 检查今天是否已签到
        if today in self.data['daily_bonus']:
            return {
                'bonus': 0,
                'streak': self.data['daily_bonus'].get('streak', 1),
                'message': '今天已经签到过了哦！',
            }
        
        # 检查连续签到
        streak = 1
        if yesterday in self.data['daily_bonus']:
            streak = self.data['daily_bonus'].get('streak', 0) + 1
        
        # 签到奖励（连续签到越多奖励越高）
        bonus = 10 + (streak - 1) * 5  # 第1天10分，之后每天+5
        if streak >= 7:
            bonus += 20  # 连续7天额外奖励
        if streak >= 30:
            bonus += 50  # 连续30天额外奖励
        
        self.add_coins(bonus)
        self.data['daily_bonus'][today] = {
            'bonus': bonus,
            'streak': streak,
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        self.data['daily_bonus']['streak'] = streak
        self._save_data()
        
        return {
            'bonus': bonus,
            'streak': streak,
            'message': f'签到成功！连续签到 {streak} 天，获得 {bonus} 积分！',
        }
    
    def get_daily_status(self) -> dict:
        """获取每日状态"""
        today = time.strftime('%Y-%m-%d')
        signed_in = today in self.data['daily_bonus']
        streak = self.data['daily_bonus'].get('streak', 0)
        
        next_bonus = 10 + streak * 5
        if streak + 1 >= 7:
            next_bonus += 20
        if streak + 1 >= 30:
            next_bonus += 50
        
        return {
            'signed_in': signed_in,
            'streak': streak,
            'next_bonus': next_bonus,
        }
    
    # ========== 看广告奖励 ==========
    
    def watch_ad_reward(self) -> dict:
        """
        观看广告获得积分奖励
        返回: {'bonus': int, 'message': str, 'ad_played': bool}
        """
        import random
        bonus = random.randint(5, 20)
        self.add_coins(bonus)
        self.data['watch_ad_bonus'] += 1
        self._save_data()
        
        return {
            'bonus': bonus,
            'message': f'感谢观看广告，获得 {bonus} 积分！',
            'ad_played': True,
        }
    
    def get_ad_reward_count(self) -> int:
        """获取看广告次数"""
        return self.data['watch_ad_bonus']
    
    # ========== 统计信息 ==========
    
    def get_statistics(self) -> dict:
        """获取完整统计信息"""
        return {
            'coins': self.data['coins'],
            'total_coins': self.data['total_coins'],
            'withdrawn_rmb': round(self.data['withdrawn_rmb'], 2),
            'can_withdraw_rmb': round(self.coins_to_rmb(self.data['coins']), 2),
            'withdraw_count': len(self.data['withdraw_history']),
            'ad_watched': self.data['watch_ad_bonus'],
            'daily_status': self.get_daily_status(),
        }


# 兼容旧版接口
reward = RewardSystem()

def add_coins(amount):
    return reward.add_coins(amount)

def get_coins():
    return reward.get_coins()

def coins_to_rmb(coins):
    return reward.coins_to_rmb(coins)

def request_withdraw(coins, method='alipay', account=''):
    return reward.request_withdraw(coins, method, account)

def daily_sign_in():
    return reward.daily_sign_in()

def watch_ad_reward():
    return reward.watch_ad_reward()

def get_statistics():
    return reward.get_statistics()


if __name__ == '__main__':
    # 测试积分系统
    rs = RewardSystem()
    print('=== 积分系统测试 ===')
    print(f'当前积分: {rs.get_coins()}')
    
    # 签到测试
    result = rs.daily_sign_in()
    print(f'签到结果: {result}')
    
    # 加积分
    rs.add_coins(500)
    print(f'加500积分后: {rs.get_coins()}')
    print(f'可兑换: ¥{rs.coins_to_rmb(rs.get_coins()):.2f}')
    
    # 提现测试（现在会提示敬请期待）
    result = rs.request_withdraw(100, 'alipay', 'test@test.com')
    print(f'提现结果: {result}')
    
    print(f'统计: {rs.get_statistics()}')
