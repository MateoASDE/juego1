# pgzero
from math import ceil, pi, sin
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
coopas = [
    Actor("ko", (x, 200))
    for x in (400, 800, 1200, 1600, 2000, 2400, 2800, 3200)
]
direcciones_coopa = [-1] * len(coopas)
koopas_derrotadas = [False] * len(coopas)
tiempos_ko_derrotado = [0] * len(coopas)
duracion_ko_derrotado = 0.5
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
posiciones_ladrillos = (
    (328, 152),
    (360, 152),
    (392, 152),
    (1240, 152),
    (1272, 152),
    (1288, 88),
    (1304, 88),
    (1320, 88),
    (1336, 88),
    (1352, 88),
    (1368, 88),
    (1384, 88),
    (1400, 88),
    (1464, 88),
    (1480, 88),
    (1496, 88),
    (1608, 152),
    (1624, 152),
    (1896, 152),
    (1944, 88),
    (1960, 88),
    (1976, 88),
    (2056, 88),
    (2072, 152),
    (2088, 152),
    (2104, 88),
    (2696, 152),
    (2712, 152),
    (2744, 152),
)
ladrillos = [Actor("ladrillo", posicion) for posicion in posiciones_ladrillos]
ladrillos_rotos = []
imagen_ladrillo = pygame.image.load(
    str(carpeta_proyecto / "images" / "ladrillo.png")
)
sprites_fragmentos_ladrillo = [
    imagen_ladrillo.subsurface((x, y, 7, 7)).copy()
    for x, y in ((0, 0), (8, 0), (0, 8), (8, 8))
]
fragmentos_ladrillo = []
duracion_fragmentos_ladrillo = 0.8
posiciones_originales = [cubo.y for cubo in cubos]
tiempos_golpe = [None] * len(cubos)
indice_bloque_hongo = 1
hongo = Actor("hongo", cubos[indice_bloque_hongo].pos)
hongo_visible = False
tiempo_salida_hongo = None
velocidad_hongo_x = 45
velocidad_hongo_y = 0
monedas = [Actor("mon1", cubo.pos) for cubo in cubos]
monedas_activas = [False] * len(monedas)
bloques_usados = [False] * len(cubos)
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
mario_grande = False
sprites_mario_grande = {}


def ancho_mario():
    return ma.width * (4 / 3 if mario_grande else 1)


def alto_mario():
    return ma.height * (4 / 3 if mario_grande else 1)


def izquierda_mario():
    return ma.x - ancho_mario() / 2


def derecha_mario():
    return ma.x + ancho_mario() / 2


def arriba_mario():
    return ma.y - alto_mario() / 2


def abajo_mario():
    return ma.y + alto_mario() / 2


def mario_choca(actor):
    return (
        izquierda_mario() < actor.right
        and derecha_mario() > actor.left
        and arriba_mario() < actor.bottom
        and abajo_mario() > actor.top
    )


def dibujar_mario():
    if not mario_grande:
        ma.draw()
        return

    if ma.image not in sprites_mario_grande:
        imagen = pygame.image.load(
            str(carpeta_proyecto / "images" / f"{ma.image}.png")
        )
        sprites_mario_grande[ma.image] = pygame.transform.scale(
            imagen, (round(ancho_mario()), round(alto_mario()))
        )
    sprite = sprites_mario_grande[ma.image]
    screen.surface.blit(sprite, sprite.get_rect(center=ma.pos))

def pixel_solido(x, y):
    x_fondo = round(x - background.left)
    y_fondo = round(y - background.top)
    if not (
        0 <= x_fondo < fondo_colisiones.get_width()
        and 0 <= y_fondo < fondo_colisiones.get_height()
    ):
        return False

    pixel = fondo_colisiones.get_at((x_fondo, y_fondo))
    if any(
        izquierda <= x_fondo < izquierda + 16
        and arriba <= y_fondo < arriba + 16
        for izquierda, arriba in ladrillos_rotos
    ):
        return False

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


def hongo_choca_objeto(x, y):
    izquierda = x - hongo.width / 2
    derecha = x + hongo.width / 2
    arriba = y - hongo.height / 2
    abajo = y + hongo.height / 2
    return any(
        izquierda < objeto.right
        and derecha > objeto.left
        and arriba < objeto.bottom
        and abajo > objeto.top
        for objeto in (*cubos, *ladrillos)
    )


def mover_hongo(dt):
    global velocidad_hongo_x, velocidad_hongo_y

    desplazamiento_x = velocidad_hongo_x * dt
    pasos_x = max(1, ceil(abs(desplazamiento_x)))
    for _ in range(pasos_x):
        x_siguiente = hongo.x + desplazamiento_x / pasos_x
        borde_mundo_izquierdo = camera_x + x_siguiente - hongo.width / 2
        borde_mundo_derecho = camera_x + x_siguiente + hongo.width / 2
        borde_x = x_siguiente + (
            hongo.width / 2 if velocidad_hongo_x > 0 else -hongo.width / 2
        )
        colision_lateral = any(
            pixel_solido(borde_x, y)
            for y in range(int(hongo.top) + 1, int(hongo.bottom) - 1)
        ) or hongo_choca_objeto(x_siguiente, hongo.y)

        if (
            borde_mundo_izquierdo < 0
            or borde_mundo_derecho > background.width
            or colision_lateral
        ):
            velocidad_hongo_x *= -1
            break
        hongo.x = x_siguiente

    y_anterior = hongo.y
    abajo_anterior = y_anterior + hongo.height / 2
    velocidad_hongo_y += 900 * dt
    y_siguiente = y_anterior + velocidad_hongo_y * dt
    abajo_siguiente = y_siguiente + hongo.height / 2
    izquierda = int(hongo.left) + 1
    derecha = int(hongo.right) - 1

    for y in range(int(abajo_anterior) + 1, int(abajo_siguiente) + 1):
        colision_suelo = any(pixel_solido(x, y) for x in range(izquierda, derecha))
        colision_bloque = any(
            izquierda < objeto.right
            and derecha > objeto.left
            and abajo_anterior <= objeto.top <= abajo_siguiente
            for objeto in (*cubos, *ladrillos)
        )
        if colision_suelo or colision_bloque:
            hongo.bottom = y if colision_suelo else min(
                objeto.top
                for objeto in (*cubos, *ladrillos)
                if izquierda < objeto.right
                and derecha > objeto.left
                and abajo_anterior <= objeto.top <= abajo_siguiente
            )
            velocidad_hongo_y = 0
            break
    else:
        hongo.y = y_siguiente


def choca_lateral(x_anterior, direccion):
    if direccion > 0:
        borde_anterior = x_anterior + ancho_mario() / 2
        borde_actual = derecha_mario()
    else:
        borde_anterior = x_anterior - ancho_mario() / 2
        borde_actual = izquierda_mario()

    inicio = min(int(borde_anterior), int(borde_actual))
    fin = max(int(borde_anterior), int(borde_actual))
    for x in range(inicio, fin + 1):
        for y in range(int(arriba_mario()) + 2, int(abajo_mario()) - 2):
            if pixel_solido(x, y):
                return True
    return False


def coopa_choca_solido(coopa, x_siguiente, direccion):
    borde_actual = coopa.right if direccion > 0 else coopa.left
    borde_siguiente = (
        x_siguiente + coopa.width / 2
        if direccion > 0
        else x_siguiente - coopa.width / 2
    )
    inicio = min(int(borde_actual), int(borde_siguiente))
    fin = max(int(borde_actual), int(borde_siguiente))

    for x in range(inicio, fin + 1):
        for y in range(int(coopa.top) + 1, int(coopa.bottom) - 1):
            if pixel_solido(x, y):
                return True

    siguiente_izquierda = x_siguiente - coopa.width / 2
    siguiente_derecha = x_siguiente + coopa.width / 2
    return any(
        siguiente_izquierda < objeto.right
        and siguiente_derecha > objeto.left
        and coopa.top < objeto.bottom
        and coopa.bottom > objeto.top
        for objeto in (*cubos, *ladrillos)
    )


def draw():
    if mode == "game":
        background.draw()
        for izquierda, arriba in ladrillos_rotos:
            screen.draw.filled_rect(
                pygame.Rect(
                    round(background.left + izquierda),
                    round(background.top + arriba),
                    16,
                    16,
                ),
                (92, 148, 252),
            )
        for x, y, velocidad_x, velocidad_y, _, sprite in fragmentos_ladrillo:
            screen.surface.blit(sprite, (round(x), round(y)))
        for ladrillo in ladrillos:
            ladrillo.draw()
        if hongo_visible:
            hongo.draw()
        dibujar_mario()
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
        for indice, coopa in enumerate(coopas):
            if (
                not koopas_derrotadas[indice]
                or tiempos_ko_derrotado[indice] < duracion_ko_derrotado
            ):
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
    global hongo_visible, tiempo_salida_hongo
    global mario_grande
    global velocidad_hongo_x, velocidad_hongo_y
    #sounds.mario.play()

    if mode == "game" and time > 0:
        tiempo_transcurrido += dt
        while tiempo_transcurrido >= 1:
            time -= 1
            tiempo_transcurrido -= 1

    for fragmento in fragmentos_ladrillo:
        fragmento[4] += dt
        fragmento[0] += fragmento[2] * dt
        fragmento[1] += fragmento[3] * dt
        fragmento[3] += 700 * dt
    fragmentos_ladrillo[:] = [
        fragmento
        for fragmento in fragmentos_ladrillo
        if fragmento[4] < duracion_fragmentos_ladrillo
    ]

    for indice, coopa in enumerate(coopas):
        if koopas_derrotadas[indice]:
            tiempos_ko_derrotado[indice] += dt
            continue

        direccion = direcciones_coopa[indice]
        x_siguiente = coopa.x + direccion * 30 * dt
        borde_mundo_izquierdo = camera_x + x_siguiente - coopa.width / 2
        borde_mundo_derecho = camera_x + x_siguiente + coopa.width / 2
        if (
            borde_mundo_izquierdo < 0
            or borde_mundo_derecho > background.width
            or coopa_choca_solido(coopa, x_siguiente, direccion)
        ):
            direcciones_coopa[indice] *= -1
        else:
            coopa.x = x_siguiente


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
            for coopa in coopas:
                coopa.x -= desplazamiento
            hongo.x -= desplazamiento
            for moneda_actual in monedas:
                moneda_actual.x -= desplazamiento
            for cubo in cubos:
                cubo.x -= desplazamiento
            for ladrillo in ladrillos:
                ladrillo.x -= desplazamiento
            for fragmento in fragmentos_ladrillo:
                fragmento[0] -= desplazamiento

        if camera_x >= limite_camara:
            ma.x = min(ma.x, WIDTH - ancho_mario() / 2)


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
            for coopa in coopas:
                coopa.x += desplazamiento
            hongo.x += desplazamiento
            for moneda_actual in monedas:
                moneda_actual.x += desplazamiento
            for cubo in cubos:
                cubo.x += desplazamiento
            for ladrillo in ladrillos:
                ladrillo.x += desplazamiento
            for fragmento in fragmentos_ladrillo:
                fragmento[0] += desplazamiento

        if camera_x <= 0:
            ma.x = max(ma.x, ancho_mario() / 2)
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
        pixel_solido(x, abajo_mario())
        for x in (izquierda_mario() + 2, ma.x, derecha_mario() - 2)
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

    if tiempo_salida_hongo is not None:
        tiempo_salida_hongo += dt
        progreso = min(tiempo_salida_hongo / duracion_salida_moneda, 1)
        cubo_hongo = cubos[indice_bloque_hongo]
        y_final = (
            cubo_hongo.y
            - cubo_hongo.height / 2
            - hongo.height / 2
            - 2
        )
        hongo.y = cubo_hongo.y + (y_final - cubo_hongo.y) * sin(pi * progreso / 2)
        if progreso >= 1:
            tiempo_salida_hongo = None

    if hongo_visible and tiempo_salida_hongo is None:
        mover_hongo(dt)
        if hongo.top >= HEIGHT:
            hongo_visible = False

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

        if monedas_activas[indice] and mario_choca(moneda_actual):
            monedas_activas[indice] = False
            coins += 1

    if (
        hongo_visible
        and tiempo_salida_hongo is None
        and not mario_grande
        and mario_choca(hongo)
    ):
        altura_anterior = alto_mario()
        mario_grande = True
        ma.y -= (alto_mario() - altura_anterior) / 2
        hongo_visible = False

    parte_superior_anterior = arriba_mario()
    parte_inferior_anterior = abajo_mario()
    if not en_suelo:
        velocidad_y += 1100 * dt
        ma.y += velocidad_y * dt

        if velocidad_y > 0:
            for indice, coopa in enumerate(coopas):
                if (
                    not koopas_derrotadas[indice]
                    and izquierda_mario() < coopa.right
                    and derecha_mario() > coopa.left
                    and parte_inferior_anterior <= coopa.top
                    and abajo_mario() >= coopa.top
                ):
                    ma.y = coopa.top - alto_mario() / 2
                    coopa.image = "cop"
                    koopas_derrotadas[indice] = True
                    tiempos_ko_derrotado[indice] = 0
                    velocidad_y = -250
                    break

        if velocidad_y > 0:
            for y in range(int(parte_inferior_anterior) + 1, int(abajo_mario()) + 1):
                if any(
                    pixel_solido(x, y)
                    for x in range(int(izquierda_mario()), int(derecha_mario()))
                ):
                    ma.y = y - alto_mario() / 2
                    velocidad_y = 0
                    en_suelo = True
                    break

        for indice, cubo in enumerate(cubos):
            if (
                velocidad_y < 0
                and izquierda_mario() < cubo.right
                and derecha_mario() > cubo.left
                and parte_superior_anterior >= cubo.bottom
                and arriba_mario() <= cubo.bottom
            ):
                ma.y = cubo.bottom + alto_mario() / 2
                velocidad_y = 0
                if not bloques_usados[indice]:
                    bloques_usados[indice] = True
                    cubo.image = "cu_usado"
                    tiempos_golpe[indice] = 0
                    if indice == indice_bloque_hongo:
                        hongo_visible = True
                        hongo.pos = cubo.pos
                        tiempo_salida_hongo = 0
                        velocidad_hongo_x = 45
                        velocidad_hongo_y = 0
                    else:
                        monedas_activas[indice] = True
                        tiempos_salida_monedas[indice] = 0
                        monedas[indice].pos = cubo.pos
                break

        if velocidad_y < 0:
            for ladrillo in ladrillos:
                if (
                    izquierda_mario() < ladrillo.right
                    and derecha_mario() > ladrillo.left
                    and parte_superior_anterior >= ladrillo.bottom
                    and arriba_mario() <= ladrillo.bottom
                ):
                    ma.y = ladrillo.bottom + alto_mario() / 2
                    velocidad_y = 0
                    izquierda = round(ladrillo.centerx - 8 - background.left)
                    arriba = round(ladrillo.centery - 8 - background.top)
                    ladrillos_rotos.append((izquierda, arriba))
                    for indice, sprite in enumerate(sprites_fragmentos_ladrillo):
                        fragmentos_ladrillo.append(
                            [
                                ladrillo.left + (indice % 2) * 8,
                                ladrillo.top + (indice // 2) * 8,
                                (-110 if indice % 2 == 0 else 110),
                                (-190 if indice // 2 == 0 else -90),
                                0,
                                sprite,
                            ]
                        )
                    ladrillos.remove(ladrillo)
                    break

        if velocidad_y < 0:
            for y in range(int(parte_superior_anterior), int(arriba_mario()) - 1, -1):
                if any(
                    pixel_solido(x, y)
                    for x in range(int(izquierda_mario()), int(derecha_mario()))
                ):
                    ma.y = y + 1 + alto_mario() / 2
                    velocidad_y = 0
                    break

        if arriba_mario() >= HEIGHT:
            mode = "end"
            return

    if any(
        not koopas_derrotadas[indice] and mario_choca(coopa)
        for indice, coopa in enumerate(coopas)
    ):
        mode = "end"
