import json
import os
import threading
import requests
from threading import Thread

model="MODEL_NAME"
output='PATH_TO_OUTPUT'
url = "https://hiapi.online/v1/completions"
AUTHORIZATIONS = [
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
    "Bearer API_KEY",
]
filename = "WereBench.json"
path='PATH_TO_BENCHMARK'
def askqwen(a,token):
    headers = {"content-type": "application/json","Authorization": token}
    data={
        "model": model,
        "messages": [
            # {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content": a}
        ],
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
            reply=reply.replace("\n","")
            id=reply.find('</think>')
            if(id!=-1):
                reply= reply[reply.find('</think>')+8:]
            return reply
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
def work(ask,reference,utterance_id,token):
    file=path+'\\'+reference[5:]
    with open(file, 'r', encoding='utf-8') as f:
        a = json.load(f)
    b=[]
    b.append(a['metadata']['game_rules'])
    b.append(a['metadata']['game_roles'])
    for i in range(0,len(a['utterances'])):
        bj=0
        for j in range(0,len(a['utterances'][i]['utterance_id'])):
            if(a['utterances'][i]['utterance_id'][j]>utterance_id):
                bj=1
        if(bj==1):
            break
        b.append({"speaker_id":a['utterances'][i]['speaker_id'],"text":a['utterances'][i]['text']})
    b.append("回答以下问题，只输出正确选项，不要输出别的内容")
    b.append("单选题")
    b.append(ask)
    b=str(b)
    ans=askqwen(b,token)
    ans.replace("\n","")
    # print(b)
    return ans
groups=[]
lock = threading.Lock()
def test(x):
    token=AUTHORIZATIONS[x]
    for j in range(0,len(data['categories'])):
        for k in range(0,len(data['categories'][j]['questions'])):
            tmp=j*10000+data['categories'][j]['questions'][k]['id']
            lock.acquire()
            if tmp in groups:
                lock.release()
                continue
            groups.append(tmp)
            lock.release()
            tmp=data['categories'][j]['questions'][k]
            try:
                ask={"role":tmp['role'],"text":tmp['text1'],"options":tmp['options']}
                reference=tmp['reference']
                utterance_id=tmp['utterance_id']
                ans=work(ask,reference,utterance_id,token)
                with open(output, 'a') as f:
                    print("ID:", j, tmp['id'], ans, tmp['answerKey'])
                    f.write("ID: " +str(j)+" "+str(tmp['id'])+" "+ans+" "+tmp['answerKey']+"\n")
            except Exception as e:
                print("发生异常:", e)





# print(askqwen("1+1等于几？",AUTHORIZATIONS[0]))
with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)
with open(output, "r") as f:
    lines = f.readlines()
for line in lines:
    parts = line.strip().split()
    if len(parts) < 5:
        continue
    x = int(parts[1])
    y = int(parts[2])
    groups.append(x*10000+y)
thread=[]
for i in range(0,len(AUTHORIZATIONS)):
    thread.append(Thread(target=test, args=(i,)))
    thread[i].start()
for i in range(0,len(AUTHORIZATIONS)):
    thread[i].join()