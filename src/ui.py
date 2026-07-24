"""
水果消消乐 - Android游戏界面
基于Python + Android Canvas实现
"""

import math
import random
import time
from typing import Optional

from java import jclass, jarray

# Android类
android_app = jclass('android.app.Activity')
Context = jclass('android.content.Context')
View = jclass('android.view.View')
MotionEvent = jclass('android.view.MotionEvent')
GestureDetector = jclass('android.view.GestureDetector')
Canvas = jclass('android.graphics.Canvas')
Paint = jclass('android.graphics.Paint')
Color = jclass('android.graphics.Color')
Rect = jclass('android.graphics.Rect')
RectF = jclass('android.graphics.RectF')
Bitmap = jclass('android.graphics.Bitmap')
Typeface = jclass('android.graphics.Typeface')
Path = jclass('android.graphics.Path')
PorterDuff = jclass('android.graphics.PorterDuff')
PorterDuffXfermode = jclass('android.graphics.PorterDuffXfermode')
Matrix = jclass('android.graphics.Matrix')
DisplayMetrics = jclass('android.util.DisplayMetrics')
Handler = jclass('android.os.Handler')
Looper = jclass('android.os.Looper')
Vibrator = jclass('android.os.Vibrator')
VibrationEffect = jclass('android.os.VibrationEffect')
AudioManager = jclass('android.media.AudioManager')
MediaPlayer = jclass('android.media.MediaPlayer')

from game_engine import GameState, FruitGrid, FRUITS, FRUIT_COLORS
from reward_system import RewardSystem
from ad_manager import AdManager


class FruitMatchGame(View):
    """水果消消乐游戏主界面"""
    
    # 游戏状态常量
    STATE_IDLE = 0
    STATE_SWAPPING = 1
    STATE_MATCHING = 2
    STATE_DROPPING = 3
    STATE_GAME_OVER = 4
    STATE_PAUSED = 5
    
    def __init__(self, context):
        super().__init__(context)
        self.context = context
        
        # 获取屏幕尺寸
        metrics = context.getResources().getDisplayMetrics()
        self.screen_width = metrics.widthPixels
        self.screen_height = metrics.heightPixels
        
        # 初始化游戏引擎
        self.game = GameState()
        self.reward = RewardSystem()
        self.ad = AdManager(debug=True)
        
        # 游戏状态
        self.state = self.STATE_IDLE
        self.selected_cell = None  # (row, col)
        self.swap_anim_progress = 0.0
        self.drop_anim_progress = 0.0
        self.animating_cells = []
        
        # 触摸相关
        self.touch_start = None
        self.swipe_threshold = 30
        
        # 动画
        self.handler = Handler(Looper.getMainLooper())
        self.anim_running = False
        
        # 画笔
        self.paint = Paint()
        self.text_paint = Paint()
        
        # 计算布局
        self._calculate_layout()
        
        # 初始化画笔
        self._init_paints()
        
        # 设置点击事件
        self.setClickable(True)
        self.setFocusable(True)
        
        # 帧率控制
        self.last_frame_time = 0
        self.fps = 60
        
        # 启动游戏循环
        self._start_game_loop()
    
    def _calculate_layout(self):
        """计算游戏布局"""
        # 顶部信息栏高度
        self.info_bar_height = int(self.screen_height * 0.12)
        
        # 底部广告栏高度
        self.banner_height = int(self.screen_height * 0.06)
        
        # 游戏区域
        game_top = self.info_bar_height
        game_bottom = self.screen_height - self.banner_height
        game_height = game_bottom - game_top
        
        # 网格尺寸
        self.margin = int(self.screen_width * 0.02)
        available_width = self.screen_width - self.margin * 2
        available_height = game_height - self.margin * 2
        
        self.cell_size = min(
            available_width // self.game.grid.cols,
            available_height // self.game.grid.rows
        )
        
        grid_width = self.cell_size * self.game.grid.cols
        grid_height = self.cell_size * self.game.grid.rows
        
        self.grid_left = (self.screen_width - grid_width) // 2
        self.grid_top = game_top + (game_height - grid_height) // 2
        self.grid_right = self.grid_left + grid_width
        self.grid_bottom = self.grid_top + grid_height
        
        # 水果字体大小
        self.fruit_text_size = int(self.cell_size * 0.65)
    
    def _init_paints(self):
        """初始化画笔样式"""
        # 背景画笔
        self.bg_paint = Paint()
        self.bg_paint.setColor(Color.parseColor('#1a1a2e'))
        
        # 网格画笔
        self.grid_paint = Paint()
        self.grid_paint.setColor(Color.parseColor('#16213e'))
        self.grid_paint.setStyle(Paint.Style.FILL)
        
        self.grid_border_paint = Paint()
        self.grid_border_paint.setColor(Color.parseColor('#0f3460'))
        self.grid_border_paint.setStyle(Paint.Style.STROKE)
        self.grid_border_paint.setStrokeWidth(2)
        
        # 选中高亮画笔
        self.select_paint = Paint()
        self.select_paint.setColor(Color.parseColor('#e94560'))
        self.select_paint.setStyle(Paint.Style.STROKE)
        self.select_paint.setStrokeWidth(4)
        
        # 文字画笔
        self.text_paint = Paint()
        self.text_paint.setColor(Color.WHITE)
        self.text_paint.setTextSize(int(self.cell_size * 0.35))
        self.text_paint.setTextAlign(Paint.Align.CENTER)
        self.text_paint.setAntiAlias(True)
        
        # 大标题画笔
        self.title_paint = Paint()
        self.title_paint.setColor(Color.WHITE)
        self.title_paint.setTextSize(int(self.screen_width * 0.06))
        self.title_paint.setTextAlign(Paint.Align.CENTER)
        self.title_paint.setAntiAlias(True)
        self.title_paint.setFakeBoldText(True)
        
        # 分数画笔
        self.score_paint = Paint()
        self.score_paint.setColor(Color.parseColor('#e94560'))
        self.score_paint.setTextSize(int(self.screen_width * 0.05))
        self.score_paint.setTextAlign(Paint.Align.CENTER)
        self.score_paint.setAntiAlias(True)
        self.score_paint.setFakeBoldText(True)
        
        # 水果文字画笔（大号显示emoji）
        self.fruit_paint = Paint()
        self.fruit_paint.setTextSize(self.fruit_text_size)
        self.fruit_paint.setTextAlign(Paint.Align.CENTER)
        self.fruit_paint.setAntiAlias(True)
    
    def _start_game_loop(self):
        """启动游戏循环"""
        def game_loop():
            self.invalidate()  # 触发重绘
            self.handler.postDelayed(game_loop, 16)  # ~60fps
        
        self.handler.post(game_loop)
    
    # ========== 触摸事件 ==========
    
    def onTouchEvent(self, event):
        """处理触摸事件"""
        action = event.getAction()
        x = event.getX()
        y = event.getY()
        
        if action == MotionEvent.ACTION_DOWN:
            self.touch_start = (x, y)
            return True
        
        elif action == MotionEvent.ACTION_UP and self.touch_start:
            dx = x - self.touch_start[0]
            dy = y - self.touch_start[1]
            
            # 判断是否点击了某个格子
            cell = self._get_cell_at(self.touch_start[0], self.touch_start[1])
            
            if abs(dx) < self.swipe_threshold and abs(dy) < self.swipe_threshold:
                # 点击选择
                if cell:
                    self._on_cell_tap(cell)
            else:
                # 滑动交换
                if cell:
                    # 判断滑动方向
                    if abs(dx) > abs(dy):
                        dc = 1 if dx > 0 else -1
                        dr = 0
                    else:
                        dr = 1 if dy > 0 else -1
                        dc = 0
                    
                    target = (cell[0] + dr, cell[1] + dc)
                    self._on_cell_swap(cell, target)
            
            self.touch_start = None
            return True
        
        return False
    
    def _get_cell_at(self, x: float, y: float):
        """获取触摸位置的格子"""
        if x < self.grid_left or x > self.grid_right:
            return None
        if y < self.grid_top or y > self.grid_bottom:
            return None
        
        col = int((x - self.grid_left) // self.cell_size)
        row = int((y - self.grid_top) // self.cell_size)
        
        if 0 <= row < self.game.grid.rows and 0 <= col < self.game.grid.cols:
            return (row, col)
        return None
    
    def _on_cell_tap(self, cell):
        """点击格子"""
        if self.state != self.STATE_IDLE:
            return
        
        if self.selected_cell == cell:
            # 取消选择
            self.selected_cell = None
        elif self.selected_cell:
            # 尝试交换
            self._on_cell_swap(self.selected_cell, cell)
        else:
            # 选择
            self.selected_cell = cell
    
    def _on_cell_swap(self, cell1, cell2):
        """交换两个格子"""
        if self.state != self.STATE_IDLE:
            return
        
        r1, c1 = cell1
        r2, c2 = cell2
        
        # 检查是否相邻
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            self.selected_cell = cell2
            return
        
        # 执行交换
        result = self.game.grid.process_turn(r1, c1, r2, c2)
        
        if result['success']:
            self.game.add_score(result['score_gained'])
            self.selected_cell = None
            self.state = self.STATE_SWAPPING
            
            # 震感反馈
            self._vibrate(50)
            
            # 检查游戏结束
            self._check_game_over()
        else:
            # 无效交换
            self.selected_cell = cell2
            self._vibrate(20)
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        if not self.game.grid.has_valid_moves():
            self.game.is_game_over = True
            self.state = self.STATE_GAME_OVER
            self.game.grid.shuffle()  # 自动洗牌
    
    def _vibrate(self, ms: int = 50):
        """震动反馈"""
        try:
            vib = self.context.getSystemService(Context.VIBRATOR_SERVICE)
            if vib and vib.hasVibrator():
                vib.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE))
        except:
            pass
    
    # ========== 绘制 ==========
    
    def onDraw(self, canvas):
        """绘制游戏界面"""
        # 清空画布 - 深色渐变背景
        self._draw_background(canvas)
        
        # 绘制顶部信息栏
        self._draw_info_bar(canvas)
        
        # 绘制游戏网格
        self._draw_grid(canvas)
        
        # 绘制水果
        self._draw_fruits(canvas)
        
        # 绘制选中高亮
        if self.selected_cell:
            self._draw_selection(canvas)
        
        # 绘制底部广告栏
        self._draw_banner(canvas)
        
        # 绘制游戏结束遮罩
        if self.game.is_game_over:
            self._draw_game_over(canvas)
    
    def _draw_background(self, canvas):
        """绘制背景"""
        canvas.drawColor(Color.parseColor('#1a1a2e'))
        
        # 渐变装饰
        paint = Paint()
        paint.setColor(Color.parseColor('#16213e'))
        paint.setAlpha(80)
        canvas.drawRect(0, 0, self.screen_width, self.screen_height, paint)
    
    def _draw_info_bar(self, canvas):
        """绘制顶部信息栏"""
        bg = Paint()
        bg.setColor(Color.parseColor('#0f3460'))
        bg.setAlpha(200)
        canvas.drawRect(0, 0, self.screen_width, self.info_bar_height, bg)
        
        # 游戏标题
        self.title_paint.setColor(Color.WHITE)
        canvas.drawText('🍎 水果消消乐 🍎', 
                       self.screen_width // 2, 
                       int(self.info_bar_height * 0.38), 
                       self.title_paint)
        
        # 分数
        score_y = int(self.info_bar_height * 0.75)
        self.score_paint.setTextSize(int(self.screen_width * 0.045))
        self.score_paint.setColor(Color.parseColor('#e94560'))
        canvas.drawText(f'⭐ {self.game.total_score}', 
                       self.screen_width // 2 - self.screen_width // 4, 
                       score_y, self.score_paint)
        
        # 等级
        self.score_paint.setColor(Color.parseColor('#00b4d8'))
        canvas.drawText(f'🏆 Lv.{self.game.level}', 
                       self.screen_width // 2, 
                       score_y, self.score_paint)
        
        # 积分（可提现金额）
        self.score_paint.setColor(Color.parseColor('#ffd60a'))
        coins = self.game.coins
        rmb = coins / 100
        canvas.drawText(f'💰 {coins}分 (≈¥{rmb:.2f})', 
                       self.screen_width // 2 + self.screen_width // 4, 
                       score_y, self.score_paint)
    
    def _draw_grid(self, canvas):
        """绘制游戏网格"""
        # 网格背景
        padding = 4
        for r in range(self.game.grid.rows):
            for c in range(self.game.grid.cols):
                left = self.grid_left + c * self.cell_size + padding
                top = self.grid_top + r * self.cell_size + padding
                right = left + self.cell_size - padding * 2
                bottom = top + self.cell_size - padding * 2
                
                # 格子背景
                if (r + c) % 2 == 0:
                    self.grid_paint.setColor(Color.parseColor('#16213e'))
                else:
                    self.grid_paint.setColor(Color.parseColor('#1a1a3e'))
                
                rect = RectF(left, top, right, bottom)
                canvas.drawRoundRect(rect, 8, 8, self.grid_paint)
                
                # 格子边框
                self.grid_border_paint.setColor(Color.parseColor('#0f3460'))
                self.grid_border_paint.setAlpha(100)
                canvas.drawRoundRect(rect, 8, 8, self.grid_border_paint)
    
    def _draw_fruits(self, canvas):
        """绘制棋盘上的水果"""
        self.fruit_paint.setTextSize(self.fruit_text_size)
        
        for r in range(self.game.grid.rows):
            for c in range(self.game.grid.cols):
                fruit = self.game.grid.get_fruit(r, c)
                if fruit:
                    # 计算水果位置（居中）
                    cx = self.grid_left + c * self.cell_size + self.cell_size // 2
                    cy = self.grid_top + r * self.cell_size + self.cell_size // 2
                    
                    # 绘制水果emoji
                    self.fruit_paint.setTextSize(self.fruit_text_size)
                    # 测量文字基线
                    metrics = self.fruit_paint.getFontMetrics()
                    baseline = cy - (metrics.top + metrics.bottom) / 2
                    
                    # 绘制阴影
                    self.fruit_paint.setColor(Color.BLACK)
                    self.fruit_paint.setAlpha(60)
                    canvas.drawText(fruit, cx + 2, baseline + 2, self.fruit_paint)
                    
                    # 绘制水果
                    self.fruit_paint.setColor(Color.WHITE)
                    self.fruit_paint.setAlpha(255)
                    canvas.drawText(fruit, cx, baseline, self.fruit_paint)
    
    def _draw_selection(self, canvas):
        """绘制选中高亮"""
        if not self.selected_cell:
            return
        
        r, c = self.selected_cell
        left = self.grid_left + c * self.cell_size + 2
        top = self.grid_top + r * self.cell_size + 2
        right = left + self.cell_size - 4
        bottom = top + self.cell_size - 4
        
        # 发光效果
        glow = Paint()
        glow.setColor(Color.parseColor('#e94560'))
        glow.setStyle(Paint.Style.FILL)
        glow.setAlpha(40)
        rect = RectF(left, top, right, bottom)
        canvas.drawRoundRect(rect, 10, 10, glow)
        
        # 边框
        self.select_paint.setColor(Color.parseColor('#e94560'))
        canvas.drawRoundRect(rect, 10, 10, self.select_paint)
    
    def _draw_banner(self, canvas):
        """绘制底部广告栏"""
        bar_top = self.screen_height - self.banner_height
        
        # 广告栏背景
        bg = Paint()
        bg.setColor(Color.parseColor('#0f3460'))
        canvas.drawRect(0, bar_top, self.screen_width, self.screen_height, bg)
        
        # 广告文字
        self.text_paint.setColor(Color.parseColor('#7ec8e3'))
        self.text_paint.setTextSize(int(self.banner_height * 0.4))
        canvas.drawText('📢 百益联盟 · 广告位', 
                       self.screen_width // 2, 
                       bar_top + self.banner_height // 2 + int(self.banner_height * 0.15), 
                       self.text_paint)
    
    def _draw_game_over(self, canvas):
        """绘制游戏结束遮罩"""
        # 半透明遮罩
        mask = Paint()
        mask.setColor(Color.parseColor('#1a1a2e'))
        mask.setAlpha(220)
        canvas.drawRect(0, 0, self.screen_width, self.screen_height, mask)
        
        # 游戏结束文字
        title = '🎉 游戏结束 🎉'
        self.title_paint.setTextSize(int(self.screen_width * 0.08))
        self.title_paint.setColor(Color.WHITE)
        canvas.drawText(title, self.screen_width // 2, self.screen_height // 2 - 100, self.title_paint)
        
        # 最终得分
        self.score_paint.setTextSize(int(self.screen_width * 0.06))
        self.score_paint.setColor(Color.parseColor('#ffd60a'))
        canvas.drawText(f'最终得分: {self.game.total_score}', 
                       self.screen_width // 2, 
                       self.screen_height // 2, 
                       self.score_paint)
        
        # 可提现金额
        self.score_paint.setColor(Color.parseColor('#e94560'))
        coins = self.game.coins
        rmb = coins / 100
        canvas.drawText(f'💰 {coins} 积分 ≈ ¥{rmb:.2f}', 
                       self.screen_width // 2, 
                       self.screen_height // 2 + 80, 
                       self.score_paint)
        
        # 提现提示
        self.text_paint.setTextSize(int(self.screen_width * 0.04))
        self.text_paint.setColor(Color.parseColor('#7ec8e3'))
        canvas.drawText('👆 点击继续 - 看广告复活或重新开始', 
                       self.screen_width // 2, 
                       self.screen_height // 2 + 160, 
                       self.text_paint)


class GameActivity(android_app):
    """游戏Activity - 承载游戏视图"""
    
    def onCreate(self, savedInstanceState):
        super().onCreate(savedInstanceState)
        
        # 隐藏标题栏
        try:
            self.getWindow().setFlags(
                0x02000000,  # WindowManager.LayoutParams.FLAG_FULLSCREEN
                0x02000000
            )
        except:
            pass
        
        # 设置游戏视图
        self.game_view = FruitMatchGame(self)
        self.setContentView(self.game_view)
    
    def onPause(self):
        super().onPause()
        self.game_view.game.is_paused = True
    
    def onResume(self):
        super().onResume()
        self.game_view.game.is_paused = False


def launch_game(context):
    """启动游戏"""
    intent = jclass('android.content.Intent')(context, GameActivity)
    context.startActivity(intent)


if __name__ == '__main__':
    print('水果消消乐游戏界面已加载')
    print('运行 main.py 启动游戏')
