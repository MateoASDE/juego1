# pgzero
from math import pi, sin
from pathlib import Path

import pygame
from pgzero import loaders

WIDTH = 400
HEIGHT = 240
FPS = 30

carpeta_proyecto = Path(__file__).resolve().parent
if not (carpeta_proyecto / "images").is_dir():
    carpeta_proyecto = Path.cwd()
if not (carpeta_proyecto / "images").is_dir():
    raise FileNotFoundError(
        "No se encontro la carpeta 'images' junto al juego ni en la carpeta actual."
    )

loaders.set_root(str(carpeta_proyecto))

background = Actor("mundomario1")
fondo_colisiones = pygame.image.load(
    str(carpeta_proyecto / "images" / "mundomario1.png")
)


def buscar_tubos():
    columnas = []
    for x in range(fondo_colisiones.get_width()):
        verdes = sum(
            fondo_colisiones.get_at((x, y))[:3] in ((0, 168, 0), (128, 208, 16))
            for y in range(145, 208)
        )
        columnas.append(verdes >= 20)

    tubos = []
    inicio = None
    for x, es_tubo in enumerate(columnas + [False]):
        if es_tubo and inicio is None:
            inicio = x
        elif not es_tubo and inicio is not None:
            if 16 <= x - inicio <= 36:
                tubos.append((inicio, x))
            inicio = None
    return tubos


tubos = buscar_tubos()
coap= Actor("cop", (400, 200))
ma = Actor("ma", (50, 195))
coopa = Actor("ko", (400,200))
ko_derrotado = False
tiempo_ko_derrotado = 0
duracion_ko_derrotado = 0.5
ladrillo = Actor("ladrillo", (100,152))
cubo1 = Actor("cu1", (264,152))
cubo2 = Actor("cu2", (345,152))
cubo3 = Actor("cu3", (376,152))
cubo4 = Actor("cu4", (360,88))
cubos = [cubo1, cubo2, cubo3, cubo4]
cubos.extend(
    Actor("cu1", posicion)
    for posicion in (
        (1256, 152),
        (1512, 88),
        (1704, 152),
        (1752, 88),
        (1752, 152),
        (1800, 152),
        (2072, 88),
        (2088, 88),
        (2728, 152),
    )
)
posiciones_originales = [cubo.y for cubo in cubos]
tiempos_golpe = [None] * len(cubos)
ladrillo= Actor("ladrillo")
hongo= Actor("hongo")
hongo.pos = cubo2.pos
monedas = [Actor("mon1", cubo.pos) for cubo in cubos]
monedas_activas = [False] * len(monedas)
monedas_reclamadas = [False] * len(monedas)
tiempos_salida_monedas = [None] * len(monedas)
duracion_salida_moneda = 0.3
# Contador para la animación
time = 400
tiempo_transcurrido = 0
contador = 0
mode =  "game"
coins = 0
score = 100
camera_x = 0
velocidad_y = 0
en_suelo = True
salto_presionado = False
posicion_suelo = ma.y
duracion_golpe = 0.25
altura_golpe = 12
posicion_camara = WIDTH / 2
lives = 3

def pixel_solido(x, y):
    x_fondo = round(x - background.left)
    y_fondo = round(y - background.top)
    if not (
        0 <= x_fondo < fondo_colisiones.get_width()
        and 0 <= y_fondo < fondo_colisiones.get_height()
    ):
        return False

    pixel = fondo_colisiones.get_at((x_fondo, y_fondo))
    color = (pixel.r, pixel.g, pixel.b)
    if color in ((0, 168, 0), (128, 208, 16)):
        return 145 <= y_fondo < 208 and any(
            inicio <= x_fondo < fin for inicio, fin in tubos
        )

    return color in (
        (200, 76, 12),
        (252, 188, 176),
        (252, 152, 56),
    )


def choca_lateral(x_anterior, direccion):
    if direccion > 0:
        borde_anterior = x_anterior + ma.width / 2
        borde_actual = ma.right
    else:
        borde_anterior = x_anterior - ma.width / 2
        borde_actual = ma.left

    inicio = min(int(borde_anterior), int(borde_actual))
    fin = max(int(borde_anterior), int(borde_actual))
    for x in range(inicio, fin + 1):
        for y in range(int(ma.top) + 2, int(ma.bottom) - 2):
            if pixel_solido(x, y):
                return True
    return False


def draw():
    if mode == "game":
        ladrillo.draw()
        background.draw()
        hongo.draw()
        ma.draw()
        screen.draw.text("score",pos=(10,0),color="white",fontsize=24)
        screen.draw.text("coins",pos=(70,0),color="white",fontsize=24)
        screen.draw.text("world",pos=(130,0),color="white",fontsize=24)
        screen.draw.text("time",pos=(190,0),color="white",fontsize=24)
        screen.draw.text("lives",pos=(240,0),color="white",fontsize=24)
        screen.draw.text(str(score),pos=(20,20),color="white",fontsize=20)
        screen.draw.text(str(coins),pos=(90,20),color="white",fontsize=20)
        screen.draw.text("1:1",pos=(140,20),color="white",fontsize=20)
        screen.draw.text(str(time),pos=(200,20),color="white",fontsize=20)
        screen.draw.text(str(lives),pos=(250,20),color="white",fontsize=20)
        if not ko_derrotado or tiempo_ko_derrotado < duracion_ko_derrotado:
            coopa.draw()
        for cubo in cubos:
            cubo.draw()
        for indice, moneda_actual in enumerate(monedas):
            if monedas_activas[indice]:
                moneda_actual.draw()
    elif mode == "end":
        screen.fill("black")
        screen.draw.text("game over",pos=(100,100),color="white",fontsize=24)


def update(dt):
    global contador, mode, camera_x, velocidad_y, en_suelo, salto_presionado, coins
    global time, tiempo_transcurrido
    global ko_derrotado, tiempo_ko_derrotado
    #sounds.mario.play()

    if mode == "game" and time > 0:
        tiempo_transcurrido += dt
        while tiempo_transcurrido >= 1:
            time -= 1
            tiempo_transcurrido -= 1

    if ko_derrotado:
        tiempo_ko_derrotado += dt
    elif coopa.x <=0:
        coopa.x =400
    else:
        coopa.x -=1


    if keyboard.right:
        x_anterior = ma.x
        ma.x += 3
        if choca_lateral(x_anterior, 1):
            ma.x = x_anterior
        limite_camara = background.width - WIDTH
        if ma.x > posicion_camara and camera_x < limite_camara:
            desplazamiento = min(ma.x - posicion_camara, limite_camara - camera_x)
            ma.x -= desplazamiento
            camera_x += desplazamiento
            background.x -= desplazamiento
            coopa.x -= desplazamiento
            hongo.x -= desplazamiento
            for moneda_actual in monedas:
                moneda_actual.x -= desplazamiento
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
        x_anterior = ma.x
        ma.x -= 3
        if choca_lateral(x_anterior, -1):
            ma.x = x_anterior
        if ma.x < posicion_camara and camera_x > 0:
            desplazamiento = min(posicion_camara - ma.x, camera_x)
            ma.x += desplazamiento
            camera_x -= desplazamiento
            background.x += desplazamiento
            coopa.x += desplazamiento
            hongo.x += desplazamiento
            for moneda_actual in monedas:
                moneda_actual.x += desplazamiento
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

    if en_suelo and ma.y < posicion_suelo and not any(
        pixel_solido(x, ma.bottom) for x in (ma.left + 2, ma.centerx, ma.right - 2)
    ):
        en_suelo = False

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

    for indice, moneda_actual in enumerate(monedas):
        if tiempos_salida_monedas[indice] is not None:
            tiempos_salida_monedas[indice] += dt
            progreso = min(
                tiempos_salida_monedas[indice] / duracion_salida_moneda, 1
            )
            y_final = (
                posiciones_originales[indice]
                - cubos[indice].height / 2
                - moneda_actual.height / 2
                - 2
            )
            moneda_actual.y = cubos[indice].y + (
                y_final - cubos[indice].y
            ) * sin(pi * progreso / 2)
            if progreso >= 1:
                tiempos_salida_monedas[indice] = None

        if monedas_activas[indice] and ma.colliderect(moneda_actual):
            monedas_activas[indice] = False
            monedas_reclamadas[indice] = True
            coins += 1

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

        if velocidad_y > 0:
            for y in range(int(parte_inferior_anterior) + 1, int(ma.bottom) + 1):
                if any(pixel_solido(x, y) for x in range(int(ma.left), int(ma.right))):
                    ma.bottom = y
                    velocidad_y = 0
                    en_suelo = True
                    break

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
                if not monedas_reclamadas[indice]:
                    monedas_activas[indice] = True
                    tiempos_salida_monedas[indice] = 0
                    monedas[indice].pos = cubo.pos
                break

        if velocidad_y < 0:
            for y in range(int(parte_superior_anterior), int(ma.top) - 1, -1):
                if any(pixel_solido(x, y) for x in range(int(ma.left), int(ma.right))):
                    ma.top = y + 1
                    velocidad_y = 0
                    break

        if ma.y >= posicion_suelo:
            ma.y = posicion_suelo
            velocidad_y = 0
            en_suelo = True

    if not ko_derrotado and ma.colliderect(coopa):
        mode = "end"
