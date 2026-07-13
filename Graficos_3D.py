import numpy as np
import warnings
import colorsys as color

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

    colores = np.round(231 + 120 * (normalizado)) 
    luminosidad = np.round(40 + 30 * (normalizado))

    colores = np.column_stack([colores,luminosidad]) 
    rgb = []
    for c,l in colores:
        i = (c) / (360)
        e = l / 100
        r,g,b = color.hls_to_rgb(i,e,1)
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

def usuario (fun):
    operaciones = {
        "raiz": np.sqrt,      "log": np.log,
        "exp":  np.exp,       "sin": np.sin,
        "cos":  np.cos,       "tan": np.tan,
        "pi" :  np.pi,        "e"  : np.e,
        "abs":  np.abs        
    }

    try:
        realizar = compile(fun, '<string>', 'eval')
    except Exception as error:
        return None, str(error)
    
    def f(x,y):
        incog = {"x" : x, "y": y, **operaciones}
        return eval(realizar, None, incog)

    return f, None

def malla (meshx,meshy,meshz,cuad=3):

    lineas = []

    fil,col = meshx.shape

    mx = meshx.copy()
    my = meshy.copy()
    mz = meshz.copy()
    for arr in [mx, my, mz]:
        vmax = np.abs(arr).max()
        if vmax > 0:
            arr /= vmax

    for i in range(0,fil,cuad):
        for j in range(col - 1):
            lineas.append([float(mx[i,j]), float(my[i,j]), float(mz[i,j])])
            lineas.append([float(mx[i,j + 1]), float(my[i,j + 1]), float(mz[i,j + 1])])

    for i in range(0,col,cuad):
        for j in range(fil - 1):
            lineas.append([float(mx[j,i]), float(my[j,i]), float(mz[j,i])])
            lineas.append([float(mx[j + 1,i]), float(my[j + 1,i]), float(mz[j + 1,i])]) 
    
    return np.array(lineas, dtype=np.float32)

def ejes(largo=12.0, radio_flecha=0.3, altura_flecha=0.8, segmentos=12):

    def cono(origen, punta, derecha, arriba, r, h, segs, color):
        tris = []
        base = origen  
        for i in range(segs):
            a0 = 2 * np.pi * i / segs
            a1 = 2 * np.pi * (i + 1) / segs
            p0 = base + r * (np.cos(a0) * derecha + np.sin(a0) * arriba)
            p1 = base + r * (np.cos(a1) * derecha + np.sin(a1) * arriba)
            tris.extend([
                [*p0, *color],
                [*p1, *color],
                [*punta, *color],
            ])
        return tris

    lineas = []
    tris   = []

    lineas.extend([[0,0,0, 1.0,0.2,0.2], [largo,0,0, 1.0,0.2,0.2]])
    tris.extend(cono(
        origen  = np.array([largo, 0, 0]),
        punta   = np.array([largo + altura_flecha, 0, 0]),
        derecha = np.array([0, 1, 0]),
        arriba  = np.array([0, 0, 1]),
        r=radio_flecha, h=altura_flecha, segs=segmentos,
        color=[1.0, 0.2, 0.2]
    ))

    lineas.extend([[0,0,0, 0.2,1.0,0.2], [0,largo,0, 0.2,1.0,0.2]])
    tris.extend(cono(
        origen  = np.array([0, largo, 0]),
        punta   = np.array([0, largo + altura_flecha, 0]),
        derecha = np.array([1, 0, 0]),
        arriba  = np.array([0, 0, 1]),
        r=radio_flecha, h=altura_flecha, segs=segmentos,
        color=[0.2, 1.0, 0.2]
    ))

    lineas.extend([[0,0,0, 0.2,0.4,1.0], [0,0,largo, 0.2,0.4,1.0]])
    tris.extend(cono(
        origen  = np.array([0, 0, largo]),
        punta   = np.array([0, 0, largo + altura_flecha]),
        derecha = np.array([1, 0, 0]),
        arriba  = np.array([0, 1, 0]),
        r=radio_flecha, h=altura_flecha, segs=segmentos,
        color=[0.2, 0.4, 1.0]
    ))

    return (np.array(lineas, dtype=np.float32),
            np.array(tris,   dtype=np.float32))

def generar(fun):
    try:
        f, error = usuario(fun)
        if error:
            return None,None,None,error
        
        # Si existe algun valor que matematicamente es imposible, existe "RuntimeWarning"
        # El codigo lo detecta y aplica la funcion verificar, si no, continúa
        with warnings.catch_warnings(record=True) as indeterminado:
            puntosx, puntosy = np.linspace(-10,10,150), np.linspace(-10,10,150)
            meshx,meshy = np.meshgrid(puntosx,puntosy)
            puntosz = f(meshx,meshy)
            if len(indeterminado) > 0:
                puntosz = verificar(puntosz)  

        com,ind = completa(meshx,meshy,puntosz)
        ind = np.array(ind.flatten(),dtype=np.uint32)
        cuadricula = malla(meshx, meshy, puntosz, cuad=3)
        
        return com, ind, cuadricula, None

    except Exception as error:
        return None, None, None, str(error)
    
ejes_lineas, ejes_tris = ejes()

com, ind, cuadricula, _ = np.array([0.0]),np.array([0.0]),np.array([0.0]),None






