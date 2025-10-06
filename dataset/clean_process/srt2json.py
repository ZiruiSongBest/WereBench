#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime, timedelta
from collections import OrderedDict

# --- 辅助函数：时间处理 ---

def parse_srt_time(time_str: str) -> timedelta:
    """将 SRT 时间字符串 (HH:MM:SS,ms) 转换为 timedelta 对象。"""
    if not time_str:
        return timedelta()
    parts = time_str.split(',')
    milliseconds = int(parts[1]) if len(parts) > 1 else 0
    hms = parts[0].split(':')
    return timedelta(
        hours=int(hms[0]),
        minutes=int(hms[1]),
        seconds=int(hms[2]),
        milliseconds=milliseconds
    )

def format_timedelta_to_srt_str(td: timedelta) -> str:
    """将 timedelta 对象格式化回 SRT 时间字符串 (HH:MM:SS,ms)。"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# --- 辅助函数：逻辑判断 ---

def get_game_status(time_td: timedelta, sorted_status_intervals: list) -> str:
    """根据时间戳从排序后的游戏状态列表中获取当前状态。"""
    current_status = None
    for status_name, status_time in sorted_status_intervals:
        if time_td >= status_time:
            current_status = status_name
        else:
            break
    # 如果状态是 'end_time'，我们将其归类为最后一个有效阶段
    if current_status == 'end_time' and len(sorted_status_intervals) > 1:
         return sorted_status_intervals[-2][0] # 返回 'end_time' 之前的最后一个状态
    
    return current_status or "pre_game" # 默认或前置状态

def get_current_sheriff(time_td: timedelta, sorted_sheriffs: list) -> str | None:
    """根据时间戳从排序后的警长任命中获取现任警长。"""
    current_sheriff = None
    for appoint_time, speaker in sorted_sheriffs:
        if time_td >= appoint_time:
            current_sheriff = speaker
        else:
            break
    return current_sheriff

# --- 主处理函数 ---

def process_srt_to_json(config: dict, srt_filepath: str, output_filepath: str):
    """
    主函数，读取SRT文件，处理数据，并根据配置生成JSON文件。
    """
    
    print(f"开始处理: {srt_filepath}")

    # 1. 准备元数据和时间锚点
    metadata_config = config['metadata']
    real_role_map = metadata_config.get('real_role', {})
    
    # (MODIFIED) 创建一个从 "说话人 X" 到 "X号" 的映射
    speaker_to_alias_map = {
        speaker: aliases[0]
        for speaker, aliases in metadata_config.get('user_aliases', {}).items()
        if aliases # 确保别名列表不为空
    }
    
    # 将 game_status 时间转换为 timedelta 并排序
    game_status_times = {}
    for status, time_str in metadata_config.get('game_status', {}).items():
        if time_str: # 过滤掉 null 值
            game_status_times[status] = parse_srt_time(time_str)

    # 创建一个按时间排序的状态区间列表
    # (OrderedDict 在这里确保了 Python 3.7+ 的 dict 排序行为)
    sorted_status_list = sorted(game_status_times.items(), key=lambda item: item[1])

    # 获取游戏的绝对开始和结束时间
    try:
        GAME_START_TD = game_status_times['first_night']
        GAME_END_TD = game_status_times['end_time']
    except KeyError as e:
        print(f"错误: game_status 缺少 {e}。无法确定游戏边界。")
        return

    # 将警长任命时间转换为 timedelta 并排序
    sheriff_appointments_sorted = sorted(
        [(parse_srt_time(time_str), speaker) for speaker, time_str in config.get('sheriff_appointments', {}).items()],
        key=lambda item: item[0]
    )

    # 2. SRT 解析 (Pass 1: 读取所有原始条目并提取摘要)
    raw_entries = []
    summary_texts = []
    summary_start, summary_end = config.get('summary_id_range', (0, 0))
    
    # 用于解析SRT中 "说话人 X: 文本" 格式的正则表达式
    speaker_text_re = re.compile(r"^(说话人 \d+): (.*)$", re.DOTALL)
    
    try:
        with open(srt_filepath, 'r', encoding='utf-8') as f:
            # 按空行分割SRT条目
            srt_blocks = f.read().split('\n\n')
            
            for block in srt_blocks:
                block = block.strip()
                if not block:
                    continue
                
                lines = block.split('\n')
                if len(lines) < 3:
                    continue # 条目不完整

                try:
                    entry_id = int(lines[0])
                    time_line = lines[1]
                    text_lines = lines[2:]
                    
                    time_match = re.match(r'([\d:,]+)\s-->\s([\d:,]+)', time_line)
                    if not time_match:
                        continue
                        
                    start_str, end_str = time_match.groups()
                    full_text = " ".join(text_lines)
                    
                    speaker_match = speaker_text_re.match(full_text)
                    if not speaker_match:
                        # 如果主持人的行没有 "说话人 X:" 前缀 (例如规则说明)
                        # 我们将其归为一个通用ID，例如 'HOST_NARRATOR'
                        # 但根据提供的SRT，主持人 (说话人 12) 总是被标记的。
                        # 我们将跳过无法识别发言人的行。
                        # print(f"警告: 跳过SRT条目 {entry_id}，未找到发言人格式: {full_text[:50]}...")
                        continue

                    speaker_id, text = speaker_match.groups()
                    
                    raw_entry = {
                        "id": entry_id,
                        "start_td": parse_srt_time(start_str),
                        "end_td": parse_srt_time(end_str),
                        "start_str": start_str,
                        "end_str": end_str,
                        "speaker": speaker_id,
                        "text": text.strip()
                    }
                    raw_entries.append(raw_entry)
                    
                    # 提取摘要
                    if summary_start <= entry_id <= summary_end:
                        summary_texts.append(text.strip())

                except Exception as e:
                    print(f"警告: 解析SRT块失败: {e}\n块内容: {block}\n")

    except FileNotFoundError:
        print(f"错误: SRT 文件未找到: {srt_filepath}")
        return
    except Exception as e:
        print(f"错误: 读取 SRT 文件时出错: {e}")
        return

    print(f"SRT解析完毕。读取 {len(raw_entries)} 个有效条目。")

    # 3. 数据处理 (Pass 2: 过滤和填充字段)
    game_utterances_unmerged = []
    for entry in raw_entries:
        # 规则: 只处理在 first_night 和 end_time 之间的对话
        if not (GAME_START_TD <= entry['start_td'] < GAME_END_TD):
            continue
            
        # (MODIFIED) 使用原始ID进行逻辑计算，然后转换为别名用于输出
        status = get_game_status(entry['start_td'], sorted_status_list)
        
        # 先获取原始ID ("说话人 X")
        raw_speaker_id = entry['speaker']
        raw_sheriff_id = get_current_sheriff(entry['start_td'], sheriff_appointments_sorted)
        
        # 使用原始ID进行逻辑判断
        role = real_role_map.get(raw_speaker_id)
        is_host = (role == 'host')
        is_sheriff = (raw_speaker_id == raw_sheriff_id)
        duration = int((entry['end_td'] - entry['start_td']).total_seconds())

        # 将ID转换为别名 ("X号") 以便输出
        aliased_speaker = speaker_to_alias_map.get(raw_speaker_id, raw_speaker_id)
        aliased_sheriff = speaker_to_alias_map.get(raw_sheriff_id) if raw_sheriff_id else None

        utterance_data = {
            "utterance_id": [entry['id']],
            "start_time": entry['start_str'],
            "end_time": entry['end_str'],
            "duration": duration,
            "status": status,
            "speaker_id": aliased_speaker,  # 使用转换后的别名
            "sheriff": aliased_sheriff,      # 使用转换后的别名
            "is_host": is_host,
            "is_sheriff": is_sheriff,
            "role": role,
            "text": entry['text']
        }
        game_utterances_unmerged.append(utterance_data)

    print(f"已过滤 {len(game_utterances_unmerged)} 条游戏内对话（合并前）。")

    # 4. 数据处理 (Pass 3: 合并)
    # 规则: 如果相邻对话的 speaker_id 和 status 相等，则合并。
    final_utterances = []
    if not game_utterances_unmerged:
        print("警告: 过滤后没有可处理的游戏对话。")
    else:
        current_merged = game_utterances_unmerged[0].copy() # 必须复制，否则会修改列表中的原始数据
        
        for next_utterance in game_utterances_unmerged[1:]:
            # 检查合并条件 (现在比较的是 "X号" 这类的别名, 逻辑依然正确)
            if (next_utterance['speaker_id'] == current_merged['speaker_id'] and
                next_utterance['status'] == current_merged['status']):
                
                # 执行合并
                current_merged['utterance_id'].extend(next_utterance['utterance_id'])
                current_merged['end_time'] = next_utterance['end_time'] # 更新为最后的时间
                current_merged['text'] += " " + next_utterance['text'] # 合并文本
                
                # 重新计算持续时间
                merged_start_td = parse_srt_time(current_merged['start_time'])
                merged_end_td = parse_srt_time(current_merged['end_time'])
                current_merged['duration'] = int((merged_end_td - merged_start_td).total_seconds())
            
            else:
                # 不合并，将前一个合并组存入，并开始新的合并组
                final_utterances.append(current_merged)
                current_merged = next_utterance.copy() # 开始新的合并组
        
        # 不要忘记添加最后一个合并组
        final_utterances.append(current_merged)

    print(f"合并后剩余 {len(final_utterances)} 条最终对话。")

    # 5. 组装最终 JSON
    
    # 填充剩余的元数据
    metadata_output = metadata_config.copy()
    metadata_output['total_utterances'] = len(game_utterances_unmerged) # 按要求，这是合并前的对话总数
    metadata_output['language'] = "chinese" # 按要求固定
    metadata_output['summary'] = " ".join(summary_texts) # 添加提取的摘要
    
    # 构建最终的输出对象
    final_json_data = {
        "metadata": metadata_output,
        "utterances": final_utterances
    }

    # 6. 写入文件
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(final_json_data, f, ensure_ascii=False, indent=4)
        print(f"成功！已将数据写入: {output_filepath}")
    except Exception as e:
        print(f"错误: 写入 JSON 文件失败: {e}")


# =============================================================================
# === 用户配置 (USER CONFIGURATION) ===
# =============================================================================
# 请在此处填写您游戏的所有特定元数据。
GAME_CONFIG = {
    # 1. 元数据 (在 'metadata' 键下)
    "metadata": {
        "game_id": 1,
        "source": "Pandakill Season 1, Episode 1",
        "game_rules": "狼人杀游戏分为两大阵营，即狼人阵营和好人阵营。好人阵营包括普通村民方和神明方。本期游戏共有 4 张狼人牌、 4 张普通村民牌和 4 张神名牌。狼人每晚可以共同杀死一名玩家，白天可以选择自爆，直接进入天黑，普通村民夜间没有特殊功能，白天可以和所有玩家一起行使公投权。神明包括预言家、女巫、潜行者、禁言长老，预言家每晚可以侦测一名玩家的身份。女巫有一瓶解药和一瓶毒药，同一晚不能使用两瓶药，只有第一晚可以自救。潜行者每局可以暗杀一名自己白天投了票但没有出局的玩家，投票仅当天有效。禁言长老每晚可以禁言一名玩家，被禁言的玩家白天不能说话，只能比手势。本期游戏采用屠边规则，狼人杀死所有普通村民和所有神明则狼人阵营胜利，好人公投出所有狼人则好人阵营胜利", # 按要求：留空或手动填写规则
        "game_roles": [ # 填写此板子中的所有角色
            "预言家",
            "女巫",
            "狼人",
            "村民",
            "禁言长老",
            "潜行者"
        ],
        "game_status": OrderedDict([ # 必须按时间顺序填写！
            ("first_night", "00:03:35,500"), # 游戏从SRT 00:00:00,120 开始
            ("sheiff_election", "00:04:13,940"), # 警长竞选从 SRT 00:03:35,500 开始 (第44条)
            ("first_day", "00:10:23,000"), # 第一个白天发言从 SRT 00:10:23,000 开始 (第89条)
            ("second_night", "00:22:50,450"), # 第二夜从 SRT 00:22:50,450 开始 (第180条)
            ("second_day", "00:23:03,490"), # 第二天从 SRT 00:23:03,490 开始 (第181条)
            ("third_night", "00:40:57,660"), # (估算值，基于第306条遗言结束)
            ("third_day", "00:41:39,700"),   # 第三天从 SRT 00:41:39,700 开始 (第310条)
            ("end_time", "00:49:36,630") # 游戏在 SRT 00:49:36,630 结束 (第380条)
        ]),
        "user_aliases": { # SRT中的发言人ID -> 别名数组
            "说话人 1": ["12号"], 
            "说话人 2": ["11号"],
            "说话人 3": ["9号"],
            "说话人 4": ["5号"],
            "说话人 5": ["4号"],
            "说话人 6": ["6号"],
            "说话人 7": ["8号"],
            "说话人 8": ["7号"],
            "说话人 9": ["2号"],
            "说话人 10": ["1号"],
            "说话人 11": ["3号"],
            "说话人 12": ["host"], # 主持人
            "说话人 13": ["10号"] 
        },
        "real_role": { # (基于 SRT 第 381-382 条复盘)
            "说话人 1": "禁言长老",   
            "说话人 2": "狼人",   
            "说话人 3": "预言家",   
            "说话人 4": "村民",    
            "说话人 5": "狼人", 
            "说话人 6": "村民",    
            "说话人 7": "村民",    
            "说话人 8": "村民",  
            "说话人 9": "狼人",   
            "说话人 10": "女巫",   
            "说话人 11": "狼人",    
            "说话人 12": "host",    
            "说话人 13": "潜行者"    
        },
        "MVP": {
            "id": "4号",
            "votes": {
                "first_day_votes": {
                    "vote_to": "6号",
                    "cut_off_time": "00:40:15,560"
                },
                "second_day_votes": {
                    "vote_to": "8号",
                    "cut_off_time": "00:49:07,210"
                }
            }
        },
        "logs": "1 号是女巫，警长竞选时反水立警查杀 2 号并建议 9 号拿警徽，第一天白天指出 2、3 是双狼且建议验 5 号，第二天跳禁言长老称第一天禁 5 号、第二天禁 4 号并建议出 4 或 6 号，后夜间被狼人刀死；2 号是狼人，警长竞选时自称预言家，警徽流先验 7 号再验 5 号且查 12 号是金水，第一天白天自爆；3 号是狼人，警长竞选时自称真预言家，称 2 号是查杀且要验 5 号和 11 号，第一天白天质疑 12 号身份，后夜间被女巫毒死；4 号是狼人，警长竞选时弃票，第一天白天说 5 号身份偏好且认可 9 号预言家，第二天被禁言，白天说 6、8 是两狼，第三天白天被投票出局；5 号是村民，警长竞选时参与竞选，第一天白天称自己是平民，第二天成为警长，第三天白天说 4 号是平民且 8 号像狼；6 号是村民，第一天白天称自己是好人且建议出 2 号，第二天跳女巫称毒了 3 号，后白天被投票出局；7 号是村民，第一天白天说投 9 号是因为觉得 2、5、12 号认识且自己是平民，第三天白天称自己是村民；8 号是村民，第一天白天跳女巫称救了 9 号且有一瓶毒并站边 9 号，第二天质疑 6 号是假女巫，第三天白天说 3 号被毒死、11 号被潜行者带走；9 号是预言家，警长竞选时参与竞选并当选警长，第一天白天自称真预言家且查 12 号是好人，后夜间被狼人刀死；10 号是潜行者，警长竞选时退水，第一天白天翻 5 号手语称 5 号认 9 号是预言家、7 号是女巫且建议出 2 号，第二天跳女巫称救了 7 号、毒了 3 号且建议出 6 号，夜间暗杀 11 号；11 号是狼人，第一天白天质疑 12 号身份，后夜间被潜行者暗杀；12 号是禁言长老，警长竞选时参与竞选并反水立警查杀 2 号，第一天白天说 2 号是狼人，第三天被禁言。" # 按要求：留空或手动填写
    },
    
    # 2. 警长任命 
    "sheriff_appointments": {
        "说话人 3": "00:10:06,400",
        "说话人 4": "00:23:29,690"
    },
    
    # 3. 摘要提取范围
    # (按要求：从第 381 条到第 398 条)
    "summary_id_range": (381, 398)
}
# =============================================================================
# === 脚本执行 ===
# =============================================================================

if __name__ == "__main__":
    # 定义输入和输出文件路径
    # 与此脚本位于同一目录中，或者在此处提供完整路径。
    INPUT_SRT_FILE = "01.srt"
    OUTPUT_JSON_FILE = "01.json"

    # 运行处理
    process_srt_to_json(
        config=GAME_CONFIG,
        srt_filepath=INPUT_SRT_FILE,
        output_filepath=OUTPUT_JSON_FILE
    )