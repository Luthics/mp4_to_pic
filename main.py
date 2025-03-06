import os
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess

class VideoToImageConverter:
	def __init__(self, root):
		self.root = root
		self.root.title("视频帧提取工具")
		self.root.geometry("700x500")
		
		# 设置主题样式
		style = ttk.Style()
		style.configure("Main.TFrame", padding=20)
		style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
		style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 10))
		style.configure("Status.TLabel", font=("Microsoft YaHei UI", 9))
		
		# 配置按钮样式
		style.configure("Action.TButton", 
					  padding=10,
					  font=("Microsoft YaHei UI", 10))
		style.configure("Browse.TButton",
					  padding=5,
					  font=("Microsoft YaHei UI", 9))
		
		# 添加终止标志
		self.stop_conversion = False
		
		# 创建主框架
		self.main_frame = ttk.Frame(root, style="Main.TFrame")
		self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
		
		# 标题
		title_frame = ttk.Frame(self.main_frame)
		title_frame.pack(fill=tk.X, pady=(0, 20))
		ttk.Label(title_frame, text="视频帧提取工具", style="Title.TLabel").pack()
		
		# 创建输入框架
		input_frame = ttk.LabelFrame(self.main_frame, text="配置", padding=15)
		input_frame.pack(fill=tk.X, pady=(0, 20))
		
		# 视频文件选择
		video_frame = ttk.Frame(input_frame)
		video_frame.pack(fill=tk.X, pady=(0, 10))
		ttk.Label(video_frame, text="视频文件:", font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
		self.video_path = tk.StringVar()
		self.video_entry = ttk.Entry(video_frame, textvariable=self.video_path, width=60)
		self.video_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
		ttk.Button(video_frame, text="浏览", command=self.browse_video, style="Browse.TButton").pack(side=tk.LEFT)
		
		# 输出目录选择
		output_frame = ttk.Frame(input_frame)
		output_frame.pack(fill=tk.X, pady=(0, 10))
		ttk.Label(output_frame, text="输出目录:", font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
		self.output_path = tk.StringVar()
		self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=60)
		self.output_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
		ttk.Button(output_frame, text="打开", command=self.open_output_folder, style="Browse.TButton").pack(side=tk.LEFT)
		
		# 帧率设置
		rate_frame = ttk.Frame(input_frame)
		rate_frame.pack(fill=tk.X)
		ttk.Label(rate_frame, text="提取帧率:", font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
		self.frame_rate = tk.StringVar(value="4")
		ttk.Entry(rate_frame, textvariable=self.frame_rate, width=10).pack(side=tk.LEFT, padx=10)
		ttk.Label(rate_frame, text="(每X帧提取一张图片)", font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
		
		# 创建状态框架
		status_frame = ttk.LabelFrame(self.main_frame, text="状态", padding=15)
		status_frame.pack(fill=tk.X, pady=(0, 20))
		
		# 进度条
		self.progress_var = tk.DoubleVar()
		self.progress = ttk.Progressbar(status_frame, length=400, mode='determinate', 
									  variable=self.progress_var, style="Horizontal.TProgressbar")
		self.progress.pack(fill=tk.X, pady=(0, 10))
		
		# 状态标签
		self.status_var = tk.StringVar(value="就绪")
		self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
									 style="Status.TLabel")
		self.status_label.pack()
		
		# 按钮框架
		button_frame = ttk.Frame(self.main_frame)
		button_frame.pack(pady=20)
		
		# 开始按钮
		self.start_button = ttk.Button(button_frame, text="开始转换", 
									 command=self.start_conversion, 
									 style="Action.TButton")
		self.start_button.pack(side=tk.LEFT, padx=10)
		
		# 终止按钮
		self.stop_button = ttk.Button(button_frame, text="终止转换", 
									 command=self.stop_conversion_process, 
									 state='disabled',
									 style="Action.TButton")
		self.stop_button.pack(side=tk.LEFT, padx=10)
		
		# 拖放支持
		self.video_entry.drop_target_register(DND_FILES)
		self.video_entry.dnd_bind('<<Drop>>', self.handle_drop)
		
		# 配置窗口大小调整行为
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		
		# 设置窗口最小尺寸
		root.minsize(600, 400)
		
		# 设置窗口图标（如果有的话）
		try:
			root.iconbitmap("icon.ico")
		except:
			pass

	def browse_video(self):
		filename = filedialog.askopenfilename(
			title="选择视频文件",
			filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
		)
		if filename:
			self.video_path.set(filename)
			# 自动设置输出目录
			output_dir = str(Path(filename).parent / Path(filename).stem)
			self.output_path.set(output_dir)

	def open_output_folder(self):
		output_dir = self.output_path.get()
		if not output_dir:
			messagebox.showerror("错误", "请先选择输出目录")
			return
			
		if not os.path.exists(output_dir):
			messagebox.showerror("错误", "输出目录不存在")
			return
			
		try:
			# 使用explorer.exe打开文件夹
			subprocess.Popen(f'explorer.exe "{output_dir}"')
		except Exception as e:
			messagebox.showerror("错误", f"无法打开文件夹：{str(e)}")

	def handle_drop(self, event):
		file_path = event.data
		if file_path.lower().endswith('.mp4'):
			self.video_path.set(file_path)
			# 自动设置输出目录
			output_dir = str(Path(file_path).parent / Path(file_path).stem)
			self.output_path.set(output_dir)
		else:
			messagebox.showerror("错误", "请选择MP4文件")

	def stop_conversion_process(self):
		self.stop_conversion = True
		self.status_var.set("正在终止...")
		self.stop_button.state(['disabled'])

	def start_conversion(self):
		# 重置终止标志
		self.stop_conversion = False
		
		video_path = self.video_path.get()
		output_dir = self.output_path.get()
		try:
			frame_rate = int(self.frame_rate.get())
		except ValueError:
			messagebox.showerror("错误", "请输入有效的帧率数字")
			return

		if not video_path or not output_dir:
			messagebox.showerror("错误", "请选择视频文件和输出目录")
			return

		if not os.path.exists(video_path):
			messagebox.showerror("错误", "视频文件不存在")
			return

		# 创建输出目录
		os.makedirs(output_dir, exist_ok=True)

		# 更新按钮状态
		self.start_button.state(['disabled'])
		self.stop_button.state(['!disabled'])
		self.status_var.set("正在处理...")
		self.progress_var.set(0)

		try:
			self.convert_video(video_path, output_dir, frame_rate)
			if not self.stop_conversion:
				messagebox.showinfo("完成", "转换完成！")
		except Exception as e:
			messagebox.showerror("错误", f"转换过程中出现错误：{str(e)}")
		finally:
			# 恢复按钮状态
			self.start_button.state(['!disabled'])
			self.stop_button.state(['disabled'])
			self.status_var.set("就绪")

	def convert_video(self, video_path, output_dir, frame_rate):
		camera = cv2.VideoCapture(video_path)
		total_frames = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
		current_frame = 0
		
		while True:
			if self.stop_conversion:
				self.status_var.set("已终止")
				break
				
			res, image = camera.read()
			if not res:
				break
				
			if current_frame % frame_rate == 0:
				output_path = os.path.join(output_dir, f"frame_{current_frame}.jpg")
				cv2.imencode('.jpg', image)[1].tofile(output_path)
				
			current_frame += 1
			progress = (current_frame / total_frames) * 100
			self.progress_var.set(progress)
			self.root.update()
			
		camera.release()

if __name__ == "__main__":
	root = TkinterDnD.Tk()
	app = VideoToImageConverter(root)
	root.mainloop()
