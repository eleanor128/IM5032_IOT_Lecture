#!/usr/bin/env python3
"""
Flask 網站控制伺服馬達和 LED 燈
GPIO 14: 伺服馬達
GPIO 26: LED 燈
"""

from flask import Flask, render_template, request, jsonify
from gpiozero import Servo, PWMLED
import time
import threading

app = Flask(__name__)

# 伺服馬達校準表 (根據實際測試結果)
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

    return 7.30  # 預設值 (90度的校準值)

def duty_cycle_to_servo_value(duty_cycle):
    """將 duty cycle 轉換為 gpiozero Servo 的值 (-1 到 1)"""
    # gpiozero Servo: -1 = 0度, 0 = 90度, 1 = 180度
    # 我們的校準資料: 12.60% = 0度, 7.30% = 90度, 2.20% = 180度
    
    # 將 duty cycle 映射到角度，再轉換為 servo 值
    if duty_cycle >= 12.60:
        return -1.0  # 0度
    elif duty_cycle <= 2.20:
        return 1.0   # 180度
    else:
        # 線性映射
        # duty_cycle 從 12.60 到 2.20 對應 servo_value 從 -1 到 1
        servo_value = -1 + 2 * (12.60 - duty_cycle) / (12.60 - 2.20)
        return max(-1, min(1, servo_value))

def angle_to_servo_value(angle):
    """將角度轉換為 gpiozero Servo 的值"""
    duty_cycle = get_calibrated_duty_cycle(angle)
    return duty_cycle_to_servo_value(duty_cycle)

# GPIO 設定
servoPIN = 13          # GPIO 13
ledPIN = 26
current_angle = 90
led_brightness = 0  # LED 亮度 (0-100)

# 初始化 gpiozero 元件
servo = Servo(servoPIN)  # GPIO 13 伺服馬達
led_pwm = PWMLED(ledPIN)  # GPIO 26 LED (PWM 控制)

# 控制鎖，防止同時操作
control_lock = threading.Lock()

def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度) - 使用 gpiozero"""
    global current_angle
    
    with control_lock:
        # 使用校準資料轉換為 servo 值
        servo_value = angle_to_servo_value(angle)
        
        # 設定伺服馬達位置
        servo.value = servo_value
        current_angle = angle
        
        duty_cycle = get_calibrated_duty_cycle(angle)
        print(f"🎯 設定角度 {angle}° (servo值: {servo_value:.3f}, 等效PWM: {duty_cycle:.2f}%)")
        
        # 等待馬達到達位置
        time.sleep(0.8)

def set_led_brightness(brightness):
    """設定 LED 亮度 (0-100) - 使用 gpiozero"""
    global led_brightness
    
    with control_lock:
        brightness = max(0, min(100, brightness))
        # gpiozero PWMLED 的值範圍是 0-1
        led_value = brightness / 100.0
        led_pwm.value = led_value
        led_brightness = brightness

def led_control(state):
    """控制 LED 開關 (保留舊功能，用於向後相容)"""
    if state:
        set_led_brightness(100)
    else:
        set_led_brightness(0)

@app.route('/')
def index():
    """主頁面"""
    return render_template('control.html', 
                         current_angle=current_angle, 
                         led_brightness=led_brightness)

@app.route('/api/servo', methods=['POST'])
def control_servo():
    """控制伺服馬達 API"""
    try:
        data = request.get_json()
        angle = int(data.get('angle', 90))
        
        if 0 <= angle <= 180:
            set_servo_angle(angle)
            return jsonify({
                'success': True,
                'message': f'馬達已轉到 {angle}度',
                'angle': current_angle
            })
        else:
            return jsonify({
                'success': False,
                'message': '角度必須在 0-180 之間'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'錯誤: {str(e)}'
        }), 500

@app.route('/api/led', methods=['POST'])
def control_led():
    """控制 LED 亮度 API"""
    try:
        data = request.get_json()
        
        # 支援舊的開關控制
        if 'state' in data:
            state = data.get('state', False)
            brightness = 100 if state else 0
        else:
            # 新的亮度控制
            brightness = int(data.get('brightness', 0))
        
        if 0 <= brightness <= 100:
            set_led_brightness(brightness)
            return jsonify({
                'success': True,
                'message': f'LED 亮度設定為 {brightness}%',
                'led_brightness': led_brightness
            })
        else:
            return jsonify({
                'success': False,
                'message': '亮度必須在 0-100 之間'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'錯誤: {str(e)}'
        }), 500

@app.route('/api/status')
def get_status():
    """獲取當前狀態"""
    return jsonify({
        'servo_angle': current_angle,
        'led_brightness': led_brightness,
        'servo_pin': servoPIN,
        'led_pin': ledPIN
    })

@app.route('/api/preset/<preset>')
def preset_action(preset):
    """預設動作"""
    try:
        if preset == 'center':
            set_servo_angle(90)
            message = '馬達已置中'
            
        elif preset == 'left':
            set_servo_angle(0)
            message = '馬達已轉到左邊'
            
        elif preset == 'right':
            set_servo_angle(180)
            message = '馬達已轉到右邊'
            
        elif preset == 'sweep':
            # 掃描動作
            angles = [0, 45, 90, 135, 180, 90]
            for angle in angles:
                set_servo_angle(angle)
                time.sleep(0.8)
            message = '掃描完成'
            
        elif preset == 'led_blink':
            # LED 閃爍
            original_brightness = led_brightness
            for _ in range(3):
                set_led_brightness(100)
                time.sleep(0.3)
                set_led_brightness(0)
                time.sleep(0.3)
            set_led_brightness(original_brightness)  # 恢復原亮度
            message = 'LED 閃爍完成'
            
        else:
            return jsonify({
                'success': False,
                'message': '未知的預設動作'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'servo_angle': current_angle,
            'led_brightness': led_brightness
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'錯誤: {str(e)}'
        }), 500

def cleanup():
    """清理 GPIO"""
    try:
        set_led_brightness(0)  # 關閉 LED
        set_servo_angle(90)    # 馬達回中心
        time.sleep(1)
        # gpiozero 會自動清理，不需要手動 cleanup
        print("GPIO 清理完成")
    except:
        pass

if __name__ == '__main__':
    try:
        print("🚀 Flask 伺服馬達和 LED 控制伺服器啟動")
        print("📍 伺服馬達: GPIO 13 (gpiozero Servo)")
        print("💡 LED 燈: GPIO 26 (gpiozero PWMLED)")
        print("🌐 網址: http://localhost:5000")
        print("🛑 按 Ctrl+C 停止伺服器")
        
        # 初始化設定
        set_servo_angle(90)     # 馬達置中
        set_led_brightness(0)   # LED 關閉
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n⚡ 伺服器被中斷")
    finally:
        cleanup()