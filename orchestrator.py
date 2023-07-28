import os
import subprocess
import sys
import paho.mqtt.client as mqtt
import atexit
import signal
import threading
import time

# Mosquitto MQTT broker
broker_address = "192.168.1.30"
broker_port = 1883
topic = "alarm/arming"
detection_script = "detect.py"
script_process = None

def on_connect(client, userdata, flags, rc):
    print("Connected to Mosquitto MQTT broker with result code: " + str(rc))
    print("waiting for messages..")
    client.publish("alarm/is_armed", 0, qos = 2)
    client.subscribe(topic)

def on_message(client, userdata, msg):
    global script_process
    payload = int(msg.payload)
    print("Message received: " + str(payload))

    if payload == 1:
        print(f"Received ARM command")
        client.publish("alarm/is_armed", 2, qos = 2)
        if script_process is None or script_process.poll() is not None:
            script_process = subprocess.Popen([sys.executable, detection_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print_output_thread = threading.Thread(target=print_subprocess_output, args=(script_process,))
            print_output_thread.start()
            print(f"Started detection script")
        else:
            print(f"..but detection script process already running")
    elif payload == 0:
        print(f"Received DISARM command")
        if script_process is not None and script_process.poll() is None:
            script_process.terminate()
            script_process.wait()
            print(f"Stopped detection script")
        else:
            print(f"..but no detection script process found")

def print_subprocess_output(process):
    while True:
        output = process.stdout.readline().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            print(f"[detect.py]: {output.strip()}")

def cleanup():
    global script_process
    if script_process is not None and script_process.poll() is None:
        script_process.terminate()
        script_process.wait()
        msg = client.publish("alarm/is_armed", 0, qos = 2)
        msg.wait_for_publish(10)
        print(f"Cleanup: Stopped detection script")

def signal_handler(sig, frame):
    msg = client.publish("alarm/is_armed", 0, qos = 2)
    msg.wait_for_publish(10)
    print("Termination signal received. Exiting...")
    sys.exit(0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, broker_port, 60)

# Register the cleanup function to run when the script exits
atexit.register(cleanup)

# Catch termination signals and perform cleanup
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

client.loop_forever()
