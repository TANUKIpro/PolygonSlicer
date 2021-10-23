from math import sqrt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# パーティクルへの拘束条件
class ParticleConstraint:
    def __init__(self, particles, index0, index1):
        self.index0 = index0
        self.index1 = index1
        delta_x = particles[index0].x - particles[index1].x
        delta_y = particles[index0].y - particles[index1].y
        delta_z = particles[index0].z - particles[index1].z
        self.particles = particles
        self.restLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        self.init_d = 0
        self.d      = 0

    def update(self):
        delta_x = self.particles[self.index1].x - self.particles[self.index0].x
        delta_y = self.particles[self.index1].y - self.particles[self.index0].y
        delta_z = self.particles[self.index1].z - self.particles[self.index0].z
        deltaLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        diff = (deltaLength - self.restLength)/(deltaLength+0.001)
        if self.particles[self.index0].fixed == False:
            self.particles[self.index0].x += 0.5 * diff * delta_x
            self.particles[self.index0].y += 0.5 * diff * delta_y
            self.particles[self.index0].z += 0.5 * diff * delta_z
        if self.particles[self.index1].fixed == False:
            self.particles[self.index1].x -= 0.5 * diff * delta_x
            self.particles[self.index1].y -= 0.5 * diff * delta_y
            self.particles[self.index1].z -= 0.5 * diff * delta_z

    def draw(self):
        x0 = self.particles[self.index0].x
        y0 = self.particles[self.index0].y
        z0 = self.particles[self.index0].z
        x1 = self.particles[self.index1].x
        y1 = self.particles[self.index1].y
        z1 = self.particles[self.index1].z
        self.d = sqrt((x0-x1)**2+(y0-y1)**2+(z0-z1)**2)

        glColor3f(1, 0, 1)
        glBegin(GL_LINES)
        glVertex3fv(tuple((x0, y0, z0)))
        glVertex3fv(tuple((x1, y1, z1)))
        glEnd()