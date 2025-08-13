import logger
import requests
import json

G_APIURL = "https://api.deepseek.com/chat/completions"

def call(api:str, model: str, prompt:str, text: str, stream:bool):

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api}"
    }

    data = {
        "model": model, # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
        "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
        ],
        "stream": stream 
    }

    response = requests.post(G_APIURL, headers=header, json=data, stream=stream)

    
    if stream:
        flag = False
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data: "):
                    jsonstr = decoded_chunk[6:]
                    if jsonstr == "[DONE]":
                        print("\n[DONE]")
                        break
                    
                    res = json.loads(decoded_chunk[6:])
                    obj = res["choices"][0]["delta"]
                    reasoning = obj["reasoning_content"]
                    content = obj["content"]
                    if reasoning is None and content is not None and not flag:
                        print("\n ----------------------------------")
                        flag = True
                    if reasoning is None and content is None:
                        print(decoded_chunk)
                    else:
                        pstr = obj["reasoning_content"] if obj["content"] is None else obj["content"] 
                        print(pstr, end="")
                else:
                    print("error data: ",decoded_chunk)
        return None,None     
    else:
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']
            return message['content'], message["reasoning_content"] if "reasoning_content" in message else None
        else:
            logger.error(f"DeepSeek API Request Failed: {response.text} Status Code: {response.status_code}")
            return None,None
    
