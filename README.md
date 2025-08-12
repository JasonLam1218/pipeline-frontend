
# 项目README.md文档

## 1. 项目简介

本项目是一个基于Django框架和Azure Blob Storage的服务，允许用户上传、列出、下载和生成Azure Blob存储中的文件。项目部署在Vercel平台上，利用Vercel的Serverless架构和Python运行时来提供服务。

## 2. 技术栈

- **后端**：Django 4.1.3
- **数据库**：无数据库（使用Django的会话存储）
- **静态文件服务**：Whitenoise
- **云服务**：Azure Blob Storage, Azure Queue Storage
- **部署平台**：Vercel
- **前端**：HTML, CSS, JavaScript, jQuery, jsTree

## 3. 项目结构

```
api/
│
├── settings.py
├── urls.py
├── wsgi.py
│
example/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── upload.js
│   │   │   ├── list.js
│   │   │   ├── process.js
│   │   └── images/
│   ├── templates/
│   │   ├── example/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   └── list.html
│   ├── views.py
│   ├── urls.py
│   └── blob_views.py
│
├── requirements.txt
└── vercel.json
```

## 4. 安装与部署

### 4.1 安装依赖

在项目根目录下运行以下命令来安装所需的Python包：

```bash
pip install -r requirements.txt
```

### 4.2 配置环境变量

确保在Vercel环境变量中设置以下值：

- `AZURE_STORAGE_CONNECTION_STRING`：Azure Blob Storage的连接字符串。
- `DJANGO_DEBUG`：设置为 `True`或 `False`以启用或禁用Django的调试模式。

### 4.3 部署到Vercel

将项目推送到Git仓库（如GitHub），然后在Vercel上导入该仓库并按照提示进行部署。

## 5. 功能介绍

### 5.1 文件上传

用户可以通过拖放或选择文件上传到Azure Blob Storage。上传过程中会显示进度条。

### 5.2 文件列表

用户可以查看Azure Blob Storage中的文件列表，并支持多选下载和生成操作。

### 5.3 文件下载

用户可以选择一个或多个文件进行下载。如果选择多个文件，它们将被压缩成一个ZIP文件下载。

### 5.4 文件生成

用户可以选择一个或多个文件进行生成操作（具体生成逻辑需根据业务需求实现）。生成过程会显示全局进度条，并支持取消操作。

## 6. 使用说明

### 6.1 上传文件

访问根URL（如 `https://your-project-name.vercel.app/`），将文件拖放到上传区域或点击选择文件，然后点击“Upload”按钮进行上传。

### 6.2 查看文件列表

点击“Go to Blob List”按钮进入文件列表页面，在这里可以查看所有上传的文件，并进行多选下载或生成操作。

### 6.3 下载文件

在文件列表页面，选择一个或多个文件，然后点击“Download”按钮进行下载。如果选择多个文件，它们将被压缩成一个ZIP文件下载。

### 6.4 生成文件

在文件列表页面，选择一个或多个文件，然后点击“Generate”按钮进行生成操作。生成过程中会显示全局进度条，并支持取消操作。

## 7. 贡献指南

欢迎对本项目进行贡献！请在提交PR之前先创建Issue进行讨论。

## 8. 许可证

本项目采用MIT许可证。请查阅 `LICENSE`文件以获取更多信息。
# pipeline_frontend
