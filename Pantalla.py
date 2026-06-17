import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
import math
import Configuracion as CF
import Graficos_3D as G3 
import Camara as CM
import ctypes


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
    indices = G3.ind         # Dibuja los triangulos

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

uniform mat4 uModelo;
uniform mat4 uVista;
uniform mat4 uProyeccion;

out vec3 vColor;
out vec3 vNormal;

void main() {
    gl_Position = uProyeccion * uVista * uModelo * vec4(aPos, 1.0);
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
UI_VERT = """
#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aUV;
out vec2 vUV;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    vUV = aUV;
}
"""

UI_FRAG = """
#version 330 core
in vec2 vUV;
uniform sampler2D uTex;
out vec4 FragColor;
void main() {
    FragColor = texture(uTex, vUV);
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

def actualizar (vbo, ebo, ver, ind):

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, 
                 ver.nbytes,
                 ver,
                 GL_DYNAMIC_DRAW)
    
    glBindBuffer(GL_ARRAY_BUFFER, ebo)
    glBufferData(GL_ARRAY_BUFFER, 
                 ind.nbytes,
                 ind,
                 GL_DYNAMIC_DRAW)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)

def crear_programa_ui():
    return crear_programa(UI_VERT, UI_FRAG)

def _renderizar_quad_ui(programa_ui,tex):

    quad = np.array([
        -1.0,  -1.0,  0.0,  0.0,
         1.0,  -1.0,  1.0,  0.0,
         1.0,   1.0,  1.0,  1.0,
        -1.0,   1.0,  0.0,  1.0,
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(8))
    glEnableVertexAttribArray(1)

    glBindTexture(GL_TEXTURE_2D, tex)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)

    glUseProgram(programa_ui)  
    loc_tex = glGetUniformLocation(programa_ui, "uTex")
    glUniform1i(loc_tex, 0)   
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex)

    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glBindVertexArray(0)
    glDeleteVertexArrays(1, [vao])
    glDeleteBuffers(1, [vbo])
    glDeleteBuffers(1, [ebo])

def crear_ui (window, fuente, tex_fun, usario, momentaneo, error, programa_ui):

    ancho,alto = window.get_size()

    ui = pygame.Surface((ancho,alto), pygame.SRCALPHA)
    ui.fill((0,0,0,0))
    
    if usario:
        pygame.draw.rect(ui, (0, 0, 0, 160), (10, alto - 50, ancho - 20, 36))
        texto = fuente.render(momentaneo, True, (255, 255, 100))
    else:
        texto = fuente.render(tex_fun,True, (200, 200, 200))

    ui.blit(texto, (20, alto - 42))

    if error:
        error_surf = fuente.render(error, True, (255, 80, 80))
        ui.blit(error_surf, (20, alto - 70))

    data = pygame.image.tostring(ui, "RGBA", True)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ancho, alto, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    _renderizar_quad_ui(programa_ui,tex)

    glDeleteTextures(1, [tex])

def main():

    phi = math.pi/4
    theta = 1.0
    radio = 10.0

    tex_funcion = "[Enter]"
    input_usuario = False
    input_momentaneo = ""
    tex_error = ""

    screen = init_window()
    glEnable(GL_DEPTH_TEST)
    
    programa_ui = crear_programa_ui()
    fuente = pygame.font.SysFont("monospace", 18)

    vbo = crear_vbo()
    ebo = crear_ebo()
    vao = crear_vao(vbo, ebo)
    program = crear_programa(VERTICE_SHADER,FRAGMENT_SHADER)

    modelo_ubi = glGetUniformLocation(program, "uModelo")
    vista_ubi = glGetUniformLocation(program, "uVista")
    proyeccion_ubi = glGetUniformLocation(program, "uProyeccion")
    
    ind_can = len(G3.ind)
    reloj = pygame.time.Clock()

    Abierto = True
    while Abierto:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                glDeleteVertexArrays(1, [vao])
                glDeleteBuffers(1, [vbo])
                glDeleteBuffers(1, [ebo])
                glDeleteProgram(program)
                Abierto = False
                return
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if input_usuario:
                        n_com, n_ind, error = G3.generar(input_momentaneo)
                        if error:
                            tex_error = f"Error: {error}"
                        elif n_com is None or n_ind is None:
                            tex_error = "Funcion Invalida" 
                        else:
                            tex_funcion = input_momentaneo
                            tex_error = ""
                            ind_can = len(n_ind)
                            actualizar(vbo, ebo, n_com, n_ind)
                        input_usuario = False
                        input_momentaneo = ""
                    else:
                        input_usuario = True
                        input_momentaneo = tex_funcion

                elif evento.key == pygame.K_ESCAPE:
                    input_usuario = False
                    input_momentaneo = ""
                    tex_error = ""

                elif input_usuario:
                    if evento.key == pygame.K_BACKSPACE:
                        input_momentaneo = input_momentaneo[:-1]
                    else:
                        input_momentaneo += evento.unicode
            

                
            elif evento.type == pygame.MOUSEMOTION:
                if evento.buttons[0]:

                    dx, dy = evento.rel

                    theta -= dx * CF.SENSIBILIDAD

                    phi -= dy * CF.SENSIBILIDAD
                    phi = max(CF.PHI_MIN, min(CF.PHI_MAX, phi))
            
            elif evento.type == pygame.MOUSEWHEEL:

                radio -= evento.y * CF.VEL_ZOOM
                radio = max(CF.R_MIN, min(CF.R_MAX,radio))
        

        modelo = CM.escala(3,3,3)
        vista = CM.pos_cam(phi,theta,radio)
        ancho,alto = screen.get_size()
        proyeccion = CM.proyeccion(CF.FOV, ancho/alto,CF.NEAR, CF.FAR)

        glUseProgram(program)

        glUniformMatrix4fv(modelo_ubi,     1, GL_TRUE, modelo)
        glUniformMatrix4fv(vista_ubi,      1, GL_TRUE, vista)
        glUniformMatrix4fv(proyeccion_ubi, 1, GL_TRUE, proyeccion)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(vao)
        glDrawElements(
            GL_TRIANGLES,
            ind_can,
            GL_UNSIGNED_INT,
            None
        )
        glBindVertexArray(0)

        glUseProgram(programa_ui)
        crear_ui(screen, fuente, tex_funcion, input_usuario,input_momentaneo, tex_error, programa_ui)

        pygame.display.flip()
        reloj.tick(30)   

if __name__ == "__main__":
    main()


