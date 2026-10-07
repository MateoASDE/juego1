#pgzero
WIDTH = 400
HEIGHT = 240
FPS = 30

background = Actor("mundomario1")
ma = Actor("ma", (50, 190))
ko = Actor("ko", (350, 190))

ground_y = 190
player_speed = 3
jump_speed = -9
gravity = 0.45
player_velocity_y = 0
enemy_speed = 1.5
coins = [(115, 155), (190, 125), (265, 155), (330, 130)]
score = 0
game_over = False
contador = 0


def draw():
    background.draw()
    for coin_x, coin_y in coins:
        screen.draw.filled_circle((coin_x, coin_y), 6, "gold")
        screen.draw.circle((coin_x, coin_y), 6, "yellow")
    ma.draw()
    ko.draw()
    screen.draw.text("MONEDAS: " + str(score), (10, 10), color="white", fontsize=22)
    screen.draw.text("Flechas: mover   Espacio: saltar", (10, 218), color="white", fontsize=14)
    if game_over:
        screen.draw.text("FIN DEL JUEGO - pulsa R", center=(WIDTH / 2, HEIGHT / 2),
                         color="white", fontsize=24)


def update(dt):
    global contador, player_velocity_y, enemy_speed, score, game_over

    if game_over:
        if keyboard.r:
            ma.pos = (50, ground_y)
            ko.pos = (350, ground_y)
            player_velocity_y = 0
            score = 0
            coins[:] = [(115, 155), (190, 125), (265, 155), (330, 130)]
            game_over = False
        return

    moving = False
    if keyboard.right:
        ma.x += player_speed
        moving = True
    if keyboard.left:
        ma.x -= player_speed
        moving = True
    ma.x = max(ma.width / 2, min(WIDTH - ma.width / 2, ma.x))

    if (keyboard.space or keyboard.up) and ma.y >= ground_y:
        player_velocity_y = jump_speed
    player_velocity_y += gravity
    ma.y += player_velocity_y
    if ma.y >= ground_y:
        ma.y = ground_y
        player_velocity_y = 0

    if moving:
        contador += 1
        if contador >= 5:
            contador = 0
            ma.image = "marc2" if ma.image == "marc1" else "marc1"
    else:
        ma.image = "ma"
        contador = 0

    ko.x += enemy_speed
    if ko.x >= WIDTH - ko.width / 2 or ko.x <= ko.width / 2:
        enemy_speed *= -1

    for coin in coins[:]:
        if abs(ma.x - coin[0]) < 16 and abs(ma.y - coin[1]) < 18:
            coins.remove(coin)
            score += 1

    if ma.colliderect(ko):
        if player_velocity_y > 0 and ma.bottom < ko.y + 4:
            ko.x = -100
            player_velocity_y = jump_speed / 2
            score += 1
        else:
            game_over = True
