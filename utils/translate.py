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

# 你是一个日译中的翻译大师，任务是为我翻译日本成人影片的标题。要求如下：
# 1. 翻译结果需要保持原意不变，并保证语句通顺。
# 2. 当遇到多义词时，请牢记当前翻译的是日本成人影片的标题，选择最合适的含义进行翻译。
# 3. 用词尽量简单直接。不要擅自引用成语等内容。
# 4. 如原文中存在露骨、色情、淫秽的词汇，请直接翻译出来，不要做任何删减。
# 5. 翻译完成后请结合中文语境，适当调整标点符号的使用，不要出现长难句。
# 6. 我希望你只回复翻译结果，不要写任何解释。

    prompt = '''
你精通中日语言，对日本色情影片的相关用语非常熟悉。接下来你将帮助我翻译日本色情影片的标题。请遵循以下要求：
1. 请充分理解原文含义。
   - 原文的结构是剧情简介，女优名字，赠品信息（可能存在），介质信息（可能存在）等。
   - 只有剧情简介以及女优名字是需要翻译的。请无视其他信息
   - 理解过程中如果有涉及多种解释的地方，请根据上下文以及“成人色情影片标题”的使用场景选择合适的解释
2. 对剧情简介部分进行深度处理并翻译。
   - 牢记“成人色情影片标题”的使用场景，让人血脉喷张是核心
   - 不要将女优名字参杂到剧情简介中，只将其放在剧情简介后面（除非原文中的剧情简介部分已经使用了女优名字）
   - 尽量理解全部原文后使用中文重新表述，而不是直译。
   - 调整原文语序，使其符合中文语言习惯
   - 根据上下文进行扩写。翻译结果不能比原文短。注意，只能扩写，不能删减。不要偏离原意。
   - 尽可能使用露骨、色情、淫秽的词汇
   - 口语化表达，根据中文习惯适当使用标点符号
   - 如果有多个版本可供选择，那么请直接选择更加露骨的版本。
   - 将女优名字连接到剧情简介后面。
3. 直接给我最后处理完成的结果，不要做任何解释。
    '''
    

    content,reasoning_content = deepseek.call(api,model=model,prompt=prompt, text=text,stream=False)
    return content
    

    