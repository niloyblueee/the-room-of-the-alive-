import math
import time
import random
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

W_WIDTH, W_HEIGHT = 800, 600
PLAYER_SPEED = 14.0

# ---------- colors ----------
C_BODY   = (0.85, 0.85, 0.85)
C_CLOTH  = (0.15, 0.15, 0.18)
C_GOLD   = (0.80, 0.65, 0.20)
C_DETAIL = (0.20, 0.20, 0.20)

ENEMY_FB_OUTER = (0.8, 0.0, 0.0) 
ENEMY_FB_INNER = (1.0, 0.8, 0.0)

# --- Darker themes for horror atmosphere ---
ROOM_THEMES = {
    1: {'floor': (0.10, 0.11, 0.12), 'wall': (0.08, 0.09, 0.10), 'mortar': (0.02, 0.02, 0.02), 'fog_col': (0.03, 0.03, 0.04)}, 
    2: {'floor': (0.10, 0.04, 0.04), 'wall': (0.08, 0.03, 0.03), 'mortar': (0.02, 0.0, 0.0), 'fog_col': (0.04, 0.01, 0.01)}, 
    3: {'floor': (0.05, 0.05, 0.05), 'wall': (0.04, 0.04, 0.04), 'mortar': (0.20, 0.02, 0.02), 'fog_col': (0.02, 0.02, 0.02)}        
}

WEAPONS = {
    "HANDGUN": {"max_ammo": 12, "damage": 40, "pellets": 1, "spread": 0.01, "color": (1.0, 0.8, 0.2), "cooldown": 0.3},
    "SHOTGUN": {"max_ammo": 6,  "damage": 25, "pellets": 6, "spread": 0.12, "color": (1.0, 0.4, 0.0), "cooldown": 0.8},
    "SMG":     {"max_ammo": 30, "damage": 30, "pellets": 1, "spread": 0.05, "color": (0.2, 1.0, 0.2), "cooldown": 0.1}
}

# --- Fixed Linear Fog System ---
def apply_fog_color(base_c, obj_x, obj_z):
    dist = math.sqrt((obj_x - state.player_x)**2 + (obj_z - state.player_z)**2)
    fog_c = ROOM_THEMES[state.room]['fog_col']
    
    factor = max(0.0, min(1.0, dist / 30.0))
    
    r = base_c[0] * (1 - factor) + fog_c[0] * factor
    g = base_c[1] * (1 - factor) + fog_c[1] * factor
    b = base_c[2] * (1 - factor) + fog_c[2] * factor
    return (r, g, b)

def check_obstacle_hit(px, py, pz):
    for obs in state.environment.obstacles:
        if py < obs.height:
            if obs.obs_type == "blood_pool": continue 
            rad = max(obs.width, obs.depth) * 0.65
            if math.sqrt((px - obs.x)**2 + (pz - obs.z)**2) < rad:
                return True
    return False

def resolve_obstacle_collision(px, pz, radius=0.6):
    for obs in state.environment.obstacles:
        if obs.obs_type == "blood_pool": continue 
        rad = max(obs.width, obs.depth) * 0.65 + radius
        dist = math.sqrt((px - obs.x)**2 + (pz - obs.z)**2)
        if 0.0001 < dist < rad:
            px = obs.x + ((px - obs.x) / dist) * rad
            pz = obs.z + ((pz - obs.z) / dist) * rad
    return px, pz

class DetailedFPSWeaponDrawer:
    @staticmethod
    def draw_weapon(weapon_type, recoil_offset):
        glPushMatrix()
        glTranslatef(0.25, -0.25 + (recoil_offset * 0.02), -0.8 + (recoil_offset * 0.05))
        glRotatef(recoil_offset * 2.0, 1, 0, 0)
        glRotatef(-8.0, 0, 1, 0)

        if weapon_type == "HANDGUN":
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix(); glTranslatef(0, -0.15, 0); glRotatef(15, 1, 0, 0); glScalef(0.1, 0.3, 0.15); dcube(1.0); glPopMatrix()
            glColor3f(0.3, 0.3, 0.35)
            glPushMatrix(); glTranslatef(0, 0.05, -0.15); glScalef(0.12, 0.12, 0.5); dcube(1.0); glPopMatrix()
            glColor3f(0.6, 0.6, 0.6)
            glPushMatrix(); glTranslatef(0, 0.1, -0.35); glScalef(0.04, 0.04, 0.08); dcube(1.0); glPopMatrix()
        elif weapon_type == "SHOTGUN":
            glColor3f(0.2, 0.1, 0.05)
            glPushMatrix(); glTranslatef(0, -0.1, 0.2); glRotatef(10, 1, 0, 0); glScalef(0.12, 0.2, 0.4); dcube(1.0); glPopMatrix()
            glColor3f(0.2, 0.2, 0.2)
            glPushMatrix(); glTranslatef(0, 0.05, -0.1); glScalef(0.15, 0.15, 0.3); dcube(1.0); glPopMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix(); glTranslatef(0.04, 0.05, -0.4); glScalef(0.06, 0.06, 0.6); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(-0.04, 0.05, -0.4); glScalef(0.06, 0.06, 0.6); dcube(1.0); glPopMatrix()
            glColor3f(0.3, 0.15, 0.05)
            glPushMatrix(); glTranslatef(0, -0.05, -0.3); glScalef(0.18, 0.1, 0.2); dcube(1.0); glPopMatrix()
        elif weapon_type == "SMG":
            glColor3f(0.15, 0.15, 0.15)
            glPushMatrix(); glTranslatef(0, 0.05, -0.1); glScalef(0.12, 0.15, 0.4); dcube(1.0); glPopMatrix()
            glColor3f(0.05, 0.05, 0.05)
            glPushMatrix(); glTranslatef(0, -0.15, 0.05); glRotatef(10, 1, 0, 0); glScalef(0.1, 0.25, 0.12); dcube(1.0); glPopMatrix()
            glColor3f(0.1, 0.1, 0.12)
            glPushMatrix(); glTranslatef(0, -0.2, -0.15); glRotatef(-5, 1, 0, 0); glScalef(0.08, 0.3, 0.1); dcube(1.0); glPopMatrix()
            glColor3f(0.05, 0.05, 0.05)
            glPushMatrix(); glTranslatef(0, 0.05, -0.4); glScalef(0.04, 0.04, 0.3); dcube(1.0); glPopMatrix()
            
        glPopMatrix()

class GameObject:
    def __init__(self, x, z, obj_type):
        self.x, self.y, self.z = x, 1.0, z
        self.obj_type = obj_type
        self.is_held, self.grounded, self.is_thrown = False, True, False
        self.velocity_x, self.velocity_y, self.velocity_z = 0.0, 0.0, 0.0
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2.0, 2.0)
        self.glow_time = random.uniform(0, 6.28)
        self.trail = []

        props = {
            "axe": ((0.6, 0.3, 0.1), 1.0, 150, False, False),
            "spear": ((0.5, 0.4, 0.2), 1.0, 120, False, False),
            "knife": ((0.8, 0.8, 0.8), 1.0, 80, False, False),
            "rock": ((0.4, 0.4, 0.4), 1.0, 50, False, False),
            "medkit": ((0.9, 0.9, 0.9), 1.0, 0, True, False),
            "shotgun": ((0.2, 0.2, 0.2), 1.0, 0, False, True),
            "smg": ((0.15, 0.15, 0.15), 1.0, 0, False, True),
            "handgun": ((0.2, 0.2, 0.2), 1.0, 0, False, True)
        }
        self.color, self.size, self.damage, self.is_consumable, self.is_gun = props.get(obj_type, ((0.5, 0.5, 0.5), 1.0, 50, False, False))
        self.has_glow = True

    def update(self, dt):
        if self.is_held: return

        if not self.grounded:
            self.velocity_y -= 45.0 * dt 
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            self.z += self.velocity_z * dt
            
            if check_obstacle_hit(self.x, self.y, self.z):
                self.velocity_x *= -0.5
                self.velocity_z *= -0.5
                spawn_wall_hit_particles(self.x, self.y, self.z)
            
            if self.is_thrown:
                self.rotation += 800.0 * dt
                self.trail.append((self.x, self.y, self.z))
                if len(self.trail) > 8: self.trail.pop(0)
            else:
                self.rotation += self.rotation_speed * 150.0 * dt

            if self.y <= 1.0:
                self.y = 1.0
                self.is_thrown = False
                self.trail.clear()
                if abs(self.velocity_y) > 8.0:
                    self.velocity_y *= -0.3
                    self.velocity_x *= 0.5
                    self.velocity_z *= 0.5
                else:
                    self.velocity_y = 0.0
                    self.velocity_x *= 0.2
                    self.velocity_z *= 0.2
                if abs(self.velocity_x) < 0.5 and abs(self.velocity_z) < 0.5:
                    self.grounded = True
                    self.velocity_x = self.velocity_y = self.velocity_z = 0.0
        else:
            self.rotation += self.rotation_speed
            self.trail.clear()
            
        self.glow_time += dt * 4.0

    def throw_from_player(self, px, py, pz, yaw, pitch, power=60.0):
        fx = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        fy = math.sin(math.radians(pitch))
        fz = -math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        
        self.is_held, self.grounded, self.is_thrown = False, False, True
        self.x, self.y, self.z = px + fx * 2.4, py - 0.2 + fy * 1.0, pz + fz * 2.4
        if self.obj_type in ["knife", "spear"]: power *= 1.3
        self.velocity_x, self.velocity_y, self.velocity_z = fx * power, (fy * power) + 5.0, fz * power
        self.trail.clear()

    def draw_world(self):
        if self.is_thrown and len(self.trail) > 1:
            glBegin(GL_LINES)
            for i in range(len(self.trail) - 1):
                glColor3f(*apply_fog_color((0.8, 0.8, 0.9), self.trail[i][0], self.trail[i][2]))
                glVertex3f(*self.trail[i])
                glVertex3f(*self.trail[i+1])
            glEnd()

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        if self.is_thrown: glRotatef(self.rotation, 1, 0, 1) 
        else:
            glRotatef(self.rotation, 0, 1, 0)
            if not self.grounded: glRotatef(self.rotation * 1.2, 1, 0, 0)
        
        glScalef(self.size, self.size, self.size)
        self.draw_model(is_held=False)
        glPopMatrix()

    def draw_fps(self, swing_progress, bob_offset):
        glPushMatrix()
        glTranslatef(0.3, -0.2 + bob_offset, -0.8)
        if swing_progress > 0:
            swing_angle = math.sin(swing_progress * math.pi)
            glRotatef(swing_angle * -70, 1, 0, 0)
            glRotatef(swing_angle * 30, 0, 1, 0) 
        glRotatef(90, 0, 1, 0); glRotatef(45, 0, 0, 1)
        glScalef(self.size * 0.8, self.size * 0.8, self.size * 0.8)
        self.draw_model(is_held=True)
        glPopMatrix()

    def draw_model(self, is_held):
        if self.has_glow and not is_held:
            pulse = 1.0 + 0.15 * math.sin(self.glow_time)
            glScalef(pulse, pulse, pulse)

        def set_col(r, g, b):
            if is_held: glColor3f(r, g, b)
            else: glColor3f(*apply_fog_color((r, g, b), self.x, self.z))

        if self.obj_type == "axe":
            set_col(0.3, 0.15, 0.05)
            glPushMatrix(); glTranslatef(0, -0.4, 0); glRotatef(-90, 1, 0, 0); dcyl(0.04, 0.04, 0.8); glPopMatrix()
            set_col(0.7, 0.7, 0.7)
            glPushMatrix(); glTranslatef(0.15, 0.2, 0); glScalef(0.4, 0.3, 0.05); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(0.25, 0.2, 0); glScalef(0.2, 0.4, 0.04); dcube(1.0); glPopMatrix()
        elif self.obj_type == "spear":
            set_col(0.3, 0.15, 0.05)
            glPushMatrix(); glTranslatef(0, -0.8, 0); glRotatef(-90, 1, 0, 0); dcyl(0.03, 0.03, 1.6); glPopMatrix()
            set_col(0.8, 0.8, 0.8)
            glPushMatrix(); glTranslatef(0, 0.8, 0); glRotatef(-90, 1, 0, 0); dcyl(0.04, 0.0, 0.3); glPopMatrix()
        elif self.obj_type == "knife":
            set_col(0.2, 0.2, 0.2)
            glPushMatrix(); glTranslatef(0, -0.2, 0); glRotatef(-90, 1, 0, 0); dcyl(0.03, 0.03, 0.2); glPopMatrix()
            set_col(0.8, 0.8, 0.8)
            glPushMatrix(); glTranslatef(0, 0.15, 0); glScalef(0.06, 0.5, 0.02); dcube(1.0); glPopMatrix()
        elif self.obj_type == "rock":
            set_col(0.4, 0.4, 0.4)
            glPushMatrix(); glScalef(0.4, 0.3, 0.35); dsph(0.6, 4, 4); glPopMatrix()
        elif self.obj_type == "medkit":
            set_col(0.9, 0.9, 0.9)
            glPushMatrix(); glScalef(0.5, 0.4, 0.2); dcube(1.0); glPopMatrix()
            set_col(0.8, 0.1, 0.1)
            glPushMatrix(); glTranslatef(0, 0, 0.11); glScalef(0.1, 0.2, 0.02); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(0, 0, 0.11); glScalef(0.2, 0.1, 0.02); dcube(1.0); glPopMatrix()
        elif self.obj_type == "shotgun":
            set_col(0.3, 0.15, 0.05)
            glPushMatrix(); glTranslatef(-0.2, 0, 0); glScalef(0.4, 0.1, 0.05); dcube(1.0); glPopMatrix()
            set_col(0.2, 0.2, 0.2)
            glPushMatrix(); glTranslatef(0.2, 0.02, 0); glScalef(0.6, 0.05, 0.05); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(0.2, -0.04, 0); glScalef(0.5, 0.04, 0.05); dcube(1.0); glPopMatrix()
        elif self.obj_type == "smg":
            set_col(0.15, 0.15, 0.15)
            glPushMatrix(); glScalef(0.4, 0.1, 0.08); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(0.1, -0.15, 0); glScalef(0.08, 0.3, 0.06); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(-0.15, -0.1, 0); glRotatef(15, 0, 0, 1); glScalef(0.08, 0.2, 0.06); dcube(1.0); glPopMatrix()
        elif self.obj_type == "handgun":
            set_col(0.2, 0.2, 0.2)
            glPushMatrix(); glTranslatef(0.05, 0, 0); glScalef(0.2, 0.08, 0.05); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(-0.05, -0.1, 0); glRotatef(15, 0, 0, 1); glScalef(0.06, 0.15, 0.05); dcube(1.0); glPopMatrix()
        else:
            set_col(0.4, 0.4, 0.4); dsph(0.3)

class Obstacle:
    def __init__(self, x, z, obs_type):
        self.x, self.z, self.obs_type = x, z, obs_type
        self.rotation = random.uniform(0, 360)
        self.seed = int((x + z) * 100) 
        
        props = {
            "pillar": (4.0, 1.2, 1.2, (0.05, 0.05, 0.08)),
            "tombstone": (2.2, 1.0, 0.3, (0.10, 0.10, 0.12)),
            "cage": (3.5, 1.8, 1.8, (0.02, 0.02, 0.02)),
            "altar": (1.2, 2.5, 1.5, (0.08, 0.05, 0.05)),
            "spike_trap": (2.0, 2.0, 2.0, (0.1, 0.1, 0.1)),
            "blood_pool": (3.0, 0.05, 3.0, (0.4, 0.0, 0.0)),
            "gore_pile": (2.5, 1.5, 2.5, (0.3, 0.05, 0.05))
        }
        self.height, self.width, self.depth, self.color = props.get(obs_type, (2.0, 2.0, 1.0, (0.2, 0.2, 0.2)))
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        
        c = apply_fog_color(self.color, self.x, self.z)
        cdark = apply_fog_color((self.color[0]*0.4, self.color[1]*0.4, self.color[2]*0.4), self.x, self.z)
        
        if self.obs_type == "pillar":
            glColor3f(*c); glPushMatrix(); glTranslatef(0, self.height/2, 0); glScalef(self.width, self.height, self.depth); dcube(1.0); glPopMatrix()
            glColor3f(*cdark); glPushMatrix(); glTranslatef(0, 0.5, 0); glScalef(self.width*1.2, 1.0, self.depth*1.2); dcube(1.0); glPopMatrix()
        elif self.obs_type == "cage":
            glColor3f(*cdark); glPushMatrix(); glTranslatef(0, 0.2, 0); glScalef(self.width, 0.4, self.depth); dcube(1.0); glPopMatrix()
            glColor3f(*c); glPushMatrix(); glTranslatef(0, self.height, 0); glScalef(self.width, 0.2, self.depth); dcube(1.0); glPopMatrix()
            for i in [-1, 1]:
                for j in [-1, 1]:
                    glPushMatrix(); glTranslatef(i*self.width/2.2, self.height/2, j*self.depth/2.2); glScalef(0.1, self.height, 0.1); dcube(1.0); glPopMatrix()
                    
        elif self.obs_type == "spike_trap":
            glColor3f(*cdark); glPushMatrix(); glTranslatef(0, 0.1, 0); glScalef(self.width, 0.2, self.depth); dcube(1.0); glPopMatrix()
            random.seed(self.seed)
            for sx in [-0.6, 0, 0.6]:
                for sz in [-0.6, 0, 0.6]:
                    if random.random() > 0.2: 
                        glPushMatrix()
                        glTranslatef(sx, 0.2, sz)
                        glRotatef(-90, 1, 0, 0)
                        glColor3f(*apply_fog_color((0.15, 0.15, 0.15), self.x, self.z))
                        dcyl(0.06, 0.03, 0.9)
                        glTranslatef(0, 0, 0.9)
                        glColor3f(*apply_fog_color((0.5, 0.0, 0.0), self.x, self.z))
                        dcyl(0.03, 0.0, 0.5) 
                        glPopMatrix()
            random.seed()
            
        elif self.obs_type == "blood_pool":
            random.seed(self.seed)
            glPushMatrix()
            glTranslatef(0, 0.01, 0) 
            for _ in range(8):
                rx = random.uniform(-self.width/2.5, self.width/2.5)
                rz = random.uniform(-self.depth/2.5, self.depth/2.5)
                rw = random.uniform(0.4, 1.4)
                rd = random.uniform(0.4, 1.4)
                ang = random.uniform(0, 360)
                glColor3f(*apply_fog_color((0.4, 0.0, 0.0), self.x + rx, self.z + rz))
                
                glPushMatrix()
                glTranslatef(rx, 0, rz)
                glRotatef(ang, 0, 1, 0)
                glScalef(rw, 0.01, rd)
                dcube(1.0)
                glPopMatrix()
            glPopMatrix()
            random.seed()
            
        elif self.obs_type == "gore_pile":
            random.seed(self.seed)
            for _ in range(15):
                bx = random.uniform(-0.8, 0.8)
                bz = random.uniform(-0.8, 0.8)
                by = random.uniform(0.1, 0.9) - (bx*bx + bz*bz)*0.3 
                
                glColor3f(*apply_fog_color((0.3, 0.02, 0.02), self.x, self.z))
                glPushMatrix()
                glTranslatef(bx, by, bz)
                glRotatef(random.uniform(0,360), 1, 1, 1)
                glScalef(0.4, random.uniform(0.2, 0.6), 0.4)
                dcube(1.0)
                glPopMatrix()
                
                if random.random() > 0.4:
                    glColor3f(*apply_fog_color((0.7, 0.7, 0.65), self.x, self.z))
                    glPushMatrix()
                    glTranslatef(bx, by, bz)
                    glRotatef(random.uniform(0, 360), 1, 1, 1)
                    dcyl(0.04, 0.0, 0.8) 
                    glPopMatrix()
            random.seed()
            
        else:
            glColor3f(*c); glPushMatrix(); glTranslatef(0, self.height/2, 0); glScalef(self.width, self.height, self.depth); dcube(1.0); glPopMatrix()
        glPopMatrix()

class Environment:
    def __init__(self, room_level):
        self.floor_tiles, self.wall_bricks = [], []
        self.obstacles, self.objects, self.chains, self.vines = [], [], [], []
        self.held_object = None
        self.room_level = room_level
        
        if room_level == 1: self.width, self.depth, obs_count, obs_choices = 20, 60, 8, ["pillar", "tombstone", "cage", "altar", "spike_trap", "blood_pool", "gore_pile"]
        elif room_level == 2: self.width, self.depth, obs_count, obs_choices = 24, 80, 14, ["pillar", "tombstone", "cage", "altar", "spike_trap", "blood_pool", "gore_pile"]
        else: self.width, self.depth, obs_count, obs_choices = 40, 60, 8, ["pillar", "blood_pool", "gore_pile"] 

        self.theme = ROOM_THEMES.get(room_level, ROOM_THEMES[1])
        
        self._generate_procedural_textures()
        self._generate_obstacles(obs_count, obs_choices)
        self._generate_objects()
        
        if room_level < 3:
            hw, hd = self.width // 2, self.depth // 2
            for _ in range(15):
                self.chains.append({'x': random.uniform(-hw+2, hw-2), 'z': random.uniform(-hd+2, hd-2), 'length': random.randint(10, 25)})
            for _ in range(80):
                x1 = random.uniform(-hw+1, hw-1); z1 = random.uniform(-hd+1, hd-1); y1 = random.uniform(18, 25)
                x2 = x1 + random.uniform(-8, 8); z2 = z1 + random.uniform(-8, 8); y2 = y1 + random.uniform(-8, 2)
                self.vines.append((x1,y1,z1, x2,y2,z2))

    def _generate_procedural_textures(self):

        hw, hd = self.width // 2, self.depth // 2
        for x in range(-int(hw), int(hw), 4):
            for z in range(-int(hd), int(hd), 4):
                bc = self.theme['floor']
                var = random.uniform(-0.02, 0.02) 
                self.floor_tiles.append({'x': x, 'z': z, 'w': 3.8, 'h': 3.8, 'base_color': (max(0, bc[0]+var), max(0, bc[1]+var), max(0, bc[2]+var))}) 

        if self.room_level < 3:
            wall_h, bw, bh = 25, 5.0, 2.5 
            self._build_wall_side(-hw, -hd, hw, -hd, wall_h, bw, bh) 
            self._build_wall_side(hw, hd, -hw, hd, wall_h, bw, bh)   
            self._build_wall_side(-hw, hd, -hw, -hd, wall_h, bw, bh) 
            self._build_wall_side(hw, -hd, hw, hd, wall_h, bw, bh)   

    def _build_wall_side(self, x1, z1, x2, z2, h, bw, bh):
        dx, dz = x2 - x1, z2 - z1
        length = math.sqrt(dx*dx + dz*dz)
        if length == 0: return
        ux, uz = dx/length, dz/length

        for r in range(int(h / bh)):
            y_b = r * bh
            offset = (bw / 2.0) if r % 2 != 0 else 0.0
            for c in range(int(length / bw) + 1):
                start_dist = max(0, c * bw - offset)
                end_dist = min(length, start_dist + bw - 0.2)
                if end_dist <= 0 or start_dist >= length: continue

                cx1, cz1 = x1 + ux * start_dist, z1 + uz * start_dist
                cx2, cz2 = x1 + ux * end_dist, z1 + uz * end_dist

                base_col = self.theme['wall']
                var = random.uniform(-0.02, 0.02)
                shade_bottom, shade_top = 0.2 + (r / float(int(h / bh))) * 0.4, 0.2 + ((r + 1) / float(int(h / bh))) * 0.4
                
                self.wall_bricks.append({
                    'x1': cx1, 'z1': cz1, 'x2': cx2, 'z2': cz2,
                    'yb': y_b + 0.2, 'yt': y_b + bh - 0.2, 
                    'color_bottom': (max(0, (base_col[0]+var)*shade_bottom), max(0, (base_col[1]+var)*shade_bottom), max(0, (base_col[2]+var)*shade_bottom)), 
                    'color_top': (max(0, (base_col[0]+var)*shade_top), max(0, (base_col[1]+var)*shade_top), max(0, (base_col[2]+var)*shade_top))
                })

    def _generate_obstacles(self, count, obs_choices):
        hw, hd, placed = self.width // 2, self.depth // 2, 0
        while placed < count:
            x, z = random.uniform(-hw+3, hw-3), random.uniform(-hd+10, hd-10) 
            if abs(x) >= 3.0 and not any(abs(obs.x - x) < 4.0 and abs(obs.z - z) < 4.0 for obs in self.obstacles):
                self.obstacles.append(Obstacle(x, z, random.choice(obs_choices)))
                placed += 1

    def _generate_objects(self):
        hw, hd = self.width // 2, self.depth // 2
        for _ in range(self.room_level * 2 + 1): self.objects.append(GameObject(random.uniform(-hw+2, hw-2), random.uniform(-hd+10, hd-10), "medkit"))
        
        gun_count = 2 if self.room_level < 3 else 3
        for _ in range(gun_count):
            g_type = random.choice(["shotgun", "smg", "handgun"])
            self.objects.append(GameObject(random.uniform(-hw+2, hw-2), random.uniform(-hd+10, hd-10), g_type))
        
        throw_count = 5 if self.room_level == 1 else (8 if self.room_level == 2 else 4)
        for _ in range(throw_count): self.objects.append(GameObject(random.uniform(-hw+2, hw-2), random.uniform(-hd+10, hd-10), random.choice(["axe", "spear", "rock", "knife"])))

    def draw_room(self):
        hw, hd = self.width / 2, self.depth / 2

        glColor3f(*apply_fog_color(self.theme['mortar'], 0, 0))
        glBegin(GL_QUADS)
        glVertex3f(-hw, 0, -hd); glVertex3f(hw, 0, -hd); glVertex3f(hw, 0, hd); glVertex3f(-hw, 0, hd)
        glEnd()
        
        glBegin(GL_QUADS)
        for t in self.floor_tiles:
            for vx, vz in [(0,0), (t['w'],0), (t['w'],t['h']), (0,t['h'])]:
                world_x, world_z = t['x'] + vx, t['z'] + vz
                shade = 1.0 - min(1.0, (abs(world_x) / hw) * 0.7)
                col = t['base_color']
                final_col = apply_fog_color((col[0]*shade, col[1]*shade, col[2]*shade), world_x, world_z)
                glColor3f(*final_col)
                glVertex3f(world_x, 0.01, world_z)
        glEnd()

        if self.room_level < 3:
            wall_h = 25.0
            glBegin(GL_QUADS)
            for w in self.wall_bricks:
                glColor3f(*apply_fog_color(w['color_bottom'], w['x1'], w['z1']))
                glVertex3f(w['x1'], w['yb'], w['z1']); glVertex3f(w['x2'], w['yb'], w['z2'])
                glColor3f(*apply_fog_color(w['color_top'], w['x2'], w['z2']))
                glVertex3f(w['x2'], w['yt'], w['z2']); glVertex3f(w['x1'], w['yt'], w['z1'])
            glEnd()
            
            glBegin(GL_LINES)
            for v in self.vines:
                glColor3f(*apply_fog_color((0.15, 0.02, 0.02), v[0], v[2]))
                glVertex3f(v[0], v[1], v[2])
                glVertex3f(v[3], v[4], v[5])
            glEnd()
            
            for chain in self.chains:
                glColor3f(*apply_fog_color((0.02, 0.02, 0.02), chain['x'], chain['z']))
                glPushMatrix()
                glTranslatef(chain['x'], wall_h, chain['z'])
                for i in range(chain['length']):
                    glTranslatef(0, -0.6, 0); glRotatef(90, 0, 1, 0)
                    glPushMatrix(); glScalef(0.1, 0.6, 0.05); dcube(1.0); glPopMatrix()
                    
                glTranslatef(0, -0.6, 0)
                if chain['length'] % 2 == 0:
                    glColor3f(*apply_fog_color((0.3, 0.3, 0.3), chain['x'], chain['z']))
                    glRotatef(-45, 0, 0, 1); dcyl(0.05, 0.01, 0.8)
                    glTranslatef(0, 0, 0.8); glRotatef(135, 0, 0, 1); dcyl(0.05, 0.01, 0.4)
                else:
                    glColor3f(*apply_fog_color((0.5, 0.0, 0.0), chain['x'], chain['z']))
                    dsph(0.4)
                    glTranslatef(0, -0.2, 0); dsph(0.2)
                glPopMatrix()

        elif self.room_level == 3:
            glColor3f(*apply_fog_color(self.theme['mortar'], 0, 0))
            glBegin(GL_LINES)
            for i in range(360):
                rad = math.radians(i); rad2 = math.radians(i+1)
                glVertex3f(math.cos(rad)*15, 0.1, math.sin(rad)*15)
                glVertex3f(math.cos(rad2)*15, 0.1, math.sin(rad2)*15)
                if i % 45 == 0:
                    glVertex3f(0, 0.1, 0); glVertex3f(math.cos(rad)*15, 0.1, math.sin(rad)*15)
            glEnd()

            for i in range(12):
                angle = math.radians(i * 30)
                px, pz = math.cos(angle)*35, math.sin(angle)*35
                glColor3f(*apply_fog_color((0.02, 0.02, 0.02), px, pz))
                glPushMatrix()
                glTranslatef(px, 10 + math.sin(time.time()+i)*5, pz)
                glScalef(2.0, 30.0, 2.0); dcube(1.0)
                glPopMatrix()

        for o in self.obstacles: o.draw()
        for obj in self.objects:
            if not obj.is_held: obj.draw_world()

    def update_objects(self, dt):
        for obj in self.objects: obj.update(dt)

    def pickup_object(self, px, pz):
        if self.held_object: return False
        n_obj, n_dist = None, 5.0
        for obj in self.objects:
            if obj.is_held or not obj.grounded: continue
            d = math.sqrt((obj.x - px) ** 2 + (obj.z - pz) ** 2)
            if d < n_dist: n_dist, n_obj = d, obj
        if n_obj:
            if n_obj.is_consumable:
                if state.hp < state.max_hp:
                    state.hp = min(state.max_hp, state.hp + 40)
                    spawn_heal_particles(state.player_x, state.player_y, state.player_z)
                    self.objects.remove(n_obj)
                    return True
                return False
            elif n_obj.is_gun:
                state.equip_weapon(n_obj.obj_type)
                self.objects.remove(n_obj)
                return True
            else:
                self.held_object, n_obj.is_held, n_obj.grounded = n_obj, True, True
                return True
        return False

    def throw_held_object(self, px, py, pz, yaw, pitch):
        if not self.held_object: return False
        self.held_object.throw_from_player(px, py, pz, yaw, pitch)
        self.held_object = None
        return True

class Enemies:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.vx = self.vy = self.vz = 0.0
        self.hp = self.max_hp = 80.0
        self.damage = 8.0 
        self.angle = 0.0
        self.last_attack_time = time.time()
        self.alive = True

    def get_blood_color(self, base_col):
        dmg_ratio = 1.0 - max(0.0, min(1.0, self.hp / self.max_hp))
        blood_red = (0.5, 0.0, 0.0)
        r = base_col[0] * (1 - dmg_ratio) + blood_red[0] * dmg_ratio
        g = base_col[1] * (1 - dmg_ratio) + blood_red[1] * dmg_ratio
        b = base_col[2] * (1 - dmg_ratio) + blood_red[2] * dmg_ratio
        return apply_fog_color((r, g, b), self.x, self.z)

    def spawn_fireball(self, speed):
        tx, ty, tz = state.player_x, state.player_y, state.player_z
        dx, dy, dz = tx - self.x, ty - self.y, tz - self.z
        d = max(math.sqrt(dx * dx + dy * dy + dz * dz), 0.0001)
        state.enemy_fireballs.append({
            'id': random.random() * 100, 'x': self.x, 'y': self.y + 0.8, 'z': self.z,
            'vx': (dx / d) * speed, 'vy': (dy / d) * speed, 'vz': (dz / d) * speed,
            'damage': self.damage, 'is_batarang': False
        })

    def draw_health_bar(self):
        if not self.alive: return
        glPushMatrix()
        glTranslatef(self.x, self.y + 2.0, self.z)
        bw, bh = 2.0, 0.2
        glColor3f(*apply_fog_color((0.8, 0.0, 0.0), self.x, self.z))
        glBegin(GL_QUADS)
        glVertex3f(-bw / 2, -bh / 2, 0); glVertex3f(bw / 2, -bh / 2, 0)
        glVertex3f(bw / 2, bh / 2, 0); glVertex3f(-bw / 2, bh / 2, 0)
        glEnd()
        hr = max(0.0, min(1.0, self.hp / self.max_hp))
        if hr > 0:
            glColor3f(*apply_fog_color((0.0, 0.8, 0.0), self.x, self.z))
            glBegin(GL_QUADS)
            glVertex3f(-bw / 2, -bh / 2, 0.01); glVertex3f(-bw / 2 + bw * hr, -bh / 2, 0.01)
            glVertex3f(-bw / 2 + bw * hr, bh / 2, 0.01); glVertex3f(-bw / 2, bh / 2, 0.01)
            glEnd()
        glPopMatrix()

class Zombie(Enemies):
    C_SKIN  = (0.15, 0.22, 0.15) 
    C_SHIRT = (0.10, 0.12, 0.14)
    C_PANTS = (0.08, 0.08, 0.10)
    C_SHOES = (0.03, 0.03, 0.03)

    def __init__(self, x, z):
        super().__init__(x, 1.2, z)
        self.walk_t = 0.0
        self.speed = 2.0 # Slightly slower base speed 

    def update(self, dt):
        if not self.alive: return
        self.walk_t += dt
        dx, dz = state.player_x - self.x, state.player_z - self.z
        dist = math.sqrt(dx * dx + dz * dz)
        if dist > 0.01:
            self.angle = math.degrees(math.atan2(dx, dz))
            self.vx, self.vz = (dx / dist) * self.speed, (dz / dist) * self.speed
        self.x += self.vx * dt; self.z += self.vz * dt
        
        if time.time() - self.last_attack_time > 4.0:
            self.spawn_fireball(8.0)
            self.last_attack_time = time.time()

        if dist < 1.5 and time.time() - self.last_attack_time > 1.0:
            state.take_damage(self.damage)
            self.last_attack_time = time.time()

    def draw(self):
        if not self.alive: return
        
        glPushMatrix()
        glTranslatef(self.x, 0.02, self.z)
        glColor3f(*apply_fog_color((0.01, 0.01, 0.01), self.x, self.z))
        glScalef(1.2, 0.01, 1.2)
        dcube(1.0)
        glPopMatrix()

        sp = self.vx ** 2 + self.vz ** 2
        wa = math.sin(self.walk_t * 8.0) * 25.0 if sp > 0.1 else 0.0

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z); glRotatef(self.angle, 0, 1, 0)
        glScalef(1.2, 1.2, 1.2)
        #foot
        for side, a in [(-1, wa), (1, -wa)]:
            glPushMatrix(); glTranslatef(side * 0.22, -0.05, 0); glRotatef(a * side, 1, 0, 0)
            glColor3f(*self.get_blood_color(self.C_PANTS)); dsph(0.15)
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.14, 0.13, 0.55); glPopMatrix()
            glPushMatrix(); glTranslatef(0, -0.30, 0); glScalef(0.28, 0.60, 0.28); dcube(1.0); glPopMatrix()
            glTranslatef(0, -0.60, 0)
            glColor3f(*self.get_blood_color(self.C_SHOES)); dsph(0.12)
            glPushMatrix(); glTranslatef(0, -0.06, 0.05); glScalef(0.26, 0.12, 0.36); dcube(1.0); glPopMatrix()
            glPopMatrix()
            
        glColor3f(*self.get_blood_color(self.C_SHIRT))
        glPushMatrix(); glTranslatef(0, 0.45, 0); glScalef(0.90, 0.90, 0.50); dcube(1.0); glPopMatrix()
        #hands 
        for side, a in [(-1, wa), (1, -wa)]:
            glPushMatrix(); glTranslatef(side * 0.60, 0.75, 0); glRotatef(-a * side * 0.5, 1, 0, 0)
            glColor3f(*self.get_blood_color(self.C_SHIRT)); dsph(0.16)
            glPushMatrix(); glTranslatef(0, -0.05, 0.20); glRotatef(-70, 1, 0, 0)
            glPushMatrix(); glScalef(0.22, 0.40, 0.22); dcube(1.0); glPopMatrix()
            glColor3f(*self.get_blood_color(self.C_SKIN))
            glTranslatef(0, 0, 0.45); dsph(0.12)
            glPushMatrix(); glScalef(0.20, 0.20, 0.40); dcube(1.0); glPopMatrix()
            glPopMatrix(); glPopMatrix()

        glPushMatrix(); glTranslatef(0, 1.55, 0)
        glColor3f(*self.get_blood_color(self.C_SKIN))
        glPushMatrix(); glScalef(0.70, 0.70, 0.70); dcube(1.0); glPopMatrix()
        
        glColor3f(1.0, 0.0, 0.0) 
        glPushMatrix(); glTranslatef(-0.15, 0.08, 0.36); glScalef(0.12, 0.10, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.08, 0.36); glScalef(0.12, 0.10, 0.02); dcube(1.0); glPopMatrix()
        glPopMatrix()

        glPopMatrix()

class Batman(Enemies):
    def __init__(self, x, z):
        super().__init__(x, 3.5, z)
        self.hp = self.max_hp = 70.0 
        self.fly_t = random.random() * 6.0

    def update(self, dt):
        if not self.alive: return
        self.fly_t += dt
        cx, cz, yaw = state.player_x, state.player_z, state.player_yaw
        fwd_x, fwd_z = math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
        right_x, right_z = -fwd_z, fwd_x
        
        target_x = cx + fwd_x * 8.0 + right_x * math.sin(self.fly_t * 1.2) * 4.0
        target_z = cz + fwd_z * 8.0 + right_z * math.sin(self.fly_t * 1.2) * 4.0
        
        self.x += (target_x - self.x) * dt * 2.5
        self.z += (target_z - self.z) * dt * 2.5
        self.y = 3.5 + math.sin(self.fly_t * 1.5) * 0.8
        self.angle = math.degrees(math.atan2(cx - self.x, cz - self.z))
        
        if time.time() - self.last_attack_time > 3.0:
            self.spawn_fireball(14.0) 
            self.last_attack_time = time.time()
            
    def spawn_fireball(self, speed):
        tx, ty, tz = state.player_x, state.player_y, state.player_z
        dx, dy, dz = tx - self.x, ty - self.y, tz - self.z
        d = max(math.sqrt(dx * dx + dy * dy + dz * dz), 0.0001)
        state.enemy_fireballs.append({
            'id': random.random() * 100, 'x': self.x, 'y': self.y + 0.8, 'z': self.z,
            'vx': (dx / d) * speed, 'vy': (dy / d) * speed, 'vz': (dz / d) * speed,
            'damage': self.damage, 'is_batarang': True
        })

    def draw(self):
        if not self.alive: return
        
        cb = self.get_blood_color((0.4, 0.4, 0.45)) 
        c_blk = self.get_blood_color((0.1, 0.1, 0.12)) 
        c_belt = self.get_blood_color((0.6, 0.5, 0.2)) 
        
        glPushMatrix()
        glTranslatef(self.x, 0.02, self.z)
        glColor3f(*apply_fog_color((0.01, 0.01, 0.01), self.x, self.z))
        glScalef(1.4, 0.01, 1.4)
        dcube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z); glRotatef(self.angle, 0, 1, 0)
        glRotatef(math.sin(self.fly_t * 2.0) * 10.0, 1, 0, 0) 
        glScalef(1.4, 1.4, 1.4)

        # Legs and boots
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.25, -0.8, 0)
            glColor3f(*cb)
            glPushMatrix(); glScalef(0.4, 0.8, 0.4); dcube(1.0); glPopMatrix()
            glTranslatef(0, -0.4, 0)
            glColor3f(*c_blk)
            glPushMatrix(); glTranslatef(0, -0.3, 0.05); glScalef(0.42, 0.6, 0.5); dcube(1.0); glPopMatrix() 
            glPopMatrix()

        glPushMatrix()
        glColor3f(*cb)
        glPushMatrix(); glScalef(0.9, 0.8, 0.5); dcube(1.0); glPopMatrix() 
        glColor3f(*c_blk)
        glPushMatrix(); glTranslatef(0, 0.1, 0.26); glScalef(0.5, 0.2, 0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(-0.25, 0.1, 0.26); glRotatef(45, 0,0,1); glScalef(0.1, 0.3, 0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.25, 0.1, 0.26); glRotatef(-45, 0,0,1); glScalef(0.1, 0.3, 0.05); dcube(1.0); glPopMatrix()
        glColor3f(*c_belt)
        glPushMatrix(); glTranslatef(0, -0.4, 0); glScalef(0.95, 0.15, 0.55); dcube(1.0); glPopMatrix()
        glPopMatrix()

        # Arms and forearm details
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.6, 0.2, 0)
            glRotatef(side * 10, 0, 0, 1) 
            glColor3f(*cb)
            glPushMatrix(); glTranslatef(0, -0.2, 0); glScalef(0.3, 0.6, 0.3); dcube(1.0); glPopMatrix()
            glColor3f(*c_blk)
            glPushMatrix(); glTranslatef(0, -0.7, 0); glScalef(0.32, 0.5, 0.32); dcube(1.0); glPopMatrix() 
            # Forearm spikes
            for sy in [-0.6, -0.75, -0.9]:
                glPushMatrix(); glTranslatef(side * 0.15, sy, -0.1); glRotatef(side * 90, 0, 1, 0); dcyl(0.04, 0.0, 0.2); glPopMatrix()
            glPopMatrix()

        glColor3f(*c_blk)
        cape_sway = math.sin(self.fly_t * 3.0) * 0.15
        glPushMatrix()
        glTranslatef(0, 0.4, -0.3)
        glRotatef(15 + cape_sway * 50, 1, 0, 0) 
        glPushMatrix(); glTranslatef(0, -1.0, 0); glScalef(1.2, 2.0, 0.05); dcube(1.0); glPopMatrix()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0.7, 0)
        glColor3f(*c_blk)
        glPushMatrix(); glScalef(0.5, 0.6, 0.5); dcube(1.0); glPopMatrix() 
        glColor3f(*self.get_blood_color((0.9, 0.8, 0.7)))
        glPushMatrix(); glTranslatef(0, -0.15, 0.26); glScalef(0.35, 0.25, 0.05); dcube(1.0); glPopMatrix()
        glColor3f(*c_blk)
        glPushMatrix(); glTranslatef(-0.15, 0.3, 0); glRotatef(-90, 1, 0, 0); dcyl(0.06, 0.0, 0.3, 4); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.3, 0); glRotatef(-90, 1, 0, 0); dcyl(0.06, 0.0, 0.3, 4); glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix(); glTranslatef(-0.12, 0.05, 0.26); glScalef(0.12, 0.05, 0.02); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.12, 0.05, 0.26); glScalef(0.12, 0.05, 0.02); dcube(1.0); glPopMatrix()
        glPopMatrix()

        glPopMatrix()

class Mahoraga:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, 0.0 
        self.vx = self.vy = self.vz = 0.0
        
        # Massive HP boost
        self.hp, self.max_hp, self.phase = 2000.0, 2000.0, 1 
        
        self.angle, self.last_attack_time = 0.0, time.time()
        self.walk_anim_time = 0.0

    def get_blood_color(self, base_col):
        dmg_ratio = 1.0 - max(0.0, min(1.0, self.hp / self.max_hp))
        blood_red = (0.5, 0.0, 0.0)
        r = base_col[0] * (1 - dmg_ratio) + blood_red[0] * dmg_ratio
        g = base_col[1] * (1 - dmg_ratio) + blood_red[1] * dmg_ratio
        b = base_col[2] * (1 - dmg_ratio) + blood_red[2] * dmg_ratio
        return apply_fog_color((r, g, b), self.x, self.z)

    def draw(self):
        if self.phase >= 4: return
        
        cb = self.get_blood_color((0.85, 0.85, 0.85))
        c_skirt = self.get_blood_color((0.15, 0.15, 0.18))
        c_gold = apply_fog_color((0.80, 0.65, 0.20), self.x, self.z)
        
        glPushMatrix()
        glTranslatef(self.x, 0.02, self.z)
        glColor3f(*apply_fog_color((0.01, 0.01, 0.01), self.x, self.z))
        glScalef(3.0, 0.01, 3.0)
        dcube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.x, self.y + 1.6, self.z) 
        glRotatef(self.angle, 0, 1, 0)
        glScalef(1.6, 1.6, 1.6)
        
        wa = math.sin(self.walk_anim_time * (10.0 if self.phase < 3 else 15.0)) * 20.0
        
        # Legs
        for side, a in [(-1, wa), (1, -wa)]:
            glPushMatrix()
            glTranslatef(side * 0.35, -0.1, 0) 
            glRotatef(a, 1, 0, 0) 
            glColor3f(*cb)
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.18, 0.15, 0.6); glPopMatrix() 
            glTranslatef(0, -0.6, 0); dsph(0.18) 
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.15, 0.12, 0.6); glPopMatrix() 
            glTranslatef(0, -0.6, 0)
            glColor3f(*c_gold)
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.14, 0.14, 0.1); glPopMatrix() 
            glColor3f(*cb)
            glPushMatrix(); glTranslatef(0, -0.1, 0.1); glScalef(0.3, 0.2, 0.4); dcube(1.0); glPopMatrix() 
            glPopMatrix()

        glPushMatrix()
        glColor3f(*c_skirt)
        glPushMatrix(); glScalef(1.0, 0.6, 0.8); dcube(1.0); glPopMatrix()
        # Skirt panels (front/back)
        for i in [-0.4, 0, 0.4]:
            glPushMatrix(); glTranslatef(i, -0.4, 0.42); glRotatef(-10, 1, 0, 0); glScalef(0.35, 0.7, 0.05); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(i, -0.4, -0.42); glRotatef(10, 1, 0, 0); glScalef(0.35, 0.7, 0.05); dcube(1.0); glPopMatrix()
        glColor3f(*c_gold)
        glPushMatrix(); glTranslatef(0, 0.2, 0); glRotatef(90, 1, 0, 0); dcyl(0.55, 0.55, 0.15); glPopMatrix()
        glTranslatef(0, 0.1, 0.55); dsph(0.1)
        glPopMatrix()

        glColor3f(*cb)
        glPushMatrix()
        glTranslatef(0, 0.7, 0)
        glPushMatrix(); glTranslatef(0, -0.3, 0.05); glScalef(0.6, 0.6, 0.5); dcube(1.0); glPopMatrix() 
        glPushMatrix(); glTranslatef(0, 0.2, 0); glScalef(1.2, 0.6, 0.6); dcube(1.0); glPopMatrix() 
        glColor3f(*self.get_blood_color((0.1, 0.1, 0.1)))
        glPushMatrix()
        glTranslatef(0, 0.3, 0.32); dsph(0.08)
        # Chest studs
        for i in [-0.15, 0.15, -0.3, 0.3]:
            glPushMatrix(); glTranslatef(i, 0.05, -abs(i)*0.2); dsph(0.06); glPopMatrix()
        glPopMatrix()

        # Arms
        for side, a in [(-1, wa), (1, -wa)]:
            glPushMatrix()
            glTranslatef(side * 0.7, 0.3, 0) 
            glRotatef(-a * 0.8, 1, 0, 0) 
            glRotatef(side * 15, 0, 0, 1) 
            glColor3f(*cb)
            dsph(0.2) 
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.15, 0.12, 0.6); glPopMatrix() 
            glTranslatef(0, -0.6, 0); dsph(0.15) 
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.12, 0.1, 0.5); glPopMatrix() 
            glTranslatef(0, -0.5, 0)
            glColor3f(*c_gold)
            glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.12, 0.12, 0.1); glPopMatrix() 
            glColor3f(*cb)
            glPushMatrix(); glTranslatef(0, -0.15, 0); glScalef(0.2, 0.3, 0.2); dcube(1.0); glPopMatrix() 
            glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0.6, 0)
        glColor3f(*cb)
        glPushMatrix(); glRotatef(90, 1, 0, 0); dcyl(0.15, 0.15, 0.3); glPopMatrix() 
        glTranslatef(0, 0.3, 0.1) 
        dsph(0.35) 
        glColor3f(1.0, 0.0, 0.0) 
        glPushMatrix(); glTranslatef(-0.15, 0.1, 0.3); glScalef(0.1, 0.05, 0.05); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.15, 0.1, 0.3); glScalef(0.1, 0.05, 0.05); dcube(1.0); glPopMatrix()
        glColor3f(0.2, 0.2, 0.2) 
        glPushMatrix(); glTranslatef(0, -0.15, 0.32); glScalef(0.25, 0.05, 0.05); dcube(1.0); glPopMatrix()
        glColor3f(*cb)
        # Head spikes
        for ang in [20, -20, 60, -60]:
            glPushMatrix()
            glRotatef(ang, 0, 0, 1) 
            glRotatef(90, 0, 1, 0) 
            glRotatef(-15, 0, 1, 0) 
            glTranslatef(0, 0, 0.2)
            dcyl(0.12, 0.0, 1.0) 
            glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -0.2, -0.3)
        # Neck/helmet ring segments
        for t in range(6):
            glRotatef(15, 1, 0, 0) 
            dcyl(0.15 - t*0.02, 0.15 - (t+1)*0.02, 0.4)
            glTranslatef(0, 0, 0.4)
        glPopMatrix()
        glPopMatrix() 

        glPushMatrix()
        glTranslatef(0, 1.8, -0.8) 
        glRotatef(self.walk_anim_time * (50.0 * self.phase), 0, 0, 1) 
        glColor3f(*c_gold)
        dsph(0.15) 
        glPushMatrix(); glTranslatef(0, 0, -0.05); dcyl(1.0, 1.0, 0.1, 16); glPopMatrix() 
        # Halo spokes
        for i in range(8):
            glPushMatrix()
            glRotatef(i * 45, 0, 0, 1)
            glRotatef(90, 0, 1, 0)
            dcyl(0.04, 0.04, 1.0) 
            glTranslatef(0, 0, 1.0)
            dsph(0.12) 
            glPopMatrix()
        glPopMatrix() 
        
        glPopMatrix() 
        glPopMatrix() 

    def draw_health_bar(self):
        if self.phase >= 4: return
        glPushMatrix(); glTranslatef(self.x, self.y + 7.5, self.z)
        bw, bh = 4.0, 0.4
        glColor3f(*apply_fog_color((0.8, 0.0, 0.0), self.x, self.z))
        glBegin(GL_QUADS)
        glVertex3f(-bw / 2, -bh / 2, 0); glVertex3f(bw / 2, -bh / 2, 0)
        glVertex3f(bw / 2, bh / 2, 0); glVertex3f(-bw / 2, bh / 2, 0)
        glEnd()
        hr = max(0.0, min(1.0, self.hp / self.max_hp))
        if hr > 0:
            glColor3f(*apply_fog_color((0.0, 0.8, 0.0), self.x, self.z))
            glBegin(GL_QUADS)
            glVertex3f(-bw / 2, -bh / 2, 0.01); glVertex3f(-bw / 2 + bw * hr, -bh / 2, 0.01)
            glVertex3f(-bw / 2 + bw * hr, bh / 2, 0.01); glVertex3f(-bw / 2, bh / 2, 0.01)
            glEnd()
        glPopMatrix()

    def spawn_fireball(self, spread_offset=0.0):
        speed = 12.0 + (self.phase * 3.0)
        tx, ty, tz = state.player_x, state.player_y, state.player_z
        
        dx, dy, dz = tx - self.x, ty - (self.y + 3.0), tz - self.z
        
        if spread_offset != 0:
            yaw = math.atan2(dx, dz) + math.radians(spread_offset)
            dist_xz = math.sqrt(dx*dx + dz*dz)
            dx = math.sin(yaw) * dist_xz
            dz = math.cos(yaw) * dist_xz
            
        d = max(math.sqrt(dx * dx + dy * dy + dz * dz), 0.0001)
        state.fireballs.append({
            'id': random.random() * 100, 'x': self.x, 'y': self.y + 3.0, 'z': self.z,
            'vx': (dx / d) * speed, 'vy': (dy / d) * speed, 'vz': (dz / d) * speed,
            'damage': 15.0 + (self.phase * 5.0) 
        })

    def update(self, dt):
        if self.phase >= 4: return
        self.walk_anim_time += dt
        
        # Shifted Phase triggers for 6000 HP pool
        if self.hp < 2000: self.phase = 3
        elif self.hp < 4000: self.phase = 2

        dx, dz = state.player_x - self.x, state.player_z - self.z
        dist = max(math.sqrt(dx * dx + dz * dz), 0.01)
        self.angle = math.degrees(math.atan2(dx, dz))
        
        speed = 2.0 + (self.phase * 1.0)
        self.vx, self.vz = (dx / dist) * speed, (dz / dist) * speed
        self.x += self.vx * dt; self.z += self.vz * dt
        
        attack_rate = max(1.0, 2.5 - (self.phase * 0.5))
        if time.time() - self.last_attack_time > attack_rate:
            self.spawn_fireball()
            if self.phase == 3: 
                self.spawn_fireball(spread_offset=15.0)
                self.spawn_fireball(spread_offset=-15.0)
            
            summon_chance = 0.25 + (0.15 * self.phase)
            max_minions = 1 + self.phase
            
            if random.random() < summon_chance and len(state.enemies) < max_minions:
                ex = max(-18, min(18, self.x + random.uniform(-6, 6)))
                ez = max(-28, min(28, self.z + random.uniform(-6, 6)))
                
                if self.phase == 3 and random.random() > 0.5:
                    minion = Batman(ex, ez)
                else:
                    minion = Zombie(ex, ez)
                    minion.speed = 2.5 + (self.phase * 0.5) 
                    
                minion.max_hp = 50.0
                minion.hp = minion.max_hp
                state.enemies.append(minion)

            self.last_attack_time = time.time()

class GameState:
    def __init__(self):
        self.last_time = time.time()
        self.quadric = None
        self.init_all()

    def init_all(self):
        self.hp, self.max_hp = 100.0, 100.0
        self.invulnerable_timer = 0.0 
        self.current_weapon = "HANDGUN"
        self.ammo = WEAPONS[self.current_weapon]["max_ammo"]
        self.max_ammo = WEAPONS[self.current_weapon]["max_ammo"]
        self.is_reloading, self.reload_timer = False, 0.0
        self.recoil_offset, self.shoot_cooldown = 0.0, 0.0
        self.screen_shake, self.damage_flash, self.hit_marker = 0.0, 0.0, 0.0
        self.dash_cooldown, self.is_dashing, self.dash_timer = 0.0, False, 0.0
        self.dash_dir_x, self.dash_dir_z = 0.0, 0.0
        self.melee_timer, self.melee_cooldown = 0.0, 0.0
        self.room, self.room_cleared, self.game_over, self.game_won = 1, False, False, False
        self.wave, self.max_waves_current, self.wave_timer = 1, 2, 3.0
        self.enemies_to_spawn, self.spawn_timer = 0, 0.0
        self.keys = {}
        self.fireballs, self.particles, self.player_fireballs, self.enemy_fireballs = [], [], [], []
        self.ambient_dust, self.enemies = [], []
        self.boss = Mahoraga()
        self.environment = Environment(self.room)
        self.player_x, self.player_y, self.player_z = 0.0, 1.6, self.environment.depth / 2 - 5
        self.player_yaw, self.player_pitch = 0.0, 0.0
        self.init_dust()
        
    def take_damage(self, amount):
        if self.invulnerable_timer <= 0:
            self.hp -= amount
            self.screen_shake = 2.0 
            self.damage_flash = 1.0
            self.invulnerable_timer = 1.0  
            spawn_blood_explosion(self.player_x, self.player_y, self.player_z)

    def equip_weapon(self, wep_type):
        self.current_weapon = wep_type.upper()
        self.max_ammo = WEAPONS[self.current_weapon]["max_ammo"]
        self.ammo = self.max_ammo
        self.is_reloading = False
        
    def init_dust(self):
        self.ambient_dust = [{'x': random.uniform(-self.environment.width/2, self.environment.width/2), 
                              'y': random.uniform(0, 20), 
                              'z': random.uniform(-self.environment.depth/2, self.environment.depth/2),
                              'vy': random.uniform(0.5, 2.0),
                              'c': random.choice([(0.5, 0.2, 0.2), (0.2, 0.2, 0.2)])} 
                             for _ in range(150 + self.environment.width * 2)]

    def load_room(self, room_num):
        self.room = room_num
        self.environment = Environment(room_num)
        self.player_x, self.player_y, self.player_z = 0.0, 1.6, self.environment.depth / 2 - 5
        self.player_yaw, self.player_pitch = 0.0, 0.0
        self.enemies.clear()
        self.enemy_fireballs.clear()
        self.player_fireballs.clear()
        self.fireballs.clear()
        self.particles.clear()
        self.room_cleared = False
        self.wave = 1
        self.init_dust()
        
        # Reduced initial enemy spawn counts
        if room_num == 1: self.max_waves_current, self.enemies_to_spawn = 3, 2
        elif room_num == 2: self.max_waves_current, self.enemies_to_spawn = 3, 3
        elif room_num == 3:
            self.max_waves_current, self.enemies_to_spawn = 1, 0
            self.boss = Mahoraga() 

    def restart_game(self):
        self.init_all()
        if self.room == 1: self.load_room(1)
            
    def trigger_attack(self):
        if self.game_over or self.game_won or self.room_cleared: return
        if self.environment.held_object:
            if self.melee_cooldown <= 0:
                self.melee_timer, self.melee_cooldown = 0.25, 0.5
                self.perform_melee()
        else:
            if not self.is_reloading and self.ammo > 0 and self.shoot_cooldown <= 0:
                self.spawn_player_fireball()
                self.shoot_cooldown = WEAPONS[self.current_weapon]["cooldown"]
                
    def perform_melee(self):
        wep_damage = self.environment.held_object.damage
        fx = math.sin(math.radians(self.player_yaw)) * math.cos(math.radians(self.player_pitch))
        fz = -math.cos(math.radians(self.player_yaw)) * math.cos(math.radians(self.player_pitch))
        hit_x, hit_z = self.player_x + fx * 2.5, self.player_z + fz * 2.5
        
        # Boss Melee Hitbox Shrink
        if self.room == 3 and not self.game_won and math.sqrt((hit_x-self.boss.x)**2 + (hit_z-self.boss.z)**2) < 3.0:
            self.boss.hp = max(0, self.boss.hp - wep_damage)
            spawn_blood_explosion(hit_x, self.player_y, hit_z)
            self.hit_marker = 1.0
            
        for e in self.enemies:
            if not e.alive: continue
            if math.sqrt((hit_x - e.x)**2 + (hit_z - e.z)**2) < 3.5:
                e.hp = max(0, e.hp - wep_damage)
                e.x += fx * 0.2; e.z += fz * 0.2
                self.hit_marker = 1.0
                spawn_blood_explosion(e.x, e.y+1.0, e.z)
                if e.hp <= 0: e.alive = False

    def spawn_player_fireball(self):
        self.ammo -= 1
        self.recoil_offset += 4.0
        self.player_pitch += 4.0
        self.screen_shake += 0.15 
        
        wep = WEAPONS[self.current_weapon]
        base_vx = math.sin(math.radians(self.player_yaw)) * math.cos(math.radians(self.player_pitch))
        base_vy = math.sin(math.radians(self.player_pitch))
        base_vz = -math.cos(math.radians(self.player_yaw)) * math.cos(math.radians(self.player_pitch))
        
        for _ in range(wep["pellets"]):
            vx, vy, vz = base_vx + random.uniform(-wep["spread"], wep["spread"]), base_vy + random.uniform(-wep["spread"], wep["spread"]), base_vz + random.uniform(-wep["spread"], wep["spread"])
            self.player_fireballs.append({
                'x': self.player_x + vx, 'y': self.player_y + vy, 'z': self.player_z + vz,
                'vx': vx * 40.0, 'vy': vy * 40.0, 'vz': vz * 40.0,
                'damage': wep["damage"], 'color': wep["color"]
            })

state = GameState()

def init():
    state.quadric = gluNewQuadric()
    glEnable(GL_DEPTH_TEST) 

def dcube(s): glutSolidCube(s)
def dcyl(b, t, h, sl=10, st=4): gluCylinder(state.quadric, b, t, h, sl, st)
def dsph(r, sl=10, st=10): gluSphere(state.quadric, r, sl, st)

def draw_fireballs():
    for fb in state.player_fireballs:
        glPushMatrix(); glTranslatef(fb['x'], fb['y'], fb['z'])
        glColor3f(*apply_fog_color(fb['color'], fb['x'], fb['z'])); dsph(0.2, 8, 8); glPopMatrix()
        
    for fb in state.enemy_fireballs + state.fireballs:
        glPushMatrix(); glTranslatef(fb['x'], fb['y'], fb['z'])
        if fb.get('is_batarang', False):
            rot = (time.time() * 800) % 360
            glRotatef(rot, 0, 1, 0)
            glColor3f(*apply_fog_color((0.2, 0.2, 0.25), fb['x'], fb['z']))
            glPushMatrix(); glScalef(0.7, 0.05, 0.15); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(0.3, 0, 0.1); glRotatef(30, 0, 1, 0); glScalef(0.3, 0.05, 0.1); dcube(1.0); glPopMatrix()
            glPushMatrix(); glTranslatef(-0.3, 0, 0.1); glRotatef(-30, 0, 1, 0); glScalef(0.3, 0.05, 0.1); dcube(1.0); glPopMatrix()
            glColor3f(1.0, 0.0, 0.0) 
            glPushMatrix(); glScalef(0.1, 0.06, 0.16); dcube(1.0); glPopMatrix()
        else:
            glColor3f(*apply_fog_color(ENEMY_FB_OUTER, fb['x'], fb['z'])); dsph(0.35, 12, 12)
        glPopMatrix()

def draw_particles():
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for d in state.ambient_dust:
        glColor3f(*apply_fog_color(d['c'], d['x'], d['z']))
        glVertex3f(d['x'], d['y'], d['z'])
    glEnd()

    if state.particles:
        glPointSize(6.0)
        glBegin(GL_POINTS)
        for p in state.particles:
            glColor3f(*apply_fog_color((p.get('r', 0.8), p.get('g', 0.1), p.get('b', 0.1)), p['x'], p['z'])) 
            glVertex3f(p['x'], p['y'], p['z'])
        glEnd()

def draw_crosshair():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    is_moving = any(state.keys.get(k) for k in ('w', 'a', 's', 'd'))
    wep_spread = WEAPONS[state.current_weapon]["spread"] * 300.0
    offset = 10 + state.recoil_offset * 3.0 + (6.0 if is_moving else 0.0) + wep_spread
    
    cx, cy = W_WIDTH//2, W_HEIGHT//2
    
    glColor3f(0.8, 0.2, 0.2)
    glBegin(GL_LINES)
    glVertex3f(cx - offset - 8, cy, 0); glVertex3f(cx - offset, cy, 0)
    glVertex3f(cx + offset, cy, 0); glVertex3f(cx + offset + 8, cy, 0)
    glVertex3f(cx, cy - offset - 8, 0); glVertex3f(cx, cy - offset, 0)
    glVertex3f(cx, cy + offset, 0); glVertex3f(cx, cy + offset + 8, 0)
    glEnd()
    
    if state.hit_marker > 0:
        glColor3f(1.0, 1.0, 1.0) 
        s = 6
        glBegin(GL_LINES)
        glVertex3f(cx - s, cy - s, 0); glVertex3f(cx + s, cy + s, 0)
        glVertex3f(cx - s, cy + s, 0); glVertex3f(cx + s, cy - s, 0)
        glEnd()
        
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_ui():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    if state.game_over:
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(W_WIDTH//2 - 60, W_HEIGHT//2)
        for c in "GAME OVER": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        glColor3f(0.9, 0.9, 0.9) 
        glRasterPos2f(W_WIDTH//2 - 90, W_HEIGHT//2 - 30)
        for c in "PRESS ENTER TO RESTART": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    elif state.game_won:
        glColor3f(1.0, 0.8, 0.0)
        glRasterPos2f(W_WIDTH//2 - 60, W_HEIGHT//2)
        for c in "YOU SURVIVED!": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        glColor3f(0.9, 0.9, 0.9)
        glRasterPos2f(W_WIDTH//2 - 90, W_HEIGHT//2 - 30)
        for c in "PRESS ENTER TO RESTART": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    elif state.room_cleared:
        glColor3f(0.0, 1.0, 0.0)
        glRasterPos2f(W_WIDTH//2 - 120, W_HEIGHT//2)
        for c in "ROOM CLEARED - PRESS ENTER": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Health Bar Background 
    glColor3f(0.3, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(10, 10, -0.5); glVertex3f(210, 10, -0.5)
    glVertex3f(210, 25, -0.5); glVertex3f(10, 25, -0.5)
    glEnd()
    
    # Health Bar Foreground
    hp_ratio = max(0.0, state.hp / state.max_hp)
    glColor3f(0.1, 0.8, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(10, 10, 0.5); glVertex3f(10 + 200 * hp_ratio, 10, 0.5)
    glVertex3f(10 + 200 * hp_ratio, 25, 0.5); glVertex3f(10, 25, 0.5)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    hp_txt = f"HP: {int(max(0, state.hp))} / {int(state.max_hp)}"
    glRasterPos2f(15, 13)
    for c in hp_txt: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    if state.ammo == 0 and not state.is_reloading:
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(W_WIDTH//2 - 40, W_HEIGHT//2 - 50)
        for c in "RELOAD! (R)": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    glColor3f(0.9, 0.9, 0.9)
    if state.environment.held_object:
        ammo_txt = f"HELD: {state.environment.held_object.obj_type.upper()} | L-CLICK: MELEE | R-CLICK: THROW"
    else:
        ammo_txt = f"{state.current_weapon}: {state.ammo}/{state.max_ammo} {'[RELOADING]' if state.is_reloading else ''}"
        
    room_txt = f"Room: {state.room}/3 | Wave: {state.wave}/{state.max_waves_current} | Enemies left: {len(state.enemies) + state.enemies_to_spawn}"
    
    glRasterPos2f(10, 40)
    for c in ammo_txt: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glRasterPos2f(10, W_HEIGHT-30)
    for c in room_txt: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    
    if hp_ratio < 0.5 or state.damage_flash > 0:
        intensity = state.damage_flash if state.damage_flash > 0 else (0.5 - hp_ratio) * 2
        glColor3f(0.8 * intensity, 0.0, 0.0)
        glBegin(GL_LINES)
        for i in range(1, 15):
            if intensity > i * 0.05:
                glVertex3f(i*5, i*5, 0); glVertex3f(W_WIDTH-i*5, i*5, 0)
                glVertex3f(i*5, W_HEIGHT-i*5, 0); glVertex3f(W_WIDTH-i*5, W_HEIGHT-i*5, 0)
                glVertex3f(i*5, i*5, 0); glVertex3f(i*5, W_HEIGHT-i*5, 0)
                glVertex3f(W_WIDTH-i*5, i*5, 0); glVertex3f(W_WIDTH-i*5, W_HEIGHT-i*5, 0)
        glEnd()
    
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def spawn_blood_explosion(x, y, z):
    state.particles.extend([
        {'x': x + random.uniform(-0.4, 0.4), 'y': y + random.uniform(-0.4, 0.4), 'z': z + random.uniform(-0.4, 0.4), 
         'vy': random.uniform(2, 6), 'vx': random.uniform(-4, 4), 'vz': random.uniform(-4, 4),
         'life': random.uniform(3.0, 7.0), 'r': random.uniform(0.4, 0.8), 'g': 0.0, 'b': 0.0, 'is_blood': True}
        for _ in range(35)
    ])

def spawn_heal_particles(x, y, z):
    state.particles.extend([
        {'x': x, 'y': y, 'z': z, 'vy': random.uniform(2, 5), 'vx': random.uniform(-2, 2), 'vz': random.uniform(-2, 2),
         'life': random.uniform(0.5, 1.0), 'r': 0.1, 'g': 1.0, 'b': 0.1}
        for _ in range(20)
    ])

def spawn_wall_hit_particles(x, y, z):
    state.particles.extend([
        {'x': x, 'y': y, 'z': z, 'vy': random.uniform(-1, 3), 'vx': random.uniform(-2, 2), 'vz': random.uniform(-2, 2),
         'life': random.uniform(0.2, 0.5), 'r': 0.4, 'g': 0.4, 'b': 0.4}
        for _ in range(10)
    ])

def update_player(dt):
    if state.game_over: return
    
    if state.melee_cooldown > 0: state.melee_cooldown -= dt
    if state.shoot_cooldown > 0: state.shoot_cooldown -= dt
    if state.melee_timer > 0: state.melee_timer -= dt
    if state.invulnerable_timer > 0: state.invulnerable_timer -= dt
    
    state.screen_shake = max(0.0, state.screen_shake - dt * 5.0)
    state.damage_flash = max(0.0, state.damage_flash - dt * 2.0)
    state.hit_marker = max(0.0, state.hit_marker - dt * 4.0)

    if state.is_reloading:
        state.reload_timer -= dt
        if state.reload_timer <= 0:
            state.ammo, state.is_reloading = state.max_ammo, False

    if state.dash_cooldown > 0: state.dash_cooldown -= dt

    fwd_x, fwd_z = math.sin(math.radians(state.player_yaw)), -math.cos(math.radians(state.player_yaw))
    right_x, right_z = -fwd_z, fwd_x

    if state.is_dashing:
        state.dash_timer -= dt
        state.player_x += state.dash_dir_x * PLAYER_SPEED * 3.5 * dt
        state.player_z += state.dash_dir_z * PLAYER_SPEED * 3.5 * dt
        if state.dash_timer <= 0: state.is_dashing = False
    elif not state.room_cleared and not state.game_won:
        mx, mz = 0.0, 0.0
        if state.keys.get('w'): mx += fwd_x; mz += fwd_z
        if state.keys.get('s'): mx -= fwd_x; mz -= fwd_z
        if state.keys.get('a'): mx -= right_x; mz -= right_z
        if state.keys.get('d'): mx += right_x; mz += right_z
        ln = math.sqrt(mx*mx + mz*mz)
        if ln > 0:
            state.player_x += (mx / ln) * PLAYER_SPEED * dt
            state.player_z += (mz / ln) * PLAYER_SPEED * dt

    state.player_x, state.player_z = resolve_obstacle_collision(state.player_x, state.player_z)

    if state.keys.get('left'): state.player_yaw -= 65.0 * dt
    if state.keys.get('right'): state.player_yaw += 65.0 * dt
    if state.keys.get('up'): state.player_pitch += 45.0 * dt
    if state.keys.get('down'): state.player_pitch -= 45.0 * dt

    if state.recoil_offset > 0:
        recovery = 15.0 * dt
        state.recoil_offset = max(0, state.recoil_offset - recovery)
        state.player_pitch -= recovery

    state.player_pitch = max(-60.0, min(60.0, state.player_pitch))
    hw, hd = state.environment.width / 2 - 2, state.environment.depth / 2 - 2
    state.player_x = max(-hw, min(hw, state.player_x))
    state.player_z = max(-hd, min(hd, state.player_z))

    if state.hp <= 0: state.game_over = True

def update(dt):
    if state.game_over: return

    update_player(dt)
    state.environment.update_objects(dt)
    
    # Boss Cinematic Death Logic
    if state.room == 3 and not state.game_won:
        state.boss.update(dt)
        if state.boss.hp <= 0: 
            state.game_won = True
            state.boss.phase = 4 
            # Epic explosion sequence
            for _ in range(10):
                spawn_blood_explosion(state.boss.x + random.uniform(-2, 2), state.boss.y + random.uniform(0, 4), state.boss.z + random.uniform(-2, 2))
            # Delete remaining minions and fireballs immediately
            state.enemies.clear()
            state.enemy_fireballs.clear()
            state.fireballs.clear()
            
    for p in state.particles: 
        if p.get('is_blood', False):
            if p['y'] > 0.02: 
                p['vy'] -= 15.0 * dt 
                p['y'] += p['vy'] * dt
                p['x'] += p.get('vx', 0) * dt
                p['z'] += p.get('vz', 0) * dt
            else:
                p['y'], p['vx'], p['vz'] = 0.02, 0, 0
            p['life'] -= dt
        else:
            p['y'] += p['vy']*dt
            p['x'] += p.get('vx', 0)*dt
            p['z'] += p.get('vz', 0)*dt
            p['life'] -= dt
            
    state.particles = [p for p in state.particles if p['life'] > 0]
    
    for d in state.ambient_dust:
        d['y'] += d['vy'] * dt
        if d['y'] > 20: d['y'] = 0

    for obj in state.environment.objects:
        if obj.is_thrown:
            # Thrown Hitbox Shrink
            if state.room == 3 and not state.game_won and math.sqrt((obj.x-state.boss.x)**2 + (obj.z-state.boss.z)**2) < 3.0:
                state.boss.hp = max(0, state.boss.hp - obj.damage)
                obj.is_thrown, obj.grounded = False, True
                spawn_blood_explosion(obj.x, obj.y, obj.z)
                state.hit_marker = 1.0
            
            for e in state.enemies:
                if not e.alive: continue
                if math.sqrt((obj.x - e.x)**2 + (obj.z - e.z)**2) < 3.5: 
                    e.hp = max(0, e.hp - obj.damage) 
                    e.x += obj.velocity_x * 0.1; e.z += obj.velocity_z * 0.1
                    obj.is_thrown, obj.grounded = False, True
                    spawn_blood_explosion(e.x, e.y+1.0, e.z)
                    state.hit_marker = 1.0
                    if e.hp <= 0: e.alive = False
                    break

    if state.room < 3 and not state.room_cleared:
        if not state.enemies and state.enemies_to_spawn <= 0:
            if state.wave < state.max_waves_current:
                state.wave_timer -= dt
                if state.wave_timer <= 0:
                    state.wave += 1
                    # Scaled down wave increments
                    state.enemies_to_spawn = (2 + state.wave) if state.room == 1 else (3 + state.wave)
                    state.wave_timer = 4.0
            else:
                state.room_cleared = True

    if state.enemies_to_spawn > 0:
        state.spawn_timer -= dt
        if state.spawn_timer <= 0:
            hw, hd = state.environment.width / 2 - 5, state.environment.depth / 2 - 5
            ex, ez = random.uniform(-hw, hw), random.uniform(-hd, -hd + 15) 
            e = Zombie(ex, ez) if random.random() > 0.4 or state.room == 1 else Batman(ex, ez)
            
            # Nerfed health and damage multipliers
            hp_mult = 1.0 + (state.room * 0.1) + (state.wave * 0.05)
            e.max_hp = 80 * hp_mult; e.hp = e.max_hp; e.damage = 6 * hp_mult
            
            if isinstance(e, Zombie): e.speed = 2.0 + (state.room * 0.15) + (state.wave * 0.05)
            
            state.enemies.append(e)
            state.enemies_to_spawn -= 1
            state.spawn_timer = max(0.5, 2.0 - state.wave * 0.3)

    for i in range(len(state.enemies)):
        e1 = state.enemies[i]
        if not e1.alive: continue
        e1.update(dt)
        e1.x, e1.z = resolve_obstacle_collision(e1.x, e1.z, radius=0.8)
        sep_x, sep_z = 0.0, 0.0
        for j in range(len(state.enemies)):
            if i == j: continue
            e2 = state.enemies[j]
            if not e2.alive: continue
            dist = math.sqrt((e1.x - e2.x)**2 + (e1.z - e2.z)**2)
            if 0 < dist < 2.5:
                sep_x += (e1.x - e2.x) / dist; sep_z += (e1.z - e2.z) / dist
        e1.x += sep_x * dt * 2.0; e1.z += sep_z * dt * 2.0

    for fb in state.player_fireballs:
        fb['x'] += fb['vx']*dt; fb['y'] += fb['vy']*dt; fb['z'] += fb['vz']*dt
        hit = False
        if check_obstacle_hit(fb['x'], fb['y'], fb['z']):
            spawn_wall_hit_particles(fb['x'], fb['y'], fb['z']); fb['y'] = -100; continue
            
        # Shrunk hit radius from 4.5 to 3.0 and adjusted headshot multiplier
        if state.room == 3 and state.boss.phase < 4 and math.sqrt((fb['x']-state.boss.x)**2 + (fb['y']-state.boss.y)**2 + (fb['z']-state.boss.z)**2) < 3.0:
            damage = fb['damage'] * 1.5 if fb['y'] > state.boss.y + 2.5 else fb['damage']
            state.boss.hp = max(0, state.boss.hp - damage)
            spawn_blood_explosion(fb['x'], fb['y'], fb['z'])
            state.hit_marker = 1.0; fb['y'] = -100; hit = True

        if not hit:
            for e in state.enemies:
                if not e.alive: continue
                if math.sqrt((fb['x'] - e.x)**2 + (fb['y'] - e.y)**2 + (fb['z'] - e.z)**2) < 2.0:
                    damage = fb['damage'] * 2 if fb['y'] > e.y + 1.0 else fb['damage']
                    e.hp = max(0, e.hp - damage)
                    e.x += fb['vx'] * 0.02; e.z += fb['vz'] * 0.02
                    spawn_blood_explosion(fb['x'], fb['y'], fb['z'])
                    state.hit_marker = 1.0
                    if e.hp <= 0: e.alive = False
                    fb['y'] = -100; break

    state.player_fireballs = [fb for fb in state.player_fireballs if fb['y'] > -5 and abs(fb['x']) < 90 and abs(fb['z']) < 90]
    
    for fb in state.enemy_fireballs + state.fireballs:
        fb['x'] += fb['vx'] * dt; fb['y'] += fb['vy'] * dt; fb['z'] += fb['vz'] * dt
        if check_obstacle_hit(fb['x'], fb['y'], fb['z']):
            spawn_wall_hit_particles(fb['x'], fb['y'], fb['z']); fb['y'] = -100; continue
            
        dist_to_player = math.sqrt((fb['x'] - state.player_x)**2 + (fb['y'] - state.player_y)**2 + (fb['z'] - state.player_z)**2)
        if dist_to_player < 1.5:
            state.take_damage(fb.get('damage', 20.0))
            fb['y'] = -100

    state.enemy_fireballs = [fb for fb in state.enemy_fireballs if fb['y'] > -5 and abs(fb['x']) < 90 and abs(fb['z']) < 90]
    state.enemies = [e for e in state.enemies if e.alive]

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    sx = random.uniform(-state.screen_shake, state.screen_shake) * 0.5
    sy = random.uniform(-state.screen_shake, state.screen_shake) * 0.5
    sz = random.uniform(-state.screen_shake, state.screen_shake) * 0.5
    
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(60.0, W_WIDTH/W_HEIGHT, 0.1, 200.0)
    
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    lx = state.player_x + math.sin(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * 10.0
    ly = state.player_y + math.sin(math.radians(state.player_pitch)) * 10.0
    lz = state.player_z - math.cos(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * 10.0
    gluLookAt(state.player_x + sx, state.player_y + sy, state.player_z + sz, lx + sx, ly + sy, lz + sz, 0, 1, 0)
    
    # Render background fog cube
    glPushMatrix()
    glTranslatef(state.player_x, state.player_y, state.player_z)
    glColor3f(*ROOM_THEMES[state.room]['fog_col'])
    dcube(180.0) 
    glPopMatrix()
    
    state.environment.draw_room()
    draw_fireballs()
    draw_particles()
    
    if state.room == 3:
        state.boss.draw(); state.boss.draw_health_bar()
    
    for e in state.enemies:
        e.draw(); e.draw_health_bar()
        
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluPerspective(60.0, W_WIDTH/W_HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    is_moving = any(state.keys.get(k) for k in ('w', 'a', 's', 'd'))
    bob_offset = math.sin(time.time() * 10.0) * 0.02 if is_moving else 0.0

    if state.environment.held_object:
        swing_prog = (state.melee_timer / 0.25) if state.melee_timer > 0 else 0
        state.environment.held_object.draw_fps(swing_prog, bob_offset)
    else: DetailedFPSWeaponDrawer.draw_weapon(state.current_weapon, state.recoil_offset)
        
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

    glClear(GL_DEPTH_BUFFER_BIT)
    draw_crosshair()
    draw_ui()
    glutSwapBuffers()

def idle():
    ct = time.time()
    dt = min(ct-state.last_time, 0.1)
    state.last_time = ct
    
    update(dt)
    
    glutPostRedisplay()

def keyboard(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    if k == b' ': state.trigger_attack()
    if k == b'e': state.environment.pickup_object(state.player_x, state.player_z)
    if k == b'f': state.environment.throw_held_object(state.player_x, state.player_y, state.player_z, state.player_yaw, state.player_pitch)
    if k in (b'w', b'a', b's', b'd'): state.keys[k.decode()] = True
    if k == b'\x1b': sys.exit(0)
    if k == b'r':
        if not state.is_reloading and state.ammo < state.max_ammo and not state.environment.held_object:
            state.is_reloading, state.reload_timer = True, 1.0
    if k == b'x' and state.dash_cooldown <= 0 and not state.is_dashing:
        state.is_dashing, state.dash_timer, state.dash_cooldown = True, 0.2, 2.0
        state.dash_dir_x, state.dash_dir_z = math.sin(math.radians(state.player_yaw)), -math.cos(math.radians(state.player_yaw))
    if k == b'\r':
        if state.game_over or state.game_won: state.restart_game()
        elif state.room_cleared and state.room < 3: state.load_room(state.room + 1)

def keyboard_up(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    if k in (b'w', b'a', b's', b'd'): state.keys[k.decode()] = False

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

def mouse_func(button, btn_state, x, y):
    if button == GLUT_LEFT_BUTTON and btn_state == GLUT_DOWN: state.trigger_attack()
    if button == GLUT_RIGHT_BUTTON and btn_state == GLUT_DOWN and state.environment.held_object:
        state.environment.throw_held_object(state.player_x, state.player_y, state.player_z, state.player_yaw, state.player_pitch)

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"House of the Dead - Corridor FPS")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_key)
    glutMouseFunc(mouse_func)
    try:
        glutKeyboardUpFunc(keyboard_up)
        glutSpecialUpFunc(special_key_up)
    except: pass
    state.load_room(1)
    glutMainLoop()