import json
import os
import requests
with open("D:/Documents/论文/狼人杀第一季/QA_unit_0928.json", 'r', encoding='utf-8') as f:
    QA = json.load(f)

for i in range(0,len(QA['categories'])):# 
    for j in range(0,len(QA['categories'][i]['questions'])):
        tmp=QA['categories'][i]['questions'][j]
        if not('id' in tmp):
            print(i,j)
        if not('utterance_id' in tmp):
            print(i,j)
        if not('role' in tmp):
            print(i,j)
        if not('text' in tmp):
            print(i,j)
        if not('options' in tmp):
            print(i,j)
        if not('answerKey' in tmp):
            print(i,j)
        if not('reference' in tmp):
            QA['categories'][i]['questions'][j]['reference']=""
        if not('explanation' in tmp):
            QA['categories'][i]['questions'][j]['explanation']=""

        if not('text1' in tmp):
            tmp=QA['categories'][i]['questions'][j]
            QA['categories'][i]['questions'][j]={
                    "id": tmp['id'],
                    "utterance_id": tmp['utterance_id'],
                    "role": tmp['role'],
                    "text": tmp['text'],
                    "text1":tmp['text'],
                    "options":tmp['options'],
                    "answerKey": tmp['answerKey'],
                    "reference": tmp['reference'],
                    "explanation":tmp['explanation'],
                }

with open("D:/Documents/论文/狼人杀第一季/QA_unit_0928_1.json", 'w', encoding='utf-8') as f:
    json.dump(QA, f, ensure_ascii=False, indent=4)  # 保持中文可读