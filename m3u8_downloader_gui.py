# -*- coding: utf-8 -*-
"""
M3U8视频下载器 - 图形界面版
支持小鹅通等平台的AES-128加密视频
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import os
import shutil
import subprocess
import binascii
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import zipfile
from datetime import datetime

class M3U8DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U8视频下载器 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 变量
        self.m3u8_url = tk.StringVar()
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads", "M3U8Videos"))
        self.video_name = tk.StringVar(value="video")
        self.max_workers = tk.IntVar(value=6)
        self.is_downloading = False
        
        # FFmpeg路径
        self.ffmpeg_path = None
        
        # Session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://xiaoe-tech.com/',
            'Accept': '*/*',
        })
        
        self.create_widgets()
        self.check_ffmpeg()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # M3U8链接输入
        row = 0
        ttk.Label(main_frame, text="M3U8链接:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        url_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(url_frame, textvariable=self.m3u8_url, width=60).grid(
            row=0, column=0, sticky=(tk.W, tk.E)
        )
        ttk.Button(url_frame, text="粘贴", command=self.paste_url, width=8).grid(
            row=0, column=1, padx=(5, 0)
        )
        
        # 视频名称
        row += 1
        ttk.Label(main_frame, text="视频名称:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.video_name, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0)
        )
        
        # 保存路径
        row += 1
        ttk.Label(main_frame, text="保存路径:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.save_path, width=50).grid(
            row=0, column=0, sticky=(tk.W, tk.E)
        )
        ttk.Button(path_frame, text="浏览", command=self.select_path, width=8).grid(
            row=0, column=1, padx=(5, 0)
        )
        
        # 线程数设置
        row += 1
        ttk.Label(main_frame, text="并发线程:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        thread_frame = ttk.Frame(main_frame)
        thread_frame.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Spinbox(thread_frame, from_=1, to=10, textvariable=self.max_workers, width=10).grid(
            row=0, column=0
        )
        ttk.Label(thread_frame, text="(建议4-8，太高可能被限速)", foreground="gray").grid(
            row=0, column=1, padx=(10, 0)
        )
        
        # 进度条
        row += 1
        ttk.Label(main_frame, text="下载进度:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 进度文本
        row += 1
        self.progress_label = ttk.Label(main_frame, text="等待开始...", foreground="blue")
        self.progress_label.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # 日志显示区域
        row += 1
        ttk.Label(main_frame, text="下载日志:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=(tk.W, tk.N), pady=5
        )
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=60, 
                                                   wrap=tk.WORD, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.rowconfigure(row, weight=1)
        
        # 按钮框架
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        self.download_btn = ttk.Button(button_frame, text="开始下载", 
                                       command=self.start_download, width=15)
        self.download_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="停止", 
                                   command=self.stop_download, width=15, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="清空日志", 
                  command=self.clear_log, width=15).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="打开保存目录", 
                  command=self.open_save_dir, width=15).grid(row=0, column=3, padx=5)
        
        # 状态栏
        self.status_label = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def paste_url(self):
        """粘贴链接"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.m3u8_url.set(clipboard_text)
            self.log("已粘贴链接")
        except:
            self.log("剪贴板为空", "warning")
    
    def select_path(self):
        """选择保存路径"""
        path = filedialog.askdirectory(title="选择保存目录")
        if path:
            self.save_path.set(path)
            self.log(f"保存路径: {path}")
    
    def log(self, message, level="info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_text.configure(state='normal')
        
        if level == "error":
            color_tag = "error"
            prefix = "❌"
        elif level == "success":
            color_tag = "success"
            prefix = "✅"
        elif level == "warning":
            color_tag = "warning"
            prefix = "⚠️"
        else:
            color_tag = "info"
            prefix = "ℹ️"
        
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="black")
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n", color_tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        
        # 更新状态栏
        self.status_label.config(text=message)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        self.log("日志已清空")
    
    def open_save_dir(self):
        """打开保存目录"""
        path = self.save_path.get()
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("提示", "保存目录不存在")
    
    def check_ffmpeg(self):
        """检查FFmpeg"""
        # 检查本地ffmpeg目录
        if os.path.exists("ffmpeg/bin/ffmpeg.exe"):
            self.ffmpeg_path = os.path.abspath("ffmpeg/bin/ffmpeg.exe")
            self.log("找到FFmpeg: ffmpeg/bin/ffmpeg.exe", "success")
        else:
            self.log("FFmpeg未找到，将在下载时自动安装", "warning")
    
    def setup_ffmpeg(self):
        """自动下载FFmpeg"""
        if self.ffmpeg_path:
            return True
        
        try:
            self.log("正在下载FFmpeg（约90MB）...")
            self.progress_label.config(text="下载FFmpeg中...")
            
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            response = requests.get(ffmpeg_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            zip_path = "ffmpeg-portable.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.progress_label.config(text=f"下载FFmpeg: {percent:.1f}%")
            
            self.log("正在解压FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # 查找并重命名
            for item in os.listdir("."):
                if "ffmpeg" in item.lower() and os.path.isdir(item) and item != "ffmpeg":
                    if os.path.exists("ffmpeg"):
                        shutil.rmtree("ffmpeg")
                    shutil.move(item, "ffmpeg")
                    break
            
            os.remove(zip_path)
            
            self.ffmpeg_path = os.path.abspath("ffmpeg/bin/ffmpeg.exe")
            if os.path.exists(self.ffmpeg_path):
                self.log("FFmpeg安装成功", "success")
                return True
            else:
                self.log("FFmpeg安装失败", "error")
                return False
                
        except Exception as e:
            self.log(f"FFmpeg安装失败: {e}", "error")
            return False
    
    def start_download(self):
        """开始下载"""
        # 验证输入
        url = self.m3u8_url.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入M3U8链接")
            return
        
        if not url.endswith('.m3u8'):
            result = messagebox.askyesno("提示", "链接不是标准M3U8格式，是否继续？")
            if not result:
                return
        
        name = self.video_name.get().strip()
        if not name:
            messagebox.showerror("错误", "请输入视频名称")
            return
        
        save_path = self.save_path.get().strip()
        if not save_path:
            messagebox.showerror("错误", "请选择保存路径")
            return
        
        # 创建保存目录
        try:
            os.makedirs(save_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建保存目录: {e}")
            return
        
        # 禁用按钮
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.is_downloading = True
        
        # 清空日志
        self.clear_log()
        
        # 重置进度
        self.progress['value'] = 0
        self.progress_label.config(text="准备下载...")
        
        # 启动下载线程
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()
    
    def stop_download(self):
        """停止下载"""
        self.is_downloading = False
        self.log("正在停止...", "warning")
        self.stop_btn.config(state='disabled')
    
    def download_video(self):
        """下载视频（在后台线程中运行）"""
        try:
            url = self.m3u8_url.get().strip()
            name = self.video_name.get().strip()
            save_path = self.save_path.get().strip()
            
            # 安全文件名
            safe_name = self.safe_filename(name)
            output_file = os.path.join(save_path, f"{safe_name}.mp4")
            temp_dir = os.path.join(save_path, f"temp_{safe_name}")
            
            self.log(f"开始下载: {name}")
            self.log(f"M3U8链接: {url}")
            
            # 检查FFmpeg
            if not self.ffmpeg_path:
                if not self.setup_ffmpeg():
                    self.log("FFmpeg不可用，将使用Python合并", "warning")
            
            # 1. 下载M3U8
            self.log("正在获取M3U8播放列表...")
            m3u8_content = self.session.get(url, timeout=30).text
            
            # 2. 解析
            base_url = '/'.join(url.split('/')[:-1]) + '/'
            segments, key_url, iv = self.parse_m3u8(m3u8_content, base_url)
            
            if not segments:
                self.log("未找到视频片段", "error")
                return
            
            self.log(f"找到 {len(segments)} 个视频片段", "success")
            
            # 3. 获取密钥
            key = None
            if key_url:
                self.log("正在获取解密密钥...")
                key = self.session.get(key_url, timeout=30).content
                self.log(f"密钥长度: {len(key)} 字节", "success")
                if iv:
                    self.log(f"IV长度: {len(iv)} 字节", "success")
            
            # 4. 创建临时目录
            os.makedirs(temp_dir, exist_ok=True)
            
            # 5. 并行下载
            self.log(f"开始并行下载（{self.max_workers.get()}线程）...")
            successful_segments = self.download_segments_parallel(
                segments, key, iv, temp_dir
            )
            
            if not successful_segments:
                self.log("所有片段下载失败", "error")
                return
            
            self.log(f"成功下载 {len(successful_segments)}/{len(segments)} 个片段", "success")
            
            # 6. 合并
            self.log("正在合并视频...")
            self.progress_label.config(text="合并视频中...")
            
            if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
                success = self.merge_with_ffmpeg(successful_segments, output_file)
            else:
                success = self.merge_with_python(successful_segments, output_file)
            
            # 7. 清理
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            if success:
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                self.log(f"下载完成: {output_file}", "success")
                self.log(f"文件大小: {file_size:.2f} MB", "success")
                self.progress['value'] = 100
                self.progress_label.config(text="下载完成！")
                
                messagebox.showinfo("成功", f"视频下载完成！\n保存位置: {output_file}")
            else:
                self.log("视频合并失败", "error")
                messagebox.showerror("错误", "视频合并失败")
            
        except Exception as e:
            self.log(f"下载失败: {e}", "error")
            messagebox.showerror("错误", f"下载失败: {e}")
        
        finally:
            # 恢复按钮
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.is_downloading = False
    
    def safe_filename(self, filename):
        """创建安全的文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def parse_m3u8(self, content, base_url):
        """解析M3U8"""
        segments = []
        key_url = None
        iv = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('#EXT-X-KEY:'):
                if 'METHOD=AES-128' in line:
                    # 提取密钥URL
                    uri_start = line.find('URI="') + 5
                    uri_end = line.find('"', uri_start)
                    if uri_start > 4 and uri_end > uri_start:
                        key_url = urljoin(base_url, line[uri_start:uri_end])
                    
                    # 提取IV
                    iv_start = line.find('IV=0x')
                    if iv_start != -1:
                        iv_hex = line[iv_start + 5:iv_start + 37]
                        try:
                            iv = binascii.unhexlify(iv_hex)
                        except:
                            pass
            
            elif line and not line.startswith('#'):
                segment_url = urljoin(base_url, line)
                segments.append(segment_url)
        
        return segments, key_url, iv
    
    def download_and_decrypt_segment(self, url, key, iv, index, temp_dir):
        """下载并解密单个片段"""
        if not self.is_downloading:
            return None
        
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                encrypted_data = b''.join(response.iter_content(8192))
                
                if not encrypted_data:
                    continue
                
                # 解密
                if key and iv:
                    segment_iv = iv[:-4] + index.to_bytes(4, byteorder='big')
                    cipher = AES.new(key, AES.MODE_CBC, segment_iv)
                    decrypted_data = cipher.decrypt(encrypted_data)
                    try:
                        decrypted_data = unpad(decrypted_data, AES.block_size)
                    except:
                        pass
                else:
                    decrypted_data = encrypted_data
                
                # 保存
                filepath = os.path.join(temp_dir, f"segment_{index:04d}.ts")
                with open(filepath, 'wb') as f:
                    f.write(decrypted_data)
                
                return filepath
                
            except Exception as e:
                if attempt < 2:
                    continue
                else:
                    self.log(f"片段{index}下载失败: {e}", "error")
                    return None
        
        return None
    
    def download_segments_parallel(self, segments, key, iv, temp_dir):
        """并行下载"""
        successful_segments = []
        failed_count = 0
        total = len(segments)
        
        with ThreadPoolExecutor(max_workers=self.max_workers.get()) as executor:
            futures = {
                executor.submit(self.download_and_decrypt_segment, 
                              url, key, iv, i, temp_dir): i
                for i, url in enumerate(segments)
            }
            
            for future in as_completed(futures):
                if not self.is_downloading:
                    executor.shutdown(wait=False)
                    break
                
                index = futures[future]
                filepath = future.result()
                
                if filepath:
                    successful_segments.append((index, filepath))
                    percent = (len(successful_segments) / total) * 100
                    self.progress['value'] = percent
                    self.progress_label.config(
                        text=f"下载进度: {len(successful_segments)}/{total} ({percent:.1f}%)"
                    )
                else:
                    failed_count += 1
        
        successful_segments.sort(key=lambda x: x[0])
        
        if failed_count > 0:
            self.log(f"失败片段: {failed_count}", "warning")
        
        return successful_segments
    
    def merge_with_ffmpeg(self, segments, output_file):
        """FFmpeg合并"""
        try:
            list_file = output_file.replace('.mp4', '_filelist.txt')
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for _, filepath in segments:
                    # 使用绝对路径
                    abs_path = os.path.abspath(filepath)
                    f.write(f"file '{abs_path}'\n")
            
            cmd = [
                self.ffmpeg_path, '-f', 'concat', '-safe', '0',
                '-i', list_file,
                '-c', 'copy',  # 使用copy更快
                '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0 and os.path.exists(output_file):
                return True
            else:
                return self.merge_with_python(segments, output_file)
                
        except Exception as e:
            self.log(f"FFmpeg合并失败: {e}", "error")
            return self.merge_with_python(segments, output_file)
    
    def merge_with_python(self, segments, output_file):
        """Python合并"""
        try:
            with open(output_file, 'wb') as outfile:
                for i, (_, filepath) in enumerate(segments):
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as infile:
                            outfile.write(infile.read())
            
            return os.path.exists(output_file) and os.path.getsize(output_file) > 0
            
        except Exception as e:
            self.log(f"Python合并失败: {e}", "error")
            return False

def main():
    root = tk.Tk()
    app = M3U8DownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()


