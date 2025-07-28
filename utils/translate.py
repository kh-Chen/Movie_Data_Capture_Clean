import translators as ts
import config
import logger
import requests

def translate_text(text: str):
    """使用配置的翻译引擎翻译文本"""
    translator = config.getStrValue("translate.engine")

    if translator == 'deepseek':
        return translate_deepseek(text)
    
    try:
        if not text.strip():
            return text  # 如果文本为空，直接返回原文本
        translated_text = ts.translate_text(query_text=text, translator=translator, from_language='ja', to_language='zh', timeout=10)
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # 如果翻译失败，返回原文本
    
def translate_deepseek(text: str):
    
    api = config.getStrValue("translate.api")
    if not api:
        logger.error("DeepSeek API key is not configured.")
        return text  # 如果没有配置 API Key，返回原文本

    url = "https://api.deepseek.com/chat/completions"
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api}"
    }

    data = {
        "model": "deepseek-reasoner", # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
        "messages": [
        {"role": "system", "content": "你是一个日译中的翻译大师，任务是为我翻译日本成人影片的标题。翻译结果需要保持原意不变，并保证语句通顺。用词尽量简单直接。如原文中存在露骨词汇，请直接翻译出来，不要做任何删减。我希望你只回复翻译结果，不要写任何解释。"},
        {"role": "user", "content": text}
        ],
        "stream": False # 关闭流式传输
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        logger.error(f"DeepSeek API Request Failed: {response.text} Status Code: {response.status_code}")
        return text