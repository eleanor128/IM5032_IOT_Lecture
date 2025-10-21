#!/usr/bin/env python3
"""
Flask 網站控制伺服馬達和 LED 燈
GPIO 14: 伺服馬達
GPIO 26: LED 燈
"""

from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time
import threading

app = Flask(__name__)

# GPIO 設定
servoPIN = 14
ledPIN = 26
current_angle = 90
led_brightness = 0  # LED 亮度 (0-100)

# 初始化 GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(ledPIN, GPIO.OUT)

# PWM 設定
p = GPIO.PWM(servoPIN, 50)
p.start(7.5)  # 90度開始

# LED PWM 設定 (用於亮度控制)
led_pwm = GPIO.PWM(ledPIN, 1000)  # 1000Hz 頻率
led_pwm.start(0)  # 從 0% 開始

# 控制鎖，防止同時操作
control_lock = threading.Lock()

def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度) - 優化版，減少抖動"""
    global current_angle
    
    with control_lock:
        # 反轉角度：0度在左邊，180度在右邊
        reversed_angle = 180 - angle
        duty_cycle = 2.5 + (reversed_angle / 180.0) * 10
        
        # 設定角度
        p.ChangeDutyCycle(duty_cycle)
        current_angle = angle
        
        # 等待馬達到達位置
        time.sleep(0.8)
        
        # 停止 PWM 訊號以減少抖動 (可選)
        # p.ChangeDutyCycle(0)

def set_led_brightness(brightness):
    """設定 LED 亮度 (0-100)"""
    global led_brightness
    
    with control_lock:
        brightness = max(0, min(100, brightness))
        led_pwm.ChangeDutyCycle(brightness)
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
        p.stop()
        led_pwm.stop()
        GPIO.cleanup()
        print("GPIO 清理完成")
    except:
        pass

if __name__ == '__main__':
    try:
        print("🚀 Flask 伺服馬達和 LED 控制伺服器啟動")
        print("📍 伺服馬達: GPIO 14")
        print("💡 LED 燈: GPIO 26")
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