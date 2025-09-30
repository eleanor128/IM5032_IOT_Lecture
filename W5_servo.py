import RPi.GPIO as GPIO
import time as time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

pwm = GPIO.PWM(32, 50) # GPIO32, frequency=50Hz
pwm.start(0)
try:
   while True:
     for dc in range(0, 101, 5):
        pwm.ChangeDutyCycle(dc)
        time.sleep(0.1)
     for dc in range(100, -1, -5):
        pwm.ChangeDutyCycle(dc)
        time.sleep(0.1)
except KeyboardInterrupt:
   pass
pwm.stop()
GPIO.cleanup()