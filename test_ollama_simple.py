#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from llm import LLMProcessor

print("测试 Ollama...")
llm = LLMProcessor(provider="ollama", model="qwen2.5:3b", ollama_base_url="http://localhost:11434")
result = llm.polish("嗯，那个，我今天要去公司")
print(f"原文: 嗯，那个，我今天要去公司")
print(f"润色: {result[\"polished_text\"]}")
print("✅ 测试成功！")
