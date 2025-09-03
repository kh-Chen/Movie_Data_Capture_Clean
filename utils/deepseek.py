import logger
import requests
import json
import datetime
from .event import register_event

G_APIURL = "https://api.deepseek.com/chat/completions"

G_PROMPT = {
    "prompt_genterer": '''
你是一位大模型提示词生成专家，请根据用户的需求编写一个智能助手的提示词，来指导大模型进行内容生成，要求：
1. 以 Markdown 格式输出
2. 贴合用户需求，描述智能助手的定位、能力、知识储备
3. 提示词应清晰、精确、易于理解，在保持质量的同时，尽可能简洁
4. 只输出提示词，不要输出多余解释
'''
}

exit_now = False
def SIGINT_callback():
    global exit_now
    exit_now = True
    logger.info(f"SIGINT_callback: exit_now={exit_now}")

class client():
    # key=''
    # model=''
    # prompt=''
    # stream=False
    # messages=[]

    # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
    # type 1=对话模式  2=机器调用
    def __init__(self, key:str, model:str, prompt:str, type:int):
        self.key = key
        self.model = model
        self.prompt = prompt
        self.messages=[]
        self.messages.append({"role": "system", "content": self.prompt})
        self.stream = (type == 1)
        register_event("SIGINT", callback=SIGINT_callback)

    def append_user(self,msg:str):
        self.messages.append({"role": "user", "content": msg})

    def append_assistant(self,msg:str):
        self.messages.append({"role": "assistant", "content": msg})

    def get_header(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key}"
        }
    
    def get_data(self,usermsg:str):
        self.append_user(usermsg)
        return {
            "model": self.model, 
            "messages": self.messages,
            "stream": self.stream 
        }

    def talk(self,response):
        flag = False
        reasoning_content = ""
        content = ""
        for chunk in response.iter_lines():
            if exit_now:
                response.close()
                break
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data: "):
                    jsonstr = decoded_chunk[6:]
                    if jsonstr == "[DONE]":
                        print("\n--[DONE]--")
                        break
                    
                    res = json.loads(decoded_chunk[6:])
                    obj = res["choices"][0]["delta"]
                    _reasoning = obj["reasoning_content"]
                    _content = obj["content"]
                    if _reasoning is None and _content is not None and not flag:
                        print("\n =======================Think end======================================")
                        flag = True
                    if _reasoning is not None:
                        reasoning_content += _reasoning
                        print(_reasoning, end="")
                    elif _content is not None:
                        content += _content
                        print(_content, end="")
                    else:
                        print("error data: ",decoded_chunk)

                else:
                    print("error data: ",decoded_chunk)
        self.messages.append({"role": "assistant", "content": content})



    def call(self, text: str):
        data = self.get_data(text)
        response = requests.post(G_APIURL, headers=self.get_header(), json=data, stream=self.stream)

        if self.stream:
            self.talk(response)
        else:
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']
                return message['content'], message["reasoning_content"] if "reasoning_content" in message else None
            else:
                logger.error(f"DeepSeek API Request Failed: {response.text} Status Code: {response.status_code}")
                return None,None

    def save(self):
        current_time = datetime.datetime.now()
        # 格式化为：年月日_时分秒
        file_path = 'z_ai/'+current_time.strftime("%Y%m%d_%H%M%S") + ".txt"

        with open(file_path, 'w', encoding='utf-8') as file:
            for msg in self.messages:
                file.write(f'\n----------{msg["role"]}: \n{msg["content"]}')
        
            

