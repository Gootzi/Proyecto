import numpy as np
from Graficos_3D import producto_cruz,producto_punto
import math

#Formula para escalar
def escala(x,y,z):

    esc = np.array([
        [x,0,0,0],
        [0,y,0,0],
        [0,0,z,0],
        [0,0,0,1]
    ], dtype=np.float32)
    return esc

# Usando coordenadas polares ubicar la posicion de vista
def pos_cam(phi,theta,radio):

    punto_vis = np.array([
        radio * math.sin(phi) * math.cos(theta),  # x
        radio * math.sin(phi) * math.sin(theta),  # y
        radio * math.cos(phi)                     # z
    ], dtype=np.float32)

    direccion = np.array([0,0,0], dtype=np.float32)

    adelante = direccion - punto_vis
    adelante = adelante/np.linalg.norm(adelante)

# Phi debe estar restringido entre 0 < phi < 180 para que no tenga error 

    if abs(math.sin(phi)) < 0.1:
        momentaneo = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    else:
        momentaneo = np.array([0.0, 0.0, 1.0], dtype=np.float32)

    derecha = producto_cruz(adelante,momentaneo)

# Si el producto cruz se acerca a cero puede generar errores por el manejo de decimales

    mag = np.linalg.norm(derecha)
    if mag < 1e-6:
        derecha = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    else:
        derecha = derecha / mag

    arriba = producto_cruz(derecha,adelante)
    arriba = arriba/ np.linalg.norm(arriba)

    matriz_vista = np.array([
        [derecha[0],derecha[1],derecha[2], -producto_punto(derecha,punto_vis)],
        [arriba[0],arriba[1],arriba[2],-producto_punto(arriba,punto_vis)],
        [-adelante[0],-adelante[1],-adelante[2],producto_punto(adelante,punto_vis)],
        [0,0,0,1]
    ], dtype=np.float32)

    return matriz_vista

def proyeccion(fov,aspecto,cerca,lejos):

    # la libreria math en python solo funciona en radianes para sus trigonometricas
    fov = math.radians(fov)

    # Vista del eje x y el eje y respectivamente
    rasp = (1/np.tan(fov/2)) / aspecto
    campv = 1/np.tan(fov/2)

    # Profundidad
    normz = -(lejos + cerca)/(lejos-cerca)
    norme = -(2*lejos * cerca)/(lejos-cerca) 

    matriz = np.array([
        [rasp,0,    0,    0],
        [0,   campv,0,    0],
        [0,   0,    normz,norme],
        [0,   0,    -1,   0]
    ], dtype=float)

    return matriz




