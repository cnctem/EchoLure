"""回声定位炮 - 游戏实体类"""

import pygame
import math
import random
from typing import List, Tuple
from .constants import *


def draw_glow(surface, pos, radius, color, alpha=30):
    """绘制发光效果"""
    for i in range(5):
        r = radius + i * 8
        surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha - i*5), (r, r), r)
        surface.blit(surf, (pos[0]-r, pos[1]-r))


class Target:
    """目标类 - 量子隐形状态的目标"""
    
    def __init__(self, x: float, y: float, speed: float, is_silent: bool = False):
        self.x = x
        self.y = y
        self.speed = speed
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = TARGET_RADIUS
        self.is_silent = is_silent
        
        # 显形状态
        self.visible = False
        self.visible_timer = 0.0
        self.beacon_timer = 0.0  # 黏着信标标记时间
        
        # 受惊效果
        self.startled = False
        self.startle_timer = 0.0
        
        # 死亡动画
        self.dead = False
        self.death_timer = 0.0
        
    def update(self, dt: float):
        if self.dead:
            self.death_timer += dt
            return
            
        # 受惊加速和偏转
        if self.startled:
            self.startle_timer -= dt
            if self.startle_timer <= 0:
                self.startled = False
            else:
                # 轻微加速
                speed_multiplier = 1.3
                self.vx *= speed_multiplier
                self.vy *= speed_multiplier
                # 随机偏转
                angle_change = random.uniform(-0.5, 0.5)
                speed = math.hypot(self.vx, self.vy)
                current_angle = math.atan2(self.vy, self.vx)
                new_angle = current_angle + angle_change
                self.vx = math.cos(new_angle) * speed
                self.vy = math.sin(new_angle) * speed
        
        # 移动
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 碰墙反弹
        bounced = False
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
            bounced = True
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -abs(self.vx)
            bounced = True
            
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy)
            bounced = True
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy = -abs(self.vy)
            bounced = True
        
        # 反弹后恢复正常速度（如果不是受惊状态）
        if bounced and not self.startled:
            current_speed = math.hypot(self.vx, self.vy)
            if current_speed > self.speed * 1.1:
                scale = self.speed / current_speed
                self.vx *= scale
                self.vy *= scale
        
        # 显形计时器
        if self.visible_timer > 0:
            self.visible_timer -= dt
            if self.visible_timer <= 0:
                self.visible = False
                self.visible_timer = 0
        
        # 黏着信标计时器
        if self.beacon_timer > 0:
            self.beacon_timer -= dt
            if self.beacon_timer <= 0:
                self.beacon_timer = 0
    
    def reveal(self, duration: float):
        """显形目标"""
        if not self.dead:
            self.visible = True
            self.visible_timer = duration
            if not self.startled:
                self.startled = True
                self.startle_timer = 0.5
    
    def apply_beacon(self, duration: float = BEACON_DURATION):
        """应用黏着信标"""
        self.beacon_timer = duration
    
    def is_revealed(self) -> bool:
        """检查目标是否被显形（包括黏着信标）"""
        return self.visible or self.beacon_timer > 0
    
    def draw(self, screen: pygame.Surface):
        if self.dead:
            # 死亡动画
            progress = min(self.death_timer / 0.3, 1.0)
            alpha = int(255 * (1 - progress))
            radius = self.radius + progress * 20
            surf = pygame.Surface((int(radius*2), int(radius*2)), pygame.SRCALPHA)
            if self.is_silent:
                color = (RED[0], RED[1], RED[2])
            else:
                color = (CYAN[0], CYAN[1], CYAN[2])
            pygame.draw.circle(surf, (*color, alpha), (int(radius), int(radius)), int(radius))
            screen.blit(surf, (int(self.x - radius), int(self.y - radius)))
            return
        
        revealed = self.is_revealed()
        
        if revealed:
            if self.is_silent and self.beacon_timer <= 0:
                # 静默目标只显示闪烁红点
                blink = (pygame.time.get_ticks() // 200) % 2 == 0
                if blink:
                    pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 6)
                    draw_glow(screen, (int(self.x), int(self.y)), 10, RED, 50)
            else:
                # 正常显形
                # 身体
                alpha = 180 if self.visible else 255
                if self.beacon_timer > 0:
                    color = ORANGE
                    # 信标发光效果
                    draw_glow(screen, (int(self.x), int(self.y)), 25, ORANGE, 40)
                else:
                    color = CYAN
                    
                surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*color, alpha), (self.radius, self.radius), self.radius)
                screen.blit(surf, (int(self.x - self.radius), int(self.y - self.radius)))
                
                # 方向箭头
                if not self.is_silent:
                    angle = math.atan2(self.vy, self.vx)
                    arrow_len = 25
                    end_x = self.x + math.cos(angle) * arrow_len
                    end_y = self.y + math.sin(angle) * arrow_len
                    pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), 
                                   (int(end_x), int(end_y)), 2)
                    # 箭头尖端
                    tip_angle1 = angle + 2.5
                    tip_angle2 = angle - 2.5
                    tip_len = 8
                    pygame.draw.line(screen, WHITE, (int(end_x), int(end_y)),
                                   (int(end_x - math.cos(tip_angle1)*tip_len), 
                                    int(end_y - math.sin(tip_angle1)*tip_len)), 2)
                    pygame.draw.line(screen, WHITE, (int(end_x), int(end_y)),
                                   (int(end_x - math.cos(tip_angle2)*tip_len), 
                                    int(end_y - math.sin(tip_angle2)*tip_len)), 2)
        else:
            # 未显形时几乎不可见，只有极淡的痕迹
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*DARK_CYAN, 8), (self.radius, self.radius), self.radius)
            screen.blit(surf, (int(self.x - self.radius), int(self.y - self.radius)))


class SonarWave:
    """声呐波类"""
    
    def __init__(self, x: float, y: float, angle: float, is_wideband: bool = False):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_wideband = is_wideband
        self.radius = 10
        self.max_radius = SONAR_WIDEBAND_MAX_RADIUS if is_wideband else SONAR_MAX_RADIUS
        self.speed = SONAR_SPEED
        self.active = True
        self.width = math.pi * 2 if is_wideband else SONAR_WIDTH
        
    def update(self, dt: float):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        
        alpha = int(200 * (1 - self.radius / self.max_radius))
        color = GOLD if self.is_wideband else CYAN
        
        if self.is_wideband:
            # 环形扫描
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha//3), (int(self.x), int(self.y)), int(self.radius), 3)
            pygame.draw.circle(surf, (*color, alpha//6), (int(self.x), int(self.y)), int(self.radius), 8)
            screen.blit(surf, (0, 0))
        else:
            # 扇形扫描
            points = [(self.x, self.y)]
            num_points = 30
            for i in range(num_points + 1):
                a = self.angle - self.width/2 + (self.width / num_points) * i
                px = self.x + math.cos(a) * self.radius
                py = self.y + math.sin(a) * self.radius
                points.append((px, py))
            
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (*color, alpha//4), points)
            pygame.draw.polygon(surf, (*color, alpha//2), points, 2)
            screen.blit(surf, (0, 0))
    
    def check_collision(self, target: Target) -> bool:
        """检查声呐是否扫到目标"""
        if not self.active:
            return False
        
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        
        if abs(dist - self.radius) > 20:  # 在声呐波前附近
            return False
        
        if self.is_wideband:
            return True
        
        # 检查是否在扇形角度内
        angle_to_target = math.atan2(dy, dx)
        angle_diff = abs(angle_to_target - self.angle)
        # 处理角度环绕
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        
        return abs(angle_diff) <= self.width / 2


class Projectile:
    """炮弹类"""
    
    def __init__(self, x: float, y: float, angle: float, is_shard: bool = False, 
                 has_sticky: bool = False, has_ricochet: bool = False):
        self.x = x
        self.y = y
        self.speed = PROJECTILE_SPEED
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.radius = SHARD_RADIUS if is_shard else PROJECTILE_RADIUS
        self.is_shard = is_shard
        self.has_sticky = has_sticky
        self.has_ricochet = has_ricochet
        self.bounces = 0
        self.max_bounces = MAX_BOUNCES
        self.active = True
        self.trail = []  # 轨迹点
        
    def update(self, dt: float):
        if not self.active:
            return
        
        # 记录轨迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # 移动
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 反弹
        bounced = False
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
            bounced = True
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -abs(self.vx)
            bounced = True
            
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy)
            bounced = True
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy = -abs(self.vy)
            bounced = True
        
        if bounced:
            self.bounces += 1
            if self.bounces > self.max_bounces:
                self.active = False
            elif self.has_ricochet and self.bounces == 1:
                # 跳弹散芯：首次反弹后分裂
                self.active = False
                return True  # 返回True表示需要分裂
        
        # 出界检查
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or \
           self.y < -50 or self.y > SCREEN_HEIGHT + 50:
            self.active = False
        
        return False
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        
        # 绘制轨迹
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(255 * (i / len(self.trail)))
                color = (*ORANGE, alpha) if self.has_ricochet else (*WHITE, alpha)
                pygame.draw.line(screen, color, 
                               (int(self.trail[i][0]), int(self.trail[i][1])),
                               (int(self.trail[i+1][0]), int(self.trail[i+1][1])), 
                               self.radius)
        
        # 绘制炮弹
        color = ORANGE if self.has_ricochet else WHITE
        if self.has_sticky:
            color = GREEN
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        draw_glow(screen, (int(self.x), int(self.y)), 15, color, 30)


class PowerUp:
    """道具类"""
    
    def __init__(self, x: float, y: float, power_type, font):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = POWERUP_RADIUS
        self.active = True
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.font = font
        
    def update(self, dt: float):
        # 漂浮动画
        self.bob_offset += dt * 3
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        
        bob_y = math.sin(self.bob_offset) * 5
        y = self.y + bob_y
        
        # 金色光球
        draw_glow(screen, (int(self.x), int(y)), 20, GOLD, 50)
        pygame.draw.circle(screen, GOLD, (int(self.x), int(y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y)), self.radius - 3)
        
        # 图标
        if self.type.name == "WIDEBAND":
            text = self.font.render("全", True, BLACK)
        elif self.type.name == "STICKY_BEACON":
            text = self.font.render("信", True, BLACK)
        else:
            text = self.font.render("跳", True, BLACK)
        
        rect = text.get_rect(center=(int(self.x), int(y)))
        screen.blit(text, rect)
    
    def check_hit(self, proj_x: float, proj_y: float, proj_radius: float) -> bool:
        """检查是否被炮弹击中"""
        dist = math.hypot(self.x - proj_x, self.y - proj_y)
        return dist < self.radius + proj_radius


class Turret:
    """炮台类"""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = TURRET_RADIUS
        self.angle = 0

        # 声呐充能
        self.sonar_cooldown = SONAR_COOLDOWN
        self.sonar_timer = 0.0
        self.sonar_charging = True

        # 道具
        self.current_powerup = None

        # 噪音干扰
        self.noise_jammed = False
        self.noise_timer = 0.0

        # 连射计数
        self.miss_streak = 0

        # 炮弹充能槽
        self.energy_slots = ENERGY_MAX_SLOTS
        self.energy_regen_timer = 0.0

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        # 更新角度
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)

        # 噪音干扰
        if self.noise_jammed:
            self.noise_timer -= dt
            if self.noise_timer <= 0:
                self.noise_jammed = False
                self.sonar_timer = 0  # 重置充能
            return

        # 声呐充能
        if self.sonar_charging:
            self.sonar_timer += dt
            if self.sonar_timer >= self.sonar_cooldown:
                self.sonar_timer = self.sonar_cooldown
                self.sonar_charging = False

        # 炮弹充能槽恢复
        if self.energy_slots < ENERGY_MAX_SLOTS:
            self.energy_regen_timer += dt
            if self.energy_regen_timer >= 1.0 / ENERGY_REGEN_RATE:
                self.energy_slots += 1
                self.energy_regen_timer = 0.0

    def can_fire(self) -> bool:
        """检查是否有足够能量发射炮弹"""
        return self.energy_slots >= ENERGY_SHOOT_COST

    def consume_energy(self) -> bool:
        """消耗能量发射炮弹，返回是否成功"""
        if self.can_fire():
            self.energy_slots -= ENERGY_SHOOT_COST
            self.energy_regen_timer = 0.0
            return True
        return False
    
    def can_fire_sonar(self) -> bool:
        return not self.sonar_charging and not self.noise_jammed
    
    def reset_sonar(self):
        self.sonar_timer = 0.0
        self.sonar_charging = True
    
    def apply_noise_jam(self, duration: float = NOISE_JAM_DURATION):
        self.noise_jammed = True
        self.noise_timer = duration
        self.miss_streak = 0
    
    def draw(self, screen: pygame.Surface, font):
        # 炮台主体
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, LIGHT_GRAY, (int(self.x), int(self.y)), self.radius - 4)
        
        # 炮管
        barrel_len = BARREL_LENGTH
        end_x = self.x + math.cos(self.angle) * barrel_len
        end_y = self.y + math.sin(self.angle) * barrel_len
        pygame.draw.line(screen, LIGHT_GRAY, (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 8)
        pygame.draw.circle(screen, WHITE, (int(end_x), int(end_y)), 5)
        
        # 充能环
        if not self.noise_jammed:
            charge_ratio = self.sonar_timer / self.sonar_cooldown
            ring_radius = self.radius + 8
            
            # 背景环
            ring_surf = pygame.Surface((ring_radius*2+4, ring_radius*2+4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*GRAY, 100), (ring_radius+2, ring_radius+2), ring_radius, 2)
            screen.blit(ring_surf, (int(self.x - ring_radius - 2), int(self.y - ring_radius - 2)))
            
            # 充能进度
            if charge_ratio > 0:
                points = []
                num_segments = int(60 * charge_ratio)
                for i in range(num_segments + 1):
                    a = -math.pi/2 + (2 * math.pi * i / 60)
                    px = self.x + math.cos(a) * ring_radius
                    py = self.y + math.sin(a) * ring_radius
                    points.append((px, py))
                
                if len(points) > 1:
                    color = CYAN if charge_ratio < 1.0 else GREEN
                    for i in range(len(points) - 1):
                        pygame.draw.line(screen, color, points[i], points[i+1], 3)
        else:
            # 噪音干扰显示
            jam_text = font.render("噪音干扰", True, RED)
            rect = jam_text.get_rect(center=(int(self.x), int(self.y) + 40))
            screen.blit(jam_text, rect)
        
        # 道具指示器
        if self.current_powerup:
            power_text = font.render(
                f"道具: {self.current_powerup.value}", True, GOLD)
            rect = power_text.get_rect(center=(int(self.x), int(self.y) - 40))
            screen.blit(power_text, rect)

    def draw_energy_bar(self, screen: pygame.Surface, font):
        """在屏幕底部绘制炮弹充能槽"""
        bar_y = SCREEN_HEIGHT - 40
        slot_width = 40
        slot_height = 20
        slot_gap = 8
        total_width = ENERGY_MAX_SLOTS * slot_width + (ENERGY_MAX_SLOTS - 1) * slot_gap
        start_x = (SCREEN_WIDTH - total_width) // 2

        # 绘制背景槽
        for i in range(ENERGY_MAX_SLOTS):
            x = start_x + i * (slot_width + slot_gap)
            rect = pygame.Rect(x, bar_y, slot_width, slot_height)
            pygame.draw.rect(screen, (*GRAY, 80), rect, border_radius=4)
            pygame.draw.rect(screen, (*LIGHT_GRAY, 120), rect, width=2, border_radius=4)

        # 绘制已充能的槽
        for i in range(self.energy_slots):
            x = start_x + i * (slot_width + slot_gap)
            rect = pygame.Rect(x, bar_y, slot_width, slot_height)
            # 充能颜色：满格为亮青色，不满为暗青色
            fill_color = CYAN if i < self.energy_slots else (*DARK_CYAN, 150)
            pygame.draw.rect(screen, fill_color, rect, border_radius=4)
            # 高光效果
            highlight = pygame.Rect(x + 2, bar_y + 2, slot_width - 4, slot_height // 2 - 2)
            pygame.draw.rect(screen, (*WHITE, 60), highlight, border_radius=2)

        # 绘制充能进度（当前正在恢复的槽）
        if self.energy_slots < ENERGY_MAX_SLOTS:
            x = start_x + self.energy_slots * (slot_width + slot_gap)
            rect = pygame.Rect(x, bar_y, slot_width, slot_height)
            fill_width = int(slot_width * self.energy_regen_timer * ENERGY_REGEN_RATE)
            if fill_width > 0:
                fill_rect = pygame.Rect(x, bar_y, fill_width, slot_height)
                pygame.draw.rect(screen, (*DARK_CYAN, 180), fill_rect, border_radius=4)

        # 标签
        label = font.render("炮弹能量", True, LIGHT_GRAY)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 15))
        screen.blit(label, label_rect)
