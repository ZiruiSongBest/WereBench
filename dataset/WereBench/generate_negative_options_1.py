import json
import os
import requests

path='D:/Documents/论文/狼人杀第一季/srt-cleaned'

url = "https://www.neuqboard.cn/api/gpt"

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/json",
    "origin": "https://www.neuqboard.cn",
    "priority": "u=1, i",
    "referer": "https://www.neuqboard.cn/gpt",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
}
data_1 ="{\"model\":\"deepseek-r1-250528\",\"stream\":true,\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant.\"},{\"role\":\"user\",\"content\":"
data_2 ="}],\"stream_options\":{\"include_usage\":true},\"enable_thinking\":true}"

def askqwen(a):
    data_=data_1+json.dumps(a)+data_2
    response = requests.post(
        url,
        headers=headers,
        data=data_,  # 自动序列化JSON并设置Content-Type
        stream=True  # 启用流式响应
    )
    ans=""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                # 解析SSE格式：data: {...}
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    json_data = decoded_line.split('data:', 1)[1].strip()
                    try:
                        event = json.loads(json_data)
                        # 在此处理事件数据
                        if(len(event['choices'])>0):
                            if(event['choices'][0]['delta']['content']!=None):
                                ans+=event['choices'][0]['delta']['content']
                    except json.JSONDecodeError:
                        pass
                        # print(f"Invalid JSON: {json_data}")
    else:
        print(f"Request failed with status {response.status_code}")
        print(response.text)
    return ans


with open("D:/Documents/论文/狼人杀第一季/QA_unit.json", 'r', encoding='utf-8') as f:
    QA = json.load(f)
with open("D:/Documents/论文/狼人杀第一季/srt-cleaned/01.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

output_path = "D:/Documents/论文/狼人杀第一季/output.json"
for i in range(4,len(QA['categories'])):# 
    for j in range(10,len(QA['categories'][i]['questions'])):
        tmp=QA['categories'][i]['questions'][j]
        # if(j==10):
        #     break
        tmp['explanation']=""
        for k in range(0,len(tmp['options'])):
            if(tmp['options'][k]['key']!=tmp['answerKey']):
                tmp['options'][k]['text']="空"
        ask=str(data)+"\n以上是背景\n"+str(tmp)+"\n以上是题目\n这道题是出现在utterance_id="+str(tmp['utterance_id'])+"的时候。你需要参考正确选项，重新设计五个错误选项，需要使得选项尽可能的混淆，难以被直接猜出答案,你的输出格式应该和题目一样，包含ABCDEF六个选项（EF是新增的）不要输出多余的内容"
    #     # print(ask)
        ans=askqwen(ask)
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(ans)
        print(ans)

# with open(output_path, 'w', encoding='utf-8') as f:
#     f.write(ask)
    # json.dump(QA, f, ensure_ascii=False, indent=4)  # 保持中文可读