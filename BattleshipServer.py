__author__ = 'n. marlow'

import select
import socket
import bs
import pickle

STATE_WAITING_FOR_PLAYERS = 0
STATE_INITIALIZE_GAME_BOARD = 1
STATE_P1_TURN = 2
STATE_P2_TURN = 3
STATE_GAME_OVER = 4

current_state = STATE_WAITING_FOR_PLAYERS
host = ''
port = 50000
backlog = 5
size = 4096
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(backlog)
input = [server]
running = 1

p1_fleet = bs.Fleet()
p2_fleet = bs.Fleet()

while running:

    if current_state == STATE_WAITING_FOR_PLAYERS:
        print("waiting for " + str(3 - len(input)) + " players...")
        inputready,outputready,exceptready = select.select(input,[],[])

        for s in inputready:

            if s == server:
                # handle the server socket
                client, address = server.accept()
                input.append(client)
                print('client connected')
                if(len(input) == 3):
                    current_state = STATE_INITIALIZE_GAME_BOARD

    elif current_state == STATE_INITIALIZE_GAME_BOARD:
        p1_fleet = bs.Fleet()
        p2_fleet = bs.Fleet()
        #set up both players' fleets here.
        p1_fleet.randomizeBoats()
        p2_fleet.randomizeBoats()

        print("sending fleet data to clients...")
        #send each player their own fleet info, first client to connect will be player 1
        for player in xrange(len(input)):
            if input[player] != server:
                if player == 1:
                    input[player].send(pickle.dumps(p1_fleet.fleetBoats))
                elif player == 2:
                    input[player].send(pickle.dumps(p2_fleet.fleetBoats))

        #wait for verification that the players got their things
        confirmed = 0
        while confirmed != len(input) - 1:
            print("waiting for confirmation from clients...")
            inputready,outputready,exceptready = select.select(input,[],[])
            for s in inputready:
                if s != server:
                    data = s.recv(size)
                    if data == "Fleet_OK":
                        confirmed += 1

        #once both are set up, start the turn sequence
        print("starting turn sequence...")
        input[1].send("go")
        input[2].send("wait")
        current_state = STATE_P1_TURN
    elif current_state == STATE_P1_TURN:
        inputready,outputready,exceptready = select.select(input,[],[])
        cursorLoc = pickle.loads(input[1].recv(size))
        p1_fleet.cursor = cursorLoc
        shot = p1_fleet.fireRound(p2_fleet)
        input[1].send(shot)
        input[2].send(pickle.dumps((shot,cursorLoc[0],cursorLoc[1])))

        if p2_fleet.isDead():
            current_state = STATE_GAME_OVER
            input[1].send('win')
            input[2].send('lose')
        else:
            input[1].send('p2t')
            input[2].send('p2t')
            current_state = STATE_P2_TURN
    elif current_state == STATE_P2_TURN:
        inputready,outputready,exceptready = select.select(input,[],[])
        cursorLoc = pickle.loads(input[2].recv(size))
        p2_fleet.cursor = cursorLoc
        shot = p2_fleet.fireRound(p1_fleet)
        print(shot)
        input[2].send(shot)
        input[1].send(pickle.dumps((shot,cursorLoc[0],cursorLoc[1])))
        if p1_fleet.isDead():
            current_state = STATE_GAME_OVER
            input[1].send('lose')
            input[2].send('win')
        else:
            input[1].send('p1t')
            input[2].send('p1t')
            current_state = STATE_P1_TURN

    if current_state == STATE_GAME_OVER:
        pass
server.close()
