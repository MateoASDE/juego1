# pgzero
WIDTH = 400
HEIGHT = 240
FPS = 30

background = Actor("mundomario1")
ma = Actor("ma", (50, 195))
coopa = Actor("ko", (400,200))
cubo1 = Actor("cu1", (264,152))
cubo2 = Actor("cu2", (345,152))
cubo3 = Actor("cu3", (376,152))
cubo4 = Actor("cu4", (360,88))

# Contador para la animación
contador = 0
mode =  "game"

def draw():
    if mode == "game":
        background.draw()
        ma.draw()
        coopa.draw()
        cubo1.draw()
        cubo2.draw()
        cubo3.draw()
        cubo4.draw()
    elif mode == "end":
        screen.fill("black")
        screen.draw.text("game over",pos=(100,100),color="white",fontsize=24)


def update(dt):
    global contador,mode


    if coopa.x <=0:
        coopa.x =400
    else:
        coopa.x -=1


    if keyboard.right:
        ma.x += 5

        contador += 1

        if contador >= 5:
            contador = 0

            if ma.image == "marc1":
                ma.image = "marc2"
            else:
                ma.image = "marc1"
    elif keyboard.left:
        ma.x -= 5
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

    if ma.colliderect(coopa):
        mode = "end"
