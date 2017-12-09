import logging
import websocket
import ssl
import json
import multiprocessing as mp

logger = mp.log_to_stderr(logging.INFO)


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
            logger.error("connect to ari Error: %s" % e)

        if ws.connected:
            return ws


def ari_wss_recv_send():
    wss = _connect_to_ari_wss()

    while True:
        # print(wss.getstatus())
        # print(wss.getheaders())
        wss_data = wss.recv()
        print(wss_data)
        # wss_data = wss_data.replace('\n ', '')
        wss_data = json.loads(wss_data)
        print(wss_data)
        endpoint = wss_data.get("endpoint")
        print(endpoint)
        if endpoint:
            state = endpoint.get("state")
            print(state)


def create_daemons():
    """
    Creating processes daemons and asked in each of them an asterisk

    :param keys_with_command: list of tuples, where each tuple consist with
        0 - str: command;
        1 - str: key in redis dict.
    :return: list of multiprocessing.Process
    """

    print('111')
    process = mp.Process(
            target=ari_wss_recv_send(),
            kwargs={},
    )
    print('222')
    process.daemon = True
    print('333')

    process.start()
    process.join()
