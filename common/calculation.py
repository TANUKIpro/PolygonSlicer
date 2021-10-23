from math import *
import numpy as np
import numpy.linalg as LA

# ガウス関数
def gaussian_function(sigma, mu, x, A=1.25):
    return A*(1/sqrt(2*pi*sigma) * exp(-1/(2*sigma*sigma)*(x-mu)**2))

# 超ガウス関数
def super_gaussian_function(sigma, mu, lmd, x, A=1.25):
    return A*exp(-(1/2*sigma*sigma*(x-mu)**2)**lmd)

# ベクトルの減算
def subtract(vec1,vec2):
    return [vec1[i]-vec2[i] for i in [0,1,2]]

# ベクトル長
def get_length(vec):
    return sum([vec[i]*vec[i] for i in [0,1,2]])**0.5

#####     https://algorithm.joho.info/programming/python/forward-kinematics-3-simulation/
## 3リンクの順運動学を計算する関数
def calcForwardKinema(init_coord, lL, theta, vias, sL=(0.8, 0.8), s_theta=(30, 30)):
    l1, l2, l3    = lL               # 各リンクの長さ
    th1, th2, th3 = theta            # 各関節角度
    sl1, sl2   = sL                  # 停止パーティクルと関節までの距離
    sth1, sth2 = s_theta             # 停止パーティクルと関節が作る角度
    vias_l1, vias_l2 = vias          # 各リンク位置のバイアス

    x0, y0 = init_coord

    x1 = l1 * cos(th1) + vias_l1[0]
    y1 = l1 * sin(th1) + vias_l1[1]

    x2 = x1 + l2 * cos(th1 + th2) + vias_l2[0]
    y2 = y1 + l2 * sin(th1 + th2) + vias_l2[1]
    x_sp1 = x1 + sl1 * cos(th1 + th2 + sth1)
    y_sp1 = y1 + sl1 * sin(th1 + th2 + sth1)

    x3 = x2 + l3 * cos(th1 + th2 + th3)
    y3 = y2 + l3 * sin(th1 + th2 + th3)
    x_sp2 = x2 + sl2 * cos(th1 + th2 + th3 + sth2)
    y_sp2 = y2 + sl2 * sin(th1 + th2 + th3 + sth2)

    return np.array([[x0, y0], [x1, y1], [x2, y2], [x3, y3], [x_sp1, y_sp1], [x_sp2, y_sp2]])

## 2点を通る直線の式
def calcStraightEquation(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    a = (y2-y1)/(x2-x1)
    b = y1-a*x1
    # y = ax + b
    return a,b

## 直線に通る一点に対する垂直な直線の式
def calcPerpendicularLine(m, a, b):
    mx, my = m
    a_PL = -1*(1/a)
    b_PL = my-a_PL*mx
    # y = a_PL*x + b_PL
    return a_PL, b_PL

#####     https://qiita.com/tydesign/items/2fd456f40f5aeeb461ff
## 3点から円の中心座標と半径を求める関数
def calcCenterOfCircle(coord):
    p1, p2, p3 = coord
    
    x1, x2, x3 = p1[0], p2[0], p3[0]
    y1, y2, y3 = p1[1], p2[1], p3[1]

    x_top    = ( (y1-y2)*(x3**2-x1**2+y3**2-y1**2) ) - ( (y1-y3)*(x2**2-x1**2+y2**2-y1**2) )
    x_bottom = ( 2*(x1-x2)*(y1-y3) ) - ( 2*(x1-x3)*(y1-y2) )
    c_x = x_top / x_bottom

    y_top    = ( (x1-x3)*(x2**2-x1**2+y2**2-y1**2) ) - ( (x1-x2)*(x3**2-x1**2+y3**2-y1**2) )
    y_bottom = x_bottom
    c_y = y_top / y_bottom

    r = sqrt(( (c_x-x1)**2 ) + ( (c_y-y1)**2 ))

    return ([c_x, c_y], r)

## X軸を回転軸とした原点から任意の座標を回転させた時の座標
def getRotX(coord, theta):
    x, y, z = coord
    x_X = x
    x_Y = y*cos(theta) + z*sin(theta)
    x_Z = -y*sin(theta) + z*cos(theta)
    return [x_X, x_Y, x_Z]

## Y軸を回転軸とした原点から任意の座標を回転させた時の座標
def getRotY(coord, theta):
    x, y, z = coord
    y_X = x*cos(theta) - z*sin(theta)
    y_Y = y
    y_Z = x*sin(theta) + z*cos(theta)
    return [y_X, y_Y, y_Z]

## Z軸を回転軸とした原点から任意の座標を回転させた時の座標
def getRotZ(coord, theta):
    x, y, z = coord
    z_X = x*cos(theta) + y*sin(theta)
    z_Y = -x*sin(theta) + y*cos(theta)
    z_Z = z
    return [z_X, z_Y, z_Z]

## 任意の点を原点とした時に任意の角度で回転させた時の座標
def calcCenterRot(c, fst_coord, theta):
    cX, cY = c
    fstX, fstY = fst_coord
    x = fstX*cos(theta) - fstY*sin(theta) + cX-cX*cos(theta)+cY*sin(theta)
    y = fstX*sin(theta) + fstY*cos(theta) + cY-cX*sin(theta)-cY*cos(theta)
    return x, y

## パーティクルとポリゴンの衝突検出関数
# https://shikousakugo.wordpress.com/2012/06/27/ray-intersection-2/
def __collisionDetectionWithTriangle(origin, ray, v0, v1, v2):
    edge1 = (v1 - v0).tolist()
    edge2 = (v2 - v0).tolist()
    cons0 = (origin - v0).tolist()
    cons1 = (ray*-1).tolist()
    denominator = LA.det([edge1, edge2, cons1])  ## クラメルの共通分母
    if denominator > 0:
        u = LA.det([cons0, edge2, cons1])  /  denominator
        if (u >= 0) & (u <= 1):
            v = LA.det([edge1, cons0, cons1])  /  denominator
            if (v >= 0) & (u+v <= 1):
                t = LA.det([edge1, edge2, cons0])  /  denominator
                intersection = origin + (ray * t)
                return intersection.tolist()

def faster_collisionDetectionWithTriangle(origin, ray, v0, v1, v2, epsilon=0.2):
    edge1 = (v1 - v0).tolist()
    edge2 = (v2 - v0).tolist()
    p = np.cross(ray, edge2).tolist()
    det = np.dot(p, edge1).tolist()  ## クラメルの共通分母
    if det > epsilon:
        t = origin - v0
        u = np.dot(p, t)
        if (u >= 0) & (u <= det):
            q = np.cross(t, edge1)
            v = np.dot(q, ray)
            if (v >= 0) & (u+v <= det):
                t = np.dot(q, edge2) / det
                intersection = origin + (ray * t)
                return intersection