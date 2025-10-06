import json
import re
import os
import logging
from typing import Dict, Any, List, Tuple

# --- Import and Configure OpenAI ---
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# 1. Load .env file variables
load_dotenv()

# 2. Get API key and initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("FATAL: OPENAI_API_KEY not found. Ensure your .env file is correct.")
    exit()

client = OpenAI(api_key="API_KEY",base_url="https://one-api.bltcy.top/v1/")

# 3. Configure logging to output to both console and file
log_file = 'vote_prediction_output_context_MODEL_NAME.txt'
# Clear the log file at the start of the run
if os.path.exists(log_file):
    os.remove(log_file)
    
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', # Keep the output clean
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler() # This will print to console
    ]
)
logger = logging.getLogger(__name__)


# --- Real API Call Module ---
def call_gpt5_api(prompt: str) -> str:
    """
    Calls the OpenAI API with the given prompt.
    """
    logger.info("--- Calling OpenAI API... ---")
    chat_completion = client.chat.completions.create(
        model="MODEL_NAME",
        messages=[{"role": "user", "content": prompt}],
    )

    logger.info(f"--- API Response: {chat_completion.choices[0].message.content} ---")
    return chat_completion.choices[0].message.content

# --- Helper Functions ---
def parse_model_response(response: str) -> str:
    """
    Parses the player number from the model's response.
    It first removes any content within <think>...</think> tags.
    """
    if response is None:
        return ""

    # Step 1: Remove the <think>...</think> block using regex.
    # The re.DOTALL flag allows '.' to match newline characters, handling multi-line thoughts.
    cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    
    # Step 2: Use the existing regex to find the player number in the cleaned string.
    match = re.search(r'(\d{1,2})号', cleaned_response)
    
    return match.group(0) if match else None

def format_dialogue(utterances: List[Dict[str, Any]], mvp_player_id: str) -> str:
    """Formats dialogue history into a readable string."""
    dialogue_lines = []
    for u in utterances:
        speaker = u.get("speaker_id", "Unknown Speaker")
        text = u.get("text", "")
        if u.get('is_host'):
            dialogue_lines.append(f"【Host】: {text}")
        elif speaker == mvp_player_id:
            dialogue_lines.append(f"{speaker}: N/A")
        else:
            dialogue_lines.append(f"{speaker}: {text}")
    return "\n".join(dialogue_lines)

def get_player_role(player_id: str, metadata: Dict[str, Any]) -> str:
    """
    Finds the real role of a player using their ID by cross-referencing
    user_aliases and real_role dictionaries in the metadata.
    """
    user_aliases = metadata.get('user_aliases')
    real_roles = metadata.get('real_role')

    if not user_aliases or not real_roles:
        return None

    # Find the internal speaker key (e.g., "说话人 1") for the given player_id (e.g., "12号")
    speaker_key = None
    for key, aliases in user_aliases.items():
        if player_id in aliases:
            speaker_key = key
            break
    
    # Use the speaker key to find the role in the real_role dictionary
    if speaker_key and speaker_key in real_roles:
        return real_roles[speaker_key]
        
    return None

# --- Core Test Logic for a Single File ---
def run_test_for_file(filepath: str) -> Tuple[int, int]:
    """
    Executes the inference test for a single JSON file and returns its score.
    Returns: A tuple of (correct_count, total_votes).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: File '{filepath}' not found.")
        return 0, 0
    except json.JSONDecodeError:
        logger.error(f"Error: File '{filepath}' is not a valid JSON.")
        return 0, 0

    metadata = data.get('metadata', {})
    all_utterances = data.get('utterances', [])
    
    mvp_player_id = metadata.get('MVP', {}).get('id')
    votes_to_test = metadata.get('MVP', {}).get('votes', {})

    if not mvp_player_id or not votes_to_test:
        logger.warning(f"No valid MVP or votes data in '{filepath}'. Skipping MVP tests for this file.")
        return 0, 0
    
    global_info = f"""
Game Global Info:
- Rules: {metadata.get('game_rules', 'N/A')}
- Roles: {', '.join(metadata.get('game_roles', []))}
- Language: {metadata.get('language', 'N/A')}
"""
    
    correct_count = 0
    total_votes = len(votes_to_test)
    
    logger.info(f"Testing MVP: {mvp_player_id}")

    for vote_name, vote_info in votes_to_test.items():
        logger.info(f"--- Running Test Case: {vote_name} ---")
        
        correct_answer = vote_info['vote_to']
        cut_off_id = vote_info['cut_off_time']
        
        relevant_utterances = [
            u for u in all_utterances if any(uid <= cut_off_id for uid in u.get('utterance_id', []))
        ]
        
        dialogue_history = format_dialogue(relevant_utterances, mvp_player_id)

        mvp_real_role = get_player_role(mvp_player_id, metadata)
        logger.info(f"Testing MVP: {mvp_player_id} (Role: {mvp_real_role or 'Unknown'})")
        if mvp_real_role:
            question_line = f"Question: You are player {mvp_player_id} and your true identity is {mvp_real_role}. You are about to vote to eliminate a player. Who do you vote for?"
        else:
            # Fallback if the role couldn't be found
            question_line = f"Question: You are player {mvp_player_id}. You are about to vote to eliminate a player. Who do you vote for?"
            logger.warning(f"Could not find the real role for MVP {mvp_player_id} in {filepath}.")

        prompt = f"""{global_info}
---
Dialogue History So Far(substitute N/A for your own lines):
{dialogue_history}
---
{question_line}
---
**IMPORTANT**: Respond in the format 'X号' where X is the player number you choose to vote for. Only provide the answer in this format without any additional text or explanation.
"""
        
        model_raw_response = call_gpt5_api(prompt)
        model_answer = parse_model_response(model_raw_response)
        
        if model_answer:
            if model_answer == correct_answer:
                correct_count += 1
                logger.info(f"Result: CORRECT (Model: {model_answer}, Correct: {correct_answer})\n")
            else:
                logger.info(f"Result: WRONG (Model: {model_answer}, Correct: {correct_answer})\n")
        else:
            logger.warning(f"Result: FORMAT ERROR (Could not parse: '{model_raw_response}')\n")

    if total_votes > 0:
        accuracy = (correct_count / total_votes) * 100
        logger.info(f"Accuracy for {filepath}: {accuracy:.2f}% ({correct_count}/{total_votes})")
    
    return correct_count, total_votes

# --- Main Batch Processing Execution ---
if __name__ == "__main__":
    total_correct_all_files = 0
    total_votes_all_files = 0
    
    # Loop from 1 to 27 to generate filenames like "01.json", "02.json", etc.
    for i in range(1, 28):
        filename = f"{i:02d}.json"
        filepath = os.path.join(os.getcwd(), filename)

        if os.path.exists(filepath):
            logger.info(f"\n{'='*60}\n--- PROCESSING FILE: {filename} ---\n{'='*60}")
            correct, total = run_test_for_file(filepath)
            total_correct_all_files += correct
            total_votes_all_files += total
        else:
            logger.warning(f"\n--- SKIPPING: File {filename} not found. ---")
            
    # Calculate and log the final overall summary
    logger.info(f"\n{'='*60}\n--- BATCH TEST SUMMARY ---\n{'='*60}")
    
    if total_votes_all_files > 0:
        overall_accuracy = (total_correct_all_files / total_votes_all_files) * 100
        logger.info(f"Total Correct Votes: {total_correct_all_files}")
        logger.info(f"Total Votes Tested: {total_votes_all_files}")
        logger.info(f"Overall Accuracy Across All Files: {overall_accuracy:.2f}%")
    else:
        logger.info("No votes were tested across all files.")

    logger.info(f"\nAll tests complete. Full output saved to {log_file}")