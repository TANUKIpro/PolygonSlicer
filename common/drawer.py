import sys, os, traceback
import ctypes

from math import sin, cos, sqrt, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#FONT = GLUT_BITMAP_HELVETICA_18
FONT = GLUT_BITMAP_8_BY_13

org = tuple((0,0,0))
org_points = [[tuple((0, 0, 0)), tuple((3, 0, 0))],
              [tuple((0, 0, 0)), tuple((0, 3, 0))],
              [tuple((0, 0, 0)), tuple((0, 0, 3))]]

def drawPoint(x,y,z, size, color):
    glColor3f(*color)
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex3fv(tuple((x,y,z)))
    glEnd()

def drawEdge(points):
    glColor3f(0,0,0)
    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex3fv(point)
    glEnd()

def drawPolygon(points):
    glLineWidth(1.0)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glColor3f(1,1,1)
    glBegin(GL_TRIANGLES)
    for point in points:
        glVertex3fv(point)
    glEnd()

def drawLines(p1, p2, size, color):
    glColor3f(*color)
    glPointSize(size)
    glBegin(GL_LINES)
    p1_x, p1_y, p1_z = p1
    p2_x, p2_y, p2_z = p2
    glVertex3fv(tuple((p1_x, p1_y, p1_z)))
    glVertex3fv(tuple((p2_x, p2_y, p2_z)))
    glEnd()

def drawAxis(x, y, z, size):
    ## X
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3fv(tuple((x, y, z)))
    glVertex3fv(tuple((x+size, y, z)))
    glEnd()

    ## Y
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3fv(tuple((x, y, z)))
    glVertex3fv(tuple((x, y+size, z)))
    glEnd()

    ## Z
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3fv(tuple((x, y, z)))
    glVertex3fv(tuple((x, y, z+size)))
    glEnd()

def drawText(value, x, y, windowHeight, windowWidth):
    ## 文字列をビットマップフォントで描画
    glMatrixMode(GL_PROJECTION)
    matrix = glGetDouble(GL_PROJECTION_MATRIX)

    glLoadIdentity()
    glOrtho(0.0, windowHeight, 0.0, windowWidth, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2i(x, y)
    lines = 0
    for character in value:
        if character == '\n':
            glRasterPos2i(x, y-(lines*18))
        else:
            #glutBitmapCharacter(FONT, ord(character))
            glutBitmapCharacter(FONT, ord(character))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(matrix)
    glMatrixMode(GL_MODELVIEW)

def drawText_3D(value, x, y, z):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(x, y, z)
    lines = 0
    for character in value:
        if character == '\n':
            glRasterPos2i(x, y-(lines*18))
        else:
            glutBitmapCharacter(FONT, ord(character))

## gpuに配列を転送する
## ここを参考(https://qiita.com/ousttrue/items/e343baabdbdd6b7891c4)
def create_vbo(buffers, vertices, colors, indices):
    # 頂点情報
    buffers = glGenBuffers(3)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glBufferData(GL_ARRAY_BUFFER,
                 len(vertices)*4,  # byte size
                 (ctypes.c_float*len(vertices))(*vertices),
                 GL_DYNAMIC_DRAW)

    # 色情報
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glBufferData(GL_ARRAY_BUFFER,
                 len(colors)*4, # byte size
                 (ctypes.c_float*len(colors))(*colors),
                 GL_DYNAMIC_DRAW)

    # 頂点のインデクス情報
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 len(indices)*4, # byte size
                 (ctypes.c_uint*len(indices))(*indices),
                 GL_DYNAMIC_DRAW)
    return buffers

def moveVer(vertices, colors, indices):
    offset  = 0
    glBufferSubData(GL_ARRAY_BUFFER,
                    offset,
                    len(vertices)*4,
                    vertices)
    #offset += len(vertices)*4
    """
    glBufferSubData(GL_ARRAY_BUFFER, 
                    offset, 
                    len(colors)*4, 
                    colors)
    #offset += len(colors)*4

    glBufferSubData(GL_ELEMENT_ARRAY_BUFFER,
                    offset,
                    len(indices)*4,
                    indices)
    #offset += len(indices)*4
    """
def draw_vbo(buffers, indices, mode_front=GL_FILL):
    glDisable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    glPolygonMode(GL_FRONT, mode_front)
    glLineWidth(1)             # ワイヤの太さ

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glVertexPointer(3, GL_FLOAT, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glColorPointer(3, GL_FLOAT, 0, None)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2])

    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

def free_vbo(buffers):
    glDeleteBuffers(3, buffers)