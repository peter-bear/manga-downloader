# 漫画下载器 (Manga Downloader)

一个基于 Flask 和 DrissionPage 的漫画下载工具，支持自动下载漫画并转换为 PDF 格式。

## ✨ 特性

- 🎨 简洁美观的 Web 界面
- 📥 自动下载漫画章节
- 📄 自动将 WebP 图片转换为 PDF
- 🔄 实时任务状态监控
- ⏸️ 支持暂停/停止下载
- 🐳 Docker 部署，开箱即用
- 💾 支持文件夹挂载，数据持久化



## 🚀 快速开始

### 使用 Docker Compose（推荐）

1. **克隆或下载项目**

```bash
git clone <repo-url>
cd manga-downloader
```

2. **启动服务**

```bash
docker-compose up -d --build
```

3. **访问界面**

打开浏览器访问：`http://localhost:25000`

3. **下载的文件位置**

下载的漫画会保存在：`/home/peter/Dockers/komga/data`（可在 docker-compose.yml 中修改）



### 手动运行（开发环境）

1. **安装依赖**

```bash
pip install -r requirements.txt
```

1. **运行应用**

```bash
python app.py
```

1. **访问界面**

打开浏览器访问：`http://localhost:5000`





## 📁 项目结构

```
manga-downloader/
├── Dockerfile              # Docker 镜像配置
├── docker-compose.yml      # Docker Compose 配置
├── requirements.txt        # Python 依赖
├── app.py                 # Flask 主应用
├── downloader.py          # 下载器核心逻辑
├── converter.py           # PDF 转换工具
├── templates/
│   └── index.html         # Web 前端界面
└── downloads/             # 下载文件保存目录（自动创建）
```



## 🛠️ 配置说明

### docker-compose.yml

```yaml
services:
  manga-downloader:
    ports:
      - "25000:5000"        # 映射端口（主机:容器）
    volumes:
      - /path/to/downloads:/app/downloads  # 下载目录挂载
    shm_size: '2gb'         # 共享内存大小（Chrome 需要）
```

### 下载参数

- **URL**: 漫画页面的完整 URL
- **章节列表选择器**: CSS 选择器，用于定位章节列表（默认：`#chapter-list-0`）
- **章节列表索引**: 选择第几个章节列表（默认：`0`）
- **无头模式**: 后台运行浏览器（Docker 中自动启用）
- **自动转换 PDF**: 下载完成后自动转换为 PDF（默认：启用）
- **代理地址**: 可选，格式：`IP:端口`



## 📦 文件结构

下载的文件会按以下结构保存：

```
downloads/
└── 漫画名称/
    ├── 漫画名称 - 第01话/
    │   ├── 001_page.webp
    │   ├── 002_page.webp
    │   └── ...
    ├── 漫画名称 - 第02话/
    │   └── ...
    └── 漫画名称 - 第01话.pdf  # 转换后的 PDF
```



## 🔧 常见问题

### 1. 下载的文件找不到

检查 docker-compose.yml 中的挂载路径是否正确：

```yaml
volumes:
  - /your/host/path:/app/downloads
```

### 2. PDF 转换失败

确保系统安装了 Pillow 库的依赖：

```bash
# Ubuntu/Debian
apt-get install -y libjpeg-dev zlib1g-dev

# 或在 Docker 中已经包含
```



## 🐳 Docker 命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build

# 查看容器状态
docker-compose ps

# 导出镜像
docker save -o manga-downloader.tar manga-manga-downloader:latest
```



## 📝 开发

### 添加新功能

1. 修改代码
2. 重新构建镜像：`docker-compose up -d --build`
3. 查看日志：`docker-compose logs -f`



### 调试

在 `app.py` 中已添加详细的调试日志，使用 `[DEBUG]` 和 `[ERROR]` 标记。





## 📄 依赖

- Python 3.11
- Flask 3.0.0
- DrissionPage
- Pillow
- Chromium





## 🎯 适用网站

**本下载器仅适用于漫画柜（看漫画）网站：**

- 🌐 官方网站：https://www.manhuagui.com/
- ⚙️ 其他网站可能需要修改选择器等参数，暂不支持



### 📚 配合 Komga 使用

本工具下载的漫画文件结构和 PDF 格式非常适合与 **[Komga](https://komga.org/)** 漫画管理系统配合使用：

**推荐工作流程：**

```
📥 使用本工具下载漫画 
    ↓
📄 自动转换为 PDF 
    ↓
📚 Komga 自动扫描并添加到库 
    ↓
📖 在 Komga 中舒适阅读
```

**配置步骤：**

1. **共享下载目录**

```yaml
# docker-compose.yml
volumes:
  - /home/peter/Dockers/komga/data:/app/downloads
```

1. **在 Komga 中添加库**

将 `/home/peter/Dockers/komga/data` 添加为 Komga 的漫画库路径

1. **自动同步**

- 启用本工具的"自动转换 PDF"选项
- Komga 会自动识别新下载的漫画
- 每个章节都会生成独立的 PDF，便于管理和阅读





## ⚠️ 重要声明

**本项目仅供个人学习交流使用，严禁用于商业用途或其他非法用途。**

- ⚖️ 请遵守相关网站的使用条款和版权规定
- 📖 下载的内容仅供个人学习研究使用
- 🚫 **严禁**将下载内容用于商业用途、二次传播或其他侵权行为
- ✋ 请尊重原作者和出版社的版权，**支持正版**
- 🗑️ 建议在阅读后 24 小时内删除下载的内容

**使用本工具造成的任何法律问题，由使用者自行承担，与本项目作者无关。**

💰 如果你喜欢某部漫画作品，请通过正规渠道购买正版支持作者和出版社！

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📜 许可证

MIT License

## 🔗 相关链接

- [DrissionPage 文档](https://drissionpage.cn/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Komga 官网](https://komga.org/)
- [漫画柜](https://www.manhuagui.com/)

## 📧 联系方式

如有问题或建议，请提交 Issue。

------

⭐ 如果这个项目对你有帮助，请给个 Star！

**🔴 再次提醒：本工具仅供学习交流，请勿用于商业或其他非法用途！请支持正版！**

