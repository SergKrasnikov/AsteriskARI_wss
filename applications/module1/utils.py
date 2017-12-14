import threading
import websocket
import ssl
import json
import time
import http.client


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
    conn = http.client.HTTPConnection(host="localhost", port=8000, timeout=60, )

    while True:
        try:
            wss_data = ari_wss.recv()
        except TimeoutError:
            ari_wss = _connect_to_ari_wss()
            wss_data = ari_wss.recv()

        try:
            wss_data = json.loads(wss_data)
        except json.decoder.JSONDecodeError:
            continue

        state, number = None, None
        if wss_data.get('variable'):
            continue

        status_type = wss_data.get('type')

        if status_type == 'PeerStatusChange':
            endpoint = wss_data.get('endpoint')
            state = endpoint.get("state")

        elif status_type == 'ChannelStateChange':
            channel = wss_data.get('channel')
            state = channel.get("state")
            caller = channel.get("caller")
            number = caller.get("name")

        if state:

            if state in ['Ring', 'Up', ]:
                request = 'status=%s&number=%s' % (state, number)
            else:
                request = 'status=%s' % state

            try:
                conn.request('GET', '/ari_rest/?%s' % request)
            except http.client.NotConnected:
                conn = http.client.HTTPConnection(host="localhost", port=8000, timeout=60, )
                conn.request('GET', '/ari_rest/?%s' % request)

            response = conn.getresponse()
            response.read()


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
