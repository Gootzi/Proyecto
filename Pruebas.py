import numpy as np

a = np.linspace(-2,2,5)
b = np.linspace(-2,2,5)
meshx,meshy = np.meshgrid(a,b)
meshz = meshx*meshy

print(a)
#print(meshx,meshy)
#print(meshz)

def colores (z):
    # Elige los colores en hls y los pasa a rgb y los asigna a un punto z en el espacio
    z = z.flatten()
    normalizado = (z - z.min()) / (z.max()-z.min())

    print(normalizado)

    colores = np.round(231 + 78 * (normalizado)) 
    luminosidad = np.round(40 + 30 * (normalizado))

    print(colores,luminosidad)

#colores(meshz)

    
