import json
import re
import os
import logging
from typing import Dict, Any, List, Tuple

# --- Import and Configure OpenAI ---
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load .env file variables
load_dotenv()

# 2. Get API key and initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("FATAL: OPENAI_API_KEY not found. Ensure your .env file is correct.")
    exit()

client = OpenAI(api_key="API_KEY",base_url="https://one-api.bltcy.top/v1/")


# 3. Configure logging
log_file = 'role_prediction_output_context_MODEL_NAME.txt'
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# --- API Call Module (Chat Version) ---
def call_gpt5_chat_api(messages: List[Dict[str, str]]) -> str:
    """
    Calls the OpenAI Chat API with the current conversation history.
    """
    logger.info("--- Calling OpenAI Chat API with accumulated context... ---")
    try:
        chat_completion = client.chat.completions.create(
            model="MODEL_NAME",
            messages=messages,
        )
        logger.info(f"--- API Response: {chat_completion.choices[0].message.content} ---")
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"--- API Call Failed: {e} ---")
        return "API_ERROR"

# --- Helper Functions ---
# MODIFICATION 2: Enhanced parsing function
def parse_model_role_response(response: str) -> Tuple[str, str]:
    """
    Parses '[player_id]号:[role]' from the model's response.
    This version first strips any <think>...</think> blocks to handle complex outputs.
    """
    # 1. Remove any thought processes enclosed in <think> tags.
    # The re.DOTALL flag ensures that '.' matches newline characters as well.
    cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()

    # 2. Parse the player ID and role from the cleaned response.
    match = re.search(r'(\d{1,2})号:\s*(.+)', cleaned_response)
    if match:
        player_id = f"{match.group(1)}号"
        role = match.group(2).strip()
        return player_id, role
    return None, None

def format_dialogue(utterances: List[Dict[str, Any]]) -> str:
    """Formats dialogue history into a readable string."""
    dialogue_lines = []
    for u in utterances:
        speaker = u.get("speaker_id", "Unknown Speaker")
        text = u.get("text", "")
        if u.get('is_host'):
            dialogue_lines.append(f"【主持人】: {text}")
        else:
            dialogue_lines.append(f"{speaker}: {text}")
    return "\n".join(dialogue_lines)

# --- MODIFIED FUNCTION ---
def get_all_player_roles(metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Creates a mapping of player ID to their real role.
    **This version explicitly filters out the 'host'.**
    """
    user_aliases = metadata.get('user_aliases', {})
    real_roles = metadata.get('real_role', {})
    player_roles = {}
    for speaker_key, role in real_roles.items():
        # FIX 1: Explicitly skip if the role is 'host'.
        if role == 'host':
            continue
        if speaker_key in user_aliases and user_aliases[speaker_key]:
            player_id = user_aliases[speaker_key][0]
            player_roles[player_id] = role
    return player_roles

def get_wolf_teammates(all_roles: Dict[str, str]) -> List[str]:
    """Returns a list of all players who are werewolves."""
    return [player_id for player_id, role in all_roles.items() if role == "狼人"]


# --- Core Test Logic for a Single File ---
def run_role_prediction_test_for_file(filepath: str) -> Tuple[int, int]:
    """
    Executes the role prediction test for a single JSON file, maintaining conversational context.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading '{filepath}': {e}")
        return 0, 0

    all_utterances = data.get('utterances', [])
    if not any(u.get('status') == 'third_day' for u in all_utterances):
        logger.info(f"Skipping '{filepath}': No 'third_day' status found.")
        return 0, 0
        
    metadata = data.get('metadata', {})
    
    last_third_day_index = -1
    for i, u in enumerate(all_utterances):
        if u.get('status') == 'third_day':
            last_third_day_index = i
    relevant_utterances = all_utterances[:last_third_day_index + 1]
    dialogue_history = format_dialogue(relevant_utterances)

    correct_roles = get_all_player_roles(metadata)
    mvp_player_id = metadata.get('MVP', {}).get('id')
    
    if not correct_roles or not mvp_player_id or mvp_player_id not in correct_roles:
        logger.warning(f"Essential data (roles/MVP) missing or invalid in '{filepath}'. Skipping.")
        return 0, 0
        
    global_info = f"游戏全局信息:\n- 规则: {metadata.get('game_rules', 'N/A')}\n- 角色: {', '.join(metadata.get('game_roles', []))}"
    
    mvp_real_role = correct_roles[mvp_player_id]

    # --- MODIFIED LINE ---
    # FIX 2: Make the sorting key more robust.
    # It attempts to find a number. If found, it uses it for sorting.
    # If not found (e.g., for a malformed key), it treats it as 0 to prevent crashing.
    def sort_key(player_id_str):
        match = re.search(r'\d+', player_id_str)
        return int(match.group()) if match else 0

    all_player_ids = sorted(correct_roles.keys(), key=sort_key)

    players_to_ask_about = []
    if mvp_real_role == "狼人" or mvp_real_role == "白狼王":
        wolf_team = get_wolf_teammates(correct_roles)
        players_to_ask_about = [pid for pid in all_player_ids if pid not in wolf_team]
    else:
        players_to_ask_about = [pid for pid in all_player_ids if pid != mvp_player_id]

    if not players_to_ask_about:
        logger.warning(f"No players to test for in '{filepath}'. Skipping.")
        return 0, 0

    # MODIFICATION 1: Enhanced system prompt for stricter output format
    messages = [
        {"role": "system", "content": "你是一位狼人杀游戏分析专家。你的任务是根据提供的游戏信息和对话，精准地分析玩家身份。在回答问题时，你的输出必须严格遵循“X号:身份”的格式，例如“7号:狼人”。不要添加任何额外的解释、思考过程或无关文字。"},
        {"role": "user", "content": f"{global_info}\n\n---\n对话记录:\n{dialogue_history}"}
    ]
    
    correct_predictions = 0
    total_players_tested = len(players_to_ask_about)
    logger.info(f"--- Testing Role Prediction for {os.path.basename(filepath)} ---")
    logger.info(f"MVP: {mvp_player_id} ({mvp_real_role}). Testing {total_players_tested} players.")
    
    for player_id_to_guess in players_to_ask_about:
        logger.info(f"\n--- Asking for {player_id_to_guess}'s role ---")
        # MODIFICATION 1: Reinforced user question for stricter output format
        question = f'根据以上全部信息，猜测{player_id_to_guess}的真实身份。记住，你的回答必须且只能是“{player_id_to_guess}:[真实身份]”这一种格式。'
        messages.append({"role": "user", "content": question})
        model_raw_response = call_gpt5_chat_api(messages)
        messages.append({"role": "assistant", "content": model_raw_response})

        _, predicted_role = parse_model_role_response(model_raw_response)
        actual_role = correct_roles.get(player_id_to_guess, "Unknown")
        
        if predicted_role and predicted_role == actual_role:
            correct_predictions += 1
            logger.info(f"Result: CORRECT (Model: {predicted_role}, Correct: {actual_role})")
        elif predicted_role:
            logger.info(f"Result: WRONG (Model: {predicted_role}, Correct: {actual_role})")
        else:
            logger.warning(f"Result: FORMAT ERROR (Could not parse: '{model_raw_response}')")

    if total_players_tested > 0:
        accuracy = (correct_predictions / total_players_tested) * 100
        logger.info(f"\n--- Summary for {os.path.basename(filepath)} ---")
        logger.info(f"Accuracy: {accuracy:.2f}% ({correct_predictions}/{total_players_tested})")
    
    return correct_predictions, total_players_tested


# --- Main Batch Processing Execution ---
if __name__ == "__main__":
    total_correct_all_files = 0
    total_tested_all_files = 0
    
    for i in range(1, 28):
        filename = f"{i:02d}.json"
        filepath = os.path.join(os.getcwd(), filename)

        if os.path.exists(filepath):
            logger.info(f"\n{'='*60}\n--- PROCESSING FILE: {filename} ---\n{'='*60}")
            correct, total = run_role_prediction_test_for_file(filepath)
            total_correct_all_files += correct
            total_tested_all_files += total
        else:
            logger.warning(f"\n--- SKIPPING: File {filename} not found. ---")
            
    logger.info(f"\n{'='*60}\n--- OVERALL BATCH TEST SUMMARY ---\n{'='*60}")
    
    if total_tested_all_files > 0:
        overall_accuracy = (total_correct_all_files / total_tested_all_files) * 100
        logger.info(f"Total Players Tested Across All Files: {total_tested_all_files}")
        logger.info(f"Total Correct Predictions: {total_correct_all_files}")
        logger.info(f"Overall Average Accuracy: {overall_accuracy:.2f}%")
    else:
        logger.info("No players were tested across all valid files.")

    logger.info(f"\nAll tests complete. Full output saved to {log_file}")