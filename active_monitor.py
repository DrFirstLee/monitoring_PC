from pynput import mouse, keyboard
from threading import Thread
from threading import Event
import os

# 현재 로그인된 사용자 아이디
user_id = os.getlogin()
print(f"Windows User ID: {user_id}")

import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QMenu, QAction, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Track last activity time
last_activity_time = time.time()
monitor_active = False  # Flag to control monitoring
final_stop_time = "없음"  # Last inactivity time
asterisk_count = 1  # Counter for asterisks
increase = True  # Direction for asterisk count
STOP_THRESHOLD = 5  # Default inactivity threshold in seconds
asterisk_max = 20

import requests

response = requests.get('https://httpbin.org/ip', verify=False)
my_public_ip =  response.json()['origin']
print(f"my_public_ip : {my_public_ip}")
import gspread
from oauth2client.service_account import ServiceAccountCredentials
SERVICE_ACCOUNT_INFO = {
}
# Authenticate with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(creds)

## 구글 시트에 저장!!
save_data = {"computer_name" : user_id
                , "computer_ip" : my_public_ip
                ,"starting_time" : time.strftime('%Y%m%d-%H%M%S', time.localtime()) }

spreadsheet = client.open('active_monitoring_usage')
worksheet = spreadsheet.worksheet('result')
# 데이터 추가
# 빈 리스트 생성
save_data_list = []

# 각 인덱스별로 데이터 묶기
row = [
    save_data['computer_name'],
    save_data['computer_ip'],
    save_data['starting_time'],
]
save_data_list.append(row)

worksheet.append_rows(
    save_data_list,
    value_input_option='USER_ENTERED'  # 데이터를 사람이 입력한 것처럼 처리
)
print("Rows appended successfully!")
print(f"save me to sheets {save_data}")
# Callback functions for mouse events
def on_mouse_move(x, y):
    global last_activity_time
    if monitor_active:
        last_activity_time = time.time()

def on_mouse_click(x, y, button, pressed):
    global last_activity_time
    if monitor_active:
        last_activity_time = time.time()

def on_mouse_scroll(x, y, dx, dy):
    global last_activity_time
    if monitor_active:
        last_activity_time = time.time()

# Callback functions for keyboard events
def on_key_press(key):
    global last_activity_time
    if monitor_active:
        last_activity_time = time.time()

def on_key_release(key):
    global last_activity_time
    if monitor_active:
        last_activity_time = time.time()
    if key == keyboard.Key.esc:  # Stop listener on 'Esc' key press
        return False

# Mouse listener thread
def mouse_listener():
    with mouse.Listener(
        on_move=on_mouse_move,
        on_click=on_mouse_click,
        on_scroll=on_mouse_scroll) as listener:
        listener.join()

# Keyboard listener thread
def keyboard_listener():
    with keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release) as listener:
        listener.join()

exit_event = Event()

# Activity monitor thread
def activity_monitor():
    global last_activity_time, final_stop_time, user_id, client, my_public_ip
    while not exit_event.is_set():
        if monitor_active and time.time() - last_activity_time > STOP_THRESHOLD:  # Inactivity threshold
            final_stop_time = time.strftime('%Y%m%d-%H%M%S', time.localtime())
            print("HHHHHHHHHHHH", final_stop_time)
            last_activity_time = time.time()  # Reset last activity time to avoid continuous printing

            ## 구글 시트에 저장!!
            save_data = {"computer_name" : user_id
                         , "computer_ip" : my_public_ip
                         ,"STOP_THRESHOLD" : STOP_THRESHOLD
                         ,"final_stop_time" : final_stop_time }
            
            spreadsheet = client.open('active_monitoring')
            worksheet = spreadsheet.worksheet('result')
            # 데이터 추가
            # 빈 리스트 생성
            save_data_list = []

            # 각 인덱스별로 데이터 묶기
            row = [
                save_data['computer_name'],
                save_data['computer_ip'],
                save_data['STOP_THRESHOLD'],
                save_data['final_stop_time']
            ]
            save_data_list.append(row)

            worksheet.append_rows(
                save_data_list,
                value_input_option='USER_ENTERED'  # 데이터를 사람이 입력한 것처럼 처리
            )
            print("Rows appended successfully!")
            print(f"save me to sheets {save_data}")
        time.sleep(1)
        
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    import sys, os
    if hasattr(sys, '_MEIPASS'):  # PyInstaller에서 실행된 경우
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
        
# PyQt GUI class
class MonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path("icon.jpg")), self)
        self.tray_icon.setToolTip("Activity Monitor")
        self.setWindowTitle("Activity Monitor")
        self.setWindowIcon(QIcon(resource_path("icon.jpg")))  # 창의 아이콘 설정

        # Create system tray icon
        

        # Add context menu to the tray icon
        self.tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show)
        self.tray_menu.addAction(restore_action)
        # Add "Quit" action (this is the part you need to add)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)  # Change from self.close to self.quit_app
        self.tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        # UI elements
        self.monitor_status_label = QLabel(f"{user_id} / Monitoring: OFF")
        self.asterisk_label = QLabel("*")  # Label for asterisks
        self.start_button = QPushButton("모니터링 시작")
        self.start_button.clicked.connect(self.start_monitoring)

        self.pause_button = QPushButton("모니터링 종료")
        self.pause_button.clicked.connect(self.pause_monitoring)

        self.status_label = QLabel("마지막으로 움직임이 없던 시간: 없음")
        self.threshold_input = QLineEdit()
        self.threshold_input.setPlaceholderText("Enter threshold (seconds)")
        self.threshold_input.returnPressed.connect(self.update_threshold)

        self.threshold_label = QLabel(f"Inactivity Threshold: {STOP_THRESHOLD} seconds")

        layout = QVBoxLayout()
        layout.addWidget(self.monitor_status_label)
        layout.addWidget(self.asterisk_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.threshold_label)
        layout.addWidget(self.threshold_input)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Update the label periodically
        self.update_timer = self.startTimer(1000)  # Update every second
        
    def quit_app(self):
        """트레이 아이콘과 함께 애플리케이션 종료"""
        exit_event.set()  # 백그라운드 스레드 종료 신호 보내기
        self.tray_icon.hide()  # Hide the tray icon
        QApplication.quit()  # 애플리케이션 종료
    
    def start_monitoring(self):
        global monitor_active, user_id
        monitor_active = True
        self.monitor_status_label.setText(f"{user_id} / Monitoring: ON")
        print("Monitoring started.")

    def pause_monitoring(self):
        global monitor_active, user_id
        monitor_active = False
        self.monitor_status_label.setText(f"{user_id} / Monitoring: OFF")
        print("Monitoring paused.")

    def update_threshold(self):
        global STOP_THRESHOLD
        try:
            new_threshold = int(self.threshold_input.text())
            if new_threshold > 0:
                STOP_THRESHOLD = new_threshold
                self.threshold_label.setText(f"Inactivity Threshold: {STOP_THRESHOLD} seconds")
                print(f"Threshold updated to {STOP_THRESHOLD} seconds")
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    def timerEvent(self, event):
        global final_stop_time, asterisk_count, increase
        self.status_label.setText(f"마지막으로 움직임이 없던 시간: {final_stop_time}")

        if monitor_active:
            self.asterisk_label.setText("*" * asterisk_count)
            if increase:
                asterisk_count += 1
                if asterisk_count > asterisk_max:
                    increase = False
                    asterisk_count = 4
            else:
                asterisk_count -= 1
                if asterisk_count < 1:
                    increase = True
                    asterisk_count = 2

    def closeEvent(self, event):
        """Handle the minimize-to-tray behavior."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Activity Monitor", "Running in the background", QSystemTrayIcon.Information)

    def on_tray_icon_activated(self, reason):
        """Restore the window if the tray icon is clicked."""
        if reason == QSystemTrayIcon.Trigger:
            self.show()

# Run mouse, keyboard, and activity monitor in separate threads
if __name__ == "__main__":
    mouse_thread = Thread(target=mouse_listener, daemon=True)
    keyboard_thread = Thread(target=keyboard_listener, daemon=True)
    monitor_thread = Thread(target=activity_monitor, daemon=True)

    mouse_thread.start()
    keyboard_thread.start()
    monitor_thread.start()

    app = QApplication([])
    window = MonitorApp()
    window.show()
    app.exec_()
