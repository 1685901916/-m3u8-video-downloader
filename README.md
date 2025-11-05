# 🎬 M3U8视频下载器

> 功能完整的M3U8视频下载工具，支持AES-128加密视频解密

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)

---

## ✨ 功能特点

- 🔐 **AES-128解密** - 完整支持小鹅通等平台的视频加密
- 🚀 **并行下载** - 6线程并发，速度提升5-6倍
- 🎬 **智能合并** - 自动FFmpeg处理，生成标准MP4格式
- 🖥️ **双界面** - 图形界面（GUI）+ 命令行界面（CLI）
- 🛡️ **容错机制** - 多层重试和错误恢复
- ♻️ **高复用性** - 适用于各种M3U8平台

---

## 📊 实战验证

| 指标 | 数据 |
|------|------|
| 测试课程数 | 28节 |
| 成功率 | 100% |
| 平均耗时 | 3-4分钟/课 |
| 视频质量 | 1080p超清 |
| 文件格式 | 标准MP4 |
| 播放兼容性 | 100% |

---

## 🚀 快速开始

### 安装依赖

```bash
pip install requests pycryptodome
```

### 图形界面版（推荐）

```bash
python m3u8_downloader_gui.py
```

**使用步骤**：
1. 粘贴M3U8链接
2. 设置视频名称和保存路径
3. 点击"开始下载"

### 命令行版

```bash
python ultimate_m3u8_downloader.py
```

**适合批量下载**，需要准备课程数据JSON文件。

---

## 📖 详细文档

- 📘 [START_HERE.md](START_HERE.md) - 快速开始指南
- 📗 [完整项目说明](README_完整项目说明.md) - 全面了解项目
- 📙 [使用指南](ULTIMATE_DOWNLOADER_GUIDE.md) - 详细功能文档
- 📕 [系统架构](系统架构图.md) - 技术架构详解
- 📝 [快速参考卡](快速参考卡.md) - 速查手册

---

## 💻 使用示例

### 图形界面版

![GUI界面](docs/screenshots/gui.png) *(示意图)*

**操作流程**：
1. 获取M3U8链接（浏览器F12 → Network → 筛选m3u8）
2. 运行程序，粘贴链接
3. 设置保存路径
4. 开始下载

### 命令行版

```python
from ultimate_m3u8_downloader import UltimateM3U8Downloader

# 创建下载器
downloader = UltimateM3U8Downloader(output_dir="downloads")

# 设置FFmpeg
downloader.setup_ffmpeg()

# 下载视频
course = {
    'chapter': 1,
    'title': '第01课-Python基础',
    'm3u8_url': 'https://example.com/video.m3u8'
}

downloader.download_course(course)
```

---

## 🔧 核心技术

### AES-128解密

```python
from Crypto.Cipher import AES

def decrypt_segment(encrypted_data, key, iv, segment_index):
    # 为每个片段生成独立IV
    segment_iv = iv[:-4] + segment_index.to_bytes(4, byteorder='big')
    
    # AES CBC模式解密
    cipher = AES.new(key, AES.MODE_CBC, segment_iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    
    return decrypted_data
```

### 并行下载

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(download_segment, url) 
               for url in segments]
    
    for future in as_completed(futures):
        result = future.result()
```

### FFmpeg合并

```bash
ffmpeg -f concat -i filelist.txt -c:v libx264 -c:a aac output.mp4
```

---

## 📁 项目结构

```
m3u8-downloader/
├── ultimate_m3u8_downloader.py    # 命令行版主程序
├── m3u8_downloader_gui.py         # 图形界面版主程序
├── xiaoe_course_data.json         # 课程数据示例
├── requirements.txt                # Python依赖
├── 安装依赖.bat                    # Windows依赖安装脚本
├── 一键下载全部课程.bat            # Windows快捷启动
│
├── docs/                          # 文档目录
│   ├── START_HERE.md
│   ├── README_完整项目说明.md
│   ├── ULTIMATE_DOWNLOADER_GUIDE.md
│   ├── 快速参考卡.md
│   ├── 系统架构图.md
│   └── ...
│
└── README.md                      # 本文件
```

---

## 🛠️ 技术栈

- **Python 3.8+** - 主要开发语言
- **requests** - HTTP请求处理
- **pycryptodome** - AES加密解密
- **concurrent.futures** - 并发下载
- **tkinter** - 图形界面（GUI版）
- **FFmpeg** - 视频格式转换

---

## 🎯 适用场景

### 支持的平台

- ✅ 小鹅通
- ✅ 网易云课堂
- ✅ 腾讯课堂
- ✅ 其他使用M3U8+AES加密的平台

### 使用场景

- 📚 在线课程离线学习
- 💾 视频内容本地备份
- 🎓 教育培训资料存档
- 📹 合法购买内容下载

---

## ⚠️ 重要声明

### 法律合规

**✅ 允许的使用**：
- 下载自己已购买的课程
- 个人学习和备份
- 离线学习使用

**❌ 禁止的行为**：
- 下载未购买的课程（侵权）
- 商业使用或盈利
- 二次分发或转售
- 上传到公共平台分享

### 免责声明

```
本工具仅供技术学习和研究使用。
用户应遵守相关法律法规和平台服务条款。
下载内容仅限个人已购买的课程。
不得用于任何侵权或违法行为。
使用本工具造成的任何法律后果由用户自行承担。
```

---

## 🐛 常见问题

### Q: 如何获取M3U8链接？

**A**: 使用浏览器开发者工具
1. 打开视频页面
2. 按F12打开开发者工具
3. 切换到Network标签
4. 筛选m3u8
5. 播放视频，复制链接

### Q: pycryptodome安装失败？

**A**: 
```bash
pip install pycryptodome --user
# 或
conda install -c conda-forge pycryptodome
```

### Q: 视频无法播放？

**A**: 
- 使用VLC播放器尝试
- 检查文件大小是否正常
- 确认FFmpeg正确安装

### Q: 下载速度慢？

**A**: 
- 增加并发线程数（6-10）
- 检查网络速度
- 使用有线网络

更多问题请查看 [完整FAQ](docs/FAQ.md)

---

## 🔄 更新日志

### v1.0 (2025-11-01)

**初始发布**
- ✅ 图形界面和命令行双版本
- ✅ AES-128加密支持
- ✅ 并行下载引擎
- ✅ 自动FFmpeg管理
- ✅ 完整错误恢复机制
- ✅ 28节课程实战验证

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [FFmpeg](https://ffmpeg.org/) - 视频处理工具
- [pycryptodome](https://pycryptodome.readthedocs.io/) - 加密解密库
- 所有贡献者和用户

---

## 📞 联系方式

- 📮 Issues: [GitHub Issues](https://github.com/yourusername/m3u8-downloader/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/m3u8-downloader/discussions)
- 🌐 博客: [ayano29.cn](https://ayano29.cn)

---

## 📝 相关文章

- [下载已购小鹅通视频 - 完整教程](https://ayano29.cn) - 详细的技术实现和使用指南

---

## ⭐ Star History

如果这个项目对你有帮助，欢迎 Star ⭐ 支持！

---

<div align="center">

**Made with ❤️**

[🌐 博客](https://ayano29.cn) | [⬆ 回到顶部](#-m3u8视频下载器)

</div>

