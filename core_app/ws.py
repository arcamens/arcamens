import paho.mqtt.client as paho
import time
 
mqtthost = "127.0.0.1"  
mqttuser = "guest"  
mqttpass = "guest"  

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))
    # client.subscribe('beta')
    client.publish('beta', 'Excellent!', 0, False)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = paho.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.username_pw_set(mqttuser,mqttpass)
client.connect(mqtthost, 1883,60)





