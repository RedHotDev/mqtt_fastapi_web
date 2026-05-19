

import random
import json
import time
import datetime
from paho.mqtt import client as mqtt_client


# broker = 'test.mosquitto.org'
# port = 1883

# broker = 'broker.emqx.io'
# port = 1883


broker = 'm8.wqtt.ru'
port = 20606

topic = "sensors/data"
topic_cfg = 'CFG_1'


__setpoint=0
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'


def setpoint_set(val):
   global __setpoint
   __setpoint = val

def setpoint_get():
   return __setpoint

def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            subscribe(client)
            client.connected_flag = True
            
            msg = {"device": 1, "data": [
                {"datestamp": 1779166905, "tag": "temp", "val": 54.3}]}
            
            msg = json.dumps(msg)
            # client.publish('CFG', msg, 2)
            
        else:
            print("Failed to connect, return code ", rc)
            client.reconnect()

def on_publish(client, userdata, mid):
        print(f"on pub {mid}" )

def on_disconnect(client, userdata, rc):
    client.connected_flag = False
    if rc != 0:
        print("Unexpected disconnection. Reconnecting...")
        client.reconnect()
    else :
        print ("Disconnected successfully")  
   

def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        m_decode = str(msg.payload.decode())
        m_in = json.loads(m_decode)
        setpoint_set(m_in['setTemp'])

    client.subscribe(topic_cfg, qos=0)
    client.on_message = on_message


client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
client.username_pw_set(username='u_BJIUEH', password='jlNoV6gO')
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(broker, port)
client.loop_start()



while True:
    
    time.sleep(10)
    temp = random.randint(20, 25)
    f = bool(random.getrandbits(1))
    current_date_time = datetime.datetime.now()
    unix_current_date_time = int(current_date_time.timestamp())
    
    
    msg = {"device": 1, "data":
           [
               {"datestamp": unix_current_date_time, "tag": "temp", "val": temp},
               {"datestamp": unix_current_date_time, "tag": "humidity", "val": random.randint(20, 70)},
           ]
           }
    
    msg = json.dumps(msg)
    
    result = client.publish(topic, msg, qos=1)
    
    status = result[0]
    if status == 0:
        print(f"Отправлено сообщение `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run():
   print('ddd') 
    

if __name__ == '__main__':
    run()
