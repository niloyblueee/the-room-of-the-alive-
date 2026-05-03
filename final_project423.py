import math
import time
import random
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

W_WIDTH, W_HEIGHT = 800, 600

PLAYER_SPEED = 12.0

# ---------- colors ----------
C_BODY   = (0.85, 0.85, 0.85)
C_CLOTH  = (0.15, 0.15, 0.18)
C_GOLD   = (0.80, 0.65, 0.20)
C_DETAIL = (0.20, 0.20, 0.20)
C_BODY3  = (0.80, 0.70, 0.90)
C_CLOTH3 = (0.30, 0.10, 0.30)

ENEMY_FB_OUTER = (0.1, 0.8, 0.2)
ENEMY_FB_INNER = (1.0, 1.0, 1.0)
ARENA_SIZE = 80
TILE_SIZE = 4.0
OBSTACLE_COUNT = 12
OBJECT_COUNT = 15

TILE_COLORS = [
    (0.25, 0.12, 0.20),  # Dark plum
    (0.30, 0.08, 0.12),  # Dark blood
    (0.18, 0.10, 0.25),  # Deep purple
    (0.28, 0.15, 0.18),  # Flesh tone
    (0.20, 0.08, 0.15),  # Dark magenta
]

FLOOR_VARIATIONS = [
    (0.15, 0.05, 0.08),  # Blood stain
    (0.25, 0.20, 0.12),  # Dirt patch
    (0.35, 0.08, 0.08),  # Fresh blood
    (0.12, 0.12, 0.18),  # Shadow patch
]



class GameObject:
    def __init__(self, x, z, obj_type):
        self.x = x
        self.y = 1.0
        self.z = z
        self.obj_type = obj_type

        self.is_held = False
        self.grounded = True

        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.velocity_z = 0.0

        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2.0, 2.0)
        self.glow_time = random.uniform(0, 6.28)

        if obj_type == "skull":
            self.color = (0.86, 0.82, 0.72)
            self.size = 0.45
        elif obj_type == "bone":
            self.color = (0.90, 0.84, 0.68)
            self.size = 0.45
        elif obj_type == "ribcage":
            self.color = (0.82, 0.76, 0.64)
            self.size = 0.55
        elif obj_type == "spine":
            self.color = (0.78, 0.72, 0.60)
            self.size = 0.50
        elif obj_type == "coffin":
            self.color = (0.23, 0.10, 0.08)
            self.size = 0.65
        elif obj_type == "candle":
            self.color = (0.85, 0.75, 0.62)
            self.size = 0.40
        elif obj_type == "book":
            self.color = (0.36, 0.10, 0.20)
            self.size = 0.48
        elif obj_type == "potion":
            self.color = (0.65, 0.10, 0.75)
            self.size = 0.38
        elif obj_type == "dagger":
            self.color = (0.70, 0.72, 0.72)
            self.size = 0.55
        elif obj_type == "heart":
            self.color = (0.68, 0.06, 0.08)
            self.size = 0.42
        elif obj_type == "eye":
            self.color = (0.90, 0.86, 0.76)
            self.size = 0.42
        else:
            self.color = (0.45, 0.35, 0.45)
            self.size = 0.45

        self.has_glow = obj_type in ["potion", "heart", "candle", "eye"]

    def update(self, dt):
        if self.is_held:
            self.rotation += 90.0 * dt
            self.glow_time += dt * 4.0
            return

        if not self.grounded:
            self.velocity_y -= 22.0 * dt

            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            self.z += self.velocity_z * dt

            self.rotation += self.rotation_speed * 160.0 * dt

            if self.y <= 1.0:
                self.y = 1.0

                
                if abs(self.velocity_y) > 4.0:
                    self.velocity_y *= -0.28
                    self.velocity_x *= 0.65
                    self.velocity_z *= 0.65
                else:
                    self.velocity_y = 0.0
                    self.velocity_x *= 0.45
                    self.velocity_z *= 0.45

                if abs(self.velocity_x) < 0.25 and abs(self.velocity_z) < 0.25:
                    self.grounded = True
                    self.velocity_x = 0.0
                    self.velocity_y = 0.0
                    self.velocity_z = 0.0

            # bounce from arena walls
            if self.x < -38 or self.x > 38:
                self.x = max(-38, min(38, self.x))
                self.velocity_x *= -0.55
            if self.z < -38 or self.z > 38:
                self.z = max(-38, min(38, self.z))
                self.velocity_z *= -0.55

        else:
            self.rotation += self.rotation_speed

        self.glow_time += dt * 4.0

    def throw_from_player(self, player_x, player_y, player_z, player_yaw, player_pitch, power=28.0):
        fx = math.sin(math.radians(player_yaw)) * math.cos(math.radians(player_pitch))
        fy = math.sin(math.radians(player_pitch))
        fz = -math.cos(math.radians(player_yaw)) * math.cos(math.radians(player_pitch))

        self.is_held = False
        self.grounded = False

        
        self.x = player_x + fx * 2.4
        self.y = player_y - 0.2 + fy * 1.0
        self.z = player_z + fz * 2.4

        self.velocity_x = fx * power
        self.velocity_y = fy * power + 5.5
        self.velocity_z = fz * power

        self.rotation_speed = random.uniform(3.0, 7.0)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)

        if not self.grounded:
            glRotatef(self.rotation * 0.7, 1, 0, 0)

        self.draw_model()
        glPopMatrix()

    def draw_model(self):

        if self.has_glow:
            
            pulse = 1.20 + 0.10 * math.sin(self.glow_time)
            glColor3f(min(self.color[0] + 0.12, 1.0),
                      min(self.color[1] + 0.08, 1.0),
                      min(self.color[2] + 0.12, 1.0))
            glPushMatrix()
            glScalef(pulse, pulse, pulse)
            dsph(self.size, 10, 10)
            glPopMatrix()

        glColor3f(*self.color)

        if self.obj_type == "skull":
            self._draw_skull()
        elif self.obj_type == "bone":
            self._draw_bone()
        elif self.obj_type == "ribcage":
            self._draw_ribcage()
        elif self.obj_type == "spine":
            self._draw_spine()
        elif self.obj_type == "coffin":
            self._draw_coffin()
        elif self.obj_type == "candle":
            self._draw_candle()
        elif self.obj_type == "book":
            self._draw_book()
        elif self.obj_type == "potion":
            self._draw_potion()
        elif self.obj_type == "dagger":
            self._draw_dagger()
        elif self.obj_type == "heart":
            self._draw_heart()
        elif self.obj_type == "eye":
            self._draw_eye()
        else:
            self._draw_generic()

    def _draw_skull(self):
        glColor3f(0.86, 0.82, 0.72)
        glPushMatrix()
        glScalef(0.55, 0.45, 0.45)
        dsph(0.75, 16, 16)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -0.30, 0.18)
        glScalef(0.45, 0.25, 0.35)
        dcube(0.8)
        glPopMatrix()

        glColor3f(0.02, 0.02, 0.02)
        for ex in [-0.18, 0.18]:
            glPushMatrix()
            glTranslatef(ex, 0.08, 0.40)
            glScalef(0.13, 0.13, 0.04)
            dcube(1.0)
            glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -0.08, 0.43)
        glScalef(0.08, 0.12, 0.04)
        dcube(1.0)
        glPopMatrix()

        # teeth
        glColor3f(0.12, 0.10, 0.08)
        for i in range(5):
            glPushMatrix()
            glTranslatef(-0.16 + i * 0.08, -0.32, 0.48)
            glScalef(0.025, 0.09, 0.03)
            dcube(1.0)
            glPopMatrix()

    def _draw_bone(self):
        glColor3f(0.90, 0.84, 0.68)
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        dcyl(0.09, 0.09, 1.1, 10, 2)
        glPopMatrix()

        for sx in [-0.55, 0.55]:
            for sy in [-0.10, 0.10]:
                glPushMatrix()
                glTranslatef(sx, sy, 0)
                dsph(0.16, 10, 10)
                glPopMatrix()

    def _draw_ribcage(self):
        glColor3f(0.82, 0.76, 0.64)

        # spine column
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        dcyl(0.06, 0.06, 0.9, 8, 2)
        glPopMatrix()

        # ribs as curved-looking side bars
        for i in range(5):
            y = 0.30 - i * 0.14
            width = 0.30 + i * 0.05
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(side * width, y, 0)
                glRotatef(side * 35, 0, 0, 1)
                glScalef(0.08, 0.55, 0.08)
                dcube(1.0)
                glPopMatrix()

    def _draw_spine(self):
        glColor3f(0.78, 0.72, 0.60)
        for i in range(7):
            glPushMatrix()
            glTranslatef(0, 0.45 - i * 0.15, 0)
            dsph(0.13, 8, 8)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(-0.18, 0.45 - i * 0.15, 0)
            glScalef(0.22, 0.04, 0.04)
            dcube(1.0)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0.18, 0.45 - i * 0.15, 0)
            glScalef(0.22, 0.04, 0.04)
            dcube(1.0)
            glPopMatrix()

    def _draw_coffin(self):
        glColor3f(0.23, 0.10, 0.08)
        glPushMatrix()
        glScalef(0.65, 0.25, 1.05)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.45, 0.20, 0.12)
        glPushMatrix()
        glTranslatef(0, 0.15, 0)
        glScalef(0.55, 0.08, 0.92)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.85, 0.70, 0.25)
        glPushMatrix()
        glTranslatef(0, 0.22, 0)
        glScalef(0.10, 0.06, 0.55)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0.23, 0.05)
        glScalef(0.38, 0.06, 0.10)
        dcube(1.0)
        glPopMatrix()

    def _draw_candle(self):
        glColor3f(0.88, 0.78, 0.65)
        glPushMatrix()
        glTranslatef(0, 0.15, 0)
        glScalef(0.28, 0.55, 0.28)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.18, 0.10, 0.05)
        glPushMatrix()
        glTranslatef(0, 0.48, 0)
        glScalef(0.05, 0.12, 0.05)
        dcube(1.0)
        glPopMatrix()

        glColor3f(1.0, 0.45, 0.05)
        glPushMatrix()
        glTranslatef(0, 0.65, 0)
        dsph(0.13, 8, 8)
        glPopMatrix()

        glColor3f(1.0, 0.90, 0.25)
        glPushMatrix()
        glTranslatef(0, 0.68, 0)
        dsph(0.07, 6, 6)
        glPopMatrix()

    def _draw_book(self):
        glColor3f(0.34, 0.07, 0.17)
        glPushMatrix()
        glScalef(0.75, 0.18, 0.55)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.78, 0.70, 0.55)
        glPushMatrix()
        glTranslatef(0.04, 0.11, 0)
        glScalef(0.66, 0.05, 0.50)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.80, 0.65, 0.15)
        glPushMatrix()
        glTranslatef(0, 0.15, 0)
        glScalef(0.09, 0.04, 0.48)
        dcube(1.0)
        glPopMatrix()

    def _draw_potion(self):
        glColor3f(0.62, 0.08, 0.72)
        glPushMatrix()
        glScalef(0.35, 0.45, 0.35)
        dsph(0.8, 12, 12)
        glPopMatrix()

        glColor3f(0.18, 0.05, 0.20)
        glPushMatrix()
        glTranslatef(0, 0.45, 0)
        glScalef(0.16, 0.28, 0.16)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.50, 0.30, 0.12)
        glPushMatrix()
        glTranslatef(0, 0.62, 0)
        glScalef(0.22, 0.12, 0.22)
        dcube(1.0)
        glPopMatrix()

    def _draw_dagger(self):
        glColor3f(0.48, 0.28, 0.12)
        glPushMatrix()
        glTranslatef(0, -0.35, 0)
        glScalef(0.12, 0.45, 0.12)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.75, 0.75, 0.70)
        glPushMatrix()
        glTranslatef(0, 0.10, 0)
        glScalef(0.45, 0.08, 0.08)
        dcube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0.52, 0)
        glRotatef(-90, 1, 0, 0)
        dcyl(0.08, 0.00, 0.85, 6, 1)
        glPopMatrix()

    def _draw_heart(self):
        pulse = 1.0 + math.sin(self.glow_time * 2.0) * 0.06
        glColor3f(0.68, 0.06, 0.08)
        glPushMatrix()
        glScalef(pulse, pulse, pulse)

        glPushMatrix()
        glTranslatef(-0.18, 0.10, 0)
        dsph(0.26, 12, 12)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.18, 0.10, 0)
        dsph(0.26, 12, 12)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -0.18, 0)
        glScalef(0.45, 0.45, 0.35)
        dsph(0.45, 10, 10)
        glPopMatrix()

        glPopMatrix()

    def _draw_eye(self):
        glColor3f(0.90, 0.86, 0.76)
        dsph(0.42, 16, 16)

        glColor3f(0.65, 0.05, 0.08)
        glPushMatrix()
        glTranslatef(0, 0, 0.34)
        dsph(0.18, 12, 12)
        glPopMatrix()

        glColor3f(0.02, 0.02, 0.02)
        glPushMatrix()
        glTranslatef(0, 0, 0.47)
        dsph(0.08, 8, 8)
        glPopMatrix()

    def _draw_generic(self):
        glPushMatrix()
        glScalef(self.size, self.size, self.size)
        dsph(0.5, 10, 10)
        glPopMatrix()



class Obstacle:
    def __init__(self, x, z, obs_type):
        self.x = x
        self.z = z
        self.obs_type = obs_type
        self.rotation = random.uniform(0, 360)
        
        if obs_type == "pillar":
            self.height = 3.5
            self.width = 1.2
            self.depth = 1.2
            self.color = (0.25, 0.22, 0.28)
        elif obs_type == "tombstone":
            self.height = 2.0
            self.width = 0.8
            self.depth = 0.2
            self.color = (0.35, 0.32, 0.35)
        elif obs_type == "cage":
            self.height = 2.8
            self.width = 1.5
            self.depth = 1.5
            self.color = (0.30, 0.28, 0.30)
        elif obs_type == "altar":
            self.height = 0.8
            self.width = 1.8
            self.depth = 1.0
            self.color = (0.28, 0.25, 0.28)
        else:
            self.height = 1.2
            self.width = 2.0
            self.depth = 0.8
            self.color = (0.32, 0.28, 0.32)
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.height / 2, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        glColor3f(*self.color)
        
        if self.obs_type == "pillar":
            self._draw_pillar()
        elif self.obs_type == "tombstone":
            self._draw_tombstone()
        elif self.obs_type == "cage":
            self._draw_cage()
        elif self.obs_type == "altar":
            self._draw_altar()
        else:
            self._draw_sarcophagus()
        
        glPopMatrix()
    
    def _draw_pillar(self):
        glPushMatrix()
        glScalef(self.width, self.height, self.depth)
        dcube(1.0)
        glPopMatrix()
        glColor3f(0.15, 0.13, 0.18)
        glBegin(GL_LINES)
        glVertex3f(-0.4, 0.5, 0.61)
        glVertex3f(-0.1, 1.2, 0.61)
        glVertex3f(0.3, 1.8, 0.61)
        glVertex3f(0.5, 2.2, 0.61)
        glEnd()
    
    def _draw_tombstone(self):
        glPushMatrix()
        glScalef(self.width, self.height, self.depth)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, self.height - 0.4, 0.12)
        glScalef(self.width * 0.9, 0.6, self.depth + 0.02)
        dsph(0.5, 8, 8)
        glPopMatrix()
        glColor3f(0.18, 0.16, 0.20)
        glPushMatrix()
        glTranslatef(0, self.height - 0.8, 0.13)
        glScalef(0.5, 0.08, 0.03)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, self.height - 1.2, 0.13)
        glScalef(0.35, 0.06, 0.03)
        dcube(1.0)
        glPopMatrix()
    
    def _draw_cage(self):
        glColor3f(0.25, 0.22, 0.25)
        for i in range(8):
            angle = i * 45.0
            rad = math.radians(angle)
            x = math.cos(rad) * 0.7
            z = math.sin(rad) * 0.7
            glPushMatrix()
            glTranslatef(x, self.height / 2, z)
            glScalef(0.08, self.height, 0.08)
            dcube(1.0)
            glPopMatrix()
        for y_level in [0.5, 1.5, 2.5]:
            glPushMatrix()
            glTranslatef(0, y_level, 0)
            glRotatef(90, 1, 0, 0)
            dcyl(0.78, 0.78, 0.08, 12)
            glPopMatrix()
    
    def _draw_altar(self):
        glPushMatrix()
        glTranslatef(0, -0.3, 0)
        glScalef(self.width + 0.3, 0.3, self.depth + 0.3)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glScalef(self.width, self.height, self.depth)
        dcube(1.0)
        glPopMatrix()
        glColor3f(0.55, 0.08, 0.08)
        glPushMatrix()
        glTranslatef(0, self.height / 2 + 0.05, 0.45)
        glScalef(0.8, 0.05, 0.6)
        dcube(1.0)
        glPopMatrix()
    
    def _draw_sarcophagus(self):
        glPushMatrix()
        glScalef(self.width, self.height, self.depth)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, self.height / 2 + 0.05, 0)
        glScalef(self.width + 0.1, 0.1, self.depth + 0.1)
        dcube(1.0)
        glPopMatrix()
        glColor3f(0.22, 0.20, 0.22)
        glPushMatrix()
        glTranslatef(0.3, 0.4, self.depth / 2 + 0.04)
        glScalef(0.2, 0.3, 0.05)
        dcube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-0.3, 0.4, self.depth / 2 + 0.04)
        glScalef(0.2, 0.3, 0.05)
        dcube(1.0)
        glPopMatrix()



class Environment:
    def __init__(self):
        self.tiles = []
        self.obstacles = []
        self.objects = []
        self.held_object = None
        self._generate_tiles()
        self._generate_obstacles()
        self._generate_objects()

    def _generate_tiles(self):
        half_arena = ARENA_SIZE // 2
        for x in range(-half_arena, half_arena, int(TILE_SIZE)):
            for z in range(-half_arena, half_arena, int(TILE_SIZE)):
                color_idx = (abs(x) + abs(z)) // int(TILE_SIZE) % len(TILE_COLORS)
                base_color = TILE_COLORS[color_idx]
                variation = random.choice(FLOOR_VARIATIONS)
                has_blood = random.random() < 0.18

                self.tiles.append({
                    'x': x, 'z': z,
                    'w': TILE_SIZE, 'h': TILE_SIZE,
                    'base_color': base_color,
                    'variation': variation,
                    'has_blood': has_blood
                })

    def _generate_obstacles(self):
        obstacle_types = ["pillar", "tombstone", "cage", "altar", "sarcophagus"]
        half_arena = ARENA_SIZE // 2

        placed = 0
        attempts = 0
        while placed < OBSTACLE_COUNT and attempts < 120:
            x = random.uniform(-half_arena + 5, half_arena - 5)
            z = random.uniform(-half_arena + 5, half_arena - 5)

            if abs(x) < 8 and abs(z) < 8:
                attempts += 1
                continue

            overlap = False
            for obs in self.obstacles:
                if abs(obs.x - x) < 3.0 and abs(obs.z - z) < 3.0:
                    overlap = True
                    break

            if not overlap:
                obs_type = random.choice(obstacle_types)
                self.obstacles.append(Obstacle(x, z, obs_type))
                placed += 1
            attempts += 1

    def _generate_objects(self):
        
        object_types = [
            "skull", "bone", "ribcage", "spine", "coffin",
            "candle", "book", "potion", "dagger", "heart", "eye"
        ]
        half_arena = ARENA_SIZE // 2

        
        fixed_spots = [
            (-8, 18, "skull"), (8, 18, "bone"), (-12, 10, "ribcage"),
            (12, 10, "spine"), (-18, 4, "coffin"), (18, 4, "candle"),
            (-16, -10, "book"), (16, -10, "potion"), (-7, -18, "dagger"),
            (7, -18, "heart"), (0, 26, "eye"), (25, 0, "skull"),
            (-25, 0, "bone"), (24, 20, "ribcage"), (-24, -20, "spine"),
            (4, 12, "coffin"), (-4, 12, "eye")
        ]

        for x, z, obj_type in fixed_spots:
            self.objects.append(GameObject(x, z, obj_type))

        placed = len(self.objects)
        attempts = 0
        while placed < OBJECT_COUNT + 10 and attempts < 300:
            x = random.uniform(-half_arena + 4, half_arena - 4)
            z = random.uniform(-half_arena + 4, half_arena - 4)

            overlap = False

            for obs in self.obstacles:
                if abs(obs.x - x) < 2.0 and abs(obs.z - z) < 2.0:
                    overlap = True
                    break

            for obj in self.objects:
                if abs(obj.x - x) < 2.0 and abs(obj.z - z) < 2.0:
                    overlap = True
                    break

            if abs(x) < 5 and abs(z) < 5:
                overlap = True

            if not overlap:
                obj_type = random.choice(object_types)
                self.objects.append(GameObject(x, z, obj_type))
                placed += 1

            attempts += 1

    def draw_floor(self):
        for tile in self.tiles:
            glPushMatrix()
            glTranslatef(tile['x'] + tile['w']/2, -0.05, tile['z'] + tile['h']/2)

            glColor3f(*tile['base_color'])
            glBegin(GL_QUADS)
            glVertex3f(-tile['w']/2, 0, -tile['h']/2)
            glVertex3f(tile['w']/2, 0, -tile['h']/2)
            glVertex3f(tile['w']/2, 0, tile['h']/2)
            glVertex3f(-tile['w']/2, 0, tile['h']/2)
            glEnd()

            glColor3f(*tile['variation'])
            glBegin(GL_QUADS)
            glVertex3f(-tile['w']/2 + 0.2, 0.01, -tile['h']/2 + 0.2)
            glVertex3f(tile['w']/2 - 0.2, 0.01, -tile['h']/2 + 0.2)
            glVertex3f(tile['w']/2 - 0.2, 0.01, tile['h']/2 - 0.2)
            glVertex3f(-tile['w']/2 + 0.2, 0.01, tile['h']/2 - 0.2)
            glEnd()

            if tile['has_blood']:
                glColor3f(0.55, 0.03, 0.04)
                glBegin(GL_POLYGON)
                for i in range(7):
                    angle = i * (6.28 / 7.0)
                    r = 0.18 + ((i * 13) % 9) * 0.035
                    xo = math.cos(angle) * r
                    zo = math.sin(angle) * r
                    glVertex3f(xo, 0.02, zo)
                glEnd()

            glColor3f(0.08, 0.05, 0.08)
            glBegin(GL_LINES)
            glVertex3f(-tile['w']/2, 0.03, -tile['h']/2)
            glVertex3f(tile['w']/2, 0.03, -tile['h']/2)
            glVertex3f(tile['w']/2, 0.03, -tile['h']/2)
            glVertex3f(tile['w']/2, 0.03, tile['h']/2)
            glVertex3f(tile['w']/2, 0.03, tile['h']/2)
            glVertex3f(-tile['w']/2, 0.03, tile['h']/2)
            glVertex3f(-tile['w']/2, 0.03, tile['h']/2)
            glVertex3f(-tile['w']/2, 0.03, -tile['h']/2)
            glEnd()

            glPopMatrix()

        
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(50):
            t = time.time() * 0.5 + i * 0.1
            x = math.sin(t) * 30
            z = math.cos(t * 0.7) * 30
            y = 0.5 + math.sin(t * 3) * 0.3
            glColor3f(0.5, 0.2, 0.3)
            glVertex3f(x, y, z)
        glEnd()

    def draw_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw()

    def draw_objects(self):
        for obj in self.objects:
            if not obj.is_held:
                obj.draw()

                
                dx = obj.x - state.player_x
                dz = obj.z - state.player_z
                dist = math.sqrt(dx * dx + dz * dz)
                if dist < 4.0 and obj.grounded:
                    glPushMatrix()
                    glTranslatef(obj.x, 0.06, obj.z)
                    glColor3f(0.85, 0.10, 0.18)
                    glRotatef(-90, 1, 0, 0)
                    dcyl(0.9, 0.9, 0.04, 20, 1)
                    glPopMatrix()

    def draw_player_hands(self):
        
        glColor3f(0.22, 0.12, 0.15)
        glPushMatrix()
        glTranslatef(-0.55, -0.78, -1.45)
        glRotatef(-15, 0, 1, 0)
        glScalef(0.22, 0.18, 0.55)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.65, 0.48, 0.38)
        glPushMatrix()
        glTranslatef(-0.32, -0.72, -1.95)
        glScalef(0.18, 0.16, 0.18)
        dsph(1.0, 8, 8)
        glPopMatrix()

        # right hand
        glColor3f(0.22, 0.12, 0.15)
        glPushMatrix()
        glTranslatef(0.55, -0.78, -1.45)
        glRotatef(15, 0, 1, 0)
        glScalef(0.22, 0.18, 0.55)
        dcube(1.0)
        glPopMatrix()

        glColor3f(0.65, 0.48, 0.38)
        glPushMatrix()
        glTranslatef(0.32, -0.72, -1.95)
        glScalef(0.18, 0.16, 0.18)
        dsph(1.0, 8, 8)
        glPopMatrix()

    def draw_held_object(self):
        """
        First-person held prop.
        This resets model-view to camera space so the object always appears in hand.
        """
        if self.held_object is None:
            return

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        self.draw_player_hands()

        glPushMatrix()
        glTranslatef(0.0, -0.55, -2.10)
        glRotatef(-18, 1, 0, 0)
        glRotatef(math.sin(time.time() * 4.0) * 4.0, 0, 1, 0)
        glScalef(0.85, 0.85, 0.85)
        self.held_object.draw_model()
        glPopMatrix()

        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def update_objects(self, dt):
        for obj in self.objects:
            obj.update(dt)

        # Clean up objects that fell out of bounds or were consumed by hit collision.
        self.objects = [obj for obj in self.objects if abs(obj.x) < 52 and abs(obj.z) < 52 and obj.y > -5]

    def pickup_object(self, player_x, player_z, player_yaw):
        """
        Press E:
        - If empty-handed, pick the closest grounded object.
        - If already holding one, keep holding it. F is throw.
        """
        if self.held_object is not None:
            return False

        nearest_dist = 4.0
        nearest_obj = None

        for obj in self.objects:
            if obj.is_held or not obj.grounded:
                continue

            dist = math.sqrt((obj.x - player_x) ** 2 + (obj.z - player_z) ** 2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_obj = obj

        if nearest_obj is not None:
            self.held_object = nearest_obj
            nearest_obj.is_held = True
            nearest_obj.grounded = True
            nearest_obj.velocity_x = 0.0
            nearest_obj.velocity_y = 0.0
            nearest_obj.velocity_z = 0.0
            return True

        return False

    def throw_held_object(self, player_x, player_y, player_z, player_yaw, player_pitch):
        
        if self.held_object is None:
            return False

        obj = self.held_object
        obj.throw_from_player(player_x, player_y, player_z, player_yaw, player_pitch, 30.0)
        self.held_object = None
        return True

    def draw_blood_particles(self):
        glPointSize(4.0)

        glBegin(GL_POINTS)
        t = time.time()
        for i in range(80):
            px = math.sin(t * 0.5 + i) * 35
            pz = math.cos(t * 0.3 + i * 1.3) * 35
            py = (t * 0.5 + i) % 8.0

            if (i + int(t)) % 3 == 0:
                glColor3f(0.55, 0.08, 0.08)
            else:
                glColor3f(0.25, 0.20, 0.25)
            glVertex3f(px, py, pz)
        glEnd()



class Enemies:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.angle = 0.0
        self.last_attack_time = time.time()
        self.alive = True

    def draw(self):
        pass

    def update(self, dt):
        pass

    def spawn_fireball(self, speed):
        tx, ty, tz = state.player_x, state.player_y, state.player_z
        dx, dy, dz = tx - self.x, ty - self.y, tz - self.z
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        if d < 0.0001:
            d = 1.0
        state.enemy_fireballs.append({
            'id': random.random() * 100,
            'x': self.x,
            'y': self.y + 0.8,
            'z': self.z,
            'vx': (dx / d) * speed,
            'vy': (dy / d) * speed,
            'vz': (dz / d) * speed,
        })

    def draw_health_bar(self):
        if not self.alive:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y + 2.0, self.z)
        bw, bh = 2.0, 0.2
        glColor3f(0.8, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-bw / 2, -bh / 2, 0)
        glVertex3f(bw / 2, -bh / 2, 0)
        glVertex3f(bw / 2, bh / 2, 0)
        glVertex3f(-bw / 2, bh / 2, 0)
        glEnd()
        hr = max(0.0, min(1.0, self.hp / self.max_hp))
        if hr > 0:
            cw = bw * hr
            glColor3f(0.0, 0.8, 0.0)
            glBegin(GL_QUADS)
            glVertex3f(-bw / 2, -bh / 2, 0.01)
            glVertex3f(-bw / 2 + cw, -bh / 2, 0.01)
            glVertex3f(-bw / 2 + cw, bh / 2, 0.01)
            glVertex3f(-bw / 2, bh / 2, 0.01)
            glEnd()
        glPopMatrix()


class Zombie(Enemies):
    C_SKIN  = (0.35, 0.60, 0.25)
    C_SHIRT = (0.20, 0.70, 0.70)
    C_PANTS = (0.25, 0.25, 0.70)
    C_SHOES = (0.30, 0.30, 0.30)
    C_EYES  = (0.05, 0.05, 0.05)

    def __init__(self, x, z):
        super().__init__(x, 0.8, z)
        self.max_hp = 100.0
        self.hp = self.max_hp
        self.walk_t = 0.0

    def update(self, dt):
        if not self.alive:
            return
        self.walk_t += dt
        dx, dz = state.player_x - self.x, state.player_z - self.z
        dist = math.sqrt(dx * dx + dz * dz)
        self.angle = math.degrees(math.atan2(dx, dz)) if dist > 0.01 else self.angle
        spd = 4.0
        if dist > 0.01:
            self.vx = (dx / dist) * spd
            self.vz = (dz / dist) * spd
        self.x += self.vx * dt
        self.z += self.vz * dt
        self.y = 0.8
        if time.time() - self.last_attack_time > 2.5:
            self.spawn_fireball(10.0)
            self.last_attack_time = time.time()

    def draw_zombie_head(self):
        glPushMatrix()
        glTranslatef(0, 1.55, 0)
        glColor3f(*self.C_SKIN)
        glPushMatrix(); glScalef(0.70, 0.70, 0.70); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_EYES)
        glPushMatrix(); glTranslatef(-0.15, 0.08, 0.36); glScalef(0.12, 0.10, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.08, 0.36); glScalef(0.12, 0.10, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -0.15, 0.36); glScalef(0.22, 0.06, 0.02); dcube(1.0); glPopMatrix()
        glColor3f(0.30, 0.52, 0.22)
        glPushMatrix(); glTranslatef(0, 0.0, 0.36); glScalef(0.08, 0.08, 0.04); dcube(1.0); glPopMatrix()
        glColor3f(0.28, 0.48, 0.20)
        glPushMatrix(); glTranslatef(-0.15, 0.18, 0.36); glScalef(0.14, 0.04, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.18, 0.36); glScalef(0.14, 0.04, 0.02); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_zombie_neck(self):
        glColor3f(*self.C_SKIN)
        glPushMatrix(); glTranslatef(0, 1.15, 0); glRotatef(-90, 1, 0, 0); dcyl(0.12, 0.15, 0.12); glPopMatrix()

    def draw_zombie_torso(self):
        glColor3f(*self.C_SHIRT)
        glPushMatrix(); glTranslatef(0, 0.45, 0); glScalef(0.90, 0.90, 0.50); dcube(1.0); glPopMatrix()
        glColor3f(0.15, 0.58, 0.58)
        glPushMatrix(); glTranslatef(-0.20, 0.65, 0.26); glScalef(0.18, 0.14, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.35, 0.26); glScalef(0.22, 0.12, 0.02); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_SKIN)
        glPushMatrix(); glTranslatef(0, 0.92, 0); glScalef(0.70, 0.06, 0.40); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.25, 0.55, 0.26); glScalef(0.10, 0.16, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.30, 0.30, 0.26); glScalef(0.08, 0.12, 0.02); dcube(1.0); glPopMatrix()

    def draw_zombie_arm(self, side, wa):
        glPushMatrix()
        glTranslatef(side * 0.60, 0.75, 0)
        glRotatef(-wa * side * 0.5, 1, 0, 0)
        glColor3f(*self.C_SHIRT)
        dsph(0.16)
        glPushMatrix(); glTranslatef(0, -0.05, 0.20)
        glRotatef(-70, 1, 0, 0)
        glColor3f(*self.C_SHIRT)
        glPushMatrix(); glScalef(0.22, 0.40, 0.22); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_SKIN)
        glTranslatef(0, 0, 0.45)
        dsph(0.12)
        glPushMatrix(); glScalef(0.20, 0.20, 0.40); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_SKIN)
        glTranslatef(0, 0, 0.35)
        glPushMatrix(); glScalef(0.18, 0.12, 0.12); dcube(1.0); glPopMatrix()
        for f in range(3):
            glPushMatrix(); glTranslatef(-0.05 + f * 0.05, 0, 0.09); glScalef(0.04, 0.06, 0.08); dcube(1.0); glPopMatrix()
        glPopMatrix()
        glPopMatrix()

    def draw_zombie_leg(self, side, wa):
        glPushMatrix()
        glTranslatef(side * 0.22, -0.05, 0)
        glRotatef(wa * side, 1, 0, 0)
        glColor3f(*self.C_PANTS)
        dsph(0.15)
        glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.14, 0.13, 0.55); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -0.30, 0); glScalef(0.28, 0.60, 0.28); dcube(1.0); glPopMatrix()
        glTranslatef(0, -0.60, 0)
        dsph(0.13)
        glPushMatrix(); glTranslatef(0, -0.25, 0); glScalef(0.26, 0.50, 0.26); dcube(1.0); glPopMatrix()
        glTranslatef(0, -0.55, 0)
        glColor3f(*self.C_SHOES)
        dsph(0.12)
        glPushMatrix(); glTranslatef(0, -0.06, 0.05); glScalef(0.26, 0.12, 0.36); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw(self):
        if not self.alive:
            return
        sp = self.vx ** 2 + self.vz ** 2
        wa = 0.0
        if sp > 0.1:
            wa = math.sin(self.walk_t * 8.0) * 25.0

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0, 1, 0)
        glScalef(0.6, 0.6, 0.6)

        self.draw_zombie_leg(-1, wa)
        self.draw_zombie_leg(1, -wa)
        self.draw_zombie_torso()
        self.draw_zombie_arm(-1, wa)
        self.draw_zombie_arm(1, -wa)
        self.draw_zombie_neck()
        self.draw_zombie_head()

        glPopMatrix()


class Batman(Enemies):
    C_COWL   = (0.05, 0.05, 0.05)
    C_ARMOR  = (0.40, 0.40, 0.45)
    C_ARMOR_D = (0.20, 0.20, 0.22)
    C_BELT   = (0.55, 0.45, 0.20)
    C_SKIN   = (0.85, 0.72, 0.55)
    C_EYES   = (1.00, 1.00, 1.00)
    C_CAPE   = (0.06, 0.06, 0.08)

    def __init__(self, x, z):
        super().__init__(x, 8.0, z)
        self.max_hp = 100.0
        self.hp = self.max_hp
        self.fly_t = random.random() * 6.0

    def update(self, dt):
        if not self.alive:
            return
        self.fly_t += dt
        radius = 10.0
        cx, cz = state.player_x, state.player_z
        self.x = cx + math.sin(self.fly_t * 0.7) * radius
        self.z = cz + math.cos(self.fly_t * 0.7) * radius
        self.y = 8.0 + math.sin(self.fly_t * 1.8) * 1.5
        self.angle = math.degrees(math.atan2(state.player_x - self.x, state.player_z - self.z))
        if time.time() - self.last_attack_time > 1.5:
            self.spawn_fireball(13.0)
            self.last_attack_time = time.time()

    def draw_bat_head(self):
        glPushMatrix()
        glTranslatef(0, 1.45, 0)
        glColor3f(*self.C_COWL)
        glPushMatrix(); glScalef(0.62, 0.65, 0.60); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.18, 0.42, 0.0); glRotatef(15, 0, 0, 1); dcyl(0.07, 0.0, 0.35, 6); glPopMatrix()
        glPushMatrix(); glTranslatef(0.18, 0.42, 0.0); glRotatef(-15, 0, 0, 1); dcyl(0.07, 0.0, 0.35, 6); glPopMatrix()
        glColor3f(*self.C_EYES)
        glPushMatrix(); glTranslatef(-0.12, 0.06, 0.31); glRotatef(12, 0, 0, 1); glScalef(0.12, 0.05, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.12, 0.06, 0.31); glRotatef(-12, 0, 0, 1); glScalef(0.12, 0.05, 0.02); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_SKIN)
        glPushMatrix(); glTranslatef(0, -0.22, 0.18); glScalef(0.30, 0.18, 0.25); dcube(1.0); glPopMatrix()
        glColor3f(0.60, 0.45, 0.35)
        glPushMatrix(); glTranslatef(0, -0.28, 0.31); glScalef(0.16, 0.03, 0.02); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_COWL)
        glPushMatrix(); glTranslatef(0, 0.16, 0.31); glScalef(0.36, 0.06, 0.03); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_bat_neck(self):
        glColor3f(*self.C_COWL)
        glPushMatrix(); glTranslatef(0, 1.08, 0); glRotatef(-90, 1, 0, 0); dcyl(0.14, 0.18, 0.14); glPopMatrix()

    def draw_bat_torso(self):
        glColor3f(*self.C_ARMOR)
        glPushMatrix(); glTranslatef(0, 0.50, 0); glScalef(1.00, 0.85, 0.55); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_ARMOR_D)
        glPushMatrix(); glTranslatef(0, 0.55, 0.28); glScalef(0.70, 0.60, 0.04); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_COWL)
        glPushMatrix(); glTranslatef(0, 0.55, 0.31); glScalef(0.28, 0.10, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.18, 0.58, 0.31); glRotatef(20, 0, 0, 1); glScalef(0.14, 0.06, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.18, 0.58, 0.31); glRotatef(-20, 0, 0, 1); glScalef(0.14, 0.06, 0.02); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_ARMOR)
        glPushMatrix(); glTranslatef(-0.52, 0.82, 0); glScalef(0.18, 0.14, 0.40); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.52, 0.82, 0); glScalef(0.18, 0.14, 0.40); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_ARMOR_D)
        glPushMatrix(); glTranslatef(0, 0.18, 0.28); glScalef(0.50, 0.30, 0.04); dcube(1.0); glPopMatrix()
        glColor3f(0.15, 0.15, 0.17)
        glPushMatrix(); glTranslatef(0, 0.18, 0.31); glScalef(0.02, 0.28, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0, 0.18, 0.31); glScalef(0.40, 0.02, 0.02); dcube(1.0); glPopMatrix()

    def draw_bat_belt(self):
        glColor3f(*self.C_BELT)
        glPushMatrix(); glTranslatef(0, 0.02, 0); glRotatef(90, 1, 0, 0); dcyl(0.54, 0.54, 0.12, 16); glPopMatrix()
        glColor3f(0.65, 0.55, 0.25)
        glPushMatrix(); glTranslatef(0, -0.02, 0.55); glScalef(0.14, 0.10, 0.06); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_BELT)
        for i in range(4):
            ang = -30 + i * 20
            px = math.sin(math.radians(ang)) * 0.52
            pz = math.cos(math.radians(ang)) * 0.52
            glPushMatrix(); glTranslatef(px, -0.02, pz); glScalef(0.10, 0.10, 0.08); dcube(1.0); glPopMatrix()

    def draw_bat_arm(self, side):
        glPushMatrix()
        glTranslatef(side * 0.62, 0.72, 0)
        glColor3f(*self.C_ARMOR)
        dsph(0.16)
        glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.12, 0.11, 0.55); glPopMatrix()
        glColor3f(*self.C_ARMOR_D)
        glPushMatrix(); glTranslatef(0, -0.28, 0); glScalef(0.24, 0.50, 0.22); dcube(1.0); glPopMatrix()
        glTranslatef(0, -0.55, 0)
        glColor3f(*self.C_ARMOR)
        dsph(0.12)
        glColor3f(*self.C_COWL)
        glPushMatrix(); glTranslatef(0, -0.25, 0); glScalef(0.22, 0.46, 0.22); dcube(1.0); glPopMatrix()
        for b in range(3):
            glPushMatrix()
            glTranslatef(side * 0.12, -0.12 - b * 0.12, -0.10)
            glScalef(0.03, 0.08, 0.14)
            dcube(1.0)
            glPopMatrix()
        glTranslatef(0, -0.52, 0)
        glColor3f(*self.C_COWL)
        dsph(0.10)
        glPushMatrix(); glScalef(0.16, 0.10, 0.12); dcube(1.0); glPopMatrix()
        for f in range(4):
            glPushMatrix(); glTranslatef(-0.05 + f * 0.035, -0.12, 0); glScalef(0.03, 0.08, 0.04); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_bat_leg(self, side):
        glPushMatrix()
        glTranslatef(side * 0.22, -0.10, 0)
        glColor3f(*self.C_ARMOR_D)
        dsph(0.14)
        glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.13, 0.12, 0.50); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -0.28, 0); glScalef(0.26, 0.52, 0.26); dcube(1.0); glPopMatrix()
        glTranslatef(0, -0.55, 0)
        glColor3f(*self.C_ARMOR)
        dsph(0.13)
        glPushMatrix(); glTranslatef(0, 0, 0.14); glScalef(0.14, 0.10, 0.06); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_COWL)
        glPushMatrix(); glTranslatef(0, -0.28, 0); glScalef(0.26, 0.52, 0.26); dcube(1.0); glPopMatrix()
        glColor3f(*self.C_ARMOR_D)
        glPushMatrix(); glTranslatef(0, -0.05, 0); glScalef(0.28, 0.06, 0.28); dcube(1.0); glPopMatrix()
        glTranslatef(0, -0.56, 0)
        glColor3f(*self.C_COWL)
        dsph(0.11)
        glPushMatrix(); glTranslatef(0, -0.05, 0.06); glScalef(0.26, 0.10, 0.36); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_bat_cape(self):
        glColor3f(*self.C_CAPE)
        cape_sway = math.sin(self.fly_t * 3.0) * 0.15
        glPushMatrix()
        glTranslatef(0, 0.80, -0.30)
        glPushMatrix(); glScalef(0.90, 0.30, 0.06); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -0.45, -0.10 + cape_sway); glScalef(1.10, 0.60, 0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -1.00, -0.20 + cape_sway * 1.5); glScalef(1.30, 0.70, 0.04); dcube(1.0); glPopMatrix()
        for i in range(5):
            tx = -0.50 + i * 0.25
            glPushMatrix()
            glTranslatef(tx, -1.45, -0.25 + cape_sway * 2.0)
            glRotatef(90, 1, 0, 0)
            dcyl(0.08, 0.0, 0.20, 4)
            glPopMatrix()
        glPopMatrix()

    def draw(self):
        if not self.alive:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0, 1, 0)

        self.draw_bat_cape()
        self.draw_bat_leg(-1)
        self.draw_bat_leg(1)
        self.draw_bat_torso()
        self.draw_bat_belt()
        self.draw_bat_arm(-1)
        self.draw_bat_arm(1)
        self.draw_bat_neck()
        self.draw_bat_head()

        glPopMatrix()


class Mahoraga:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 5.4, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.hp = 100.0
        self.angle = 0.0
        self.phase = 1
        self.transition_time = 0.0
        self.death_time = 0.0
        self.last_attack_time = time.time()
        self.walk_anim_time = 0.0

    def start_death_blast(self):
        if self.phase >= 4:
            return
        self.phase = 4
        self.death_time = 0.0
        self.transition_time = 0.0
        self.vx = self.vy = self.vz = 0.0
        self.last_attack_time = time.time()
        for _ in range(50):
            ang = random.random() * math.pi * 2.0
            elev = (random.random() - 0.5) * math.pi * 0.7
            state.particles.append({
                'x': self.x + math.cos(ang) * math.cos(elev) * 1.5,
                'y': self.y + 1.0 + math.sin(elev) * 1.5,
                'z': self.z + math.sin(ang) * math.cos(elev) * 1.5,
                'vy': 4.0 + random.random() * 7.0,
                'life': 0.8 + random.random() * 0.6,
            })

    def draw_death_blast(self):
        if self.phase != 4:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y + 1.0, self.z)
        burst = 2.0 + self.death_time * 8.0
        glColor3f(1.0, 0.95, 0.45)
        dsph(burst, 16, 16)
        glColor3f(1.0, 0.45, 0.0)
        dsph(burst * 0.72, 16, 16)
        glColor3f(1.0, 1.0, 1.0)
        dsph(burst * 0.35, 12, 12)
        glPopMatrix()

    def draw_leg(self, side, wa, cb, cg):
        glPushMatrix()
        glTranslatef(side*0.5, -0.9, 0)
        glRotatef(wa*side, 1,0,0)
        glColor3f(*cb); dsph(0.22)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.18,0.16,0.95); glPopMatrix()
        glTranslatef(0,-0.95,0); dsph(0.20)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.16,0.14,0.95); glPopMatrix()
        glTranslatef(0,-0.95,0)
        glColor3f(*cg)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.20,0.20,0.10,12); glPopMatrix()
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,-0.12,0.1); glScalef(0.32,0.12,0.50); dcube(1.0); glPopMatrix()
        for t in range(4):
            glPushMatrix(); glTranslatef(-0.10+t*0.07, -0.20, 0.32); glScalef(0.06,0.07,0.10); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_arm(self, side, wa, cb, cg):
        glPushMatrix()
        glTranslatef(side*1.05, 0.55, 0)
        glRotatef(-wa*side, 1,0,0)
        glColor3f(*cb); dsph(0.22)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.14,0.12,0.80); glPopMatrix()
        glTranslatef(0,-0.80,0); dsph(0.16)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.12,0.10,0.75); glPopMatrix()
        glTranslatef(0,-0.75,0)
        glColor3f(*cg)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.15,0.15,0.08,12); glPopMatrix()
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,-0.15,0); glScalef(0.20,0.15,0.12); dcube(1.0); glPopMatrix()
        for f in range(4):
            glPushMatrix(); glTranslatef(-0.07+f*0.05, -0.30, 0); glScalef(0.035,0.10,0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(side*0.12, -0.18, 0.05); glScalef(0.04,0.08,0.04); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_skirt(self, cc):
        glColor3f(*cc)
        glPushMatrix(); glTranslatef(0,-1.1,0.22); glScalef(1.3,1.1,0.06); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0,-1.1,-0.22); glScalef(1.3,1.1,0.06); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.60,-1.1,0); glScalef(0.06,1.1,0.50); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.60,-1.1,0); glScalef(0.06,1.1,0.50); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.40,-1.25,0.20); glRotatef(8,0,0,1); glScalef(0.45,0.90,0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.40,-1.25,0.20); glRotatef(-8,0,0,1); glScalef(0.45,0.90,0.05); dcube(1.0); glPopMatrix()

    def draw_belt(self, cb, cg):
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,-0.50,0); glRotatef(90,1,0,0); dcyl(0.70,0.70,0.22,16); glPopMatrix()
        glColor3f(*cg)
        glPushMatrix(); glTranslatef(0,-0.55,0.72); dsph(0.15); glPopMatrix()
        glPushMatrix(); glTranslatef(0,-0.55,0.72); glRotatef(90,1,0,0); dcyl(0.20,0.20,0.05,12); glPopMatrix()

    def draw_torso(self, cb):
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,0.15,0); glScalef(1.45,1.10,0.65); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.30,0.48,0.28); glScalef(0.40,0.28,0.15); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.30,0.48,0.28); glScalef(0.40,0.28,0.15); dcube(1.0); glPopMatrix()
        for r in range(3):
            for c in range(2):
                glPushMatrix()
                glTranslatef(-0.13+c*0.26, 0.05-r*0.20, 0.34)
                glScalef(0.20,0.16,0.04)
                dcube(1.0)
                glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.15,-0.34); glScalef(1.0,0.80,0.05); dcube(1.0); glPopMatrix()

    def draw_necklace(self, cd):
        glColor3f(*cd)
        for i in range(7):
            glPushMatrix()
            a = -60+i*20.0
            cx = math.sin(math.radians(a))*0.65
            cy = 0.65 - abs(math.sin(math.radians(a)))*0.12
            glTranslatef(cx, cy, 0.35); dsph(0.055,6,6)
            glPopMatrix()
        for i in range(6):
            glPushMatrix()
            a1, a2 = -60+i*20.0, -60+(i+1)*20.0
            x1 = math.sin(math.radians(a1))*0.65
            y1 = 0.65-abs(math.sin(math.radians(a1)))*0.12
            x2 = math.sin(math.radians(a2))*0.65
            y2 = 0.65-abs(math.sin(math.radians(a2)))*0.12
            mx, my = (x1+x2)/2, (y1+y2)/2
            dx, dy = x2-x1, y2-y1
            ln = math.sqrt(dx*dx+dy*dy)
            ang = math.degrees(math.atan2(dy, dx))
            glTranslatef(mx, my, 0.35)
            glRotatef(ang,0,0,1); glRotatef(90,0,1,0)
            dcyl(0.02,0.02,ln,6)
            glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.38,0.37); glScalef(0.08,0.12,0.05); dcube(1.0); glPopMatrix()

    def draw_neck(self, cb):
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,0.80,0); glRotatef(-90,1,0,0); dcyl(0.16,0.20,0.30); glPopMatrix()

    def draw_head(self, cb):
        glPushMatrix()
        glTranslatef(0,1.40,0.04)
        glColor3f(*cb)
        dsph(0.42,16,16)
        glPushMatrix(); glTranslatef(-0.28,0.18,0.08); glRotatef(40,0,0,1); glRotatef(-15,1,0,0); dcyl(0.07,0.0,0.85,8); glPopMatrix()
        glPushMatrix(); glTranslatef(0.28,0.18,0.08); glRotatef(-40,0,0,1); glRotatef(-15,1,0,0); dcyl(0.07,0.0,0.85,8); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.32,-0.02,0.12); glRotatef(55,0,0,1); glRotatef(-8,1,0,0); dcyl(0.055,0.0,0.65,8); glPopMatrix()
        glPushMatrix(); glTranslatef(0.32,-0.02,0.12); glRotatef(-55,0,0,1); glRotatef(-8,1,0,0); dcyl(0.055,0.0,0.65,8); glPopMatrix()
        glColor3f(0.05,0.05,0.05)
        glPushMatrix(); glTranslatef(-0.14,0.08,0.38); glRotatef(15,0,0,1); glScalef(0.10,0.05,0.03); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.14,0.08,0.38); glRotatef(-15,0,0,1); glScalef(0.10,0.05,0.03); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0,-0.10,0.40); glScalef(0.22,0.025,0.025); dcube(1.0); glPopMatrix()
        for t in range(6):
            glPushMatrix(); glTranslatef(-0.09+t*0.036,-0.14,0.40); glScalef(0.03,0.04,0.025); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.35,0); glRotatef(-90,1,0,0); dcyl(0.06,0.0,0.45,8); glPopMatrix()
        glPopMatrix()

    def draw_wheel(self, cg, anim_t):
        glColor3f(*cg)
        glPushMatrix()
        glTranslatef(0,1.85,-0.55)
        glRotatef(anim_t*40.0, 0,0,1)
        R = 1.30
        segs = 32
        for i in range(segs):
            a1 = i*360.0/segs; a2 = (i+1)*360.0/segs
            x1,y1 = math.cos(math.radians(a1))*R, math.sin(math.radians(a1))*R
            x2,y2 = math.cos(math.radians(a2))*R, math.sin(math.radians(a2))*R
            dx,dy = x2-x1,y2-y1
            sl = math.sqrt(dx*dx+dy*dy)
            ang = math.degrees(math.atan2(dy,dx))
            glPushMatrix(); glTranslatef(x1,y1,0); glRotatef(ang,0,0,1); glRotatef(90,0,1,0); dcyl(0.06,0.06,sl,6,1); glPopMatrix()
        for i in range(6):
            glPushMatrix(); glRotatef(i*60,0,0,1); glRotatef(90,0,1,0); dcyl(0.04,0.04,R,6); glPopMatrix()
        dsph(0.10,8,8)
        for i in range(6):
            glPushMatrix()
            a = math.radians(i*60.0)
            glTranslatef(math.cos(a)*R, math.sin(a)*R, 0)
            dsph(0.14,8,8)
            glPopMatrix()
        glPopMatrix()

    def draw_tail(self, cb):
        glColor3f(*cb)
        glPushMatrix()
        glTranslatef(0, -0.4, -0.35)
        for i in range(10):
            glPushMatrix()
            glTranslatef(0, -i*0.15, -i*0.25 - (i*i)*0.03)
            dsph(0.22 - i*0.018, 8, 8)
            glPopMatrix()
        glPopMatrix()

    def draw(self):
        if self.phase >= 4:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0,1,0)
        glScalef(1.8, 1.8, 1.8)

        p3 = self.phase == 3
        cb = C_BODY3 if p3 else C_BODY
        cc = C_CLOTH3 if p3 else C_CLOTH
        cg = C_GOLD
        cd = C_DETAIL
        belt_c = (0.25,0.08,0.25) if p3 else (0.12,0.12,0.15)

        wa = 0.0
        if self.phase != 2:
            sp = self.vx**2 + self.vz**2
            if sp > 0.1:
                wa = math.sin(self.walk_anim_time*12.0)*28.0

        self.draw_tail(cb)
        self.draw_leg(-1, wa, cb, cg)
        self.draw_leg(1, -wa, cb, cg)
        self.draw_skirt(cc)
        self.draw_belt(belt_c, cg)
        self.draw_torso(cb)
        self.draw_necklace(cd)
        self.draw_arm(-1, wa, cb, cg)
        self.draw_arm(1, -wa, cb, cg)
        self.draw_neck(cb)
        self.draw_head(cb)
        self.draw_wheel(cg, self.walk_anim_time)

        glPopMatrix()

    def draw_health_bar(self):
        if self.phase >= 4:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y+7.5, self.z)
        bw, bh = 4.0, 0.4
        glColor3f(0.8,0.0,0.0)
        glBegin(GL_QUADS)
        glVertex3f(-bw/2,-bh/2,0); glVertex3f(bw/2,-bh/2,0); glVertex3f(bw/2,bh/2,0); glVertex3f(-bw/2,bh/2,0)
        glEnd()
        hr = max(0.0, min(1.0, self.hp/100.0))
        if hr > 0:
            cw = bw*hr
            glColor3f(0.0,0.8,0.0)
            glBegin(GL_QUADS)
            glVertex3f(-bw/2,-bh/2,0.01); glVertex3f(-bw/2+cw,-bh/2,0.01); glVertex3f(-bw/2+cw,bh/2,0.01); glVertex3f(-bw/2,bh/2,0.01)
            glEnd()
        glPopMatrix()

    def spawn_fireball(self, phase3=False):
        speed = 18.0 if phase3 else 8.0
        tx, ty, tz = state.player_x, state.player_y, state.player_z
        if phase3:
            tx += (random.random()-0.5)*15; ty += (random.random()-0.5)*10; tz += (random.random()-0.5)*15
        dx, dy, dz = tx-self.x, ty-self.y, tz-self.z
        d = math.sqrt(dx*dx+dy*dy+dz*dz)
        if d < 0.0001: d = 1.0
        state.fireballs.append({'id':random.random()*100, 'x':self.x, 'y':self.y+1.0, 'z':self.z,
                                'vx':(dx/d)*speed, 'vy':(dy/d)*speed, 'vz':(dz/d)*speed})

    def update(self, dt):
        self.walk_anim_time += dt
        if self.phase == 4:
            self.death_time += dt
            self.y += 4.0 * dt
            for _ in range(8):
                ang = random.random() * math.pi * 2.0
                elev = (random.random() - 0.5) * math.pi
                state.particles.append({
                    'x': self.x + math.cos(ang) * math.cos(elev) * 1.2,
                    'y': self.y + 1.0 + math.sin(elev) * 1.2,
                    'z': self.z + math.sin(ang) * math.cos(elev) * 1.2,
                    'vy': 3.0 + random.random() * 6.0,
                    'life': 0.35 + random.random() * 0.45,
                })
            if self.death_time >= 1.3:
                self.phase = 5
            return
        if self.phase == 1:
            if self.hp <= 50.0:
                self.phase = 2; self.transition_time = 0.0
            dx, dz = state.player_x-self.x, state.player_z-self.z
            dist = math.sqrt(dx*dx+dz*dz)
            self.angle = math.degrees(math.atan2(dx, dz))
            fs = 3.0 if dist > 12.0 else (-2.0 if dist < 8.0 else 0.0)
            ss = math.sin(time.time()*0.8)*4.0
            if dist > 0.01:
                self.vx = (dx/dist)*fs - (dz/dist)*ss
                self.vz = (dz/dist)*fs + (dx/dist)*ss
            if self.y <= 5.4:
                self.y, self.vy = 5.4, 0
                if random.random() < dt*0.4: self.vy = 12.0
            else:
                self.vy -= 25.0*dt
            self.x += self.vx*dt; self.y += self.vy*dt; self.z += self.vz*dt
            if time.time()-self.last_attack_time > 2.0:
                self.spawn_fireball(); self.last_attack_time = time.time()
        elif self.phase == 2:
            self.transition_time += dt
            self.hp = min(100.0, self.hp + 25.0*dt)
            ty = 15.0; self.y += (ty-self.y)*(dt/max(0.1,2.0-self.transition_time))
            for _ in range(3):
                state.particles.append({'x':self.x+(random.random()-0.5)*6, 'y':self.y-2+random.random()*4,
                                        'z':self.z+(random.random()-0.5)*6, 'vy':2+random.random()*5, 'life':1.0})
            if self.transition_time >= 2.0: self.phase = 3; self.hp = 100.0
        elif self.phase == 3:
            if self.hp <= 0.0:
                self.start_death_blast()
                return
            ty = 15.0+math.sin(time.time()*1.5)*3; tx = math.sin(time.time()*1.2)*12
            tz = state.player_z-12+math.cos(time.time()*0.9)*12
            self.vx, self.vy, self.vz = (tx-self.x)*1.5, (ty-self.y)*1.5, (tz-self.z)*1.5
            self.x += self.vx*dt; self.y += self.vy*dt; self.z += self.vz*dt
            self.angle = math.degrees(math.atan2(state.player_x-self.x, state.player_z-self.z))
            if time.time()-self.last_attack_time > 0.5:
                self.spawn_fireball(True); self.last_attack_time = time.time()


class GameState:
    def __init__(self):
        self.last_time = time.time()
        self.player_x, self.player_y, self.player_z = 0.0, 2.5, 20.0
        self.player_yaw = 180.0
        self.player_pitch = 0.0
        self.mouse_held = False
        self.mouse_x, self.mouse_y = W_WIDTH//2, W_HEIGHT//2
        self.keys = {}
        self.boss = Mahoraga()
        self.fireballs, self.particles = [], []
        self.player_fireballs = []
        self.enemy_fireballs = []
        self.enemies = []
        self.environment = Environment()
        
        for _ in range(4):
            ex = (random.random() - 0.5) * 60
            ez = (random.random() - 0.5) * 60
            self.enemies.append(Zombie(ex, ez))
        for _ in range(2):
            ex = (random.random() - 0.5) * 50
            ez = (random.random() - 0.5) * 50
            self.enemies.append(Batman(ex, ez))
        self.quadric = None


state = GameState()

# ============ UTILITY FUNCTIONS ============
def init():
    state.quadric = gluNewQuadric()
    glClearColor(0.05, 0.03, 0.08, 1.0)

def dcube(s):
    glutSolidCube(s)

def dcyl(b, t, h, sl=10, st=4):
    gluCylinder(state.quadric, b, t, h, sl, st)

def dsph(r, sl=10, st=10):
    gluSphere(state.quadric, r, sl, st)

def draw_fireballs():
    for fb in state.fireballs:
        glPushMatrix()
        glTranslatef(fb['x'], fb['y'], fb['z'])
        s = 1.0+0.3*math.sin(time.time()*15.0+fb['id'])
        glScalef(s,s,s)
        if state.boss.phase==3: glColor3f(0.0,0.8,1.0)
        else: glColor3f(1.0,0.5,0.0)
        dsph(0.4,12,12)
        glColor3f(1.0,1.0,1.0); dsph(0.2,8,8)
        glPopMatrix()
    for fb in state.player_fireballs:
        glPushMatrix()
        glTranslatef(fb['x'], fb['y'], fb['z'])
        glScalef(1.2, 1.2, 1.2)
        glColor3f(0.2, 0.2, 1.0)
        dsph(0.3, 12, 12)
        glColor3f(0.8, 0.8, 1.0)
        dsph(0.15, 8, 8)
        glPopMatrix()
    for fb in state.enemy_fireballs:
        glPushMatrix()
        glTranslatef(fb['x'], fb['y'], fb['z'])
        s = 1.0 + 0.2 * math.sin(time.time() * 12.0 + fb['id'])
        glScalef(s, s, s)
        glColor3f(*ENEMY_FB_OUTER)
        dsph(0.35, 12, 12)
        glColor3f(*ENEMY_FB_INNER)
        dsph(0.18, 8, 8)
        glPopMatrix()

def draw_particles():
    if not state.particles: return
    glPointSize(5.0)
    glColor3f(1.0,1.0,0.0)
    glBegin(GL_POINTS)
    for p in state.particles: glVertex3f(p['x'],p['y'],p['z'])
    glEnd()

def draw_crosshair():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.8, 0.2, 0.2)
    cx, cy = W_WIDTH//2, W_HEIGHT//2
    glBegin(GL_LINES)
    glVertex3f(cx-12,cy,0); glVertex3f(cx+12,cy,0)
    glVertex3f(cx,cy-12,0); glVertex3f(cx,cy+12,0)
    glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_text():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.9, 0.9, 0.9)
    t1 = "Boss HP: {:.0f}  Phase: {}".format(state.boss.hp, state.boss.phase)
    glRasterPos2f(10, W_HEIGHT-30)
    for c in t1: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    t2 = "WASD: Move | LMB: Shoot | E: HOLD closest prop | F: THROW held prop | Arrows: Look"
    glRasterPos2f(10, W_HEIGHT-60)
    for c in t2: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    
    if state.environment.held_object:
        glColor3f(0.8, 0.3, 0.3)
        glRasterPos2f(W_WIDTH//2 - 80, 50)
        text = "HOLDING: " + state.environment.held_object.obj_type.upper()
        for c in text: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
        glColor3f(0.6, 0.6, 0.6)
        glRasterPos2f(W_WIDTH//2 - 50, 30)
        text2 = "Press F to THROW"
        for c in text2: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
    
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def spawn_player_fireball():
    speed = 25.0
    vx = math.sin(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch))
    vy = math.sin(math.radians(state.player_pitch))
    vz = -math.cos(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch))
    sx = state.player_x + vx * 1.0
    sy = state.player_y + vy * 1.0
    sz = state.player_z + vz * 1.0
    state.player_fireballs.append({'x': sx, 'y': sy, 'z': sz, 'vx': vx * speed, 'vy': vy * speed, 'vz': vz * speed})

def update_player(dt):
    fwd_x = math.sin(math.radians(state.player_yaw))
    fwd_z = -math.cos(math.radians(state.player_yaw))
    right_x, right_z = -fwd_z, fwd_x
    mx, mz = 0.0, 0.0
    if state.keys.get('w'): mx += fwd_x; mz += fwd_z
    if state.keys.get('s'): mx -= fwd_x; mz -= fwd_z
    if state.keys.get('a'): mx -= right_x; mz -= right_z
    if state.keys.get('d'): mx += right_x; mz += right_z
    ln = math.sqrt(mx*mx + mz*mz)
    if ln > 0:
        mx /= ln; mz /= ln
        state.player_x += mx * PLAYER_SPEED * dt
        state.player_z += mz * PLAYER_SPEED * dt
    if state.keys.get('q'): state.player_yaw -= 120.0 * dt
    if state.keys.get('e'): state.player_yaw += 120.0 * dt
    if state.keys.get('left'):  state.player_yaw -= 120.0 * dt
    if state.keys.get('right'): state.player_yaw += 120.0 * dt
    if state.keys.get('up'):    state.player_pitch += 90.0 * dt
    if state.keys.get('down'):  state.player_pitch -= 90.0 * dt
    state.player_pitch = max(-60.0, min(60.0, state.player_pitch))
    if state.mouse_held:
        dx = state.mouse_x - W_WIDTH / 2.0
        dy = state.mouse_y - W_HEIGHT / 2.0
        state.player_yaw += dx * 0.3 * dt * 10.0
        state.player_pitch -= dy * 0.2 * dt * 10.0
        state.player_pitch = max(-60.0, min(60.0, state.player_pitch))
    state.player_x = max(-38, min(38, state.player_x))
    state.player_z = max(-38, min(38, state.player_z))

def update(dt):
    update_player(dt)
    state.environment.update_objects(dt)
    state.boss.update(dt)
    
    # Object collision with enemies
    for obj in state.environment.objects:
        if not obj.is_held and not obj.grounded:
            dist_to_boss = math.sqrt((obj.x - state.boss.x)**2 + (obj.y - state.boss.y)**2 + (obj.z - state.boss.z)**2)
            if dist_to_boss < 3.0:
                if state.boss.phase in (1, 3):
                    state.boss.hp = max(0, state.boss.hp - 8)
                    for _ in range(5):
                        state.particles.append({'x': obj.x, 'y': obj.y, 'z': obj.z, 'vy': 2 + random.random() * 5, 'life': 0.5})
                    obj.y = -10
            
            for enemy in state.enemies:
                if not enemy.alive:
                    continue
                dist = math.sqrt((obj.x - enemy.x)**2 + (obj.y - enemy.y)**2 + (obj.z - enemy.z)**2)
                if dist < 2.0:
                    enemy.hp = max(0, enemy.hp - 30)
                    for _ in range(4):
                        state.particles.append({'x': obj.x, 'y': obj.y, 'z': obj.z, 'vy': 2 + random.random() * 4, 'life': 0.4})
                    obj.y = -10
                    if enemy.hp <= 0:
                        enemy.alive = False
                    break
    
    state.environment.objects = [obj for obj in state.environment.objects if obj.y > -5]
    
    # Respawn objects if too few
    if len(state.environment.objects) < 8:
        half_arena = 40
        new_x = random.uniform(-half_arena + 5, half_arena - 5)
        new_z = random.uniform(-half_arena + 5, half_arena - 5)
        obj_types = ["skull", "bone", "ribcage", "spine", "coffin", "candle", "book", "potion", "dagger", "heart", "eye"]
        new_type = random.choice(obj_types)
        state.environment.objects.append(GameObject(new_x, new_z, new_type))
    
    for e in state.enemies:
        e.update(dt)
    
    for p in state.particles: p['y'] += p['vy']*dt; p['life'] -= dt
    state.particles = [p for p in state.particles if p['life'] > 0]
    
    for fb in state.fireballs: fb['x'] += fb['vx']*dt; fb['y'] += fb['vy']*dt; fb['z'] += fb['vz']*dt
    state.fireballs = [fb for fb in state.fireballs if fb['y'] > -5 and abs(fb['x']) < 60 and abs(fb['z']) < 60]
    
    for fb in state.enemy_fireballs:
        fb['x'] += fb['vx'] * dt; fb['y'] += fb['vy'] * dt; fb['z'] += fb['vz'] * dt
    state.enemy_fireballs = [fb for fb in state.enemy_fireballs if fb['y'] > -5 and abs(fb['x']) < 70 and abs(fb['z']) < 70]
    
    for fb in state.player_fireballs:
        fb['x'] += fb['vx']*dt; fb['y'] += fb['vy']*dt; fb['z'] += fb['vz']*dt
        hit = False
        dist = math.sqrt((fb['x']-state.boss.x)**2 + (fb['y']-state.boss.y)**2 + (fb['z']-state.boss.z)**2)
        if dist < 4.5:
            if state.boss.phase in (1, 3):
                state.boss.hp = max(0, state.boss.hp - 10)
                for _ in range(5):
                    state.particles.append({'x':fb['x']+(random.random()-0.5)*2, 'y':fb['y']+(random.random()-0.5)*2,
                                            'z':fb['z']+(random.random()-0.5)*2, 'vy':2+random.random()*5, 'life':0.5})
                if state.boss.hp <= 0:
                    state.boss.start_death_blast()
            fb['y'] = -100
            hit = True
        if not hit:
            for e in state.enemies:
                if not e.alive:
                    continue
                dist = math.sqrt((fb['x'] - e.x)**2 + (fb['y'] - e.y)**2 + (fb['z'] - e.z)**2)
                if dist < 2.0:
                    e.hp = max(0, e.hp - 50.0)
                    for _ in range(4):
                        state.particles.append({
                            'x': fb['x'] + (random.random() - 0.5) * 1.5,
                            'y': fb['y'] + (random.random() - 0.5) * 1.5,
                            'z': fb['z'] + (random.random() - 0.5) * 1.5,
                            'vy': 2 + random.random() * 4,
                            'life': 0.4,
                        })
                    if e.hp <= 0:
                        e.alive = False
                    fb['y'] = -100
                    break
    state.player_fireballs = [fb for fb in state.player_fireballs if fb['y'] > -5 and abs(fb['x']) < 60 and abs(fb['z']) < 60]
    state.enemies = [e for e in state.enemies if e.alive]

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, W_WIDTH/W_HEIGHT, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # NO LIGHTING - to preserve original colors!
    # Just draw everything with original colors
    
    look_dist = 10.0
    lx = state.player_x + math.sin(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * look_dist
    ly = state.player_y + math.sin(math.radians(state.player_pitch)) * look_dist
    lz = state.player_z - math.cos(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * look_dist
    gluLookAt(state.player_x, state.player_y, state.player_z,
              lx, ly, lz, 0, 1, 0)
    
    # Draw environment (floor, obstacles, particles)
    state.environment.draw_floor()
    state.environment.draw_obstacles()
    state.environment.draw_objects()
    state.environment.draw_blood_particles()
    
    # Draw game elements
    draw_particles()
    draw_fireballs()
    state.boss.draw()
    state.boss.draw_death_blast()
    state.boss.draw_health_bar()
    
    for e in state.enemies:
        e.draw()
        e.draw_health_bar()
    
    # Draw held object in first-person
    state.environment.draw_held_object()
    
    draw_crosshair()
    draw_text()
    glutSwapBuffers()

def idle():
    ct = time.time()
    dt = min(ct-state.last_time, 0.1)
    state.last_time = ct
    update(dt)
    glutPostRedisplay()

def keyboard(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    
    if k == b' ':
        spawn_player_fireball()
    
    if k == b'e':
        state.environment.pickup_object(state.player_x, state.player_z, state.player_yaw)
    
    if k == b'f':
        state.environment.throw_held_object(
            state.player_x,
            state.player_y,
            state.player_z,
            state.player_yaw,
            state.player_pitch
        )
    
    if k in (b'w', b'a', b's', b'd', b'q'):
        state.keys[k.decode()] = True
    
    # For 'e' key for turning (if needed)
    if k == b'e' and len(k) > 0:
        # Only treat as turn if no object pickup happened? 
        # Actually let's use Q for left turn, E for right turn
        if not state.environment.held_object:  # If not picking up, then turn
            pass

def keyboard_up(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    if k in (b'w', b'a', b's', b'd', b'q', b'e'):
        state.keys[k.decode()] = False

def mouse_func(button, btn_state, x, y):
    if button == GLUT_LEFT_BUTTON:
        if btn_state == GLUT_DOWN:
            state.mouse_held = True
            state.mouse_x, state.mouse_y = x, y
        else:
            state.mouse_held = False
    if button == GLUT_RIGHT_BUTTON and btn_state == GLUT_DOWN:
        spawn_player_fireball()

def special_key(key, x, y):
    if key == GLUT_KEY_UP:    state.keys['up'] = True
    if key == GLUT_KEY_DOWN:  state.keys['down'] = True
    if key == GLUT_KEY_LEFT:  state.keys['left'] = True
    if key == GLUT_KEY_RIGHT: state.keys['right'] = True

def special_key_up(key, x, y):
    if key == GLUT_KEY_UP:    state.keys['up'] = False
    if key == GLUT_KEY_DOWN:  state.keys['down'] = False
    if key == GLUT_KEY_LEFT:  state.keys['left'] = False
    if key == GLUT_KEY_RIGHT: state.keys['right'] = False

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Boss Fight - Horror Arena")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_key)
    glutMouseFunc(mouse_func)
    try:
        glutKeyboardUpFunc(keyboard_up)
        glutSpecialUpFunc(special_key_up)
    except:
        pass
    glutMainLoop()
