# 月度之星制作助手

这是一个基于 Electron + Python 的桌面工具，用来批量生成“月度之星”人物海报。新版界面参考现代 Web Dashboard 视觉结构，保留原有抠图与合成流程，同时把桌面体验升级为更直观的三栏工作台。

## 功能亮点
- Electron 桌面 UI：更现代的仪表盘式布局，集中展示目录、状态与日志
- 复用稳定后端：继续使用原有 Python 海报生成逻辑、抠图模型与模板合成流程
- 自动初始化环境：首次启动自动创建输入图片、输出海报和使用说明目录
- 一键生成：从桌面界面直接启动批处理并实时查看日志
- Windows 安装包：通过 GitHub Actions 的 Windows Runner 自动构建并发布 Release

## 文件命名规则
输入图片请使用以下格式命名：

`部门-姓名-YYYYMM.jpg`

例如：

`制造部-张三-202603.jpg`

## 本地开发
### 1. 安装 Python 依赖
```powershell
python -m pip install -r requirements.txt
```

### 2. 安装 Node / Electron 依赖
```powershell
npm.cmd install
```

### 3. 启动桌面应用
```powershell
npm run dev
```

应用默认会在“文档/月度之星制作助手”下创建运行目录。

## 打包 Windows 安装包
```powershell
npm run dist
```

构建流程会先：
- 用 PyInstaller 生成后端 `poster-backend.exe`
- 再用 `electron-builder` 生成 Windows NSIS 安装包

输出目录：
- `release/`：Electron 安装包
- `build/backend/`：打包后的 Python 后端

## GitHub Release 自动发布
仓库内置了 GitHub Actions 工作流：
- 当推送 tag（如 `v1.0`）时
- 自动在 Windows Runner 上构建安装包
- 自动创建或更新 GitHub Release，并上传安装包附件

## 运行说明
应用启动后会自动提供：
- 输入图片目录
- 输出海报目录
- 内置模板文件
- 使用说明文件

你只需要把照片放到输入目录，然后在桌面界面点击“开始生成”即可。
