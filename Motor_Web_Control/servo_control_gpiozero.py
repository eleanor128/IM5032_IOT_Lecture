#!/usr/bin/env python3
"""
使用 gpiozero 的伺服馬達控制程式
"""

from gpiozero import Servo, LED
import time

# 伺服馬達校準表
SERVO_CALIBRATION = {
    0: 12.60,
    45: 11.00,
    90: 7.30,
    135: 4.50,
    180: 2.20,
}

def get_calibrated_duty_cycle(target_angle):
    """根據校準資料獲取角度對應的 duty cycle"""
    if target_angle in SERVO_CALIBRATION:
        return SERVO_CALIBRATION[target_angle]

    # 線性插值
    angles = sorted(SERVO_CALIBRATION.keys())

    if target_angle <= angles[0]:
        return SERVO_CALIBRATION[angles[0]]
    if target_angle >= angles[-1]:
        return SERVO_CALIBRATION[angles[-1]]

    # 找到相鄰的兩個校準點
    for i in range(len(angles) - 1):
        if angles[i] <= target_angle <= angles[i + 1]:
            angle1, angle2 = angles[i], angles[i + 1]
            duty1, duty2 = SERVO_CALIBRATION[angle1], SERVO_CALIBRATION[angle2]

            # 線性插值
            ratio = (target_angle - angle1) / (angle2 - angle1)
            return duty1 + ratio * (duty2 - duty1)

    return 7.30  # 預設值

def duty_cycle_to_servo_value(duty_cycle):
    """將 duty cycle 轉換為 gpiozero Servo 的值 (-1 到 1) - SG90 專用"""
    # SG90 標準: 1ms = 0度, 1.5ms = 90度, 2ms = 180度
    pulse_width_ms = (duty_cycle / 100) * 20
    
    if pulse_width_ms >= 2.52:
        return -1.0
    elif pulse_width_ms <= 0.44:
        return 1.0
    else:
        normalized = (2.52 - pulse_width_ms) / (2.52 - 0.44)
        servo_value = -1 + 2 * normalized
        return max(-1, min(1, servo_value))

def angle_to_servo_value(angle):
    """將角度轉換為 gpiozero Servo 的值 - 修正方向映射法"""
    # 修正方向：0度 -> +1 (右邊), 90度 -> 0 (中間), 180度 -> -1 (左邊)
    servo_value = 1 - (angle / 180.0) * 2
    return max(-1, min(1, servo_value))

# GPIO 設定 - SG90 伺服馬達專用設定 (0度=右邊，180度=左邊)
servo = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)  # 調整脈衝範圍
led = LED(26)      # GPIO 26

def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度)"""
    servo_value = angle_to_servo_value(angle)
    servo.value = servo_value
    duty_cycle = get_calibrated_duty_cycle(angle)
    print(f"馬達轉到 {angle}度 (servo值: {servo_value:.3f}, 等效PWM: {duty_cycle:.2f}%)")
    time.sleep(1)

def led_on():
    """開啟 LED"""
    led.on()
    print("LED 開啟")

def led_off():
    """關閉 LED"""
    led.off()
    print("LED 關閉")

def led_blink(times=3, delay=0.5):
    """LED 閃爍"""
    print(f"LED 閃爍 {times} 次")
    for i in range(times):
        led_on()
        time.sleep(delay)
        led_off()
        time.sleep(delay)

# 初始化
print("硬體初始化完成 (gpiozero + SG90):")
print(f"🤖 Raspberry Pi 4 4GB + Raspbian Buster")
print(f"📍 SG90 伺服馬達: GPIO 13")
print(f"💡 LED 燈: GPIO 26")
print(f"🔧 SG90 脈衝範圍: 1-2ms")

# 馬達置中
print("馬達置中...")
servo.value = angle_to_servo_value(90)
time.sleep(2)

try:
    print("測試馬達角度和 LED...")
    
    # 先測試 LED
    print("\n=== LED 測試 ===")
    led_blink(3)
    time.sleep(1)
    
    print("\n=== 馬達測試 ===")
    # 測試各個角度，每次移動時點亮 LED
    angles = [0, 45, 90, 135, 180]
    
    for angle in angles:
        led_on()  # 移動時點亮 LED
        set_servo_angle(angle)
        led_off()  # 移動完成後關閉 LED
        time.sleep(1)
    
    # 回到90度
    led_on()
    set_servo_angle(90)
    led_off()
    print("測試完成")
        
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    print("清理中...")
    led_off()  # 確保 LED 關閉
    set_servo_angle(90)  # 馬達回到中心位置
    time.sleep(1)
    print("清理完成 (gpiozero 自動處理)")