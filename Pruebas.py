import numpy as np
import math as mt

def producto_punto(x,y):
    x,y = np.array(x), np.array(y)
    propu = np.sum(x * y)
    normax = (np.sum(x ** 2)) ** 0.5
    normay = (np.sum(y ** 2)) ** 0.5
    angulo = propu / (normax * normay)
    return (propu,angulo)

def producto_cruz (x,y):
    a1,a2,a3 = x[0],x[1],x[2]
    b1,b2,b3 = y[0],y[1],y[2]
    cx = a2 * b3 - a3 * b2
    cy = a3 * b1 - a1 * b3
    cz = a1 * b2 - a2 * b1
    return [cx,cy,cz]

def normal_triangulo (a,b,c):
    a,b,c = np.array(a),np.array(b),np.array(c) 
    normal = producto_cruz((b - a),(c - a))
    return normal



puntosx, puntosy = np.linspace(-6,6,50), np.linspace(-6,6,50)
meshgridx,meshgridy = np.meshgrid(puntosx,puntosy)

funcion = np.sin(meshgridx) * np.sin(meshgridy)

x= meshgridx.flatten()
y= meshgridy.flatten()
z= funcion.flatten()
vectores = np.column_stack([x,y,z])






