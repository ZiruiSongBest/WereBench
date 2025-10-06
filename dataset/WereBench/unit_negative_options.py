import json
import os
import requests
from threading import Thread

with open("D:/Documents/论文/狼人杀第一季/QA_unit_0928_2.json", 'r', encoding='utf-8') as f:
    QA = json.load(f)
with open("D:/Documents/论文/狼人杀第一季/QA_4question_0928_1.json", 'r', encoding='utf-8') as f:
    QA2 = json.load(f)


for i in range(0,len(QA['categories'])):# 
    for j in range(0,len(QA['categories'][i]['questions'])):
        QA['categories'][i]['questions'][j]['options'].append(
                        {
                            "key": "G",
                            "text": QA2['categories'][i]['questions'][j]['options'][1]['text']
                        })
        QA['categories'][i]['questions'][j]['options'].append(
                        {
                            "key": "H",
                            "text": QA2['categories'][i]['questions'][j]['options'][2]['text']
                        })
        QA['categories'][i]['questions'][j]['options'].append(
                        {
                            "key": "I",
                            "text": QA2['categories'][i]['questions'][j]['options'][3]['text']
                        })

with open("D:/Documents/论文/狼人杀第一季/QA_9question_0928_1.json", 'w', encoding='utf-8') as f:
    json.dump(QA, f, ensure_ascii=False, indent=4)  # 保持中文可读