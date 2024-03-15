import paho.mqtt.client as mqtt
import json
import os
from datetime import date, datetime
from random import uniform
import time

class MQTTProtocol:
    def __init__(self, client_name):
        self.client = mqtt.Client(client_name)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        self.client.on_disconnect = self.on_disconnect
        self.connected_flag = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected_flag = True
            print("Connected to broker")
        else:
            print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection. Result code: {rc}")
        else:
            print("Disconnected from the broker")

    def on_publish(self, client, userdata, mid):
        print(f"Message published with mid: {mid}")

    def on_log(self, client, userdata, level, buf):
        print(f"Log: {buf}")

    def connect(self, broker):
        try:
            self.client.connect(broker)
        except Exception as e:
            print(f"Connection failed - The error was: {e} \n disconnecting...")
            self.client.disconnect()

    def start_loop(self):
        self.client.loop_start()

class BoatPrototype:
    def __init__(self, prototype_no, weight, mqtt_protocol):
        self.prototype_no = prototype_no
        self.weight = weight
        self.mqtt_protocol = mqtt_protocol

    def departing(self, fuel_tank_volume, frequency_sensor, acceleration_sensor, amplitude_sensor):
        print("Boat is moving...")

        result, mid = self.mqtt_protocol.client.publish("Frequency", frequency_sensor, qos=2, retain=True)
        print(f"Just published {frequency_sensor} to topic Frequency")
        time.sleep(2)

        result, mid = self.mqtt_protocol.client.publish("Fuel", fuel_tank_volume, qos=2, retain=True)
        print(f"Just published {fuel_tank_volume} to topic Fuel")
        time.sleep(2)

        result, mid = self.mqtt_protocol.client.publish("Amplitude", amplitude_sensor, qos=2, retain=True)
        print(f"Just published {amplitude_sensor} to topic Amplitude")
        time.sleep(2)

        result, mid = self.mqtt_protocol.client.publish("Acceleration", acceleration_sensor, qos=2, retain=True)
        print(f"Just published {acceleration_sensor} to topic Acceleration")
        time.sleep(2)

class Sensors:
    def __init__(self):
        self.sensor_data = {
            "Frequency": "default_frequency_value",
            "Amplitude": "default_amplitude_value",
            "Acceleration": "default_acceleration_value",
            "Fuel": "default_fuel_value",
        }

    def get_sensor_value(self, sensor_name):
        return self.sensor_data.get(sensor_name, "Invalid sensor")

    def set_sensor_value(self, sensor_name, value):
        if sensor_name in self.sensor_data:
            self.sensor_data[sensor_name] = value
        else:
            print("Invalid sensor name")

    def turn_off_sensor(self, sensor_name):
        self.set_sensor_value(sensor_name, "off")

    def print_sensor_data(self):
        for sensor, value in self.sensor_data.items():
            print(f"{sensor}: {value}")

# Example usage:
mqtt_protocol = MQTTProtocol("BoatPrototype1")
mqtt_protocol.connect("mqtt.eclipseprojects.io")
mqtt_protocol.start_loop()

sensors = Sensors()
boat = BoatPrototype(1, 40000000, mqtt_protocol)

while True:
    choice = input("Would you like to turn off any sensors?\n")
    choice = choice.lower()

    if choice == "yes":
        print("1)Frequency \n2)Amplitude \n3)Acceleration \n4)Fuel")
        sensor_to_turn_off = int(input("What sensor would you like to turn off?"))
        sensor_name = list(sensors.sensor_data.keys())[sensor_to_turn_off - 1]
        sensors.turn_off_sensor(sensor_name)
        boat.departing(
            sensors.get_sensor_value("Fuel"),
            sensors.get_sensor_value("Frequency"),
            sensors.get_sensor_value("Acceleration"),
            sensors.get_sensor_value("Amplitude"),
        )

    elif choice == "no":
        sensors.set_sensor_value("Frequency", uniform(1.0, 10.0))
        sensors.set_sensor_value("Fuel", uniform(20.0, 50.0))
        sensors.set_sensor_value("Amplitude", uniform(1.0, 10.0))
        sensors.set_sensor_value("Acceleration", uniform(50.0, 100.0))

        boat.departing(
            sensors.get_sensor_value("Fuel"),
            sensors.get_sensor_value("Frequency"),
            sensors.get_sensor_value("Acceleration"),
            sensors.get_sensor_value("Amplitude"),
        )

    else:
        print("You can either answer yes or no")