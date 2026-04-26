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

class Mahoraga:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 3.1, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.hp = 100.0
        self.angle = 0.0
        self.phase = 1
        self.transition_time = 0.0
        self.last_attack_time = time.time()
        self.walk_anim_time = 0.0

    def draw_leg(self, side, wa, cb, cg):
        glPushMatrix()
        glTranslatef(side*0.5, -0.9, 0)
        glRotatef(wa*side, 1,0,0)
        # hip
        glColor3f(*cb); dsph(0.22)
        # upper leg
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.18,0.16,0.95); glPopMatrix()
        # knee
        glTranslatef(0,-0.95,0); dsph(0.20)
        # lower leg
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.16,0.14,0.95); glPopMatrix()
        # ankle ring
        glTranslatef(0,-0.95,0)
        glColor3f(*cg)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.20,0.20,0.10,12); glPopMatrix()
        # foot
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,-0.12,0.1); glScalef(0.32,0.12,0.50); dcube(1.0); glPopMatrix()
        # toes
        for t in range(4):
            glPushMatrix(); glTranslatef(-0.10+t*0.07, -0.20, 0.32); glScalef(0.06,0.07,0.10); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_arm(self, side, wa, cb, cg):
        glPushMatrix()
        glTranslatef(side*1.05, 0.55, 0)
        glRotatef(-wa*side, 1,0,0)
        # shoulder
        glColor3f(*cb); dsph(0.22)
        # upper arm
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.14,0.12,0.80); glPopMatrix()
        # elbow
        glTranslatef(0,-0.80,0); dsph(0.16)
        # lower arm
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.12,0.10,0.75); glPopMatrix()
        # wrist ring
        glTranslatef(0,-0.75,0)
        glColor3f(*cg)
        glPushMatrix(); glRotatef(90,1,0,0); dcyl(0.15,0.15,0.08,12); glPopMatrix()
        # hand
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,-0.15,0); glScalef(0.20,0.15,0.12); dcube(1.0); glPopMatrix()
        # fingers
        for f in range(4):
            glPushMatrix(); glTranslatef(-0.07+f*0.05, -0.30, 0); glScalef(0.035,0.10,0.05); dcube(1.0); glPopMatrix()
        # thumb
        glPushMatrix(); glTranslatef(side*0.12, -0.18, 0.05); glScalef(0.04,0.08,0.04); dcube(1.0); glPopMatrix()
        glPopMatrix()

    def draw_skirt(self, cc):
        glColor3f(*cc)
        # front
        glPushMatrix(); glTranslatef(0,-1.1,0.22); glScalef(1.3,1.1,0.06); dcube(1.0); glPopMatrix()
        # back
        glPushMatrix(); glTranslatef(0,-1.1,-0.22); glScalef(1.3,1.1,0.06); dcube(1.0); glPopMatrix()
        # left
        glPushMatrix(); glTranslatef(-0.60,-1.1,0); glScalef(0.06,1.1,0.50); dcube(1.0); glPopMatrix()
        # right
        glPushMatrix(); glTranslatef(0.60,-1.1,0); glScalef(0.06,1.1,0.50); dcube(1.0); glPopMatrix()
        # front flaps
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
        # main chest
        glPushMatrix(); glTranslatef(0,0.15,0); glScalef(1.45,1.10,0.65); dcube(1.0); glPopMatrix()
        # pecs
        glPushMatrix(); glTranslatef(-0.30,0.48,0.28); glScalef(0.40,0.28,0.15); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.30,0.48,0.28); glScalef(0.40,0.28,0.15); dcube(1.0); glPopMatrix()
        # abs
        for r in range(3):
            for c in range(2):
                glPushMatrix()
                glTranslatef(-0.13+c*0.26, 0.05-r*0.20, 0.34)
                glScalef(0.20,0.16,0.04)
                dcube(1.0)
                glPopMatrix()
        # back detail
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
        # pendant
        glPushMatrix(); glTranslatef(0,0.38,0.37); glScalef(0.08,0.12,0.05); dcube(1.0); glPopMatrix()

    def draw_neck(self, cb):
        glColor3f(*cb)
        glPushMatrix(); glTranslatef(0,0.80,0); glRotatef(-90,1,0,0); dcyl(0.16,0.20,0.30); glPopMatrix()

    def draw_head(self, cb):
        glPushMatrix()
        glTranslatef(0,1.40,0.04)
        glColor3f(*cb)
        dsph(0.42,16,16)
        # horns - upper pair (long, outward)
        glPushMatrix(); glTranslatef(-0.28,0.18,0.08); glRotatef(40,0,0,1); glRotatef(-15,1,0,0); dcyl(0.07,0.0,0.85,8); glPopMatrix()
        glPushMatrix(); glTranslatef(0.28,0.18,0.08); glRotatef(-40,0,0,1); glRotatef(-15,1,0,0); dcyl(0.07,0.0,0.85,8); glPopMatrix()
        # horns - lower pair (shorter, wider)
        glPushMatrix(); glTranslatef(-0.32,-0.02,0.12); glRotatef(55,0,0,1); glRotatef(-8,1,0,0); dcyl(0.055,0.0,0.65,8); glPopMatrix()
        glPushMatrix(); glTranslatef(0.32,-0.02,0.12); glRotatef(-55,0,0,1); glRotatef(-8,1,0,0); dcyl(0.055,0.0,0.65,8); glPopMatrix()
        # eyes (dark slanted)
        glColor3f(0.05,0.05,0.05)
        glPushMatrix(); glTranslatef(-0.14,0.08,0.38); glRotatef(15,0,0,1); glScalef(0.10,0.05,0.03); dcube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0.14,0.08,0.38); glRotatef(-15,0,0,1); glScalef(0.10,0.05,0.03); dcube(1.0); glPopMatrix()
        # mouth line
        glPushMatrix(); glTranslatef(0,-0.10,0.40); glScalef(0.22,0.025,0.025); dcube(1.0); glPopMatrix()
        # teeth
        for t in range(6):
            glPushMatrix(); glTranslatef(-0.09+t*0.036,-0.14,0.40); glScalef(0.03,0.04,0.025); dcube(1.0); glPopMatrix()
        # top spike (from top view)
        glPushMatrix(); glTranslatef(0,0.35,0); glRotatef(-90,1,0,0); dcyl(0.06,0.0,0.45,8); glPopMatrix()
        glPopMatrix()

    def draw_wheel(self, cg, anim_t):
        glColor3f(*cg)
        glPushMatrix()
        glTranslatef(0,1.85,-0.55)
        glRotatef(anim_t*40.0, 0,0,1)
        R = 1.30
        # ring
        segs = 32
        for i in range(segs):
            a1 = i*360.0/segs; a2 = (i+1)*360.0/segs
            x1,y1 = math.cos(math.radians(a1))*R, math.sin(math.radians(a1))*R
            x2,y2 = math.cos(math.radians(a2))*R, math.sin(math.radians(a2))*R
            dx,dy = x2-x1,y2-y1
            sl = math.sqrt(dx*dx+dy*dy)
            ang = math.degrees(math.atan2(dy,dx))
            glPushMatrix(); glTranslatef(x1,y1,0); glRotatef(ang,0,0,1); glRotatef(90,0,1,0); dcyl(0.06,0.06,sl,6,1); glPopMatrix()
        # 6 spokes
        for i in range(6):
            glPushMatrix(); glRotatef(i*60,0,0,1); glRotatef(90,0,1,0); dcyl(0.04,0.04,R,6); glPopMatrix()
        # center sphere
        dsph(0.10,8,8)
        # spoke-end spheres
        for i in range(6):
            glPushMatrix()
            a = math.radians(i*60.0)
            glTranslatef(math.cos(a)*R, math.sin(a)*R, 0)
            dsph(0.14,8,8)
            glPopMatrix()
        glPopMatrix()

    def draw_tail(self, cb):
        """Tail visible from side/back views - segmented spheres curving down and back."""
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
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0,1,0)

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
        glPushMatrix()
        glTranslatef(self.x, self.y+4.5, self.z)
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
            if self.y <= 3.1:
                self.y, self.vy = 3.1, 0
                if random.random() < dt*0.4: self.vy = 12.0
            else:
                self.vy -= 25.0*dt
            self.x += self.vx*dt; self.y += self.vy*dt; self.z += self.vz*dt
            if time.time()-self.last_attack_time > 2.0:
                self.spawn_fireball(); self.last_attack_time = time.time()
        elif self.phase == 2:
            self.transition_time += dt
            self.hp = min(100.0, self.hp + 25.0*dt)
            ty = 10.0; self.y += (ty-self.y)*(dt/max(0.1,2.0-self.transition_time))
            for _ in range(3):
                state.particles.append({'x':self.x+(random.random()-0.5)*6, 'y':self.y-2+random.random()*4,
                                        'z':self.z+(random.random()-0.5)*6, 'vy':2+random.random()*5, 'life':1.0})
            if self.transition_time >= 2.0: self.phase = 3; self.hp = 100.0
        elif self.phase == 3:
            ty = 10+math.sin(time.time()*1.5)*3; tx = math.sin(time.time()*1.2)*12
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
        self.player_yaw = 180.0   # degrees, 180 = facing -Z (toward boss)
        self.player_pitch = 0.0   # degrees, look up/down
        self.mouse_held = False
        self.mouse_x, self.mouse_y = W_WIDTH//2, W_HEIGHT//2
        self.keys = {}
        self.boss = Mahoraga()
        self.fireballs, self.particles = [], []
        self.player_fireballs = []
        self.quadric = None

state = GameState()

def init():
    state.quadric = gluNewQuadric()
    glEnable(GL_DEPTH_TEST)

def dcube(s):
    glutSolidCube(s)
def dcyl(b, t, h, sl=10, st=4):
    gluCylinder(state.quadric, b, t, h, sl, st)
def dsph(r, sl=10, st=10):
    gluSphere(state.quadric, r, sl, st)

def draw_ground():
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-40,0,-40); glVertex3f(40,0,-40); glVertex3f(40,0,40); glVertex3f(-40,0,40)
    glEnd()
    glColor3f(0.35, 0.35, 0.35)
    glBegin(GL_LINES)
    for i in range(-40, 41, 4):
        glVertex3f(i,0.01,-40); glVertex3f(i,0.01,40)
        glVertex3f(-40,0.01,i); glVertex3f(40,0.01,i)
    glEnd()

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
        glColor3f(0.2, 0.2, 1.0)  # blue player fireballs
        dsph(0.3, 12, 12)
        glColor3f(0.8, 0.8, 1.0)
        dsph(0.15, 8, 8)
        glPopMatrix()

def draw_particles():
    if not state.particles: return
    glPointSize(5.0); glColor3f(1.0,1.0,0.0)
    glBegin(GL_POINTS)
    for p in state.particles: glVertex3f(p['x'],p['y'],p['z'])
    glEnd()

def draw_crosshair():
    """Simple crosshair at screen center."""
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1,1,1)
    cx, cy = W_WIDTH//2, W_HEIGHT//2
    glBegin(GL_LINES)
    glVertex3f(cx-12,cy,0); glVertex3f(cx+12,cy,0)
    glVertex3f(cx,cy-12,0); glVertex3f(cx,cy+12,0)
    glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_text():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,W_WIDTH,0,W_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1,1,1)
    t1 = "Boss HP: {:.0f}  Phase: {}".format(state.boss.hp, state.boss.phase)
    glRasterPos2f(10, W_HEIGHT-30)
    for c in t1: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    t2 = "WASD: Move | Arrows/LMB: Look | RMB/SPACE: Attack | Q/E: Turn"
    glRasterPos2f(10, W_HEIGHT-60)
    for c in t2: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
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
    # movement relative to player yaw
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
    # turn with Q/E
    if state.keys.get('q'): state.player_yaw -= 120.0 * dt
    if state.keys.get('e'): state.player_yaw += 120.0 * dt
    # look around with arrow keys
    if state.keys.get('left'):  state.player_yaw -= 120.0 * dt
    if state.keys.get('right'): state.player_yaw += 120.0 * dt
    if state.keys.get('up'):    state.player_pitch += 90.0 * dt
    if state.keys.get('down'):  state.player_pitch -= 90.0 * dt
    state.player_pitch = max(-60.0, min(60.0, state.player_pitch))
    # mouse look: when held, turn based on mouse offset from center
    if state.mouse_held:
        dx = state.mouse_x - W_WIDTH / 2.0
        dy = state.mouse_y - W_HEIGHT / 2.0
        state.player_yaw += dx * 0.3 * dt * 10.0
        state.player_pitch -= dy * 0.2 * dt * 10.0
        state.player_pitch = max(-60.0, min(60.0, state.player_pitch))
    # clamp to ground area
    state.player_x = max(-38, min(38, state.player_x))
    state.player_z = max(-38, min(38, state.player_z))

def update(dt):
    update_player(dt)
    state.boss.update(dt)
    for p in state.particles: p['y'] += p['vy']*dt; p['life'] -= dt
    state.particles = [p for p in state.particles if p['life'] > 0]
    for fb in state.fireballs: fb['x'] += fb['vx']*dt; fb['y'] += fb['vy']*dt; fb['z'] += fb['vz']*dt
    state.fireballs = [fb for fb in state.fireballs if fb['y'] > -5 and abs(fb['x']) < 60 and abs(fb['z']) < 60]
    
    for fb in state.player_fireballs:
        fb['x'] += fb['vx']*dt; fb['y'] += fb['vy']*dt; fb['z'] += fb['vz']*dt
        # Boss collision
        dist = math.sqrt((fb['x']-state.boss.x)**2 + (fb['y']-state.boss.y)**2 + (fb['z']-state.boss.z)**2)
        if dist < 4.5:
            if state.boss.phase in (1, 3):
                state.boss.hp = max(0, state.boss.hp - 10)
                for _ in range(5):
                    state.particles.append({'x':fb['x']+(random.random()-0.5)*2, 'y':fb['y']+(random.random()-0.5)*2,
                                            'z':fb['z']+(random.random()-0.5)*2, 'vy':2+random.random()*5, 'life':0.5})
            fb['y'] = -100 # destroy
    state.player_fireballs = [fb for fb in state.player_fireballs if fb['y'] > -5 and abs(fb['x']) < 60 and abs(fb['z']) < 60]

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(60.0, W_WIDTH/W_HEIGHT, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    # first person camera with pitch
    look_dist = 10.0
    lx = state.player_x + math.sin(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * look_dist
    ly = state.player_y + math.sin(math.radians(state.player_pitch)) * look_dist
    lz = state.player_z - math.cos(math.radians(state.player_yaw)) * math.cos(math.radians(state.player_pitch)) * look_dist
    gluLookAt(state.player_x, state.player_y, state.player_z,
              lx, ly, lz, 0, 1, 0)
    draw_ground(); draw_particles(); draw_fireballs(); state.boss.draw(); state.boss.draw_health_bar()
    draw_crosshair(); draw_text()
    glutSwapBuffers()

def idle():
    ct = time.time(); dt = min(ct-state.last_time, 0.1); state.last_time = ct
    update(dt); glutPostRedisplay()

def keyboard(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    if k == b' ':
        spawn_player_fireball()
    if k in (b'w', b'a', b's', b'd', b'q', b'e'):
        state.keys[k.decode()] = True

def keyboard_up(key, x, y):
    k = key.lower() if isinstance(key, bytes) else key
    if k in (b'w', b'a', b's', b'd', b'q', b'e'):
        state.keys[k.decode()] = False

def mouse_func(button, btn_state, x, y):
    """Hold left button and move mouse to look around."""
    if button == GLUT_LEFT_BUTTON:
        if btn_state == GLUT_DOWN:
            state.mouse_held = True
            state.mouse_x, state.mouse_y = x, y
        else:
            state.mouse_held = False
    # right click = attack
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
    glutCreateWindow(b"3D Boss Fight - Mahoraga")
    init()
    glutDisplayFunc(display); glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_key)
    glutMouseFunc(mouse_func)
    try:
        glutKeyboardUpFunc(keyboard_up)
        glutSpecialUpFunc(special_key_up)
    except:
        pass
    glutMainLoop()
