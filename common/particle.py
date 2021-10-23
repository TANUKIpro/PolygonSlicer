import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

if __package__==None:
    print("__package__==None && __name__==__main__")
    import sys
    sys.exit()
else:
    from . import common_constants as cc
    from . import drawer
    from . import calculation

## パーティクルの生成、演算、描画
class Particle:
    def __init__(self, x, y, z, m=1.0):
        self.m = m
        self.x, self.y, self.z                = x, y, z
        self.oldx, self.oldy, self.oldz       = x, y, z
        self.newx, self.newy, self.newz       = x, y, z
        self.ax, self.ay, self.az = 1e-10, 1e-10, 1e-10
        self.vx, self.vy, self.vz = 0., 0., 0.
        #self.angle = 0

        self.collided = False
        self.fixed = False
        self.color = None

    def update(self, delta_t=cc.DT):
        if self.fixed:
            self.color = cc.GREEN
        else:
            self.color = cc.RED
            # Verlet Integration
            # (https://www.watanabe-lab.jp/blog/archives/1993)
            self.newx = 2.0 * self.x - self.oldx + self.ax * delta_t**2
            self.newy = 2.0 * self.y - self.oldy + self.ay * delta_t**2
            self.newz = 2.0 * self.z - self.oldz + self.az * delta_t**2
            self.oldx = self.x
            self.oldy = self.y
            self.oldz = self.z
            self.x = self.newx
            self.y = self.newy
            self.z = self.newz
    
    def updateCollision(self, bone_mesh, threshold):
        # ポリゴンとパーティクルの衝突判定
        origin      = np.array([self.oldx, self.oldy, self.oldz])
        next_origin = np.array([self.x, self.y, self.z])
        for polygon in bone_mesh:
            # パーティクルとポリゴンのユークリッド距離を計算
            poly2ray = np.linalg.norm(origin - (np.sum(polygon, axis=0)/3))
            if poly2ray > threshold:
                continue
            ray = origin - next_origin
            collision_coord = calculation.faster_collisionDetectionWithTriangle(origin, ray, *polygon, epsilon=0.2)
            if collision_coord is not None:
                self.collided = True
                drawer.drawPoint(*collision_coord, 5, (1,1,0))
                cx, cy, cz = collision_coord
                self.x -= (self.x-cx)
                self.y -= (self.y-cy)
                self.z -= (self.z-cz)
            else:
                self.collided = False

    def set_pos(self, pos):
        self.x, self.y, self.z = pos

    def set_oldpos(self, pos):
        self.oldx, self.oldy, self.oldz = pos

    def set_newpos(self, pos):
        self.newx, self.newy, self.newz = pos
    
    def getPos(self):
        return self.x, self.y, self.z

    def draw_sp(self, Show=False):
        glColor3f(*self.color)
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex3fv(tuple((self.x, self.y, self.z)))
        glEnd()

        if Show:
            drawer.drawText_3D(str(self.x)+", "+str(self.y)+", "+str(self.z),
                               self.x, self.y, self.z)

    def draw(self):
        if self.fixed:
            self.draw_sp()
        else:
            glColor3f(*self.color)
            glPointSize(3)
            glBegin(GL_POINTS)
            glVertex3fv(tuple((self.x, self.y, self.z)))
            glEnd()
