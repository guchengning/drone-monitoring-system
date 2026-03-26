import socket
import json
import time
import threading
from datetime import datetime
import csv

class GroundStation:
    def __init__(self, host='127.0.0.1', port=9998, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.last_heartbeat_time = None
        self.is_online = False
        self.heartbeat_data = []
        self.running = False
        self.lock = threading.Lock()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(1.0)
        print(f"地面站已启动，监听 {self.host}:{self.port}")

    def check_connection_status(self):
        while self.running:
            current_time = time.time()
            
            with self.lock:
                if self.last_heartbeat_time:
                    time_since_last = current_time - self.last_heartbeat_time
                    
                    if time_since_last > self.timeout:
                        if self.is_online:
                            print(f"⚠️ 警报：无人机掉线！{time_since_last:.1f}秒未收到心跳包")
                            self.is_online = False
                    else:
                        if not self.is_online:
                            print("✅ 无人机已重新连接")
                            self.is_online = True
                else:
                    self.is_online = False
            
            time.sleep(0.5)

    def save_heartbeat_data(self, data):
        with self.lock:
            self.heartbeat_data.append(data)
            if len(self.heartbeat_data) > 1000:
                self.heartbeat_data = self.heartbeat_data[-1000:]
        
        with open('heartbeat_data.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([data['sequence'], data['timestamp'], data['status']])

    def receive_heartbeat(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                heartbeat = json.loads(data.decode('utf-8'))
                
                current_time = time.time()
                with self.lock:
                    self.last_heartbeat_time = current_time
                    self.is_online = True
                
                print(f"收到心跳包 #{heartbeat['sequence']} - {heartbeat['timestamp']}")
                self.save_heartbeat_data(heartbeat)
                
            except socket.timeout:
                continue
            except json.JSONDecodeError as e:
                print(f"数据解析错误: {e}")
            except Exception as e:
                print(f"接收错误: {e}")

    def start(self):
        self.connect()
        self.running = True
        
        receiver_thread = threading.Thread(target=self.receive_heartbeat)
        checker_thread = threading.Thread(target=self.check_connection_status)
        
        receiver_thread.daemon = True
        checker_thread.daemon = True
        
        receiver_thread.start()
        checker_thread.start()
        
        print("地面站正在运行... (按 Ctrl+C 停止)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n地面站已停止")
            self.running = False
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    station = GroundStation()
    station.start()
