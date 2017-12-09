from channels import route
from applications.module1.consumers import ws_add, ws_disconnect


channel_routing = [
    route("websocket.connect", ws_add),
    route("websocket.disconnect", ws_disconnect),
]