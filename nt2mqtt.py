import ntcore
import logging
import argparse
import time
import paho.mqtt.client as mqtt

def eventdata_to_mqtt(data: ntcore.ValueEventData) -> str | int | float | None:    
    if data.value.isString():
        return data.value.getString()
    elif data.value.isInteger():
        return data.value.getInteger()
    elif data.value.isDouble():
        return data.value.getDouble()
    elif data.value.isFloat():
        return data.value.getFloat()
    elif data.value.isBoolean():
        return "true" if data.value.getBoolean() else "false"
    else: 
        return None

def eventname_to_mqtt(name: str) -> str:
    name = name.replace(" ", "_")
    
    return f"NT{name}"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--protocol",
        type=int,
        choices=[3, 4],
        help="NT Protocol to use",
        default=4,
    )
    parser.add_argument("ip", type=str, help="IP address to connect to")
    args = parser.parse_args()

    mqtt = mqtt.Client()
    mqtt.connect("localhost", 1883, 10)
    inst = ntcore.NetworkTableInstance.getDefault()
    
    identity = "nt2mqtt"
    if args.protocol == 3:
        inst.startClient3(identity)
    else:
        inst.startClient4(identity)
        
    inst.setServer(args.ip)

    # Create a poller
    poller = ntcore.NetworkTableListenerPoller(inst)

    # Listen for all connection events
    poller.addConnectionListener(True)

    # Listen to all changes
    msub = ntcore.MultiSubscriber(inst, [""])
    poller.addListener(msub, ntcore.EventFlags.kValueRemote)
    
    while True:
        for event in poller.readQueue():
            print(f"Event: {event.data}")
            
            if event.is_(ntcore.EventFlags.kValueAll):
                data = eventdata_to_mqtt(event.data)
                
                if data is not None:
                    mqtt.publish(eventname_to_mqtt(event.data.topic.getName()), data)

        time.sleep(0.002)
    
