# -*- coding: utf-8 -*-
"""
终极M3U8下载器 - 集成FFmpeg下载和AES解密
从第15课开始下载
"""

import json
import os
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import subprocess
import shutil
import zipfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

class UltimateM3U8Downloader:
    def __init__(self, output_dir="D:/ai/UV4/downloads/new"):
        self.output_dir = output_dir
        self.ffmpeg_path = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://xiaoe-tech.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
    def setup_ffmpeg(self):
        """设置FFmpeg"""
        # 检查是否已有FFmpeg
        if os.path.exists("ffmpeg/bin/ffmpeg.exe"):
            self.ffmpeg_path = os.path.abspath("ffmpeg/bin/ffmpeg.exe")
            print(f"找到现有FFmpeg: {self.ffmpeg_path}")
            return True
        
        print("正在下载便携版FFmpeg...")
        try:
            # 下载便携版FFmpeg
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            response = requests.get(ffmpeg_url, stream=True, timeout=120)
            response.raise_for_status()
            
            zip_path = "ffmpeg-portable.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print("解压FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # 找到解压后的文件夹
            for item in os.listdir("."):
                if "ffmpeg" in item.lower() and os.path.isdir(item):
                    if os.path.exists("ffmpeg"):
                        shutil.rmtree("ffmpeg")
                    shutil.move(item, "ffmpeg")
                    break
            
            os.remove(zip_path)
            
            self.ffmpeg_path = os.path.abspath("ffmpeg/bin/ffmpeg.exe")
            if os.path.exists(self.ffmpeg_path):
                print(f"FFmpeg安装成功: {self.ffmpeg_path}")
                return True
            else:
                print("FFmpeg安装失败")
                return False
                
        except Exception as e:
            print(f"FFmpeg设置失败: {e}")
            return False
        
    def safe_filename(self, filename):
        """创建安全的文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def download_m3u8_content(self, url):
        """下载M3U8播放列表"""
        try:
            print(f"获取M3U8播放列表: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"M3U8下载失败: {e}")
            return None
    
    def parse_m3u8(self, content, base_url):
        """解析M3U8内容，提取加密信息"""
        segments = []
        encryption_key_url = None
        encryption_iv = None
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 检查加密信息
            if line.startswith('#EXT-X-KEY:'):
                if 'METHOD=AES-128' in line:
                    # 提取密钥URL
                    uri_start = line.find('URI="') + 5
                    uri_end = line.find('"', uri_start)
                    if uri_start > 4 and uri_end > uri_start:
                        key_url = line[uri_start:uri_end]
                        if not key_url.startswith('http'):
                            encryption_key_url = urljoin(base_url, key_url)
                        else:
                            encryption_key_url = key_url
                    
                    # 提取IV
                    iv_start = line.find('IV=0x')
                    if iv_start != -1:
                        iv_hex = line[iv_start + 5:iv_start + 37]
                        try:
                            encryption_iv = binascii.unhexlify(iv_hex)
                        except:
                            encryption_iv = None
            
            # 提取片段URL
            elif line and not line.startswith('#'):
                if line.startswith('http'):
                    segment_url = line
                else:
                    segment_url = urljoin(base_url, line)
                segments.append(segment_url)
        
        print(f"找到 {len(segments)} 个视频片段")
        if encryption_key_url:
            print("检测到加密: AES-128")
        
        return segments, encryption_key_url, encryption_iv
    
    def download_encryption_key(self, key_url):
        """下载加密密钥"""
        try:
            print(f"下载加密密钥: {key_url}")
            response = self.session.get(key_url, timeout=30)
            response.raise_for_status()
            key = response.content
            print(f"密钥长度: {len(key)} 字节")
            return key
        except Exception as e:
            print(f"密钥下载失败: {e}")
            return None
    
    def decrypt_segment(self, encrypted_data, key, iv):
        """解密视频片段"""
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # 去除填充
            try:
                decrypted_data = unpad(decrypted_data, AES.block_size)
            except:
                # 如果去填充失败，可能不需要去填充
                pass
            
            return decrypted_data
        except Exception as e:
            print(f"解密失败: {e}")
            return encrypted_data
    
    def download_and_decrypt_segment(self, url, filepath, key, iv, segment_index, max_retries=3):
        """下载并解密单个视频片段"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # 下载加密数据
                encrypted_data = b''
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        encrypted_data += chunk
                
                if not encrypted_data:
                    continue
                
                # 解密数据
                if key and iv:
                    # 为每个片段生成IV
                    segment_iv = iv[:-4] + segment_index.to_bytes(4, byteorder='big')
                    decrypted_data = self.decrypt_segment(encrypted_data, key, segment_iv)
                else:
                    decrypted_data = encrypted_data
                
                # 保存解密后的数据
                with open(filepath, 'wb') as f:
                    f.write(decrypted_data)
                
                if os.path.getsize(filepath) > 0:
                    return True
                    
            except Exception as e:
                print(f"下载片段失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        return False
    
    def download_segments_parallel(self, segments, temp_dir, key=None, iv=None, max_workers=6):
        """并行下载和解密所有片段"""
        print(f"开始并行下载和解密 {len(segments)} 个片段...")
        
        def download_with_index(args):
            index, url = args
            filename = f"segment_{index:04d}.ts"
            filepath = os.path.join(temp_dir, filename)
            
            success = self.download_and_decrypt_segment(url, filepath, key, iv, index)
            return index, success, filepath
        
        successful_segments = []
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(download_with_index, (i, url)): i 
                for i, url in enumerate(segments)
            }
            
            for future in as_completed(future_to_index):
                index, success, filepath = future.result()
                
                if success:
                    successful_segments.append((index, filepath))
                    print(f"片段 {index + 1}/{len(segments)} 下载解密成功")
                else:
                    failed_count += 1
                    print(f"片段 {index + 1}/{len(segments)} 下载解密失败")
        
        successful_segments.sort(key=lambda x: x[0])
        print(f"下载完成: 成功 {len(successful_segments)}, 失败 {failed_count}")
        return successful_segments
    
    def merge_segments_with_ffmpeg(self, segments, output_file):
        """使用FFmpeg合并片段"""
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            print("FFmpeg不可用，使用Python合并")
            return self.merge_segments_python(segments, output_file)
        
        try:
            # 创建文件列表
            list_file = output_file.replace('.mp4', '_filelist.txt')
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for _, filepath in segments:
                    rel_path = os.path.relpath(filepath, os.path.dirname(list_file))
                    f.write(f"file '{rel_path}'\n")
            
            # FFmpeg命令 - 重新编码确保MP4格式
            cmd = [
                self.ffmpeg_path, '-f', 'concat', '-safe', '0',
                '-i', list_file,
                '-c:v', 'libx264',  # 重新编码视频
                '-c:a', 'aac',      # 重新编码音频
                '-movflags', '+faststart',  # 优化MP4结构
                '-y',  # 覆盖输出文件
                output_file
            ]
            
            print("使用FFmpeg合并片段...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0 and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 0:
                    print(f"FFmpeg合并成功: {output_file} ({file_size // (1024*1024)}MB)")
                    return True
                else:
                    print("FFmpeg合并失败: 输出文件为空")
                    return False
            else:
                print(f"FFmpeg合并失败，使用Python备用方案")
                return self.merge_segments_python(segments, output_file)
                
        except Exception as e:
            print(f"FFmpeg合并异常，使用Python备用方案: {e}")
            return self.merge_segments_python(segments, output_file)
    
    def merge_segments_python(self, segments, output_file):
        """使用Python直接合并片段（备用方案）"""
        try:
            print("使用Python合并片段...")
            
            with open(output_file, 'wb') as outfile:
                for i, (_, filepath) in enumerate(segments):
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as infile:
                            data = infile.read()
                            if data:
                                outfile.write(data)
                        print(f"合并片段 {i + 1}/{len(segments)}")
                    else:
                        print(f"片段文件不存在: {filepath}")
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 0:
                    print(f"Python合并成功: {output_file} ({file_size // (1024*1024)}MB)")
                    return True
                else:
                    print("Python合并失败: 输出文件为空")
                    return False
            else:
                print("Python合并失败: 输出文件未创建")
                return False
                
        except Exception as e:
            print(f"Python合并异常: {e}")
            return False
    
    def download_course(self, course):
        """下载单个课程"""
        print(f"\n开始下载: {course['title']}")
        print("=" * 60)
        
        # 创建课程目录
        safe_title = self.safe_filename(course['title'])
        course_dir_name = f"{course['chapter']:02d}_{safe_title}"
        course_dir = os.path.join(self.output_dir, course_dir_name)
        
        if not os.path.exists(course_dir):
            os.makedirs(course_dir)
        
        # 检查是否已下载
        mp4_files = [f for f in os.listdir(course_dir) if f.endswith('.mp4')]
        if mp4_files:
            print(f"课程已存在，跳过: {course['title']}")
            return True
        
        # 创建临时目录
        temp_dir = os.path.join(course_dir, "temp_segments")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        try:
            # 1. 下载M3U8播放列表
            m3u8_content = self.download_m3u8_content(course['m3u8_url'])
            if not m3u8_content:
                return False
            
            # 2. 解析片段URL和加密信息
            base_url = '/'.join(course['m3u8_url'].split('/')[:-1]) + '/'
            segments, key_url, iv = self.parse_m3u8(m3u8_content, base_url)
            
            if not segments:
                print("未找到视频片段")
                return False
            
            # 3. 下载加密密钥
            key = None
            if key_url:
                key = self.download_encryption_key(key_url)
                if key:
                    print(f"IV长度: {len(iv) if iv else 0} 字节")
            
            # 4. 下载和解密所有片段
            successful_segments = self.download_segments_parallel(segments, temp_dir, key, iv)
            
            if not successful_segments:
                print("所有片段下载失败")
                return False
            
            # 5. 合并片段
            output_file = os.path.join(course_dir, f"{course['chapter']:02d}_{safe_title}.mp4")
            
            merge_success = self.merge_segments_with_ffmpeg(successful_segments, output_file)
            
            # 6. 清理临时文件
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            if merge_success:
                print(f"课程下载完成: {course['title']}")
                return True
            else:
                print(f"课程合并失败: {course['title']}")
                return False
                
        except Exception as e:
            print(f"下载异常: {e}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False

def load_course_data():
    """加载课程数据"""
    with open('xiaoe_course_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['courses']

def main():
    print("终极M3U8下载器 - 从第15课开始")
    print("=" * 60)
    
    # 创建下载器
    downloader = UltimateM3U8Downloader()
    
    # 设置FFmpeg
    print("正在设置FFmpeg...")
    ffmpeg_ready = downloader.setup_ffmpeg()
    if ffmpeg_ready:
        print("FFmpeg准备就绪")
    else:
        print("FFmpeg设置失败，将使用Python合并")
    
    # 创建输出目录
    os.makedirs(downloader.output_dir, exist_ok=True)
    
    # 加载课程数据
    try:
        courses = load_course_data()
        print(f"加载了 {len(courses)} 节课程")
    except Exception as e:
        print(f"加载课程数据失败: {e}")
        return False
    
    # 从第15课开始（索引14）
    start_index = 14  # 第15课
    courses_to_download = courses[start_index:]
    
    print(f"从第{start_index + 1}课开始，需要下载 {len(courses_to_download)} 节课程")
    print(f"下载目录: {downloader.output_dir}")
    print()
    
    # 开始下载
    success_count = 0
    failed_courses = []
    
    start_time = time.time()
    
    for i, course in enumerate(courses_to_download, 1):
        actual_course_num = start_index + i
        print(f"\n进度: {i}/{len(courses_to_download)} (总进度: {actual_course_num}/{len(courses)})")
        
        success = downloader.download_course(course)
        
        if success:
            success_count += 1
        else:
            failed_courses.append(f"第{course['chapter']}课")
        
        print(f"当前统计 - 成功: {success_count}/{i}")
        
        # 短暂延迟
        time.sleep(1)
    
    # 最终统计
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("下载完成!")
    print("=" * 60)
    print(f"本次下载: {len(courses_to_download)}")
    print(f"成功: {success_count}")
    print(f"成功率: {success_count/len(courses_to_download)*100:.1f}%")
    print(f"用时: {duration/60:.1f}分钟")
    
    if failed_courses:
        print(f"失败: {', '.join(failed_courses)}")
    
    print(f"\n所有文件保存在: {downloader.output_dir}")
    print("=" * 60)
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n下载任务完成!")
    else:
        print("\n下载失败!")
    
    try:
        input("按任意键退出...")
    except:
        pass
