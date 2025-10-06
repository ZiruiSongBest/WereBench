import json
import logging
import re
import os
import time
from collections import defaultdict
import concurrent.futures
from openai import OpenAI, RateLimitError, APIConnectionError, AuthenticationError, BadRequestError, APIError

# =========================== 配置区域 ===========================

# 题库文件名
QA_DATA_FILE = 'WereBench.jsons'

# 测试结果保存的文件名
REPORT_OUTPUT_FILE = 'OUTPUT_NAME.txt'

# 用于保存进度的文件 (JSON Lines格式)
PROGRESS_FILE = 'progress_results_MODEL_NAME.jsonl'

# 需要测试的角色列表
ROLES_TO_TEST = ['狼人', '预言家', '女巫', '村民']

# 并发API调用的数量 (根据你的API速率限制调整)
CONCURRENCY_LEVEL = 100

# 日志设置 (显示在控制台的运行过程)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =========================== API & 文件处理 ===========================

# 【安全提示】建议使用环境变量存储API密钥
client = OpenAI(api_key="API_KEY",base_url="https://one-api.bltcy.top/v1/")

# 全局缓存游戏数据
GAME_CONTEXT_CACHE = {}

def call_model_api(prompt: str) -> str:
    """
    调用 OpenAI 兼容的 API，并增加了详细的异常处理和重试机制。
    """
    max_retries = 5
    timeout_seconds = 60

    for attempt in range(max_retries):
        try:
            logger.debug(f"--- Calling API (Attempt {attempt + 1}/{max_retries})... ---")
            chat_completion = client.chat.completions.create(
                model="MODEL_NAME",
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout_seconds,
                # max_tokens=10,
                # temperature=0.0
            )

            if not chat_completion.choices:
                logger.warning("API response did not contain any choices.")
                continue

            response_content = chat_completion.choices[0].message.content
            logger.debug(f"--- API Raw Response: {response_content} ---")
            return response_content

        except AuthenticationError as e:
            logger.error(f"Authentication Error: API key or base URL is incorrect. Aborting. Error: {e}")
            return ""
        except BadRequestError as e:
            logger.error(f"Bad Request Error: The request is malformed (e.g., prompt too long). Aborting. Error: {e}")
            return ""
        except RateLimitError as e:
            wait_time = (attempt + 1) * 20
            logger.warning(f"Rate Limit Error. Waiting for {wait_time} seconds... Error: {e}")
            time.sleep(wait_time)
        except (APIConnectionError, TimeoutError) as e:
            wait_time = 4 ** attempt  # Exponential backoff
            logger.warning(f"Connection/Timeout Error. Waiting for {wait_time} seconds... Error: {e}")
            time.sleep(wait_time)
        except APIError as e:
            wait_time = 4 ** attempt
            logger.warning(f"Generic API Server Error (Status: {e.status_code}). Waiting {wait_time}s... Error: {e}")
            time.sleep(wait_time)
        except Exception as e:
            wait_time = 4 ** attempt
            logger.error(f"An unexpected error occurred: {type(e).__name__}. Waiting {wait_time}s... Error: {e}")
            time.sleep(wait_time)

    logger.error(f"Failed to get a response from the API after {max_retries} attempts.")
    return ""

def load_json_file(filename: str):
    """加载并返回 JSON 文件内容"""
    if not os.path.exists(filename):
        logger.error(f"错误: 文件 '{filename}' 未在当前目录下找到。")
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"错误: 文件 '{filename}' 不是有效的 JSON 格式。")
        return None
    return None
    
# =========================== 辅助函数 ===========================
# (build_role_map, get_game_context, format_utterances, build_prompt, clean_response 保持不变)

def build_role_map(metadata: dict) -> dict:
    alias_map = metadata.get('user_aliases', {})
    role_map = metadata.get('real_role', {})
    player_to_role = {}
    for speaker_key, real_role in role_map.items():
        player_to_role[speaker_key] = real_role
        aliases = alias_map.get(speaker_key, [])
        for alias in aliases:
            player_to_role[alias] = real_role
    return player_to_role

def get_game_context(reference_path: str):
    filename = os.path.basename(reference_path)
    if filename in GAME_CONTEXT_CACHE:
        return GAME_CONTEXT_CACHE[filename]
    
    logger.info(f"正在加载新的游戏数据文件: {filename}")
    game_data = load_json_file(filename)
    if not game_data:
        GAME_CONTEXT_CACHE[filename] = (None, None)
        return None, None
    
    role_map = build_role_map(game_data.get('metadata', {}))
    utterances = game_data.get('utterances', [])
    GAME_CONTEXT_CACHE[filename] = (role_map, utterances)
    return role_map, utterances

def format_utterances(utterances: list, target_utterance_id: int) -> str:
    history = []
    for utt in utterances:
        current_ids = utt.get('utterance_id', [])
        if not current_ids: continue
        
        if current_ids[0] <= target_utterance_id:
            speaker = utt.get('speaker_id', '未知')
            text = utt.get('text', '').strip()
            STATUS_MAP = {
                "sheiff_election": "警长竞选",
                "first_day": "第一天白天",
                "second_day": "第二天白天",
                "third_day": "第三天白天",
            }
            status = STATUS_MAP.get(utt.get('status'), utt.get('status'))
            
            if text:
                history.append(f"[{status}] {speaker}: {text}")
    
    return "\n".join(history)

def build_prompt(history: str, question_text: str, options: list, assigned_role: str) -> str:
    options_str = ""
    for option in options:
        options_str += f"{option['key']}: {option['text']}\n"
        
    prompt = f"""
你正在参与一个狼人杀游戏的逻辑能力测试。
【当前设定】请你代入局中玩家“{assigned_role}”的视角和身份进行思考。

以下是截止到当前时刻的游戏对话记录：
--- 游戏记录开始 ---
{history}
--- 游戏记录结束 ---

请基于以上信息和你的角色视角，回答以下问题：
{question_text}

选项：
{options_str}

【要求】请只输出一个代表正确选项的大写字母（例如：A），不要包含任何其他推理、标点或文字。
"""
    return prompt

def clean_response(response: str) -> str:
    if not response:
        return ""
    match = re.search(r'[A-I]', response.strip().upper())
    return match.group(0) if match else ""

# =========================== 核心测试与报告逻辑 ===========================

def process_question(question_data):
    """处理单个问题的函数，用于并发调用"""
    category_name, question = question_data
    q_id = question.get('id')
    
    # 准备数据
    reference = question.get('reference', '')
    role_map, all_utterances = get_game_context(reference)
    
    player_alias_in_q = question.get('role')
    actual_role = role_map.get(player_alias_in_q)
    
    target_utt_id_list = question.get('utterance_id')
    target_utt_id = target_utt_id_list[0] if isinstance(target_utt_id_list, list) else target_utt_id_list

    history_text = format_utterances(all_utterances, target_utt_id)
    question_text = question.get('text1', question.get('text'))
    options_list = question.get('options', [])
    
    prompt = build_prompt(history_text, question_text, options_list, player_alias_in_q)
    
    # 调用 API
    raw_response = call_model_api(prompt)
    model_choice = clean_response(raw_response)
    correct_key = question.get('answerKey', '').strip().upper()
    
    # 返回结果字典
    return {
        "unique_id": f"{category_name}-{q_id}",
        "role": actual_role,
        "category": category_name,
        "is_correct": model_choice == correct_key if model_choice else False,
        "model_choice": model_choice,
        "correct_key": correct_key,
        "raw_response": raw_response
    }

def run_test():
    """主测试流程，使用并发"""
    qa_data = load_json_file(QA_DATA_FILE)
    if not qa_data:
        logger.error("题库加载失败，终止测试。")
        return

    # 1. 加载已完成的题目ID
    completed_ids = set()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    completed_ids.add(json.loads(line)['unique_id'])
                except (json.JSONDecodeError, KeyError):
                    continue
    logger.info(f"已加载 {len(completed_ids)} 条已完成的测试结果。")

    # 2. 准备所有待测试的任务
    tasks_to_submit = []
    total_eligible_questions = 0
    
    for category in qa_data.get('categories', []):
        category_name = category.get('categoryName', 'Unknown')
        for question in category.get('questions', []):
            q_id = question.get('id')
            unique_id = f"{category_name}-{q_id}"

            # 检查是否已完成
            if unique_id in completed_ids:
                continue

            # 检查是否符合测试条件
            reference = question.get('reference', '')
            if not reference: continue
            
            role_map, _ = get_game_context(reference)
            if not role_map: continue
            
            player_alias_in_q = question.get('role')
            actual_role = role_map.get(player_alias_in_q)
            
            if actual_role and actual_role in ROLES_TO_TEST:
                tasks_to_submit.append(((category_name, question), unique_id))
                total_eligible_questions += 1

    logger.info(f"共有 {total_eligible_questions} 个新题目待测试。")
    if not tasks_to_submit:
        logger.info("没有需要测试的新题目。直接生成报告。")
        generate_report(PROGRESS_FILE)
        return

    # 3. 使用线程池并发执行
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor, \
         open(PROGRESS_FILE, 'a', encoding='utf-8') as progress_f:
        
        future_to_unique_id = {executor.submit(process_question, data): uid for data, uid in tasks_to_submit}
        
        processed_count = 0
        for future in concurrent.futures.as_completed(future_to_unique_id):
            unique_id = future_to_unique_id[future]
            try:
                result = future.result()
                processed_count += 1
                
                # 立即将结果写入文件
                progress_f.write(json.dumps(result) + '\n')
                progress_f.flush() # 确保立即写入磁盘

                is_correct = result.get('is_correct', False)
                logger.info(f"({processed_count}/{total_eligible_questions}) "
                            f"Completed Q: {unique_id} | Result: {'✅' if is_correct else '❌'}")

            except Exception as exc:
                logger.error(f'Question {unique_id} generated an exception: {exc}')

    logger.info("所有新题目测试完成。")
    # 4. 从最终的进度文件生成报告
    generate_report(PROGRESS_FILE)

report_lines = []
def log_report(line: str):
    """同时打印到控制台并添加到报告列表"""
    print(line)
    report_lines.append(line)

def generate_report(progress_file):
    """根据进度文件生成最终报告"""
    if not os.path.exists(progress_file):
        logger.error("进度文件未找到，无法生成报告。")
        return
        
    stats = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    all_categories_seen = set()
    total_tested = 0

    with open(progress_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                result = json.loads(line)
                role = result['role']
                category = result['category']
                is_correct = result['is_correct']
                model_choice = result['model_choice']

                if role in ROLES_TO_TEST and model_choice:
                    stats[role][category]['total'] += 1
                    if is_correct:
                        stats[role][category]['correct'] += 1
                    all_categories_seen.add(category)
                    total_tested +=1
            except (json.JSONDecodeError, KeyError):
                continue

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_report("\n" + "="*60)
    log_report(f" 狼人杀模型能力评估报告 ".center(60, "="))
    log_report(f" 测试时间: {timestamp}")
    log_report(f" 报告基于 {total_tested} 条有效测试结果")
    log_report("="*60 + "\n")

    ordered_categories = ["Role Inference", "Strategic Judgment", "Deception Reasoning", "Social Interaction", "Counterfactual Trade-off"]
    for cat in sorted(list(all_categories_seen)):
        if cat not in ordered_categories:
            ordered_categories.append(cat)

    for role in ROLES_TO_TEST:
        log_report(f"--- [ 角色代入: {role} ] ---")
        
        role_total_correct, role_total_count = 0, 0
        if role not in stats:
            log_report("  (无相关测试数据)")
        else:
            for category in ordered_categories:
                if category not in stats[role]: continue
                data = stats[role][category]
                correct, total = data['correct'], data['total']
                role_total_correct += correct
                role_total_count += total
                acc = (correct / total * 100) if total > 0 else 0.0
                log_report(f"  - {category:<25} : 准确率 {acc:6.2f}%  ({correct:3d} / {total:3d})")

        role_acc = (role_total_correct / role_total_count * 100) if role_total_count > 0 else 0.0
        log_report(f"\n  >> [{role}] 总体准确率 : {role_acc:6.2f}%  ({role_total_correct} / {role_total_count})")
        log_report("-" * 60 + "\n")

    try:
        with open(REPORT_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        logger.info(f"评估报告已成功保存至: {os.path.abspath(REPORT_OUTPUT_FILE)}")
    except Exception as e:
        logger.error(f"保存评估报告失败: {e}")

if __name__ == '__main__':
    logger.info("开始狼人杀逻辑测试脚本...")
    if not os.path.exists(QA_DATA_FILE):
        logger.error(f"致命错误: 题库文件 '{QA_DATA_FILE}' 不存在。")
    else:
        run_test()