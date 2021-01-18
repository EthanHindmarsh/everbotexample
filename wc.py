import socket
import config
import random
import requests

def sendData(data):
    print("sending data: ", data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("192.168.1.50", 65432))
        sock.sendall(data.encode('utf-8'))
        result = sock.recv(1024)
        sock.close()
        return (result.decode('utf-8'))
    except OSError:
        return "Sorry! The AI is offline right now!\nTo disable this message, type .ai again.\nTry again later!"
def SAI(data):
    r=requests.get("https://some-random-api.ml/chatbot?key="+config.bconfig["apikey"]+"&message="+data)
    return r.json()['response']

def myAI(data):
    if bool(random.getrandbits(1)):
        return SAI(data)
    else:
        return myAI(data)

if __name__ == "__main__":
    data = str(input("Data: "))
    result = sendData(data)
    print(result)
