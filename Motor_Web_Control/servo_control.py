import RPi.GPIO as GPIO
import time

# 伺服馬達設定
servoPIN = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)  # GPIO 14, 50Hz

# 伺服馬達角度控制函數
def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度)"""
    duty_cycle = 2.5 + (angle / 180.0) * 10
    p.ChangeDutyCycle(duty_cycle)
    print(f"馬達轉到 {angle}度")
    time.sleep(1)

# 初始化
p.start(7.5)  # 90度開始
print("伺服馬達初始化完成")
time.sleep(1)

try:
    print("測試馬達角度...")
    
    # 測試各個角度
    angles = [0, 45, 90, 135, 180]
    
    for angle in angles:
        set_servo_angle(angle)
        time.sleep(2)
    
    # 回到90度
    set_servo_angle(90)
    print("測試完成")
        
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    print("馬達回到中心位置...")
    set_servo_angle(90)  # 結束前置中
    time.sleep(1)
    p.stop()
    GPIO.cleanup()
    print("清理完成")