__author__ = 'n. marlow'

import socket
import sys
import pickle
import bs
import libtcodpy as libtcod
import time

STATE_SETUP = 0
STATE_OUR_TURN = 1
STATE_ENEMY_TURN = 2
STATE_BEGIN_GAME = 3
STATE_GAME_OVER = 4

host = raw_input("Enter server address: ")
port = 50000
size = 4096
current_state = STATE_SETUP

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
sys.stdout.write('client started')


libtcod.console_set_custom_font('prestige12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(60, 50, 'ASCIIship', False)
libtcod.sys_set_fps(60)
game = bs.Battleship()

while not libtcod.console_is_window_closed():
    if current_state != STATE_GAME_OVER:
        game.update()
    game.drawGameScreen()

    if current_state == STATE_SETUP:
        data = s.recv(size)
        if data:
            game.player.fleetBoats = pickle.loads(data)
            s.send("Fleet_OK")
            current_state = STATE_BEGIN_GAME
    elif current_state == STATE_BEGIN_GAME:
        data = s.recv(size)
        if data == "go":
            current_state = STATE_OUR_TURN
        elif data == "wait":
            current_state = STATE_ENEMY_TURN
            game.state = game.stateEnemyTarget

    elif current_state == STATE_OUR_TURN:
        game.state = game.statePlayerTarget
        keyInput = game.handleKeys()
        if keyInput == 'valid_shot':
            s.send(pickle.dumps(game.player.cursor))
            #wait for response
            data = s.recv(size)
            if data == "hit":
                game.enemy.playGrid[(game.player.cursor[0],game.player.cursor[1])] = 3 #tile code, see bs.py
            elif data == "miss":
                game.enemy.playGrid[(game.player.cursor[0],game.player.cursor[1])] = 2 #tile code, see bs.py
            data = s.recv(size)
            if data != 'win':
                current_state = STATE_ENEMY_TURN
                game.state = game.stateEnemyTarget
            else:
                game.statusText = ["Victory."]
                current_state = STATE_GAME_OVER

        elif keyInput == 'exit':
            break
    elif current_state == STATE_ENEMY_TURN:
        time.sleep(0.5)
        data = pickle.loads(s.recv(size))
        if data[0] == "hit":
            game.player.playGrid[(data[1],data[2])] = 3 #tile code, see bs.py

        elif data[0] == "miss":
            game.player.playGrid[(data[1],data[2])] = 2 #tile code, see bs.py
        data = s.recv(size)
        if data != 'lose':
            current_state = STATE_OUR_TURN
        else:
            game.statusText = ["Defeat."]
            current_state = STATE_GAME_OVER
        keyInput = game.handleKeys()
s.close()