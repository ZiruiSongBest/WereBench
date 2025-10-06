import random
import json
import os
import requests
def shuffle_options(question_obj):
    # 复制选项列表
    options = question_obj['options'][:]
    
    # 保存原始正确答案的文本内容
    original_answer_key = question_obj['answerKey']
    original_correct_text = next(opt['text'] for opt in options if opt['key'] == original_answer_key)
    
    # 随机打乱选项顺序
    random.shuffle(options)
    
    # 重新映射选项的key
    new_keys = ['A', 'B', 'C', 'D', 'E', 'F','G','H','I']
    for i, option in enumerate(options):
        option['key'] = new_keys[i]
        
        # 找到新位置对应的正确答案key
        if option['text'] == original_correct_text:
            question_obj['answerKey'] = new_keys[i]
    
    # 更新问题对象中的选项
    question_obj['options'] = options
    return question_obj

def check_option_lengths(question_obj):
    """
    检查正确选项的文本长度是否在6个选项中是最长或最短的
    
    参数:
        question_obj: 包含问题和选项的字典对象
        
    返回:
        tuple: (is_longest, is_shortest, all_lengths)
        is_longest: 布尔值，表示正确选项是否是最长的
        is_shortest: 布尔值，表示正确选项是否是最短的
        all_lengths: 所有选项长度的列表
    """
    # 获取正确答案的key
    correct_key = question_obj['answerKey']
    
    # 找到正确答案的选项
    correct_option = next(opt for opt in question_obj['options'] if opt['key'] == correct_key)
    correct_length = len(correct_option['text'])
    
    # 获取所有选项的长度
    all_lengths = [len(opt['text']) for opt in question_obj['options']]
    
    # 检查是否是最长或最短
    is_longest = correct_length == max(all_lengths)
    is_shortest = correct_length == min(all_lengths)
    
    return is_longest, is_shortest, all_lengths


with open("D:/Documents/论文/狼人杀第一季/QA_9question_0928_1.json", 'r', encoding='utf-8') as f:
    QA = json.load(f)

less=0
long=0
for i in range(0,len(QA['categories'])):# 
    for j in range(0,len(QA['categories'][i]['questions'])):
        if(len(QA['categories'][i]['questions'][j]['options'])!=9):
            print(i,j)
        QA['categories'][i]['questions'][j]=shuffle_options(QA['categories'][i]['questions'][j])
        a,b,c=check_option_lengths(QA['categories'][i]['questions'][j])
        long+=a
        less+=b

print(less)
print(long)

with open("D:/Documents/论文/狼人杀第一季/QA_9question_1001.json", 'w', encoding='utf-8') as f:
    json.dump(QA, f, ensure_ascii=False, indent=4)  # 保持中文可读