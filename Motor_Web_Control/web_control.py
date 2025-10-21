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
led_status = False

# 初始化 GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(ledPIN, GPIO.OUT)

# PWM 設定
p = GPIO.PWM(servoPIN, 50)
p.start(7.5)  # 90度開始

# 控制鎖，防止同時操作
control_lock = threading.Lock()

def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度)"""
    global current_angle
    
    with control_lock:
        # 反轉角度：0度在左邊，180度在右邊
        reversed_angle = 180 - angle
        duty_cycle = 2.5 + (reversed_angle / 180.0) * 10
        p.ChangeDutyCycle(duty_cycle)
        current_angle = angle
        time.sleep(0.5)  # 給馬達時間移動

def led_control(state):
    """控制 LED 開關"""
    global led_status
    
    with control_lock:
        if state:
            GPIO.output(ledPIN, GPIO.HIGH)
            led_status = True
        else:
            GPIO.output(ledPIN, GPIO.LOW)
            led_status = False

@app.route('/')
def index():
    """主頁面"""
    return render_template('control.html', 
                         current_angle=current_angle, 
                         led_status=led_status)

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
    """控制 LED API"""
    try:
        data = request.get_json()
        state = data.get('state', False)
        
        led_control(state)
        
        return jsonify({
            'success': True,
            'message': f'LED {"開啟" if state else "關閉"}',
            'led_status': led_status
        })
        
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
        'led_status': led_status,
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
            for _ in range(3):
                led_control(True)
                time.sleep(0.3)
                led_control(False)
                time.sleep(0.3)
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
            'led_status': led_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'錯誤: {str(e)}'
        }), 500

def cleanup():
    """清理 GPIO"""
    try:
        led_control(False)  # 關閉 LED
        set_servo_angle(90)  # 馬達回中心
        time.sleep(1)
        p.stop()
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
        set_servo_angle(90)  # 馬達置中
        led_control(False)   # LED 關閉
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n⚡ 伺服器被中斷")
    finally:
        cleanup()