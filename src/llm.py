"""
LLM 模块 - 支持 OpenRouter 和 Ollama API 进行文本润色
"""
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class LLMProcessor:
    """LLM 文本处理器 - 支持多种后端"""
    
    def __init__(self, provider: str = "openrouter", api_key: Optional[str] = None,
                 model: str = "anthropic/claude-3.5-sonnet",
                 ollama_base_url: str = "http://localhost:11434",
                 system_prompt: Optional[str] = None, max_tokens: int = 1000,
                 temperature: float = 0.3, timeout: int = 30):
        """
        初始化 LLM 处理器
        
        Args:
            provider: 后端提供商 ("openrouter" 或 "ollama")
            api_key: OpenRouter API 密钥（provider=openrouter 时需要）
            model: 模型名称
            ollama_base_url: Ollama API 地址
            system_prompt: 系统提示词
            max_tokens: 最大 token 数
            temperature: 温度参数
            timeout: 请求超时时间（秒）
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.ollama_base_url = ollama_base_url.rstrip('/')
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        
        self.system_prompt = system_prompt or """你是一个专业的语音文本润色助手。用户会给你语音识别后的原始文本，你需要：
1. 去除语气词（嗯、啊、那个、就是等）
2. 去除重复和口吃片段
3. 修正改口（保留最终想表达的内容）
4. 适当添加标点符号
5. 保持原意，使文本更清晰可读

直接输出润色后的文本，不要添加任何解释或前缀。"""
        
        # 设置 API URL
        if self.provider == "openrouter":
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            if not self.api_key:
                logger.warning("OpenRouter provider 需要 API Key")
        elif self.provider == "ollama":
            self.api_url = f"{self.ollama_base_url}/api/chat"
        else:
            raise ValueError(f"不支持的 provider: {provider}")
        
        logger.info(f"初始化 LLM 处理器: provider={provider}, model={model}")
    
    def polish(self, raw_text: str) -> dict:
        """
        润色文本
        
        Args:
            raw_text: 原始识别文本
            
        Returns:
            包含润色结果的字典 {polished_text, original_text, model, usage}
        """
        if not raw_text or not raw_text.strip():
            logger.warning("输入文本为空，跳过润色")
            return {
                "polished_text": "",
                "original_text": raw_text,
                "model": self.model,
                "usage": {}
            }
        
        try:
            logger.info(f"开始润色文本（长度: {len(raw_text)}）")
            logger.debug(f"原始文本: {raw_text}")
            
            if self.provider == "openrouter":
                result = self._polish_openrouter(raw_text)
            elif self.provider == "ollama":
                result = self._polish_ollama(raw_text)
            else:
                raise ValueError(f"不支持的 provider: {self.provider}")
            
            logger.info(f"润色完成: {result['polished_text']}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"请求超时（{self.timeout}秒）")
            return {
                "polished_text": raw_text,
                "original_text": raw_text,
                "error": "timeout"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求失败: {e}")
            return {
                "polished_text": raw_text,
                "original_text": raw_text,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"润色失败: {e}")
            return {
                "polished_text": raw_text,
                "original_text": raw_text,
                "error": str(e)
            }
    
    def _polish_openrouter(self, raw_text: str) -> dict:
        """使用 OpenRouter API 润色"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/typeless-mac",
            "X-Title": "Typeless Mac"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": raw_text}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        data = response.json()
        
        polished_text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        
        return {
            "polished_text": polished_text,
            "original_text": raw_text,
            "model": self.model,
            "provider": "openrouter",
            "usage": usage
        }
    
    def _polish_ollama(self, raw_text: str) -> dict:
        """使用 Ollama API 润色"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": raw_text}
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        response = requests.post(
            self.api_url,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        data = response.json()
        
        polished_text = data["message"]["content"].strip()
        
        return {
            "polished_text": polished_text,
            "original_text": raw_text,
            "model": self.model,
            "provider": "ollama",
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            }
        }
    
    def test_connection(self) -> bool:
        """测试 API 连接"""
        try:
            result = self.polish("测试")
            return "error" not in result
        except:
            return False


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # 测试 OpenRouter
    print("=" * 60)
    print("测试 OpenRouter")
    print("=" * 60)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key and api_key != "sk-or-v1-your-api-key-here":
        llm = LLMProcessor(
            provider="openrouter",
            api_key=api_key,
            model=os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        )
        
        test_text = "嗯，那个，我今天，就是，我今天想要，不对，我想说的是我明天想要去，去公园散步"
        result = llm.polish(test_text)
        
        print(f"原文: {result['original_text']}")
        print(f"润色: {result['polished_text']}")
        print(f"模型: {result.get('model')}")
        print(f"用量: {result.get('usage')}")
    else:
        print("⚠️  未设置 OPENROUTER_API_KEY")
    
    print()
    
    # 测试 Ollama
    print("=" * 60)
    print("测试 Ollama")
    print("=" * 60)
    
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        llm_ollama = LLMProcessor(
            provider="ollama",
            model=ollama_model,
            ollama_base_url=ollama_url
        )
        
        test_text = "嗯，那个，我今天，就是，我今天想要，不对，我想说的是我明天想要去，去公园散步"
        result = llm_ollama.polish(test_text)
        
        print(f"原文: {result['original_text']}")
        print(f"润色: {result['polished_text']}")
        print(f"模型: {result.get('model')}")
        print(f"用量: {result.get('usage')}")
        
    except Exception as e:
        print(f"⚠️  Ollama 测试失败: {e}")
        print(f"   请确保 Ollama 已安装并运行在 {ollama_url}")
        print(f"   安装: https://ollama.ai")
        print(f"   启动: ollama serve")
        print(f"   拉取模型: ollama pull {ollama_model}")
