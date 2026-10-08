# pgzero
from math import pi, sin

WIDTH = 400
HEIGHT = 240
FPS = 30

background = Actor("mundomario1")
moneda= Actor("mon1", (264,130))
coap= Actor("cop", (400, 200))
ma = Actor("ma", (50, 195))
coopa = Actor("ko", (400,200))
cubo1 = Actor("cu1", (264,152))
cubo2 = Actor("cu2", (345,152))
cubo3 = Actor("cu3", (376,152))
cubo4 = Actor("cu4", (360,88))
cubos = [cubo1, cubo2, cubo3, cubo4]
posiciones_originales = [cubo.y for cubo in cubos]
tiempos_golpe = [None] * len(cubos)

# Contador para la animación
contador = 0
mode =  "game"
camera_x = 0
velocidad_y = 0
en_suelo = True
salto_presionado = False
posicion_suelo = ma.y
duracion_golpe = 0.25
altura_golpe = 12
posicion_camara = WIDTH / 2

def draw():
    if mode == "game":
        background.draw()
        moneda.draw()
        coap.draw()
        ma.draw()
        coopa.draw()
        for cubo in cubos:
            cubo.draw()
    elif mode == "end":
        screen.fill("black")
        screen.draw.text("game over",pos=(100,100),color="white",fontsize=24)


def update(dt):
    global contador, mode, camera_x, velocidad_y, en_suelo, salto_presionado


    if coopa.x <=0:
        coopa.x =400
    else:
        coopa.x -=1


    if keyboard.right:
        ma.x += 3
        limite_camara = background.width - WIDTH
        if ma.x > posicion_camara and camera_x < limite_camara:
            desplazamiento = min(ma.x - posicion_camara, limite_camara - camera_x)
            ma.x -= desplazamiento
            camera_x += desplazamiento
            background.x -= desplazamiento
            coopa.x -= desplazamiento
            for cubo in cubos:
                cubo.x -= desplazamiento

        if camera_x >= limite_camara:
            ma.x = min(ma.x, WIDTH - ma.width / 2)


        contador += 1

        if contador >= 5:
            contador = 0

            if ma.image == "marc1":
                ma.image = "marc2"
            else:
                ma.image = "marc1"
    elif keyboard.left:
        ma.x -= 3
        if ma.x < posicion_camara and camera_x > 0:
            desplazamiento = min(posicion_camara - ma.x, camera_x)
            ma.x += desplazamiento
            camera_x -= desplazamiento
            background.x += desplazamiento
            coopa.x += desplazamiento
            for cubo in cubos:
                cubo.x += desplazamiento

        if camera_x <= 0:
            ma.x = max(ma.x, ma.width / 2)
        contador += 1

        if contador >= 5:

            contador = 0

            if ma.image == "marc1left":
                ma.image = "marc2left"
            else:
                ma.image = "marc1left"
    else:
        # Cuando no se mueve, vuelve al sprite quieto
        ma.image = "ma"
        contador = 0

    if keyboard.space and not salto_presionado and en_suelo:
        velocidad_y = -420
        en_suelo = False
    salto_presionado = keyboard.space

    for indice, cubo in enumerate(cubos):
        if tiempos_golpe[indice] is not None:
            tiempos_golpe[indice] += dt
            if tiempos_golpe[indice] >= duracion_golpe:
                tiempos_golpe[indice] = None
                cubo.y = posiciones_originales[indice]
            else:
                cubo.y = posiciones_originales[indice] - altura_golpe * sin(
                    pi * tiempos_golpe[indice] / duracion_golpe
                )

    parte_superior_anterior = ma.top
    if not en_suelo:
        velocidad_y += 1100 * dt
        ma.y += velocidad_y * dt

        for indice, cubo in enumerate(cubos):
            if (
                velocidad_y < 0
                and ma.left < cubo.right
                and ma.right > cubo.left
                and parte_superior_anterior >= cubo.bottom
                and ma.top <= cubo.bottom
            ):
                ma.top = cubo.bottom
                velocidad_y = 0
                tiempos_golpe[indice] = 0
                break

        if ma.y >= posicion_suelo:
            ma.y = posicion_suelo
            velocidad_y = 0
            en_suelo = True

    if ma.colliderect(coopa):
        mode = "end"
