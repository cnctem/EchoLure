"""回声定位炮 - EchoLure 游戏常量与配置"""

import os
import sys

# 屏幕设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
DARK_BLUE = (10, 15, 30)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 150, 200)
GOLD = (255, 215, 0)
RED = (255, 50, 50)
ORANGE = (255, 150, 50)
GREEN = (50, 255, 100)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)

# 声呐设置
SONAR_COOLDOWN = 4.0
SONAR_REVEAL_DURATION = 2.5
SONAR_WIDEBAND_REVEAL_DURATION = 4.0
SONAR_MAX_RADIUS = 800  # 普通声呐最远距离
SONAR_WIDEBAND_MAX_RADIUS = 1000  # 全频扫描最远距离
SONAR_SPEED = 300
SONAR_WIDTH = 3.14159 / 4  # 45度扇形

# 炮台设置
TURRET_RADIUS = 20
BARREL_LENGTH = 35

# 目标设置
TARGET_RADIUS = 15
TARGET_BASE_SPEED = 80
TARGET_START_COUNT = 2
TARGET_MAX_COUNT = 8

# 炮弹设置
PROJECTILE_SPEED = 500
PROJECTILE_RADIUS = 6
SHARD_RADIUS = 4
MAX_BOUNCES = 1

# 充能槽设置
ENERGY_MAX_SLOTS = 5
ENERGY_REGEN_RATE = 1.0  # 每秒恢复1格
ENERGY_SHOOT_COST = 1    # 发射消耗1格

# 道具设置
POWERUP_RADIUS = 12
POWERUP_SPAWN_INTERVAL = 15.0
POWERUP_MAX_COUNT = 2
BEACON_DURATION = 6.0

# 计分设置
SCORE_KILL = 100
SCORE_BLINDSHOT = 400
SCORE_QUICK_BONUS = 50
SCORE_COMBO_BASE = 50
SCORE_LEVEL_UP = 800

# 难度设置
DIFFICULTY_SPEED_INCREMENT = 0.08
DIFFICULTY_SILENT_THRESHOLD = 4  # 4个目标后出现静默目标

# 噪音干扰设置
NOISE_JAM_THRESHOLD = 3
NOISE_JAM_DURATION = 2.0

# 字体设置（按优先级排序）
def _get_font_path(filename):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)

FONT_PATHS = [
    _get_font_path('DinkieBitmap.ttf'),
    "/Users/a11111/Library/Fonts/阿里巴巴普惠体 R.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
