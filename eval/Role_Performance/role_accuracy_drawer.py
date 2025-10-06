import json
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects

# 增大全局字体
plt.rcParams.update({'font.size': 16, 'axes.titlesize': 18, 'axes.labelsize': 16})
plt.rcParams['axes.linewidth'] = 1.6

# 初始化角色及其颜色，使用新的配色方案
roles = ['Werewolf', 'Prophet', 'Witch', 'Villagers']
role_colors = {
    'Werewolf': '#102E50',
    'Prophet': '#F5C45E',
    'Witch': '#E78B48',
    'Villagers': '#BE3D2A'
}

# 定义模型展示名称 —— 顺序很重要
model_display_names = {
    'DeepSeek-V3.1': 'DeepSeek-V3.1',
    'DeepSeek-V3.2-Exp': 'DeepSeek-V3.2-Exp',
    'Gemini-2.5-flash': 'Gemini-2.5-flash',
    'GLM-4.5': 'GLM-4.5',
    'GPT-5': 'GPT-5'
}
models = list(model_display_names.keys())

# 从结果文件中提取角色特定数据的函数
def extract_role_specific_data(file_path):
    role_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            if 'summary' in data and 'role_specific' in data['summary']:
                for role in roles:
                    if role in data['summary']['role_specific'] and '3' in data['summary']['role_specific'][role]:
                        role_data[role] = {
                            'Speech_accuracy': data['summary']['role_specific'][role]['3']['Speech_accuracy'],
                            'role_accuracy': data['summary']['role_specific'][role]['3']['role_accuracy']
                        }
    return role_data

# yh：全部使用硬编码
special_model_data = {
    'DeepSeek-V3.1': {
        'Werewolf': {'Speech_accuracy': 55.42, 'role_accuracy': 25.00},
        'Prophet': {'Speech_accuracy': 62.00, 'role_accuracy': 48.15},
        'Witch': {'Speech_accuracy': 52.70, 'role_accuracy': 58.33},
        'Villagers': {'Speech_accuracy': 61.33, 'role_accuracy': 52.50}
    },
    'DeepSeek-V3.2-Exp': {
        'Werewolf': {'Speech_accuracy': 53.61, 'role_accuracy': 30.00},
        'Prophet': {'Speech_accuracy': 64.00, 'role_accuracy': 44.44},
        'Witch': {'Speech_accuracy': 50.00, 'role_accuracy': 58.33},
        'Villagers': {'Speech_accuracy': 57.33, 'role_accuracy': 47.50}
    },
    'Gemini-2.5-flash': {
        'Werewolf': {'Speech_accuracy': 57.06, 'role_accuracy': 35.00},
        'Prophet': {'Speech_accuracy': 55.00, 'role_accuracy': 48.15},
        'Witch': {'Speech_accuracy': 52.78, 'role_accuracy': 66.67},
        'Villagers': {'Speech_accuracy': 51.33, 'role_accuracy': 45.00}
    },
    'GLM-4.5': {
        'Werewolf': {'Speech_accuracy': 60.24, 'role_accuracy': 45.00},
        'Prophet': {'Speech_accuracy': 58.00, 'role_accuracy': 44.44},
        'Witch': {'Speech_accuracy': 47.30, 'role_accuracy': 58.33},
        'Villagers': {'Speech_accuracy': 57.33, 'role_accuracy': 50.00}
    },
    'GPT-5': {
        'Werewolf': {'Speech_accuracy': 60.49, 'role_accuracy': 50.00},
        'Prophet': {'Speech_accuracy': 64.00, 'role_accuracy': 48.15},
        'Witch': {'Speech_accuracy': 58.11, 'role_accuracy': 66.67},
        'Villagers': {'Speech_accuracy': 56.38, 'role_accuracy': 35.90}
    }
}

# 收集所有模型的数据
results = {}
for model in models:
    if model in special_model_data:
        results[model] = special_model_data[model]
    else:
        file_path = f"blood/results/{model}_6_all_results.json"
        results[model] = extract_role_specific_data(file_path)

# 创建绘图窗口
fig, ax_bar = plt.subplots(figsize=(10, 6))
ax_line = ax_bar.twinx()

# 设置柱状图宽度
bar_width = 0.2
index = np.arange(len(models))

# 用来存放图例元素
legend_elements = []

# 针对每个角色分别绘图
for i, role in enumerate(roles):
    Speech_accuracy_data = []
    role_accuracy_data = []

    for model in models:
        model_data = results.get(model, {})
        role_data = model_data.get(role, {'Speech_accuracy': 0, 'role_accuracy': 0})
        Speech_accuracy_data.append(role_data.get('Speech_accuracy', 0))
        role_accuracy_data.append(role_data.get('role_accuracy', 0))

    # 计算柱状图位置
    bar_position = index + (i - 1.5) * bar_width
    # 绘制自身角色识别准确率柱状图（左侧坐标轴）
    ax_bar.bar(bar_position, role_accuracy_data, bar_width, 
               color=role_colors[role], edgecolor='black', linewidth=1.5, alpha=0.6)

    # 绘制犯罪角色识别准确率的折线图（右侧坐标轴）
    line = ax_line.plot(index, Speech_accuracy_data, marker='o', linestyle='-', 
                 color=role_colors[role], linewidth=4, markersize=8,
                 markeredgecolor='black', markeredgewidth=0.8
                 )
    
    # 添加黑色描边效果
    line[0].set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'),
                           path_effects.Normal()])

    # 为每个角色添加图例元素（一次添加柱状图和折线图图例）
    legend_elements.append(Patch(facecolor=role_colors[role], edgecolor='black', alpha=0.6,
                                 label=f'{role} (Role)'))
    legend_elements.append(Line2D([0], [0], color=role_colors[role], marker='o', linestyle='-',
                                  linewidth=2, markersize=8, markeredgecolor='black', markeredgewidth=0.5,
                                  path_effects=[path_effects.Stroke(linewidth=2, foreground='black'),
                                               path_effects.Normal()],
                                  label=f'{role} (Speech)'))

# 设置y轴标签（保留y轴标签以便说明数值含义）
ax_bar.set_ylabel('Role Performance Acc. (%)', fontsize=14)
ax_line.set_ylabel('Speech Performance Acc. (%)', fontsize=14)

# 设置x轴刻度
ax_bar.set_xticks(index)
ax_bar.set_xticklabels([model_display_names[model] for model in models], rotation=20, ha='center', fontsize=14)

# 设置y轴范围
ax_bar.set_ylim(0, 70)
ax_line.set_ylim(30, 70)

# 添加网格线
ax_bar.grid(axis='y', linestyle='--', alpha=0.3)

# 将图例放置在图上方，并设置半透明背景
ax_bar.legend(handles=legend_elements, ncol=4, loc='upper center', bbox_to_anchor=(0.5, 1.3), 
             framealpha=0.8, fontsize=14)

plt.tight_layout()
plt.savefig('role_accuracy.pdf', dpi=300, bbox_inches='tight')