import zmq
import time

def p2p():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:43000')

    while True:
        try:
            message = socket.recv()
            print('recieved reply %s' %message)
            socket.send('k')
        except Exception as e:
            print  e


def subscription():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://127.0.0.1:43001')
    while True:
        for i in range(1,1000,10):
            print str(i)
            socket.send(str(i))
            time.sleep(1)

subscription()