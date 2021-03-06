from flask import Flask, request
import requests
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import os
from urllib.parse import urlparse


ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

#hold sender id
history = dict()

set_cmd = 'floor1/room1/led1'
get_cmd = 'floor1/room1/temp1'

#respond to FB messenger
def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)

#MQTT handler
def on_connect(client, obj, flags, rc):
    print("rc: "+str(rc))
    client.subscribe("floor1/#", 0)

def on_message(client, obj, msg):
    print(msg.topic+": "+str(msg.payload))
    if msg.topic in history:
        user_id = history[msg.topic]
        #reply FB messenger
        reply(user_id, msg.payload)
        history.pop(msg.topic, None)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://localhost:1883')
url = urlparse(url_str)
client.connect(url.hostname, url.port)
client.loop_start()


#Flask web server instance
app = Flask(__name__)

#handle GET request from Facebook
@app.route('/', methods=['GET'])
def handle_verification():
   if(request.args['hub.verify_token'] == VERIFY_TOKEN):
      return request.args['hub.challenge']
   else:
      return ('not matched')

#handle POST request from Facebook
@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.get_json()
    sender = ' '
    message = ' '
    for entry_event in data['entry']:
        for message_event in entry_event['messaging']:
            if message_event.get('message'):
                sender = message_event['sender']['id']
                message =  message_event['message']['text']
    print(data)
    #sender = data['entry'][0]['messaging'][0]['sender']['id']
    #message = data['entry'][0]['messaging'][0]['message']['text']
    print(message)

    if(message.startswith('set')):
        arr = message.split()
        l = len(arr)
        if(l == 3 and set_cmd == arr[1]):
            cmd = arr[1]
            val = '1' if arr[2]=='on' else '0'
            publish.single(cmd, val, hostname="localhost")
            #record command with sender id
            history[cmd+'/res'] = sender
            return 'ok'

    elif(message.startswith('get')):
        arr = message.split()
        l = len(arr)
        if(l == 2 and get_cmd == arr[1]):
            cmd = arr[1]
            publish.single(cmd, '', hostname="localhost")
            #record command with sender id
            history[cmd+'/res'] = sender 
            return 'ok'

    else:
        reply(sender, 'invalid query')
 
    return "ok"

if __name__ == '__main__':
	app.run(debug=True)
