import numpy as np
import Graficos_3D as G3
import math
import Configuracion as CF

def traslacion(x,y,z):

    tras = np.array([
        [1,0,0,x],
        [0,1,0,y],
        [0,0,1,z],
        [0,0,0,1]
    ], dtype=np.float32)
    return tras

def rotacion(alpha,mu,theta):

    eje_z = np.array([
        [np.cos(alpha),-np.sin(alpha),0,0],
        [np.sin(alpha), np.cos(alpha),0,0],
        [0,          0,               1,0],
        [0,          0,               0,1]
    ], dtype=np.float32)
    eje_y = np.array([
        [np.cos(mu), 0,np.sin(mu),0],
        [0,          1,0,            0],
        [-np.sin(mu),0,np.cos(mu),   0],
        [0,          0,0,            1]
    ], dtype=np.float32)
    eje_x = np.array([
        [1, 0,             0,             0],
        [0, np.cos(theta),-np.sin(theta), 0],
        [0, np.sin(theta), np.cos(theta), 0],
        [0, 0,             0,             1]
    ], dtype=np.float32)
    matriz = eje_x @ eje_y @ eje_z
    return matriz

def escala(x,y,z):

    esc = np.array([
        [x,0,0,0],
        [0,y,0,0],
        [0,0,z,0],
        [0,0,0,1]
    ], dtype=np.float32)
    return esc

def mundo3D (e,r,t):

    producto = e @ r @ t
    return producto

def pos_cam():

    punto_vis = np.array([0,0,10])
    direccion = np.array([0,0,0])
    momentaneo = np.array([0,1,0])

    adelante = direccion - punto_vis
    adelante = adelante/np.linalg.norm(adelante)

    derecha = G3.producto_cruz(adelante,momentaneo)
    derecha = derecha / np.linalg.norm(derecha)

    arriba = G3.producto_cruz(derecha,adelante)

    matriz_vista = np.array([
        [derecha[0],derecha[1],derecha[2], -G3.producto_punto(derecha,punto_vis)],
        [arriba[0],arriba[1],arriba[2],-G3.producto_punto(arriba,punto_vis)],
        [-adelante[0],-adelante[1],-adelante[2],G3.producto_punto(adelante,punto_vis)],
        [0,0,0,1]
    ], dtype=np.float32)

    return matriz_vista

def proyeccion(fov,aspecto,cerca,lejos):

    fov = math.radians(fov)
    rasp = aspecto * (1/np.tan(fov/2))
    campv = 1/np.tan(fov/2)
    normz = -(lejos + cerca)/(lejos-cerca)
    norme = -(2*lejos * cerca)/(lejos-cerca) 

    matriz = np.array([
        [rasp,0,    0,    0],
        [0,   campv,0,    0],
        [0,   0,    normz,norme],
        [0,   0,    -1,   0]
    ], dtype=float)

    return matriz

def div_perspec (matriz):

    w = matriz[3]
    return matriz/w

def normalizacion (matriz):

    return matriz/np.linalg.norm(matriz)

def imagen (norm,alto,ancho):

    x = (norm[0] + 1) / 2 * ancho
    y = (1 - norm[1]) / 2 * alto
    z = (norm[2] + 1) / 2

    return np.array([x,y,z])

def proyectar_vertice (vertice, MVP, ancho, alto):

    homogenea = np.array([vertice[0],vertice[1],vertice[2],1.0])
    perspectiva = MVP @ homogenea
    if perspectiva[3] <= 0:
        return None
    normalizada = div_perspec(perspectiva)

    return imagen(normalizada, ancho, alto)

S   = escala(3, 3, 3)
R   = rotacion(0,0,0)
T   = traslacion(0, 0, 0)
M   = mundo3D(S, R, T)

V   = pos_cam()
P   = proyeccion(CF.FOV, CF.ASPECT, CF.NEAR, CF.FAR)

MVP = M @ V @ P #Model matrix, View matrix, Projection matrix



