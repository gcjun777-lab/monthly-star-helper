# 订阅管理助手（桌面版）

基于你提供的 Excel（`订阅管理系统_终极版.xlsx`）实现，支持在 **macOS / Windows** 本地运行。

## 功能

- 订阅清单管理：新增、编辑、删除
- 订阅清单筛选：关键词、类别、状态、提醒级别
- 清单底部合计：筛选结果条数/月均合计/年成本合计/待取消可省
- 新增/编辑支持点击按钮选择下次续费日期（稳定日期选择窗口）
- 服务支持设置图标（图片文件）
- 类别字段支持下拉选择
- 自动计算：月均成本、年成本、取消后年省
- 仪表盘统计：总月订阅、总年订阅、待取消可省、活跃/待取消/低使用率数量
- 分类统计与高成本 TOP5
- 续费提醒：剩余天数、提醒级别（紧急/关注/正常/已过期）
- Excel 导入与导出
- 本地 JSON 持久化（离线可用）

## 项目结构

- `main.py`：主程序（Tkinter 桌面应用）
- `requirements.txt`：依赖
- `run_mac.command`：mac 一键启动
- `run_windows.bat`：Windows 一键启动
- `data/subscriptions.json`：本地数据文件（首次运行自动生成）

## 运行方式

### macOS

1. 打开终端，进入项目目录：
   ```bash
   cd /Users/guo/Downloads/订阅管理助手
   ```
2. 执行：
   ```bash
   ./run_mac.command
   ```

### Windows

1. 双击 `run_windows.bat`，或在 CMD 中执行：
   ```bat
   cd /d 项目目录
   run_windows.bat
   ```

## 首次数据来源

- 首次启动会优先尝试从：
  - `/Users/guo/Documents/订阅管理系统_终极版.xlsx`
  导入 `订阅清单` 工作表数据。
- 如果找不到该文件，程序会以空数据启动。
- 后续数据以 `data/subscriptions.json` 为准。

## 打包为可执行程序（可选）

### Windows 打包 EXE

```bat
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name 订阅管理助手 main.py
```

产物在 `dist/订阅管理助手.exe`。

### macOS 打包 APP

```bash
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --windowed --name 订阅管理助手 main.py
```

产物在 `dist/订阅管理助手.app`。

## 说明

- 软件名已设置为：`订阅管理助手`
- 计算规则与 Excel 保持一致：
  - 周期：`月 / 季 / 年 / 2年`
  - 续费提醒：`已过期 / 7天内续费 / 30天内续费 / 正常`
