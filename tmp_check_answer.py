import os
import json
import time
import shutil
import re
from concurrent.futures import ThreadPoolExecutor
from utils.agent import ArkAgent
from utils.wiki import search_wikipedia
from utils.utils import get_system_prompt, query_prompt, \
    save_string_as_json, save_list_as_json, \
    get_key_from_file, get_keywords_from_summary

from wikipedia import add_subscription

NUM_LOOPS = 2
NUM_RESULTS = 3
NUM_PARALLEL = 64
DEEPSEEK_ENDPOINT_ID = "deepseek-r1-250120" 
DOUBAO_ENDPOINT_ID = "doubao-1-5-pro-256k-250115"
DOUBAO_THINKING_ENDPOINT_ID = "doubao-1-5-thinking-pro-250415"
LANGUAGE = "en"
RESULT_DIR = "/data1/lz/loop_QA/test1"

"""
    # 1. 创建一个 Agent 实例
    my_agent = ArkAgent(model_id=MODEL_ENDPOINT_ID, system_prompt="你是一个乐于助人的代码助手。")

    # 2. 测试标准（非流式）请求
    print("\n--- 测试标准请求 ---")
    prompt1 = "你好，请用 Python 写一个快速排序算法。"
    response1 = my_agent.run(prompt1)
    print(f"Agent 返回 (标准): {response1}") # run 方法内部已经打印
"""

def loop_over_prompts(read_answer: str, read_wiki_summary: str, loop_id : int) -> str:
    sumary_agent = init_agent("summary_prompt")
    sumary_user_prompt = query_prompt("summary_prompt", prompt1 = read_wiki_summary, prompt2=loop_id, prompt3=read_answer)
    sumary_response = sumary_agent.run(sumary_user_prompt)
    
    ### 如果sumary_response 是一个字符串，且开头为 ```json, 就手动去掉
    if isinstance(sumary_response, str) and sumary_response.startswith("```json"):
        sumary_response = sumary_response[8:].strip()  # 去掉开头的 ```json 和换行符
        sumary_response = sumary_response.rstrip("```")  # 去掉结尾的 ```
        
    return sumary_response

def init_agent(choose_prompt: str = "system_prompt", is_student: int = 0) -> ArkAgent:
    """
    Initialize the agent with the system prompt.
    """
    system_prompt = get_system_prompt(choose_prompt)
    if is_student:
        return ArkAgent(model_id=DOUBAO_THINKING_ENDPOINT_ID, system_prompt=system_prompt,
            api_key_env_var = "75a7a2b3-c147-4005-8c14-45a65fe2da90")
    else:
        return ArkAgent(model_id=DEEPSEEK_ENDPOINT_ID, system_prompt=system_prompt,
            api_key_env_var = "6d6f26d9-4bad-4280-8972-347815f959b2")

def refindoll_str(json_string: str) -> list[str]:
    regex_pattern = r'"question_text"\s*:\s*"(.*?)"'

    # 使用 re.findall 寻找所有匹配项
    # 它会返回一个列表，其中只包含捕获组(括号里的部分)的内容
    extracted_questions = re.findall(regex_pattern, json_string, flags=re.DOTALL)

    all_questions = []
    
    # 打印结果
    print("--- 使用正则表达式提取的结果 ---\n")
    if extracted_questions:
        for i, question in enumerate(extracted_questions):
            # print(f"question_text: {question}\n")
            all_questions.append({"question_text": question})
    else:
        print("没有找到匹配 'question_text' 的内容。")
    
    return all_questions

def main():
    answer = get_key_from_file()
    with ThreadPoolExecutor(max_workers=NUM_PARALLEL) as pool:
        list(pool.map(process_single, answer))
      
def process_single(now_answer: str):
    sanitized_answer_name = now_answer.replace(" ", "_").lower()
    current_result_dir = os.path.join(RESULT_DIR, sanitized_answer_name)
    # 读取 current_result_dir 下的 student_answers.json 文件
    # 格式如下
    """
    [
    {
        "question_text": "Which animated TV special from a popular children's series features characters celebrating a Jewish holiday involving an eight-day candle lighting tradition, while indirectly referencing an ancient rebellion against foreign cultural influence?",
        "answer": "\n\nA Charlie Brown Chanukah"
    },
    {
        "question_text": "What holiday-themed episode of a 90s cartoon depicts the miracle of oil lasting eight nights, while making subtle connections to a historical victory documented in ancient Hebrew texts?",
        "answer": "\n\nThe Simpsons' \"Chanukah Story\""
    },
    {
        "question_text": "In what Nickelodeon production do animated babies interact with a nine-branched candelabrum while their story parallels events from a 2nd century BCE conflict in the Eastern Mediterranean?",
        "answer": "\n\nRugrats"
    }
    ]
    """
    # 用 agent 检查文件中的问题和答案是否正确
    # now_answer 是真实答案，question_text 是问题，answer是模型做出来的答案，需要检查now_answer的语义和answer的语义是否一致
    # 一个 json 中，有多个问题和答案对
    source_file_path = f"{current_result_dir}/student_loop.json"
    output_file_path = f"{current_result_dir}/student_answers_checked.json"
    
    # 如果 source_file_path 不存在，直接返回
    if not os.path.exists(source_file_path):
        print(f"--- ⚠️ {now_answer} 的检查源文件不存在: {source_file_path} ---")
        return
    
    # 如果output_file_path存在，就return
    if os.path.exists(output_file_path):
        print(f"--- ✅ 已存在检查结果文件: {output_file_path}，跳过检查 ---")
        return
    
    check_agent = init_agent("check_prompt", is_student=1)
    
    # 循环读取 question_text 和 answer
    with open(source_file_path, "r") as f:
        student_answers = json.load(f)
    # 循环处理每一个问题和答案，用 check_agent 检查
    all_answers = []
    for i, item in enumerate(student_answers):
        if "question_text" in item and "answer1" in item:
            question = item["question_text"]
            answer_list = []
            answer1 = item["answer1"]
            answer2 = item["answer2"]
            answer3 = item["answer3"]
            answer_list.append(answer1)
            answer_list.append(answer2)
            answer_list.append(answer3)
            # print(f"\n--- [问题 {i+1}/{len(student_answers)}] ---")
            # print(f"正在检查: {question}")
            # print(f"模型答案: {answer}")
            
            check_response_list = []
            
            # 为当前问题创建prompt并运行agent
            for attempt, answer in enumerate(answer_list):
                check_user_prompt = query_prompt("check_prompt", prompt1=now_answer, prompt2=answer)
                check_response = check_agent.run(check_user_prompt)
                check_response_list.append(check_response)
                
            # print(f"Agent 返回的检查结果: {check_response}")
            
            # 将问题和答案配对，存入结果列表
            all_answers.append({
                "question_text": question,
                "answer1": answer_list[0],
                "answer2": answer_list[1],
                "answer3": answer_list[2],
                "check_result1": check_response_list[0],
                "check_result2": check_response_list[1],
                "check_result3": check_response_list[2]
            })
    # 将所有结果一次性写入新的JSON文件
    if all_answers:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 使用 json.dump 来美化输出 (indent=2)
            json.dump(all_answers, f, ensure_ascii=False, indent=2)
        print(f"\n--- ✅ {now_answer} 全部检查完毕 ---")
    else:
        print(f"\n--- ⚠️ {now_answer} 未处理任何问题 ---")

if __name__ == "__main__":
    main()