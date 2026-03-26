import socket
import time
import json
from datetime import datetime

class DroneHeartbeatSender:
    def __init__(self, host='127.0.0.1', port=9998):
        self.host = host
        self.port = port
        self.sequence_number = 0
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"无人机心跳发送器已启动，发送到 {self.host}:{self.port}")

    def send_heartbeat(self):
        heartbeat_data = {
            'sequence': self.sequence_number,
            'timestamp': datetime.now().isoformat(),
            'status': 'online'
        }
        
        message = json.dumps(heartbeat_data).encode('utf-8')
        self.socket.sendto(message, (self.host, self.port))
        
        print(f"发送心跳包 #{self.sequence_number} - {heartbeat_data['timestamp']}")
        self.sequence_number += 1

    def start(self):
        self.connect()
        try:
            while True:
                self.send_heartbeat()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n无人机心跳发送器已停止")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    sender = DroneHeartbeatSender()
    sender.start()
