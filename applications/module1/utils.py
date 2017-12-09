import threading
import websocket
import ssl
import json
import time


def _connect_to_ari_wss() -> websocket.WebSocket():
    """
    Connecting to asterisk(ARI)wss
    """

    websocket.enableTrace(True)

    while True:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        try:

            ws.connect("wss://192.168.168.150:8089/ari/events?api_key=asterisk:asterisk&app=dialer&subscribeAll=true")

        except websocket.WebSocketException as e:
            print("connect to ari Error: %s" % e)

        if ws.connected:
            return ws


def _connect_to_console_ws() -> websocket.WebSocket():
    """
    Connecting to Django Websocket server(channels)ws
    """

    websocket.enableTrace(True)

    while True:
        ws = websocket.WebSocket()
        try:

            ws.connect("ws://127.0.0.1:8000/")

        except websocket.WebSocketException as e:
            print("connect to console Error: %s" % e)

        except ConnectionRefusedError as e:
            print("connect to console Error: %s" % e)

        if ws.connected:
            return ws
        time.sleep(1)


def ari_wss_recv_send():
    ari_wss = _connect_to_ari_wss()
    console_ws = _connect_to_console_ws()

    while True:
        wss_data = ari_wss.recv()
        wss_data = json.loads(wss_data)
        endpoint = wss_data.get("endpoint")
        if endpoint:
            state = endpoint.get("state")
            console_ws.send(state)


def create_daemons():
    """
    Creating processes daemons and asked in each of them an asterisk

    :param keys_with_command: list of tuples, where each tuple consist with
        0 - str: command;
        1 - str: key in redis dict.
    :return: list of multiprocessing.Process
    """

    thread = threading.Thread(target=ari_wss_recv_send, daemon=True, )

    thread.start()
