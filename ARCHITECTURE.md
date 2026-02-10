# Typeless Mac - 项目架构文档

## 📋 项目概述

Typeless Mac 是一个 AI 驱动的语音输入法，通过本地 ASR（自动语音识别）和云端 LLM（大语言模型）实现智能语音转文字功能。

### 核心特性
- ✅ 本地 ASR（Whisper tiny 模型 ~75MB）
- ✅ 智能文本润色（去语气词、改口修正、格式化）
- ✅ 全局快捷键触发（Cmd+Shift+Space）
- ✅ 自动粘贴到光标位置
- ✅ 支持多模型切换（OpenRouter）
- ✅ 静音自动检测
- ✅ 隐私保护（语音本地处理）

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Typeless Mac                         │
│                     (main.py)                           │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐   ┌───▼───┐   ┌──▼──┐
    │ Input │   │  UI   │   │ Hot │
    │Handler│   │Window │   │ key │
    └───────┘   └───────┘   └──┬──┘
                               │ 触发
                    ┌──────────▼──────────┐
                    │   Recording Loop    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Audio Recorder    │
                    │  (SmartRecorder)    │
                    └──────────┬──────────┘
                               │ 音频数据
                    ┌──────────▼──────────┐
                    │    ASR Engine       │
                    │  (faster-whisper)   │
                    └──────────┬──────────┘
                               │ 原始文本
                    ┌──────────▼──────────┐
                    │   LLM Processor     │
                    │   (OpenRouter)      │
                    └──────────┬──────────┘
                               │ 润色文本
                    ┌──────────▼──────────┐
                    │   Input Handler     │
                    │    (Auto Paste)     │
                    └─────────────────────┘
```

## 📁 项目结构

```
typeless-mac/
├── main.py                  # 主程序入口，应用核心逻辑
├── config.yaml              # 配置文件（模型、参数等）
├── .env                     # 环境变量（API Key）
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明
├── QUICKSTART.md            # 快速开始指南
├── install.sh               # 安装脚本
├── test.py                  # 测试脚本
│
└── src/                     # 源代码目录
    ├── __init__.py          # 包初始化
    ├── asr.py               # ASR 引擎（语音识别）
    ├── llm.py               # LLM 处理器（文本润色）
    ├── audio_recorder.py    # 音频录制（含智能静音检测）
    ├── input_handler.py     # 输入处理（自动粘贴）
    ├── hotkey.py            # 快捷键监听
    └── ui.py                # 状态窗口
```

## 🔧 核心模块详解

### 1. ASR Engine (`src/asr.py`)

**职责**: 将音频转换为文本

**技术栈**: faster-whisper (Whisper.cpp 的 Python 封装)

**关键特性**:
- 支持多种模型大小 (tiny/base/small/medium/large)
- VAD (Voice Activity Detection) 自动过滤静音
- 支持多语言识别
- 本地运行，无需网络

**流程**:
```python
audio_data → ASREngine.transcribe_numpy() → {text, language, segments}
```

**模型选择**:
| 模型 | 大小 | 速度 | 准确率 | 适用场景 |
|------|------|------|--------|----------|
| tiny | 75MB | 最快 | ~85% | 实时输入 |
| base | 142MB | 快 | ~90% | 平衡选择 |
| small | 466MB | 中 | ~95% | 高准确度 |

### 2. LLM Processor (`src/llm.py`)

**职责**: 润色和优化识别文本

**技术栈**: OpenRouter API (支持多模型)

**核心功能**:
- 去除语气词（嗯、啊、那个、就是）
- 去除重复片段
- 改口自动修正
- 添加标点符号
- 格式化输出

**提示词策略**:
```python
system_prompt = """
你是一个专业的语音文本润色助手。
1. 去除语气词
2. 去除重复和口吃片段
3. 修正改口（保留最终想表达的内容）
4. 适当添加标点符号
5. 保持原意，使文本更清晰可读
直接输出润色后的文本。
"""
```

**模型推荐**:
- **Claude 3.5 Sonnet**: 质量最高，理解力强
- **GPT-4o-mini**: 快速便宜，适合大量使用
- **Gemini 2.0 Flash**: 免费试用（有限额）

### 3. Audio Recorder (`src/audio_recorder.py`)

**职责**: 录制和管理音频数据

**类层次**:
- `AudioRecorder`: 基础录音功能
- `SmartRecorder`: 智能静音检测（继承自 AudioRecorder）

**智能静音检测**:
```python
# 计算音频 RMS（音量）
rms = sqrt(mean(audio_chunk^2))

# 判断静音
if rms < silence_threshold:
    silence_frames += 1
else:
    silence_frames = 0

# 达到阈值则停止
if silence_frames >= silence_duration * sample_rate:
    stop_recording()
```

**参数配置**:
- `sample_rate`: 16000 Hz (Whisper 标准)
- `channels`: 1 (单声道)
- `silence_threshold`: 500 (音量阈值)
- `silence_duration`: 2.0 秒
- `max_duration`: 60 秒

### 4. Input Handler (`src/input_handler.py`)

**职责**: 将文本输入到当前应用

**实现方式**:
1. 保存当前剪贴板内容
2. 将文本复制到剪贴板
3. 模拟 Cmd+V 粘贴
4. 恢复原剪贴板内容

**技术栈**:
- `pyperclip`: 剪贴板操作
- `pynput`: 键盘模拟

**权限要求**: macOS 辅助功能权限

### 5. Hotkey Listener (`src/hotkey.py`)

**职责**: 监听全局快捷键

**技术栈**: pynput.keyboard.GlobalHotKeys

**默认快捷键**: `Cmd+Shift+Space`

**工作原理**:
```python
hotkeys = {"<cmd>+<shift>+space": callback}
listener = GlobalHotKeys(hotkeys)
listener.start()
```

### 6. Status Window (`src/ui.py`)

**职责**: 显示录音和处理状态

**技术栈**: tkinter

**特性**:
- 无边框悬浮窗
- 半透明背景
- 置顶显示
- 右上角定位
- 自动隐藏

**状态消息**:
- 🎤 录音中...
- 🎯 识别中...
- 🤖 润色中...
- ⌨️ 输入中...
- ✅ 完成
- ❌ 出错了

## 🔄 工作流程

```
1. 用户按下 Cmd+Shift+Space
         ↓
2. HotkeyListener 触发回调
         ↓
3. 开始录音（SmartRecorder）
   - 显示 "🎤 录音中..."
         ↓
4. 检测到静音或再次按快捷键
         ↓
5. 停止录音，获取音频数据
         ↓
6. ASR 识别（faster-whisper）
   - 显示 "🎯 识别中..."
   - audio → raw_text
         ↓
7. LLM 润色（OpenRouter）
   - 显示 "🤖 润色中..."
   - raw_text → polished_text
         ↓
8. 自动输入（InputHandler）
   - 显示 "⌨️ 输入中..."
   - 粘贴到光标位置
         ↓
9. 完成
   - 显示 "✅ 完成"
   - 自动隐藏窗口
```

## ⚙️ 配置系统

### 配置文件层级

1. **config.yaml**: 应用配置
2. **.env**: 敏感信息（API Key）
3. **命令行参数** (TODO): 运行时覆盖

### 主要配置项

```yaml
# 应用设置
app:
  hotkey: "cmd+shift+space"

# ASR 设置
asr:
  model_size: "tiny"
  language: "zh"
  device: "cpu"
  compute_type: "int8"

# LLM 设置
llm:
  model: "anthropic/claude-3.5-sonnet"
  max_tokens: 1000
  temperature: 0.3

# 音频设置
audio:
  sample_rate: 16000
  silence_duration: 2.0
  max_duration: 60

# 功能开关
features:
  auto_paste: true
  offline_mode: false
```

## 🔒 隐私与安全

### 数据流

1. **音频数据**: 仅在本地设备处理（Whisper 模型）
2. **识别文本**: 发送到 OpenRouter API（可选，离线模式不发送）
3. **历史记录**: 默认不保存

### 隐私保护措施

- ✅ 语音识别在本地完成
- ✅ 不存储录音文件
- ✅ 不存储文本历史
- ✅ 可选离线模式（不使用 LLM）
- ✅ API 请求加密（HTTPS）

## 📊 性能指标

### 延迟分析

| 步骤 | 时间 (tiny 模型) | 时间 (base 模型) |
|------|------------------|------------------|
| 录音 | 实时 + 2s 静音检测 | 实时 + 2s 静音检测 |
| ASR | ~0.5-1s (3s 音频) | ~1-2s (3s 音频) |
| LLM | ~1-3s | ~1-3s |
| 输入 | ~0.2s | ~0.2s |
| **总计** | **~4-6s** | **~5-7s** |

### 资源占用

- **内存**: ~500MB (tiny 模型)
- **磁盘**: ~200MB (模型 + 依赖)
- **CPU**: 录音时 <5%, 识别时 30-50%

## 🚀 未来扩展

### 短期 (v0.2)
- [ ] 多语言混合识别
- [ ] 按应用自动切换润色风格
- [ ] 个人词典（专有名词）
- [ ] 历史记录（可选）
- [ ] 菜单栏图标

### 中期 (v0.3)
- [ ] 实时流式识别
- [ ] 自定义快捷键面板
- [ ] 模型下载管理器
- [ ] 使用统计

### 长期 (v1.0)
- [ ] iOS/Android 版本
- [ ] 自定义训练（个人语音适配）
- [ ] 多人说话识别
- [ ] 云端同步（可选）

## 🛠️ 开发指南

### 添加新功能

1. 在 `src/` 下创建新模块
2. 在 `main.py` 的 `TypelessApp` 中集成
3. 更新 `config.yaml` 添加配置
4. 更新 `test.py` 添加测试

### 调试技巧

```bash
# 查看详细日志
python3 main.py  # 日志会同时输出到终端和 typeless.log

# 测试单个模块
python3 src/asr.py
python3 src/llm.py
python3 src/audio_recorder.py

# 运行测试
python3 test.py
```

### 代码风格

- 遵循 PEP 8
- 函数和类添加 docstring
- 使用类型提示（Type Hints）
- 异常处理要详细记录日志

## 📝 依赖说明

| 包 | 版本 | 用途 |
|----|------|------|
| faster-whisper | 1.0.3 | 语音识别 |
| openai | 1.54.3 | OpenRouter API 客户端 |
| sounddevice | 0.4.6 | 音频录制 |
| numpy | 1.26.4 | 音频数据处理 |
| pynput | 1.7.7 | 快捷键和输入模拟 |
| pyperclip | 1.8.2 | 剪贴板操作 |
| python-dotenv | 1.0.0 | 环境变量 |
| PyYAML | 6.0.1 | 配置文件 |

## 🐛 已知问题

1. **macOS Ventura+**: 首次运行需要多次授予权限
2. **M1/M2 Mac**: faster-whisper 可能需要额外配置
3. **多显示器**: 状态窗口可能显示在主显示器

## 📞 联系与支持

- **文档**: `README.md`, `QUICKSTART.md`
- **测试**: `python3 test.py`
- **日志**: `typeless.log`
