from tkinter import *
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import queue
import os

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation Controller")
        
        # 初始化变量
        self.output_queue = queue.Queue()
        self.process = None
        self.running = False
        
        # 创建界面
        self.create_navigation()
        self.create_content_frames()
        self.create_output_area()
        self.push_process = None

    def create_navigation(self):
        """左侧导航菜单"""
        nav_frame = ttk.Frame(self.root, width=150, padding="10")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 导航按钮
        ttk.Button(
            nav_frame,
            text="Station Status",
            command=lambda: self.show_frame("station"),
            width=18
        ).pack(pady=5)

        ttk.Button(
            nav_frame,
            text="MPA Automation",
            command=lambda: self.show_frame("mpa"),
            width=18
        ).pack(pady=5)

    def create_content_frames(self):
        """右侧内容区域容器"""
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Station Status 页面
        self.station_frame = ttk.Frame(self.content_frame)
        self.create_station_controls()
        
        # MPA Automation 页面
        self.mpa_frame = ttk.Frame(self.content_frame)

        ttk.Label(
            self.mpa_frame,
            text="Test Scope",
            font=('Arial', 12),
            foreground="gray"
        ).pack(pady=50)
        # 添加Listbox
        listbox = Listbox(self.mpa_frame, height=10)  # 设置高度显示所有选项
        listbox.pack()
        # 插入数字1到5
        listbox.insert(END, 'Committe','Charging','Map','Service','My')  # 使用END常量逐项添加
        # 默认显示 Station Status
        self.show_frame("station")

    def create_station_controls(self):
        """Station Status 的控制按钮"""
        self.start_btn = ttk.Button(
            self.station_frame,
            text="Automation Start",
            command=self.start_automation,
            width=18
        )
        self.start_btn.pack(pady=5)

        self.stop_btn = ttk.Button(
            self.station_frame,
            text="Stop",
            command=self.stop_automation,
            width=18,
            state=tk.DISABLED
        )
        self.stop_btn.pack(pady=5)
# 新增Run Push按钮
        self.push_btn = ttk.Button(
            self.station_frame,
            text="Run Push",
            command=self.run_push,
            width=18
        )
        self.push_btn.pack(pady=5)

    def create_output_area(self):
        """右侧输出区域"""
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.output_area = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            state='disabled',
            width=60,
            height=20
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)

    def show_frame(self, frame_name):
        """切换内容页面"""
        if frame_name == "station":
            self.station_frame.pack(fill=tk.BOTH, expand=True)
            self.mpa_frame.pack_forget()
        elif frame_name == "mpa":
            self.mpa_frame.pack(fill=tk.BOTH, expand=True)
            self.station_frame.pack_forget()

    def start_automation(self):
        if not self.running:
            self.running = True
            self.start_btn.config(text="Running...", state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            script_path = os.path.join(os.path.dirname(__file__), "automation.py")
            self.process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            threading.Thread(
                target=self.read_output,
                daemon=True
            ).start()
            
            self.check_queue()

    def read_output(self):
        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                self.output_queue.put(output)
        self.output_queue.put(None)

    def check_queue(self):
        try:
            while True:
                output = self.output_queue.get_nowait()
                if output is None:
                    self.process_finished()
                    break
                self.update_output(output)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def update_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def process_finished(self):
        self.running = False
        self.start_btn.config(text="Automation Start", state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_output("\nProcess finished with exit code: {}\n".format(self.process.poll()))

    def stop_automation(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.update_output("\n[Process manually stopped]\n")
            self.running = False
            self.start_btn.config(text="Automation Start",state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
    def run_push(self):
        """运行push.py文件"""
        script_path = os.path.join(os.path.dirname(__file__), "push.py")
        try:
            self.push_process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            threading.Thread(
                target=self.read_push_output,
                daemon=True
            ).start()
        except Exception as e:
            self.output_queue.put(f"Error running push.py: {str(e)}\n")

    def read_push_output(self):
        """读取push.py的输出并放入队列"""
        while True:
            output = self.push_process.stdout.readline()
            if output == '' and self.push_process.poll() is not None:
                break
            if output:
                self.output_queue.put(output)
        self.output_queue.put("\n[Push process finished]\n")
if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()