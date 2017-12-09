from channels import Group


# Connected to websocket.connect
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    # Add to the chat group
    Group("console").add(message.reply_channel)


# Connected to websocket.receive
def ws_message(message):
    Group("console").send({
        "text": message.content['text'],
    })


# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("console").discard(message.reply_channel)
