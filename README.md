# 🎬 小鹅通已购视频下载器

> 下载小鹅通已购课程，支持AES-128加密解密，6线程并发下载

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ 功能特点

- 🎓 **专为小鹅通设计** - 支持已购课程本地备份
- 🔐 **AES-128解密** - 完整支持小鹅通视频加密
- 🚀 **并行下载** - 6线程并发，速度快5-6倍
- 🎬 **自动合并** - 生成标准MP4格式，兼容所有播放器
- 🖥️ **双界面** - 图形界面 + 命令行版本

**实战验证**：28节课程，100%成功率，平均3-4分钟/课

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pycryptodome
```

### 2. 获取M3U8链接

1. 打开小鹅通课程视频页面
2. 按 `F12` 打开开发者工具
3. 切换到 `Network` 标签
4. 筛选 `m3u8`
5. 播放视频，复制 M3U8 链接

### 3. 开始下载

**图形界面版（推荐新手）**：
```bash
python m3u8_downloader_gui.py
```

**命令行版（适合批量下载）**：
```bash
python ultimate_m3u8_downloader.py
```

---

## ⚠️ 重要声明

**✅ 合法使用**：
- 仅下载自己已购买的小鹅通课程
- 个人学习和本地备份使用

**❌ 禁止行为**：
- 下载未购买的课程
- 商业使用、二次分发、转售

**免责声明**：本工具仅供技术学习使用。用户应遵守法律法规和平台服务条款，仅下载个人已购课程。使用本工具造成的任何法律后果由用户自行承担。

---

## 🐛 常见问题

**Q: pycryptodome 安装失败？**
```bash
pip install pycryptodome --user
```

**Q: 视频无法播放？**
- 使用 VLC 播放器尝试
- 确认 FFmpeg 正确安装

**Q: 下载速度慢？**
- 检查网络速度
- 增加并发线程数（6-10）

---

## 📝 相关文章

📖 [**下载已购小鹅通视频 - 完整教程**](https://ayano29.cn/posts/programming/xiaoe-downloader/)  
详细的技术实现和使用指南

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 了解详情

---

<div align="center">

**如果这个项目对你有帮助，欢迎 Star ⭐ 支持！**

[🌐 博客文章](https://ayano29.cn/posts/programming/xiaoe-downloader/) | [⬆ 回到顶部](#-小鹅通已购视频下载器)

</div>

