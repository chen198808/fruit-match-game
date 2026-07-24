#!/usr/bin/env python3
"""
🍎 水果消消乐 - 主入口
融合百益联盟广告 + 积分兑换人民币系统

技术栈: Python + Android Canvas + Chaquopy
"""

import sys
import os

# 确保能导入各模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine import GameState, FruitGrid, FRUITS, FRUIT_COLORS
from reward_system import RewardSystem, add_coins, get_coins, coins_to_rmb, request_withdraw, daily_sign_in, watch_ad_reward, get_statistics
from ad_manager import AdManager, BaiYiAdSDK, init_ads, watch_ad_for_coins, watch_ad_for_revive


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║       🍎 水果消消乐 🍊               ║
    ║     🍋 三消闯关 · 广告变现 🍇        ║
    ║   💰 积分兑换人民币 · 提现待续 🍑    ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def show_menu():
    """显示主菜单"""
    print()
    print('=' * 45)
    print('📋 主菜单')
    print('=' * 45)
    print('1️⃣  开始游戏 (🎮 水果消消乐)')
    print('2️⃣  每日签到 (🎁 领积分)')
    print('3️⃣  看广告赚积分 (📺 得5-20分)')
    print('4️⃣  积分提现 (🔄 待续···)')
    print('5️⃣  我的钱包 (📊 查看统计)')
    print('6️⃣  提现记录 (📜 历史记录)')
    print('0️⃣  退出游戏')
    print('=' * 45)


def run_game():
    """运行控制台版水果消消乐"""
    game = GameState()
    grid = game.grid
    
    print('\n🎮=== 水果消消乐 ===🎮')
    print(f'目标: {game.target_score} 分 | 关卡: {game.level}')
    print()
    
    while not game.is_game_over:
        # 显示棋盘
        print('    ', end='')
        for c in range(grid.cols):
            print(f' {c} ', end=' ')
        print()
        print('    ' + '----' * grid.cols)
        
        for r in range(grid.rows):
            print(f'{r} ║ ', end='')
            for c in range(grid.cols):
                fruit = grid.get_fruit(r, c) or '⬜'
                print(f'{fruit} ', end=' ')
            print('║')
        print('    ' + '----' * grid.cols)
        
        print(f'\n⭐ 得分: {game.total_score} | 💰 积分: {game.coins} (≈¥{game.coins/100:.2f})')
        print(f'🎯 目标: {game.target_score} 分')
        
        # 用户输入
        try:
            cmd = input('\n📌 输入命令 [r1 c1 r2 c2交换 / s洗牌 / q退出]: ').strip()
            
            if cmd.lower() == 'q':
                print('👋 感谢游戏！')
                break
            elif cmd.lower() == 's':
                grid.shuffle()
                print('🔄 已洗牌！')
                continue
            
            parts = cmd.split()
            if len(parts) == 4:
                r1, c1, r2, c2 = map(int, parts)
                
                result = grid.process_turn(r1, c1, r2, c2)
                if result['success']:
                    score = result['score_gained']
                    game.add_score(score)
                    
                    if result['chain'] > 1:
                        print(f'🔥 连消 {result["chain"]} 链！+{score} 分')
                    else:
                        print(f'✨ 消除成功！+{score} 分')
                    
                    # 检查关卡升级
                    if game.check_level_up():
                        print(f'🎉🎉🎉 恭喜升到第 {game.level} 关！')
                else:
                    print('❌ 无法交换，没有匹配！')
            
            # 检查无路可走
            if not grid.has_valid_moves():
                print('🔄 没有可行的移动了，自动洗牌...')
                grid.shuffle()
                
        except (ValueError, IndexError):
            print('⚠️ 输入格式错误！格式: r1 c1 r2 c2')
        except KeyboardInterrupt:
            print('\n👋 再见！')
            break
    
    # 游戏结束
    print(f'\n🏁 游戏结束！最终得分: {game.total_score}')
    print(f'💰 获得 {game.coins} 积分 (≈¥{game.coins/100:.2f})')
    
    return game.coins


def main():
    """主函数"""
    print_banner()
    
    # 初始化积分系统
    rs = RewardSystem()
    stats = rs.get_statistics()
    print(f'👋 欢迎回来！当前积分: {stats["coins"]} | 可兑换: ¥{stats["can_withdraw_rmb"]:.2f}')
    
    # 初始化广告
    ad = AdManager(debug=True)
    print('📢 百益联盟广告已就绪')
    
    while True:
        show_menu()
        choice = input('👉 请选择: ').strip()
        
        if choice == '1':
            # 开始游戏
            coins_earned = run_game()
            print(f'\n💡 看广告可获额外积分！')
            watch = input('📺 看广告赚积分？(y/n): ').strip().lower()
            if watch == 'y':
                result = watch_ad_for_coins()
                print(f'   {result["message"]}')
                if result['success']:
                    rs.add_coins(result['coins'])
        
        elif choice == '2':
            # 每日签到
            result = rs.daily_sign_in()
            print(f'\n🎁 {result["message"]}')
            print(f'📅 连续签到: {result["streak"]} 天')
        
        elif choice == '3':
            # 看广告赚积分
            result = watch_ad_for_coins()
            print(f'\n📺 {result["message"]}')
            if result['success']:
                rs.add_coins(result['coins'])
        
        elif choice == '4':
            # 积分提现（待续）
            print('\n' + '=' * 45)
            print('💳 积分提现')
            print('=' * 45)
            stats = rs.get_statistics()
            print(f'💰 当前积分: {stats["coins"]} (≈¥{stats["can_withdraw_rmb"]:.2f})')
            print()
            print('   ┌──────────────────────────────┐')
            print('   │  🚧  提现功能即将上线！       │')
            print('   │                               │')
            print('   │  积分照常累计到你的账户        │')
            print('   │  开放提现后可直接兑换 💰       │')
            print('   │                               │')
            print('   │  比例: 100积分 = 1元           │')
            print('   │  起提: 1元 (100积分)           │')
            print('   │  支持: 支付宝 / 微信           │')
            print('   └──────────────────────────────┘')
            print()
            print('💡 继续玩游戏攒积分，等提现开放秒到账！')
        
        elif choice == '5':
            # 我的钱包
            stats = rs.get_statistics()
            print('\n' + '=' * 40)
            print('📊 我的钱包')
            print('=' * 40)
            print(f'💰 当前积分: {stats["coins"]}')
            print(f'📈 总获得积分: {stats["total_coins"]}')
            print(f'💵 可兑换金额: ¥{stats["can_withdraw_rmb"]:.2f}')
            print(f'🏧 已提现金额: ¥{stats["withdrawn_rmb"]:.2f}')
            print(f'📋 提现次数: {stats["withdraw_count"]}')
            print(f'📺 看广告次数: {stats["ad_watched"]}')
            
            daily = stats['daily_status']
            print(f'\n📅 签到状态: {"✅ 已签到" if daily["signed_in"] else "❌ 未签到"}')
            print(f'🔥 连续签到: {daily["streak"]} 天')
            print(f'🎁 下次签到奖励: {daily["next_bonus"]} 积分')
            
            if stats['coins'] >= 100:
                print(f'\n💡 你有 {stats["coins"]} 积分，可兑换 ¥{stats["can_withdraw_rmb"]:.2f}')
                print('   提现功能即将上线，敬请期待！')
        
        elif choice == '6':
            # 提现记录
            history = rs.get_withdraw_history()
            print('\n' + '=' * 45)
            print('📜 提现记录')
            print('=' * 45)
            if not history:
                print('暂无提现记录')
            else:
                for h in history:
                    status_emoji = '🟢' if h['status'] == 'completed' else '🟡' if h['status'] == 'processing' else '🔴'
                    print(f'{status_emoji} {h["time"]} | {h["coins"]}积分→¥{h["rmb"]:.2f} | {h["method_name"]} | {h["status"]}')
        
        elif choice == '0':
            stats = rs.get_statistics()
            print(f'\n👋 感谢玩水果消消乐！')
            print(f'💰 当前累计: {stats["coins"]} 积分 (≈¥{stats["can_withdraw_rmb"]:.2f})')
            print('🎮 下次再见！')
            break
        
        else:
            print('⚠️ 无效选择，请重新输入')
        
        print()
        input('按回车继续...')


if __name__ == '__main__':
    main()
