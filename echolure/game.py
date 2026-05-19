"""回声定位炮 - 游戏主类"""

import pygame
import math
import random
import sys
import numpy as np
from typing import List, Tuple

from .constants import *
from .constants import _get_asset_path
from .entities import Target, SonarWave, Projectile, PowerUp, Turret, draw_glow


class Game:
    """游戏主类"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("回声定位炮 - EchoLure")
        try:
            icon = pygame.image.load(_get_asset_path('icon.png'))
            pygame.display.set_icon(icon)
        except:
            pass
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 初始化字体
        self._init_fonts()
        
        # 游戏对象
        self.turret = Turret(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.targets: List[Target] = []
        self.projectiles: List[Projectile] = []
        self.sonar_waves: List[SonarWave] = []
        self.powerups: List[PowerUp] = []
        
        # 游戏状态
        self.score = 0
        self.total_score = 0
        self.window_kills = 0  # 当前窗口期击杀数
        self.last_window_time = 0.0
        self.difficulty_level = 0
        self.target_base_speed = TARGET_BASE_SPEED
        
        # 生成初始目标
        self.spawn_initial_targets()
        
        # 音效
        self.has_sound = False
        try:
            self.sonar_sound = self._create_beep(800, 0.1)
            self.shoot_sound = self._create_beep(400, 0.05)
            self.hit_sound = self._create_beep(600, 0.15)
            self.powerup_sound = self._create_beep(1000, 0.2)
            self.has_sound = True
        except:
            pass
        
        # 道具生成计时器
        self.powerup_spawn_timer = 0.0
        self.powerup_spawn_interval = POWERUP_SPAWN_INTERVAL
        
        # 击杀信息
        self.kill_messages: List[Tuple[str, float, Tuple[int, int, int]]] = []
        
        # 道具触发反馈
        self.powerup_activated_messages: List[Tuple[str, float]] = []
    
    def _init_fonts(self):
        """初始化字体"""
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_tiny = None
        
        # 尝试加载中文字体
        for font_path in FONT_PATHS:
            try:
                self.font_large = pygame.font.Font(font_path, 36)
                self.font_medium = pygame.font.Font(font_path, 24)
                self.font_small = pygame.font.Font(font_path, 18)
                self.font_tiny = pygame.font.Font(font_path, 14)
                print(f"Loaded font: {font_path}")
                break
            except:
                continue
        
        # 回退到系统默认字体
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
            self.font_tiny = pygame.font.Font(None, 20)
            print("Using default font")
    
    def _create_beep(self, frequency: int, duration: float) -> pygame.mixer.Sound:
        """创建简单的beep音效"""
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        wave = np.sin(2 * np.pi * frequency * t) * 0.3
        
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    
    def spawn_initial_targets(self):
        """生成初始目标"""
        for _ in range(TARGET_START_COUNT):
            self.spawn_target()
    
    def spawn_target(self):
        """生成一个新目标"""
        # 在边缘生成
        side = random.randint(0, 3)
        if side == 0:  # 上
            x = random.uniform(50, SCREEN_WIDTH - 50)
            y = 50
        elif side == 1:  # 右
            x = SCREEN_WIDTH - 50
            y = random.uniform(50, SCREEN_HEIGHT - 50)
        elif side == 2:  # 下
            x = random.uniform(50, SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT - 50
        else:  # 左
            x = 50
            y = random.uniform(50, SCREEN_HEIGHT - 50)
        
        # 检查是否距离炮台太近
        dist_to_turret = math.hypot(x - self.turret.x, y - self.turret.y)
        if dist_to_turret < 150:
            return
        
        speed = self.target_base_speed * (1 + self.difficulty_level * DIFFICULTY_SPEED_INCREMENT)
        is_silent = len(self.targets) >= DIFFICULTY_SILENT_THRESHOLD
        
        target = Target(x, y, speed, is_silent)
        self.targets.append(target)
    
    def spawn_powerup(self):
        """生成道具"""
        x = random.uniform(100, SCREEN_WIDTH - 100)
        y = random.uniform(100, SCREEN_HEIGHT - 100)
        
        # 检查是否距离炮台太近
        dist_to_turret = math.hypot(x - self.turret.x, y - self.turret.y)
        if dist_to_turret < 100:
            return
        
        from enum import Enum
        class PowerUpType(Enum):
            WIDEBAND = "全频扫描"
            STICKY_BEACON = "黏着信标"
            RICOCHET_CORE = "跳弹散芯"
        
        power_type = random.choice(list(PowerUpType))
        self.powerups.append(PowerUp(x, y, power_type, self.font_tiny))
    
    def update_difficulty(self):
        """更新难度"""
        new_level = int(self.total_score // SCORE_LEVEL_UP)
        if new_level > self.difficulty_level:
            self.difficulty_level = new_level
            self.spawn_target()
    
    def fire_sonar(self):
        """发射声呐"""
        if not self.turret.can_fire_sonar():
            return
        
        is_wideband = False
        if self.turret.current_powerup and self.turret.current_powerup.name == "WIDEBAND":
            is_wideband = True
            self.turret.current_powerup = None
            self.powerup_activated_messages.append(("全频扫描已触发!", 2.0))
        
        wave = SonarWave(self.turret.x, self.turret.y, self.turret.angle, is_wideband)
        self.sonar_waves.append(wave)
        self.turret.reset_sonar()
        
        if self.has_sound:
            self.sonar_sound.play()
        
        # 重置窗口击杀计数
        self.window_kills = 0
        self.last_window_time = pygame.time.get_ticks() / 1000.0
    
    def fire_projectile(self):
        """发射炮弹"""
        # 检查能量是否足够
        if not self.turret.consume_energy():
            return

        has_sticky = self.turret.current_powerup and self.turret.current_powerup.name == "STICKY_BEACON"
        has_ricochet = self.turret.current_powerup and self.turret.current_powerup.name == "RICOCHET_CORE"

        if has_sticky:
            self.turret.current_powerup = None
            self.powerup_activated_messages.append(("黏着信标已触发!", 2.0))
        elif has_ricochet:
            self.turret.current_powerup = None
            self.powerup_activated_messages.append(("跳弹散芯已触发!", 2.0))

        proj = Projectile(self.turret.x, self.turret.y, self.turret.angle,
                         has_sticky=has_sticky, has_ricochet=has_ricochet)
        self.projectiles.append(proj)

        if self.has_sound:
            self.shoot_sound.play()
    
    def add_score(self, points: int, message: str = "", color: Tuple[int, int, int] = WHITE):
        """增加分数"""
        self.score += points
        self.total_score += points
        
        if message:
            self.kill_messages.append((f"{message} +{points}", 2.0, color))
        
        self.update_difficulty()
    
    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新炮台
        self.turret.update(dt, mouse_pos)
        
        # 自动发射声呐
        if self.turret.can_fire_sonar():
            self.fire_sonar()
        
        # 更新目标
        for target in self.targets:
            target.update(dt)
        
        # 更新炮弹
        new_shards = []
        for proj in self.projectiles:
            should_split = proj.update(dt)
            if should_split:
                # 跳弹散芯：分裂为3发小弹片
                base_angle = math.atan2(proj.vy, proj.vx)
                for i in range(-1, 2):
                    shard_angle = base_angle + i * math.pi / 12  # 30度扇形
                    shard = Projectile(proj.x, proj.y, shard_angle, is_shard=True)
                    new_shards.append(shard)
        
        self.projectiles.extend(new_shards)
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # 更新声呐
        for wave in self.sonar_waves:
            wave.update(dt)
            
            # 检查声呐碰撞
            for target in self.targets:
                if not target.dead and wave.check_collision(target):
                    if wave.is_wideband:
                        target.reveal(SONAR_WIDEBAND_REVEAL_DURATION)
                    else:
                        target.reveal(SONAR_REVEAL_DURATION)
        
        self.sonar_waves = [w for w in self.sonar_waves if w.active]
        
        # 更新道具
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0
            if len(self.powerups) < POWERUP_MAX_COUNT:
                self.spawn_powerup()
        
        for powerup in self.powerups:
            powerup.update(dt)

        self.powerups = [p for p in self.powerups if p.active]

        # 炮弹与目标/道具碰撞检测
        hit_any = False
        for proj in self.projectiles:
            if not proj.active:
                continue

            # 先检查是否击中道具（道具判定优先）
            hit_powerup = False
            for powerup in self.powerups:
                if not powerup.active:
                    continue
                if powerup.check_hit(proj.x, proj.y, proj.radius):
                    # 炮弹击中道具！
                    hit_powerup = True
                    powerup.active = False
                    self.turret.current_powerup = powerup.type
                    self.powerup_activated_messages.append((f"获得: {powerup.type.value}!", 2.0))
                    if self.has_sound:
                        self.powerup_sound.play()
                    break

            if hit_powerup:
                proj.active = False
                continue

            for target in self.targets:
                if target.dead:
                    continue

                dist = math.hypot(proj.x - target.x, proj.y - target.y)
                if dist < proj.radius + target.radius:
                    # 命中！
                    hit_any = True
                    proj.active = False

                    # 检查是否显形
                    revealed = target.is_revealed()

                    if revealed:
                        # 黏着信标效果
                        if proj.has_sticky:
                            target.apply_beacon(BEACON_DURATION)
                            self.add_score(0, "信标标记!", ORANGE)
                        else:
                            # 击杀
                            target.dead = True

                            # 计分
                            points = SCORE_KILL
                            message = "击杀"
                            color = WHITE

                            # 检查是否盲狙
                            if not target.visible and target.beacon_timer > 0:
                                # 这是信标击杀，不算盲狙
                                pass
                            elif not target.visible:
                                points = SCORE_BLINDSHOT
                                message = "盲狙!"
                                color = GOLD

                            # 检查极速反应
                            reaction_time = (pygame.time.get_ticks() / 1000.0) - self.last_window_time
                            if reaction_time <= 1.0 and target.visible:
                                points += SCORE_QUICK_BONUS
                                message += " 极速!"

                            # 窗口连击
                            if target.visible:
                                self.window_kills += 1
                                if self.window_kills > 1:
                                    combo_points = SCORE_COMBO_BASE * (self.window_kills - 1)
                                    points += combo_points
                                    message += f" 连击x{self.window_kills}!"

                            self.add_score(points, message, color)

                            if self.has_sound:
                                self.hit_sound.play()
                    else:
                        # 未显形，炮弹穿过
                        pass
        
        # 更新miss streak
        if not hit_any and any(not p.active for p in self.projectiles):
            # 有炮弹失效但没有命中
            self.turret.miss_streak += 1
            if self.turret.miss_streak >= NOISE_JAM_THRESHOLD:
                self.turret.apply_noise_jam()
        elif hit_any:
            self.turret.miss_streak = 0
        
        # 清理死亡目标
        self.targets = [t for t in self.targets if not t.dead or t.death_timer < 0.5]
        
        # 补充目标
        while len(self.targets) < min(TARGET_START_COUNT + self.difficulty_level, TARGET_MAX_COUNT):
            self.spawn_target()
        
        # 更新击杀信息
        new_messages = []
        for msg, timer, color in self.kill_messages:
            timer -= dt
            if timer > 0:
                new_messages.append((msg, timer, color))
        self.kill_messages = new_messages
        
        # 更新道具触发反馈
        new_powerup_msgs = []
        for msg, timer in self.powerup_activated_messages:
            timer -= dt
            if timer > 0:
                new_powerup_msgs.append((msg, timer))
        self.powerup_activated_messages = new_powerup_msgs
    
    def draw(self):
        # 深色背景
        self.screen.fill(DARK_BLUE)
        
        # 绘制网格（微妙的背景）
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(grid_surf, (*GRAY, 20), (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(grid_surf, (*GRAY, 20), (0, i), (SCREEN_WIDTH, i), 1)
        self.screen.blit(grid_surf, (0, 0))
        
        # 绘制声呐
        for wave in self.sonar_waves:
            wave.draw(self.screen)
        
        # 绘制道具
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # 绘制目标
        for target in self.targets:
            target.draw(self.screen)
        
        # 绘制炮弹
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        # 绘制炮台
        self.turret.draw(self.screen, self.font_small)
        
        # 绘制分数
        score_text = self.font_large.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 280, 20))
        
        # 绘制击杀信息
        for i, (msg, timer, color) in enumerate(self.kill_messages):
            alpha = int(255 * min(timer / 0.5, 1.0))
            surf = self.font_medium.render(msg, True, color)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (SCREEN_WIDTH - 350, 70 + i * 30))
        
        # 绘制道具触发反馈
        for i, (msg, timer) in enumerate(self.powerup_activated_messages):
            alpha = int(255 * min(timer / 0.5, 1.0))
            surf = self.font_medium.render(msg, True, GOLD)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - 100, 100 + i * 30))
        
        # 绘制难度信息
        level_text = self.font_small.render(f"等级: {self.difficulty_level}", True, GRAY)
        self.screen.blit(level_text, (20, 20))
        
        target_count_text = self.font_small.render(f"目标: {len(self.targets)}", True, GRAY)
        self.screen.blit(target_count_text, (20, 45))
        
        # 绘制道具说明
        if self.turret.current_powerup:
            power_text = self.font_medium.render(
                f"已装备: {self.turret.current_powerup.value}", True, GOLD)
            self.screen.blit(power_text, (20, SCREEN_HEIGHT - 60))
            
            # 绘制道具效果说明
            if self.turret.current_powerup.name == "WIDEBAND":
                hint = self.font_small.render("下一次声呐将变为全屏360°扫描", True, (*GRAY, 200))
            elif self.turret.current_powerup.name == "STICKY_BEACON":
                hint = self.font_small.render("下一次命中将标记目标6秒", True, (*GRAY, 200))
            else:
                hint = self.font_small.render("下一次炮弹反弹后分裂为3发", True, (*GRAY, 200))
            self.screen.blit(hint, (20, SCREEN_HEIGHT - 35))
        
        # 绘制炮弹充能槽
        self.turret.draw_energy_bar(self.screen, self.font_small)

        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.fire_projectile()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def draw_title_screen(self):
        """绘制启动页"""
        self.screen.fill(DARK_BLUE)

        # 绘制网格背景
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(grid_surf, (*GRAY, 20), (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(grid_surf, (*GRAY, 20), (0, i), (SCREEN_WIDTH, i), 1)
        self.screen.blit(grid_surf, (0, 0))

        # 标题
        title = self.font_large.render("回声定位炮", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        subtitle = self.font_medium.render("EchoLure", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)

        # 核心规则说明
        rules = [
            ("核心规则", WHITE, 240),
            ("", None, 0),
            ("• 目标处于量子隐形状态，肉眼不可见", LIGHT_GRAY, 280),
            ("• 声呐每4秒自动充能，向鼠标方向发射扇形探测波", LIGHT_GRAY, 310),
            ("• 被声呐扫到的目标会短暂显形2.5秒", LIGHT_GRAY, 340),
            ("• 未显形的目标炮弹直接穿过，无法造成伤害", LIGHT_GRAY, 370),
            ("", None, 0),
            ("操作方式", WHITE, 420),
            ("", None, 0),
            ("• 鼠标移动：控制炮台瞄准方向", LIGHT_GRAY, 460),
            ("• 空格：发射炮弹（消耗1格能量）", LIGHT_GRAY, 490),
            ("• 能量槽共5格，每秒恢复1格", LIGHT_GRAY, 520),
            ("", None, 0),
            ("道具系统", WHITE, 570),
            ("", None, 0),
            ("• 射击金色光球获取道具，最多持有1个", LIGHT_GRAY, 610),
            ("• 全频扫描：下一次声呐变为360°全屏扫描", LIGHT_GRAY, 640),
            ("• 黏着信标：下一次命中标记目标6秒", LIGHT_GRAY, 670),
            ("• 跳弹散芯：下一次反弹后分裂为3发弹片", LIGHT_GRAY, 700),
        ]

        for text, color, y in rules:
            if color is not None:
                surf = self.font_small.render(text, True, color)
                rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(surf, rect)

        # Start 按钮
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 100, 160, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_hover = button_rect.collidepoint(mouse_pos)

        button_color = CYAN if button_hover else DARK_CYAN
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, button_rect, width=2, border_radius=8)

        start_text = self.font_medium.render("START", True, WHITE)
        start_rect = start_text.get_rect(center=button_rect.center)
        self.screen.blit(start_text, start_rect)

        pygame.display.flip()
        return button_rect

    def run_title_screen(self):
        """运行启动页"""
        in_title = True
        while in_title and self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    in_title = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        in_title = False
                    elif event.key == pygame.K_SPACE:
                        in_title = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        button_rect = self.draw_title_screen()
                        if button_rect.collidepoint(event.pos):
                            in_title = False

            if in_title:
                self.draw_title_screen()

    def run(self):
        # 显示启动页
        self.run_title_screen()

        # 主游戏循环
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
