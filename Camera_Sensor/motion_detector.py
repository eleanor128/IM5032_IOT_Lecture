#!/usr/bin/env python3
"""
進階物體移動偵測系統
支援 PIR 感測器和攝影機視覺偵測
"""

from gpiozero import MotionSensor, LED, Button
import cv2
import numpy as np
from time import sleep, time
import threading
from datetime import datetime
import os

# GPIO 設定
pir = MotionSensor(2)          # PIR 感測器接在 GPIO 2
status_led = LED(18)           # 狀態 LED 接在 GPIO 18
alarm_led = LED(24)            # 警報 LED 接在 GPIO 24
reset_button = Button(3)       # 重置按鈕接在 GPIO 3

# 全域變數
motion_detected = False
last_motion_time = 0
detection_count = 0
camera_active = False

class MotionDetector:
    def __init__(self):
        self.background = None
        self.motion_threshold = 1000  # 移動偵測閾值
        self.min_area = 500          # 最小偵測區域
        self.detection_active = True
        self.save_images = True
        
        # 確保儲存目錄存在
        if self.save_images:
            os.makedirs('motion_captures', exist_ok=True)
    
    def camera_motion_detection(self):
        """使用攝影機進行移動偵測"""
        global motion_detected, last_motion_time, detection_count, camera_active
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ 無法開啟攝影機")
                return
            
            print("📹 攝影機移動偵測啟動")
            camera_active = True
            
            # 設定攝影機參數
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            frame_count = 0
            
            while self.detection_active:
                ret, frame = cap.read()
                if not ret:
                    print("❌ 無法讀取攝影機畫面")
                    break
                
                frame_count += 1
                
                # 轉換為灰階
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                
                # 建立背景模型
                if self.background is None:
                    self.background = gray
                    continue
                
                # 計算背景差異
                frame_delta = cv2.absdiff(self.background, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # 尋找輪廓
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                motion_areas = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < self.min_area:
                        continue
                    
                    motion_areas.append(area)
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # 檢查是否偵測到移動
                if motion_areas:
                    total_motion = sum(motion_areas)
                    if total_motion > self.motion_threshold:
                        motion_detected = True
                        last_motion_time = time()
                        detection_count += 1
                        
                        print(f"📹 攝影機偵測到移動！面積: {total_motion:.0f}")
                        
                        # 儲存截圖
                        if self.save_images:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"motion_captures/motion_{timestamp}_{detection_count}.jpg"
                            cv2.imwrite(filename, frame)
                            print(f"💾 已儲存: {filename}")
                
                # 顯示畫面 (如果有顯示器)
                try:
                    cv2.putText(frame, f"Motion Count: {detection_count}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                               (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Motion Detection', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except:
                    # 無顯示器環境，跳過顯示
                    pass
                
                # 更新背景模型
                if frame_count % 30 == 0:  # 每30幀更新一次背景
                    self.background = gray.copy()
                
                sleep(0.1)  # 控制處理頻率
        
        except Exception as e:
            print(f"❌ 攝影機偵測錯誤: {e}")
        
        finally:
            camera_active = False
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            print("📹 攝影機偵測結束")

def pir_callback():
    """PIR 感測器回調函數"""
    global motion_detected, last_motion_time, detection_count
    
    motion_detected = True
    last_motion_time = time()
    detection_count += 1
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"🚨 PIR 偵測到移動！時間: {timestamp} (第 {detection_count} 次)")

def reset_callback():
    """重置按鈕回調函數"""
    global detection_count, motion_detected
    detection_count = 0
    motion_detected = False
    print("🔄 偵測計數已重置")

def status_monitor():
    """狀態監控執行緒"""
    global motion_detected, last_motion_time
    
    while True:
        current_time = time()
        
        # 控制狀態 LED
        if motion_detected and (current_time - last_motion_time < 5):
            # 偵測到移動後5秒內保持亮起
            status_led.on()
            alarm_led.blink(on_time=0.2, off_time=0.2)  # 警報閃爍
        else:
            status_led.blink(on_time=0.1, off_time=1.9)  # 正常閃爍
            alarm_led.off()
            if current_time - last_motion_time > 10:
                motion_detected = False
        
        sleep(0.1)

def main():
    """主程式"""
    print("🎯 物體移動偵測系統啟動")
    print("=" * 40)
    print("📍 PIR 感測器: GPIO 2")
    print("💡 狀態 LED: GPIO 18")
    print("🚨 警報 LED: GPIO 24")
    print("🔘 重置按鈕: GPIO 3")
    print("=" * 40)
    
    # 設定回調函數
    pir.when_motion = pir_callback
    reset_button.when_pressed = reset_callback
    
    # 啟動狀態監控執行緒
    status_thread = threading.Thread(target=status_monitor, daemon=True)
    status_thread.start()
    
    # 選擇偵測模式
    print("\n🎮 偵測模式選擇:")
    print("1. 僅 PIR 感測器")
    print("2. 僅攝影機偵測")
    print("3. PIR + 攝影機 (雙重偵測)")
    
    try:
        choice = input("請選擇模式 (1-3): ").strip()
        
        detector = MotionDetector()
        
        if choice in ['2', '3']:
            # 啟動攝影機偵測執行緒
            camera_thread = threading.Thread(target=detector.camera_motion_detection, daemon=True)
            camera_thread.start()
        
        if choice == '1':
            print("🔍 PIR 感測器模式啟動")
        elif choice == '2':
            print("📹 攝影機偵測模式啟動")
        elif choice == '3':
            print("🔍📹 雙重偵測模式啟動")
        else:
            print("🔍 預設使用 PIR 感測器模式")
        
        print("✅ 系統就緒，開始偵測移動...")
        print("🛑 按 Ctrl+C 停止程式")
        print("🔄 按重置按鈕清除計數")
        
        # 主迴圈
        while True:
            sleep(1)
            
            # 每10秒顯示狀態
            if detection_count > 0 and detection_count % 10 == 0:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"📊 {current_time} - 累積偵測: {detection_count} 次")
    
    except KeyboardInterrupt:
        print("\n⚡ 程式被中斷")
    
    except Exception as e:
        print(f"❌ 程式錯誤: {e}")
    
    finally:
        # 清理資源
        detector.detection_active = False
        status_led.off()
        alarm_led.off()
        print("🧹 清理完成")

if __name__ == '__main__':
    main()