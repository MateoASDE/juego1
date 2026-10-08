# pgzero
from math import pi, sin

WIDTH = 400
HEIGHT = 240
FPS = 30

background = Actor("mundomario1")
coap= Actor("cop", (400, 200))
ma = Actor("ma", (50, 195))
coopa = Actor("ko", (400,200))
ko_derrotado = False
tiempo_ko_derrotado = 0
duracion_ko_derrotado = 0.5
espera_reaparicion_ko = 0.5
cubo1 = Actor("cu1", (264,152))
cubo2 = Actor("cu2", (345,152))
cubo3 = Actor("cu3", (376,152))
cubo4 = Actor("cu4", (360,88))
cubos = [cubo1, cubo2, cubo3, cubo4]
posiciones_originales = [cubo.y for cubo in cubos]
tiempos_golpe = [None] * len(cubos)
hongo= Actor("hongo")
hongo.pos = cubo2.pos
moneda= Actor("mon1")
moneda.pos = cubo1.pos
moneda1 = Actor("mon1")
moneda1.pos = cubo3.pos
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
        hongo.draw()
        moneda.draw()
        ma.draw()
        if not ko_derrotado or tiempo_ko_derrotado < duracion_ko_derrotado:
            coopa.draw()
        moneda1.draw()
        for cubo in cubos:
            cubo.draw()
    elif mode == "end":
        screen.fill("black")
        screen.draw.text("game over",pos=(100,100),color="white",fontsize=24)


def update(dt):
    global contador, mode, camera_x, velocidad_y, en_suelo, salto_presionado
    global ko_derrotado, tiempo_ko_derrotado


    if ko_derrotado:
        tiempo_ko_derrotado += dt
        if tiempo_ko_derrotado >= duracion_ko_derrotado + espera_reaparicion_ko:
            coopa.pos = (400, 200)
            coopa.image = "ko"
            ko_derrotado = False
            tiempo_ko_derrotado = 0
    elif coopa.x <=0:
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
            hongo.x -= desplazamiento
            moneda1.x -= desplazamiento
            moneda.x -= desplazamiento
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
            hongo.x += desplazamiento
            moneda1.x += desplazamiento
            moneda.x += desplazamiento
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
    parte_inferior_anterior = ma.bottom
    if not en_suelo:
        velocidad_y += 1100 * dt
        ma.y += velocidad_y * dt

        if (
            not ko_derrotado
            and velocidad_y > 0
            and ma.left < coopa.right
            and ma.right > coopa.left
            and parte_inferior_anterior <= coopa.top
            and ma.bottom >= coopa.top
        ):
            ma.bottom = coopa.top
            coopa.image = "cop"
            ko_derrotado = True
            tiempo_ko_derrotado = 0
            velocidad_y = -250

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

    if not ko_derrotado and ma.colliderect(coopa):
        mode = "end"
