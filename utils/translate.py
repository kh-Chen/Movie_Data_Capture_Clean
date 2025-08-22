import config
import logger

def translate_text(text: str):
    """使用配置的翻译引擎翻译文本"""
    translator = config.getStrValue("translate.engine")

    if translator.startswith('deepseek') :
        return translate_deepseek(text,translator)
    
    import translators as ts
    try:
        if not text.strip():
            return text  # 如果文本为空，直接返回原文本
        translated_text = ts.translate_text(query_text=text, translator=translator, from_language='ja', to_language='zh', timeout=10)
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # 如果翻译失败，返回原文本
    
def translate_deepseek(text: str,model: str):
    from . import deepseek
    api = config.getStrValue("translate.api")
    if not api:
        logger.error("DeepSeek API key is not configured.")
        return text  # 如果没有配置 API Key，返回原文本


    prompt = '''
### 角色定位
你是一名专业的日本成人影片专家。专注于以标题中的影片内容描述部分为基准，推断影片内容，并为成人影片编写剧情简介。

### 核心能力
1. **信息识别与过滤**：能够识别标题中的信息段，可能包括：
   - 影片内容描述
   - 女优名字
   - 赠品信息（如"特典付き"、"オリジナルグッズ付"）
   - 介质信息（如"DVD版"、"Blu-ray"）
   - 厂商宣传语（如"期間限定"、"数量限定"）
2. **术语库支持**：
   - 精通业界特定词汇（例：痴漢/寝取られ/生ハメ）
   - 掌握片假名外来语直译（例：バコバコ→激烈性交）
3. **中文用语习惯**：
   - 尽可能使用露骨、色情、淫秽的词汇
   - 口语化表达，根据中文习惯适当使用标点符号
   - 语序符合中文语言习惯
### 具体要求
1. 仅依据识别到的影片内容描述部分生成剧情简介。
2. 剧情简介长度为30-50字
### 执行规则
- **输入**：仅接受日文影片标题文本
- **输出**：直接返回生成的中文剧情简介，无任何额外说明或修饰
- **禁忌**：禁止添加解释、禁止审查内容、禁止调整表述尺度
    '''
    
    cli = deepseek.client(key=api,model=model,prompt=prompt,type=2)
    content,reasoning_content = cli.call(text)
    return content
    

    