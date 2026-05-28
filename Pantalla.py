import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
import math
import Configuracion as CF
import Graficos_3D as G3 
import ctypes


# Convierte coordenadas polares a coordenadas cuadradas
def pos_camara (phi,theta,radio):

    tx,ty,tz = 0,0,0
    
    camara = [
        tx + radio * math.sin(phi) * math.cos(theta),
        ty + radio * math.sin(phi) * math.sin(theta),
        tz + radio * math.cos(phi)
    ]

    return camara

# Crea los valores iniciales para una ventana
def init_window():

    pygame.init()                           

    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )

    pantalla = pygame.display.set_mode(        
        (CF.ANCHURA, CF.ALTURA),
        pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
    )
    pygame.display.set_caption("Graficador en R3")
    return pantalla

# VAO = Vertex Array Object
def crear_vao(vbo,ebo):
    vao = glGenVertexArrays(1)           # Genera un pointer

    glBindVertexArray(vao)               # Activa el pointer

    glBindBuffer(GL_ARRAY_BUFFER, vbo)   # asocia el VBO a este VAO
    
    glVertexAttribPointer(
        0,                               # Ubicacion que debe estar igual con el shader
        3,                               # 3 componentes por vértice (x, y, z)
        GL_FLOAT,                        # tipo de dato
        GL_FALSE,                        # True si se quieren normalizar enteros
        36,                              # bytes por vertice (color y posicion)
        ctypes.c_void_p(0)               # posicion del primer componente
    )
    glEnableVertexAttribArray(0)         # Activar el VAO

    # Toma 12 bytes por dato 
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    # Se asigna un pointer offset para mantenga la posicion de la lista
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,ebo) # Vincula el ebo

    glBindVertexArray(0)                  # Desactiva el VAO y el VBO
    glBindBuffer(GL_ARRAY_BUFFER,0)

    return vao

# VBO = Vertex Buffer Object
def crear_vbo ():
    vertices = G3.com

    vbo = glGenBuffers(1)                # Genera un pointer

    glBindBuffer(GL_ARRAY_BUFFER, vbo)   # Activa el pointer
    glBufferData(                                         
        GL_ARRAY_BUFFER,                 # Destino
        vertices.nbytes,                 # Tamaño en bytes
        vertices,                        # Puntero a los datos RAM             
        GL_STATIC_DRAW                   # Datos estaticos       
    )

    return vbo

# Element Buffer Object (la conexion con el VAO es automatica)
def crear_ebo ():
    indices = G3.ind

    ebo = glGenBuffers(1)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData (
        GL_ELEMENT_ARRAY_BUFFER,         
        indices.nbytes,
        indices,
        GL_STATIC_DRAW
    )

    return ebo

VERTICE_SHADER = """
#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aColor;

out vec3 vColor;
out vec3 vNormal;

void main() {
    gl_Position = vec4(aPos, 1.0);
    vColor    = aColor;
    vNormal   = aNormal;
}
"""

FRAGMENT_SHADER = """
#version 330 core

in vec3 vColor;
out vec4 FragColor;

void main() {
    FragColor = vec4(vColor, 1.0);
}
"""

def compile_shader(origen, shaderT):
    shader = glCreateShader(shaderT)   # Pointer con un GL_VERTEX_SHADER o GL_FRAGMENT_SHADER
    glShaderSource(shader, origen)
    glCompileShader(shader)            # Compila directamente en GPU
    
    if not glGetShaderiv(shader, GL_COMPILE_STATUS): # Devuelve un entero, si GL_COMPILE_STATUS == False ejecuta el argumento
        log = glGetShaderInfoLog(shader).decode()    # Mira la posicion del shader y la devuelve
        glDeleteShader(shader)
        raise RuntimeError(f"Error en la compilacion de shader:\n{log}")
    
    return shader

def crear_programa(VERTICE_SHADER, FRAGMENT_SHADER):
    vert = compile_shader(VERTICE_SHADER, GL_VERTEX_SHADER)
    frag = compile_shader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    
    programa = glCreateProgram()      # Inicializa un objeto programa que contiene todos los elementos antes creados
    glAttachShader(programa, vert)    # Al contenedor creado ingresa los shaders 
    glAttachShader(programa, frag)   
    glLinkProgram(programa)           # Ejecuta los shaders en GPU
    
    
    if not glGetProgramiv(programa, GL_LINK_STATUS): #Si no se enlaza correctamente devuelve falso e inicia el argumento
        log = glGetProgramInfoLog(programa).decode() 
        raise RuntimeError(f"Error linkeando programa:\n{log}")
    
    glDeleteShader(vert)              # Una ves asignado los datos en GPU no es necesaria la ejecuacion de los shaders
    glDeleteShader(frag)

    return programa

def main():

    phi = math.pi/4
    theta = 1.0
    radio = 10.0

    screen = init_window()
    vbo = crear_vbo()
    ebo = crear_ebo()
    vao = crear_vao(vbo, ebo)
    program = crear_programa(VERTICE_SHADER,FRAGMENT_SHADER)
    
    ind_can = len(G3.ind)

    reloj = pygame.time.Clock()

    Abierto = True
    while Abierto:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                glDeleteVertexArrays(1, [vao])
                glDeleteBuffers(1, [vbo])
                glDeleteProgram(program)
                Abierto = False
                return
                
            elif evento.type == pygame.MOUSEMOTION:
                if evento.buttons[0]:
                    dx, dy = evento.rel

                    theta -= dx * CF.SENSIBILIDAD
                    phi -= dy * CF.SENSIBILIDAD

                    phi = max(CF.PHI_MIN, min (CF.PHI_MAX,phi))
            
            elif evento.type == pygame.MOUSEWHEEL:
                radio -= evento.y * CF.VEL_ZOOM
                radio = max(CF.R_MIN, min(CF.R_MAX,radio))

        cam = pos_camara(phi,theta,radio)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(program)

        glBindVertexArray(vao)

        glDrawElements(
            GL_TRIANGLES,
            ind_can,
            GL_UNSIGNED_INT,
            None
        )

        glBindVertexArray(0)

        pygame.display.flip()
        reloj.tick(30)
    

if __name__ == "__main__":
    main()


