import os
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp', '.ts', '.mts', '.m2ts'}

class FastVideoMaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FastVideoMask - 视频元数据修改工具")
        self.root.geometry("750x600")
        self.root.minsize(650, 500)
        
        self.is_processing = False
        self.current_process = None
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 14, 'bold'), foreground='#2c3e50')
        style.configure('Info.TLabel', font=('Microsoft YaHei UI', 10), foreground='#7f8c8d')
        style.configure('Status.TLabel', font=('Microsoft YaHei UI', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Microsoft YaHei UI', 10), foreground='#e74c3c')
        style.configure('Primary.TButton', font=('Microsoft YaHei UI', 10), padding=(20, 10))
        style.configure('Danger.TButton', font=('Microsoft YaHei UI', 10), padding=(20, 10))
        style.configure('TLabelframe.Label', font=('Microsoft YaHei UI', 10, 'bold'), foreground='#2c3e50')
        style.configure('TEntry', padding=5)
        style.configure('Horizontal.TProgressbar', thickness=20)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="🎬 FastVideoMask", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="快速修改视频元数据", style='Info.TLabel')
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=(5, 0))
        
        source_frame = ttk.LabelFrame(main_frame, text="📁 源目录", padding="15")
        source_frame.pack(fill=tk.X, pady=(0, 12))
        
        source_inner = ttk.Frame(source_frame)
        source_inner.pack(fill=tk.X)
        
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(source_inner, textvariable=self.source_var, font=('Microsoft YaHei UI', 10))
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        source_btn = ttk.Button(source_inner, text="浏览...", command=self.browse_source, width=10)
        source_btn.pack(side=tk.RIGHT)
        
        target_frame = ttk.LabelFrame(main_frame, text="📂 目标目录", padding="15")
        target_frame.pack(fill=tk.X, pady=(0, 12))
        
        target_inner = ttk.Frame(target_frame)
        target_inner.pack(fill=tk.X)
        
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(target_inner, textvariable=self.target_var, font=('Microsoft YaHei UI', 10))
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        target_btn = ttk.Button(target_inner, text="浏览...", command=self.browse_target, width=10)
        target_btn.pack(side=tk.RIGHT)
        
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 元数据设置", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 12))
        
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(fill=tk.X)
        options_grid.columnconfigure(1, weight=1)
        
        ttk.Label(options_grid, text="标题:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=8)
        self.title_var = tk.StringVar(value="Modified by AI")
        ttk.Entry(options_grid, textvariable=self.title_var, font=('Microsoft YaHei UI', 10)).grid(row=0, column=1, sticky='ew', pady=8)
        
        ttk.Label(options_grid, text="注释:", font=('Microsoft YaHei UI', 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 15), pady=8)
        self.comment_var = tk.StringVar(value="Processed by FastVideoMask")
        ttk.Entry(options_grid, textvariable=self.comment_var, font=('Microsoft YaHei UI', 10)).grid(row=1, column=1, sticky='ew', pady=8)
        
        ttk.Label(options_grid, text="作者:", font=('Microsoft YaHei UI', 10)).grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=8)
        self.artist_var = tk.StringVar(value="AI")
        ttk.Entry(options_grid, textvariable=self.artist_var, font=('Microsoft YaHei UI', 10)).grid(row=2, column=1, sticky='ew', pady=8)
        
        ttk.Label(options_grid, text="文件名后缀:", font=('Microsoft YaHei UI', 10)).grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=8)
        self.suffix_var = tk.StringVar(value="_MASK")
        ttk.Entry(options_grid, textvariable=self.suffix_var, font=('Microsoft YaHei UI', 10)).grid(row=3, column=1, sticky='ew', pady=8)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_btn = ttk.Button(btn_frame, text="▶ 开始转换", command=self.start_conversion, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ 取消", command=self.stop_conversion, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT)
        
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="0%", font=('Microsoft YaHei UI', 10, 'bold'), width=8)
        self.progress_label.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="就绪，请选择源目录和目标目录")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(0, 12))
        
        log_frame = ttk.LabelFrame(main_frame, text="📋 处理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_inner = ttk.Frame(log_frame)
        log_inner.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_inner, 
            height=8, 
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#2c3e50',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        scrollbar = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)
        
    def browse_source(self):
        path = filedialog.askdirectory(title="选择源目录")
        if path:
            self.source_var.set(path)
            
    def browse_target(self):
        path = filedialog.askdirectory(title="选择目标目录")
        if path:
            self.target_var.set(path)
            
    def log(self, message, level='info'):
        self.log_text.configure(state=tk.NORMAL)
        timestamp = __import__('datetime').datetime.now().strftime('%H:%M:%S')
        
        if level == 'error':
            self.log_text.insert(tk.END, f"[{timestamp}] ❌ {message}\n", 'error')
        elif level == 'success':
            self.log_text.insert(tk.END, f"[{timestamp}] ✓ {message}\n", 'success')
        else:
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.progress_label.configure(text=f"{value:.1f}%")
        
    def start_conversion(self):
        source_dir = self.source_var.get().strip()
        target_dir = self.target_var.get().strip()
        
        if not source_dir:
            messagebox.showerror("错误", "请选择源目录")
            return
            
        if not target_dir:
            messagebox.showerror("错误", "请选择目标目录")
            return
            
        if not os.path.isdir(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
            
        self.is_processing = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_label.configure(style='Status.TLabel')
        
        thread = threading.Thread(target=self.process_videos, args=(source_dir, target_dir), daemon=True)
        thread.start()
        
    def stop_conversion(self):
        self.is_processing = False
        if self.current_process:
            self.current_process.terminate()
            self.current_process = None
        self.status_var.set("正在取消...")
        self.status_label.configure(style='Error.TLabel')
        
    def process_videos(self, source_dir, target_dir):
        video_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in VIDEO_EXTENSIONS:
                    video_files.append(os.path.join(root, file))
                    
        total = len(video_files)
        if total == 0:
            self.log("未找到视频文件")
            self.status_var.set("未找到视频文件")
            self.status_label.configure(style='Error.TLabel')
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            return
            
        self.log(f"找到 {total} 个视频文件，开始处理...")
        
        success_count = 0
        fail_count = 0
        
        for i, video_path in enumerate(video_files):
            if not self.is_processing:
                self.log("已取消转换", level='error')
                break
                
            rel_path = os.path.relpath(video_path, source_dir)
            self.status_var.set(f"处理中 ({i+1}/{total}): {rel_path}")
            self.log(f"处理: {rel_path}")
            
            try:
                result = self.process_single_video(video_path, source_dir, target_dir)
                if result:
                    success_count += 1
                    self.log("转换成功", level='success')
                else:
                    fail_count += 1
                    self.log("转换失败", level='error')
            except Exception as e:
                fail_count += 1
                self.log(f"错误: {str(e)}", level='error')
                
            if self.is_processing:
                progress = ((i + 1) / total) * 100
                self.root.after(0, lambda p=progress: self.update_progress(p))
            
        if self.is_processing:
            self.status_var.set(f"完成! 成功: {success_count}, 失败: {fail_count}")
            self.log(f"\n全部完成! 成功: {success_count}, 失败: {fail_count}", level='success')
            self.root.after(0, lambda: self.update_progress(100))
        else:
            self.status_var.set(f"已取消. 成功: {success_count}, 失败: {fail_count}")
            self.log(f"\n已取消. 已处理: 成功 {success_count}, 失败 {fail_count}", level='error')
        
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.is_processing = False
        
    def process_single_video(self, video_path, source_dir, target_dir):
        rel_path = os.path.relpath(video_path, source_dir)
        
        name = Path(rel_path).stem
        ext = Path(rel_path).suffix
        parent = Path(rel_path).parent
        
        suffix = self.suffix_var.get()
        new_name = f"{name}{suffix}{ext}"
        
        target_path = os.path.join(target_dir, parent, new_name)
        target_dir_path = os.path.dirname(target_path)
        
        os.makedirs(target_dir_path, exist_ok=True)
        
        title = self.title_var.get()
        comment = self.comment_var.get()
        artist = self.artist_var.get()
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-metadata', f'title={title}',
            '-metadata', f'comment={comment}',
            '-metadata', f'artist={artist}',
            '-codec', 'copy',
            target_path
        ]
        
        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        stdout, stderr = self.current_process.communicate()
        self.current_process = None
        
        return self.current_process is None or self.current_process.returncode == 0

def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    app = FastVideoMaskApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
