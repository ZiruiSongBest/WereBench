import json
import os
import requests
from threading import Thread
AUTHORIZATIONS = [
    "Bearer 9117dd3c-236c-4e29-89bf-7cdbbd38bc19",
    "Bearer af5af190-0a06-4c45-8043-9d3cb4e6884b",
    "Bearer 7f1ee767-cf4a-4e46-a7e2-c502df663cd4",
    "Bearer 16a4c287-f4f1-4239-8144-90f2446c6c6d",
    "Bearer ace422b8-1b9d-4707-bda7-161858fb1389"
]
url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

def askqwen(a,token):
    headers = {
        "content-type": "application/json",
        "Authorization": token,
    }
    data={
        "model": "deepseek-v3-1-terminus",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": a
            }
        ],
        # "enable_thinking": True
    }
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return reply
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")


with open("D:/Documents/论文/狼人杀第一季/QA_unit_0928_2.json", 'r', encoding='utf-8') as f:
    QA = json.load(f)
with open("D:/Documents/论文/狼人杀第一季/QA_4question_0928_1.json", 'r', encoding='utf-8') as f:
    QA2 = json.load(f)
def parse_options(ans):
    try:
        # 尝试解析 JSON 并获取 'options'
        data = json.loads(ans)
        options = data.get('options', [])  # 使用 get 避免 KeyError
        return options
    except (json.JSONDecodeError, TypeError, KeyError):
        # 捕获以下异常：
        # 1. JSONDecodeError: JSON 解析失败
        # 2. TypeError: ans 不是字符串（如 None）
        # 3. KeyError: 已通过 get 避免，此处可省略
        return []
    except Exception:
        # 其他未知异常也返回空列表
        return []
def test(i):
# for i in range(4,len(QA['categories'])):# 
    token=AUTHORIZATIONS[i]
    for j in range(0,len(QA['categories'][i]['questions'])):
        if(len(QA2['categories'][i]['questions'][j]['options'])>0):
            QA['categories'][i]['questions'][j]=QA2['categories'][i]['questions'][j]
            continue######
        print(i,j)
        tmp=QA['categories'][i]['questions'][j]# 只改option
        answerKey=tmp['answerKey']
        for k in range(0,len(tmp['options'])):
            if(tmp['options'][k]['key']==answerKey):
                answercontent=tmp['options'][k]['text']
        reference=tmp['reference']
        file='D:/Documents/论文/狼人杀第一季/data/'+reference[5:]
        with open(file, 'r', encoding='utf-8') as f:
            a = json.load(f)

        tmp2={"content": tmp['text1'],
            "options": [
                {
                    "key": "A",
                    "text": answercontent
                },
                {
                    "key": "B",
                    "text": "空"
                },
                {
                    "key": "C",
                    "text": "空"
                },
                {
                    "key": "D",
                    "text": "空"
                }
            ],
            "answerKey": "A",
        }
        ask=str(a)+"\n以上是背景\n"+str(tmp2)+"\n以上是题目\n这道题是出现在utterance_id="+str(tmp['utterance_id'])+"的时候。你需要参考正确选项，重新设计三个错误选项，需要使得选项尽可能的混淆，难以被直接猜出答案,你的输出格式应该和题目的格式一模一样，不要输出多余的内容"
        ans=askqwen(ask,token)
        QA['categories'][i]['questions'][j]['answerKey']='A'
        QA['categories'][i]['questions'][j]['options']= parse_options(ans)
        # return
        # with open(output_path, 'a', encoding='utf-8') as f:
        #     f.write(ans)
        # print(ans)

thread1 = Thread(target=test, args=(0,))
thread2 = Thread(target=test, args=(1,))
thread3 = Thread(target=test, args=(2,))
thread4 = Thread(target=test, args=(3,))
thread5 = Thread(target=test, args=(4,))
 
thread1.start()  # 线程1启动
thread2.start()  # 任务2启动
thread3.start()  # 任务2启动
thread4.start()  # 任务2启动
thread5.start()  # 任务2启动

thread1.join()   # 等待线程1完成线程
thread2.join()   # 等待线程2
thread3.join()   # 等待线程1完成线程
thread4.join()   # 等待线程1完成线程
thread5.join()   # 等待线程1完成线程

with open("D:/Documents/论文/狼人杀第一季/QA_4question_0928_1.json", 'w', encoding='utf-8') as f:
    json.dump(QA, f, ensure_ascii=False, indent=4)  # 保持中文可读