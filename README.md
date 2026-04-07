# 月度之星海报生成器

一个用于批量生成“月度之星”个人海报的 Windows GUI 工具。

## 功能
- 双击启动 GUI，不弹命令行黑框
- 自动抠图并合成海报
- 默认使用程序同目录下的“输入图片”和“输出海报”文件夹
- 支持自定义输入目录、输出目录、模板图片和字体文件
- 支持 GitHub Actions 在 Windows Runner 上自动构建 EXE 和安装包，并发布 Release

## 文件名规则
输入图片文件名必须为：`部门-姓名-YYYYMM`

例如：`制造部-张三-202603.jpg`

## 本地运行
```powershell
python -m pip install -r requirements.txt
python gui_launcher.py
```

## 本地打包 EXE
```powershell
python build_windows_exe.py
```

打包完成后会在 `dist/` 中生成：
- `月度之星海报生成器.exe`
- `输入图片/`
- `输出海报/`
- `使用说明.txt`

## GitHub Actions 发布
推送标签 `v*` 后，工作流会在 Windows Runner 上：
- 安装 Python 依赖
- 下载 `u2net.onnx` 模型
- 构建 GUI EXE
- 用 Inno Setup 生成安装包
- 创建 GitHub Release
- 上传 EXE 和安装包产物

Release 产物包括：
- 便携版目录中的 `月度之星海报生成器.exe`
- 安装包 `月度之星海报生成器-Setup-vX.Y.Z.exe`
