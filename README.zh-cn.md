# Claude Desktop Buddy — M5 StickS3 增强版

> 本文档介绍 `m5stick-s3` 分支在官方仓库基础上新增的全部功能。
> 原项目说明请参阅 [README.md](README.md)。

---

## 适用硬件

| 型号 | 支持 | PlatformIO env |
|---|---|---|
| M5 StickS3 （ESP32-S3, 8MB Flash, 8MB PSRAM）| ✅ 主要开发板 | `m5sticks3` |
| M5 StickC Plus （ESP32, 4MB Flash）| ✅ 双板兼容 | `m5stickc-plus` |

---

## 快速开始

```bash
git clone https://github.com/yummysource/claude-desktop-buddy.git
cd claude-desktop-buddy
git checkout m5stick-s3
```

烧录固件（StickS3 需要手动进 bootloader：按住 B 键 → 短按电源键 → 松开 B）：

```bash
pio run -e m5sticks3 -t upload
```

烧录 GIF 角色包（同样需要进 bootloader）：

```bash
python3 tools/flash_character.py characters/bufo
python3 tools/flash_character.py characters/capy
python3 tools/flash_character.py characters/claude
```

---

## 相对官方版本新增的功能

### 1. M5 StickS3 移植

官方固件依赖 `m5stack/M5StickCPlus` 库，不支持 ESP32-S3 架构。本分支换用
`m5stack/M5Unified`，它会在运行时自动识别设备并适配 PY32 PMIC、BMI270 IMU、
ES8311 音频编解码器等 StickS3 特有硬件。

主要 API 映射：

| 旧接口 | 新接口 |
|---|---|
| `M5.Axp.*` | `M5.Power.*` / `M5.Display.*` |
| `M5.Beep.*` | `M5.Speaker.*` |
| `M5.Imu.Init()` | `M5.begin()` 自动初始化 |
| `RTC_TimeTypeDef` | `m5::rtc_time_t` |
| `TFT_eSprite` | `M5Canvas` |
| `TFT_eSPI*` | `LovyanGFX*` |

StickS3 没有物理红色 LED，等待审批时改为屏幕四周**红色边框闪烁**（2 Hz），
可以在设置菜单 `led` 条目关闭。

### 2. 中文及 CJK 字符显示

Claude 桌面端发来的中文消息、审批工具名、提示文字现在能正确显示。
采用内置的 `efontCN_14` 点阵字体，同时兼容日文假名和常用繁体汉字。

只在 StickS3 上启用（StickC Plus Flash 空间不足），由编译宏 `BUDDY_BOARD_S3` 控制。

### 3. 消息列表改为顺序翻页

原版新消息到来后滚动到最底部，按 B 向上翻——读起来像"倒着看书"。
改为：**新消息先定位到最顶部**，按 B 向下翻页（每页 4 行），
最终到达最新消息后再按一次跳回顶部。

### 4. 消息显示区扩展到 4 行

StickS3 屏幕高度足够，从 3 行扩展到 4 行显示，避免频繁翻页。
使用 `efontCN_14` 字体（14px），行高 15px，共 64px 高度，
与 ASCII 宠物清屏区之间保留 13px 安全间距。

### 5. 审批提示音可选

收到权限审批提示时，除屏幕红边框之外还播放声音。
在设置菜单（长按 A → settings → alert）中可以循环试听并选择：

| 选项 | 描述 |
|---|---|
| `chirp` | 短促单音（默认） |
| `rise` | 三音上行 |
| `alarm` | 高-低-高警示 |
| `fall` | 三音下行 |
| `ding` | 单声响铃 |

按 B 切换时立即预览当前选项。

### 6. 多 GIF 角色包支持

原版只能装一个 GIF 角色包，装新的会删掉旧的。本版本支持在 LittleFS 上**同时安装多个**，
在设置菜单 `ascii pet` 条目中循环切换，和 18 种 ASCII 宠物无缝衔接。

菜单计数示例（装了三个 GIF 包时）：
```
cat (1/21) → ... → capybara (18/21) → bufo (19/21) → capy (20/21) → claude (21/21) → cat (1/21) → ...
```

选择会持久化到 NVS，重启后自动恢复。

`tools/flash_character.py` 同步更新：
- 不再清空整个 `data/characters/` 目录，只替换同名角色包
- 默认针对 StickS3 env（`--env` 参数可指定其他板子）

### 7. 自带三款 GIF 角色包

| 角色 | 说明 | 目录 |
|---|---|---|
| bufo | 社区 bufo 青蛙表情包（来自 bufo.zone） | `characters/bufo/` |
| capy | AI 生成的卡皮巴拉，珊瑚色围巾 | `characters/capy/` |
| claude | 像素风 Claude 官方吉祥物风格，多帧 AI 生成 | `characters/claude/` |

三款均为 7 状态（sleep / idle / busy / attention / celebrate / dizzy / heart），
96px 宽，总大小约 800 KB，远低于 LittleFS 1.8 MB 上限。

### 8. GIF 多帧循环修复

官方版本中，单文件多帧 GIF 播放完一轮后会冻结在最后一帧（原为优化单帧静态 GIF 而设计）。
本版本通过追踪已播放帧数，区分真静态 GIF（冻结）和多帧动画 GIF（循环），
使 capy / claude 等自定义角色包能持续循环播放。

---

## 烧录手册

详细的分步操作流程（含常见故障排查）参见：
[docs/flashing-m5stickx.md](docs/flashing-m5stickx.md)

---

## 已知限制

- **StickS3 没有外置 RTC 芯片**：时钟显示功能（充电时的表盘）需要 Claude 桌面端
  先发送时间同步包，断电后时间不保留。
- **USB Serial 命令通道**：StickS3 的 USB-OTG CDC 有幻读问题，已禁用从 USB 接收
  JSON 命令的通道；BLE 是主要通信方式，不受影响。
- **CJK 字体仅 StickS3**：StickC Plus 的 2 MB app 分区装不下 `efontCN_14`（约 +264 KB），
  中文在该板上仍显示为方块。
- **欧洲重音字符**（é ü ñ 等）及韩文：当前字体不覆盖，需要额外集成对应字库。

---

## 分支说明

```
upstream/main            ← 官方仓库
  └─ main (本地镜像)
      └─ m5stick-s3     ← 本分支，所有增强在此
```

Fork 地址：https://github.com/yummysource/claude-desktop-buddy

---

## 许可证

代码部分遵循 [MIT License](LICENSE)。

`characters/bufo/` 中的 GIF 来自社区 bufo 表情包（https://bufo.zone），
版权归原作者所有，不在 MIT 覆盖范围内。

`characters/capy/` 和 `characters/claude/` 为 AI 生成内容，供个人使用。
