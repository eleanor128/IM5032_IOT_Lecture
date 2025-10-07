from gpiozero import MotionSensor
from time import sleep

pir = MotionSensor(17)  # GPIO 2

print("PIR sensor ready...")

try:
    while True:
        pir.wait_for_motion()
        print("Move detected!!")
        pir.wait_for_no_motion()
        print("No movement.")
except KeyboardInterrupt:
    print("Bye")