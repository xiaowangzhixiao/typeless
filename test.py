"""
测试脚本 - 验证各个组件是否正常工作
"""
import os
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("  Typeless Mac 组件测试")
print("=" * 60)
print()

# 1. 测试依赖
print("1️⃣  测试 Python 依赖...")
dependencies = [
    "faster_whisper",
    "openai",
    "dotenv",
    "yaml",
    "sounddevice",
    "numpy",
    "pynput",
    "pyperclip",
    "requests"
]

missing_deps = []
for dep in dependencies:
    try:
        __import__(dep if dep != "dotenv" else "dotenv")
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - 未安装")
        missing_deps.append(dep)

if missing_deps:
    print()
    print("⚠️  缺少依赖，请运行: pip3 install -r requirements.txt")
    sys.exit(1)

print()

# 2. 测试配置文件
print("2️⃣  测试配置文件...")
config_files = ["config.yaml", ".env"]
for config_file in config_files:
    if os.path.exists(config_file):
        print(f"   ✅ {config_file}")
    else:
        print(f"   ⚠️  {config_file} - 不存在")
        if config_file == ".env":
            print("      请复制 .env.example 到 .env 并填入 API Key")

print()

# 3. 测试环境变量
print("3️⃣  测试环境变量...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if api_key and api_key != "sk-or-v1-your-api-key-here":
    print(f"   ✅ OPENROUTER_API_KEY (前10位: {api_key[:10]}...)")
else:
    print("   ❌ OPENROUTER_API_KEY - 未设置或使用示例值")
    print("      请在 .env 文件中设置你的 API Key")

print()

# 4. 测试 ASR 模块
print("4️⃣  测试 ASR 模块...")
try:
    from asr import ASREngine
    asr = ASREngine(model_size="tiny", language="zh")
    print("   ✅ ASR 模块加载成功")
    
    print("   ⏳ 正在下载/加载 Whisper 模型（首次运行会较慢）...")
    asr.load_model()
    print("   ✅ Whisper 模型加载成功")
except Exception as e:
    print(f"   ❌ ASR 模块失败: {e}")

print()

# 5. 测试 LLM 模块
print("5️⃣  测试 LLM 模块...")
try:
    from llm import LLMProcessor
    
    if api_key and api_key != "sk-or-v1-your-api-key-here":
        llm = LLMProcessor(api_key=api_key, model="anthropic/claude-3.5-sonnet")
        print("   ✅ LLM 模块加载成功")
        
        # 测试连接
        print("   ⏳ 测试 API 连接...")
        if llm.test_connection():
            print("   ✅ API 连接正常")
        else:
            print("   ⚠️  API 连接失败，请检查 API Key 和网络")
    else:
        print("   ⚠️  跳过（未设置 API Key）")
except Exception as e:
    print(f"   ❌ LLM 模块失败: {e}")

print()

# 6. 测试音频设备
print("6️⃣  测试音频设备...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    if input_devices:
        print(f"   ✅ 找到 {len(input_devices)} 个输入设备")
        default_input = sd.query_devices(kind='input')
        print(f"   📍 默认输入: {default_input['name']}")
    else:
        print("   ❌ 未找到音频输入设备")
except Exception as e:
    print(f"   ❌ 音频设备测试失败: {e}")

print()

# 7. 测试其他模块
print("7️⃣  测试其他模块...")
modules = [
    ("audio_recorder", "AudioRecorder"),
    ("input_handler", "InputHandler"),
    ("hotkey", "HotkeyListener"),
    ("ui", "StatusWindow")
]

for module_name, class_name in modules:
    try:
        module = __import__(module_name)
        getattr(module, class_name)
        print(f"   ✅ {module_name}.{class_name}")
    except Exception as e:
        print(f"   ❌ {module_name}.{class_name}: {e}")

print()
print("=" * 60)
print("  测试完成！")
print("=" * 60)
print()
print("如果所有测试通过，可以运行: python3 main.py")
print()
