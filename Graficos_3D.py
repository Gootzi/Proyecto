import numpy as np
import warnings
import colorsys as color
import Pantalla

def producto_punto(x,y):
    x,y = np.array(x,dtype=np.float32), np.array(y,dtype=np.float32)
    propu = np.sum(x * y)
    return propu

# Regresa el vector paralelo a los vectores x,y
def producto_cruz (x,y):
    a1,a2,a3 = x[0],x[1],x[2]
    b1,b2,b3 = y[0],y[1],y[2]
    cx = a2 * b3 - a3 * b2
    cy = a3 * b1 - a1 * b3
    cz = a1 * b2 - a2 * b1
    return [cx,cy,cz]

# Regresa el vector paralelo al triangulo
def normal_triangulo (a,b,c):
    a,b,c = np.array(a,dtype=np.float32),np.array(b,dtype=np.float32),np.array(c,dtype=np.float32) 
    normal = producto_cruz((b - a),(c - a))
    magnitud = np.linalg.norm(normal)
    return normal / magnitud if magnitud > 0 else normal

# Retorna el Meshgrid con valores maximo y minimos graficables
def max_min (puntosz):
    puntosz = np.clip(puntosz,-10000,10000)
    return puntosz

# Los valores nan e infinitos son convertidos en 0 y una valor muy grande o muy pequeño respectivamente
def verificar (puntosz):
    puntosz = np.nan_to_num(puntosz)
    return max_min(puntosz)

def convertir_vectores (x,y,z):
    x= x.flatten()
    y= y.flatten()
    z= z.flatten()
    return np.column_stack([x,y,z])

def triangulacion (malla):
    #Divide la cantidad de puntos en una cuadricula
    filas = int(np.sqrt(len(malla))) -1
    paso = filas + 1
    indice_triangulo = []
    for fil in range(filas):
        for colum in range(filas):
            #Crea los indices de los triangulos, teniendo en cuenta los vertices de un
            #cuadrado y sacando de este dos triangulos con vertices en la direccion de las manecillas del reloj
            vertice1_2 = fil*paso+colum
            vertice3_4 = (fil+1)*paso+colum
            indice_triangulo.append([vertice1_2,vertice1_2+1,vertice3_4])
            indice_triangulo.append([vertice1_2+1,vertice3_4+1,vertice3_4])
    return indice_triangulo

def lista_normales(meshx,meshy,meshz):
    # busca la lista de triangulos y saca sus normales
    vector = convertir_vectores(meshx,meshy,meshz)
    triangula = triangulacion(vector)
    normal = []
    for i in triangula:
        vector1 = vector[(i[0])]
        vector2 = vector[(i[1])]
        vector3 = vector[(i[2])]
        normal.append(normal_triangulo(vector1,vector2,vector3))
    def normal_vertices (triangulos,vertices,normales):
        # Busca la lista de vectores asociados a los triangulos
        # Saca las normales de los vectores
        puntos = [[] for i in range (len(vertices))]
        num_triangulo = 0
        normal_vert = []
        for A,B,C in triangulos:
            puntos[A].append(num_triangulo)
            puntos[B].append(num_triangulo)
            puntos[C].append(num_triangulo)
            num_triangulo += 1
        for i in puntos:
            if type(i) == list:
                suma = np.zeros(3,dtype=np.float32)
                for j in i:
                    suma += np.array(normales[j], dtype=np.float32)    
                normalizado = suma / np.linalg.norm(suma) 
                normal_vert.append(normalizado)
        return normal_vert
    return [vector,triangula,normal_vertices(triangula,vector,normal)]


#cambiar la luminosidad 
def colores (z):
    # Elige los colores en hls y los pasa a rgb y los asigna a un punto z en el espacio
    z = z.flatten()
    normalizado = (z - z.min()) / (z.max()-z.min())
    colores = np.round(309 - 78 * (normalizado)) 
    rgb = []
    for i in colores:
        i = (i) / (360)
        h,l,s = i,0.5,1
        r,g,b = color.hls_to_rgb(h,l,s)
        r,g,b = r*255,g*255,b*255
        rgb.append([r,g,b])
    
    # Normalizar los colores
    rgb = np.array(rgb)

    r_min = np.min(rgb)
    r_max = np.max(rgb)

    rgb_nor = (rgb - r_min) / (r_max - r_min)

    return np.array(rgb_nor)

def completa (meshx,meshy,meshz):
    lista = lista_normales(meshx,meshy,meshz)

    vectores = np.array(lista[0],dtype=np.float32)

    v = vectores.copy()

    for i in range(3):  # normalizar los vectores
        col = v[:, i]
        vmax = np.abs(col).max()
        if vmax > 0:
            v[:, i] = col / vmax

    indices_tri = np.array(lista[1],dtype=np.uint32)
    normales_vert = np.array(lista[2],dtype=np.float32)
    color = np.array(colores(meshz),dtype=np.float32)

    completo = np.concatenate([v,normales_vert,color],axis=1)

    return completo,indices_tri

# Si existe algun valor que matematicamente es imposible, existe "RuntimeWarning"
# El codigo lo detecta y aplica la funcion verificar, si no, continúa
with warnings.catch_warnings(record=True) as indeterminado:
    puntosx, puntosy = np.linspace(-10,10,100), np.linspace(-10,10,100)
    meshgridx,meshgridy = np.meshgrid(puntosx,puntosy)
    puntosz = np.pow(meshgridx,2) * np.pow(meshgridy,2)
    if len(indeterminado) > 0:
        puntosz = verificar(puntosz)  

com,ind = completa(meshgridx,meshgridy,puntosz)

ind = np.array(ind.flatten(),dtype=np.uint32)







