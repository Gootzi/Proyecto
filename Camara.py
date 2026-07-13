import numpy as np
from Graficos_3D import producto_cruz,producto_punto
import math


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

def div_perspec (matriz):

    w = matriz[3]
    return matriz/w

# Convierte el cubo perspectiva a pixeles en pantalla
def imagen (norm,alto,ancho):

    x = (norm[0] + 1) / 2 * ancho
    y = (1 - norm[1]) / 2 * alto
    z = (norm[2] + 1) / 2

    return np.array([x,y,z])

# Devuelve los cambios en la proyeccion para mostrarlas en pantalla
def proyectar_vertice (vertice, MVP, ancho, alto):

    homogenea = np.array([vertice[0],vertice[1],vertice[2],1.0])
    perspectiva = MVP @ homogenea
    if perspectiva[3] <= 0:
        return None
    normalizada = div_perspec(perspectiva)

    return imagen(normalizada, alto, ancho)



