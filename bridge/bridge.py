import ntcore
import logging
import argparse
from time import sleep
import paho.mqtt.client as mqtt

# Only write valid types to MQTT
def nt_data_to_mqtt(data: ntcore.ValueEventData) -> str | int | float | None:    
    if data.value.isString():
        return data.value.getString()
    elif data.value.isInteger():
        return data.value.getInteger()
    elif data.value.isDouble():
        return data.value.getDouble()
    elif data.value.isFloat():
        return data.value.getFloat()
    elif data.value.isBoolean():
        return str(data.value.getBoolean()).lower()
    else: 
        return None

# Convert NT names to valid MQTT topics
def nt_name_to_mqtt(name: str) -> str:
    name = name.replace(" ", "_")
    
    return f"NT{name}"

def main():
    logging.basicConfig(level=logging.DEBUG)

    # Set up arguments
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--identity", type=str, help="Client identity", default="nt2mqtt")
    
    ntparser = parser.add_argument_group("Network Tables Options")
    ntparser.add_argument(
        "--ntversion",
        type=int,
        choices=[3, 4],
        help="NT Protocol to use",
        default=4,
    )
    conn = ntparser.add_mutually_exclusive_group(required=True)
    conn.add_argument(
        "--ntteam",
        type=int,
        help="FRC Team Number",
    )
    conn.add_argument("--ntaddr", type=str, help="IP address of the NT server")
    ntparser.add_argument("--ntport", type=int, help="Port of the NT server", default=0)
    
    mqttparser = parser.add_argument_group("MQTT Options")
    mqttparser.add_argument("--mqaddr", type=str, help="IP address of the MQTT server", default="mqtt")
    mqttparser.add_argument("--mqport", type=int, help="Port of the MQTT server", default=1883)
    mqttparser.add_argument("--mqkeepalive", type=int, help="Max period in seconds between communication with the broker", default=60)
    mqttparser.add_argument("--mquser", type=str, help="MQTT username (if required)")
    mqttparser.add_argument("--mqpass", type=str, help="MQTT password (if required)")

    args = parser.parse_args()
    
    # Set up MQTT client
    mq = mqtt.Client()
    if args.mquser is not None and args.mqpass is not None:
        mq.username_pw_set(args.mquser, args.mqpass)
    mq.connect(args.mqaddr, args.mqport, args.mqkeepalive)
    
    # Set up NT client
    nt = ntcore.NetworkTableInstance.getDefault()
    
    if args.protocol == 3:
        nt.startClient3(args.identity)
    else:
        nt.startClient4(args.identity)
        
    if args.ntteam is not None:
        nt.setServerTeam(args.ntteam, args.ntport)
    else:
        nt.setServer(args.ntaddr, args.ntport)

    # Create a poller
    ntpoller = ntcore.NetworkTableListenerPoller(nt)
    ntpoller.addConnectionListener(True)
    ntsub = ntcore.MultiSubscriber(nt, [""])
    ntpoller.addListener(ntsub, ntcore.EventFlags.kValueRemote)
    
    # Start MQTT loop
    mq.loop_start()
    while True:
        for event in ntpoller.readQueue():            
            if type(event.data) is ntcore.ValueEventData:
                data = nt_data_to_mqtt(event.data)
                
                if data is not None:
                    mq.publish(nt_name_to_mqtt(event.data.topic.getName()), data)

        sleep(0.002) # Loop every 20ms
    
if __name__ == "__main__": main()