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

NUM_PARALLEL = 64
DEEPSEEK_ENDPOINT_ID = "deepseek-r1-250120" 
DOUBAO_ENDPOINT_ID = "doubao-1-5-pro-256k-250115"
DOUBAO_THINKING_ENDPOINT_ID = "doubao-1-5-thinking-pro-250415"
RESULT_DIR = "/data1/lz/loop_QA/test1"
NUM_STUDENT_LOOPS = 5

"""
    # 1. 创建一个 Agent 实例
    my_agent = ArkAgent(model_id=MODEL_ENDPOINT_ID, system_prompt="你是一个乐于助人的代码助手。")

    # 2. 测试标准（非流式）请求
    print("\n--- 测试标准请求 ---")
    prompt1 = "你好，请用 Python 写一个快速排序算法。"
    response1 = my_agent.run(prompt1)
    print(f"Agent 返回 (标准): {response1}") # run 方法内部已经打印
"""

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


def student_task(current_result_dir: str, now_answer: str):
    source_file_path = f"{current_result_dir}/relation_response.json"
    output_file_path = f"{current_result_dir}/student_loop.json"

    all_answers = []

    # 读取包含问题的JSON文件
    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
            print(f"成功读取 {len(questions_data)} 个问题，来源: {source_file_path}")
    except FileNotFoundError:
        # # read txt file
        # with open(source_file_path.replace('.json', '.txt'), 'r', encoding='utf-8') as f:
        #     lines = f.readlines()
        #     questions_data = [{"question_text": line.strip()} for line in lines if line.strip()]
        #     print(f"成功读取 {len(questions_data)} 个问题，来源: {source_file_path}")
        txt_file_path = source_file_path.replace('.json', '.txt')
        
        try:
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                json_string = f.read()
                questions_data = refindoll_str(json_string)
                print(f"成功从TXT文件读取并解析了 {len(questions_data)} 个问题，来源: {txt_file_path}")
        except:
            print(f"错误: 无法读取或解析输入文件 {source_file_path} 或 {txt_file_path}")
            questions_data = []
            
    except json.JSONDecodeError:
        print(f"错误: 无法解析JSON文件 {source_file_path}")
        questions_data = [] # Assign empty list to prevent crash


    # 循环处理每一个问题
    for i, item in enumerate(questions_data):
        if "question_text" in item:
            question = item["question_text"]
            print(f"\n--- [问题 {i+1}/{len(questions_data)}] ---")
            print(f"正在作答: {question}")
            
            # 为当前问题创建prompt并运行agent
            # 循环三次response，并且都存储起来
            # 这里的 student_user_prompt 是一个字符串，包含了问题
            
            for attempt in range(NUM_STUDENT_LOOPS):
                student_agent = init_agent("student_prompt", is_student=1)
                student_user_prompt = query_prompt("student_prompt", prompt1=question)
                student_response = student_agent.run(student_user_prompt)
                
                check_agent = init_agent("check_prompt")
                check_user_prompt = query_prompt("check_prompt", prompt1=now_answer, prompt2=student_response)
                check_response = check_agent.run(check_user_prompt)
                # 存储每次的答案 answer 1， answer 2， answer 3，到all_answers中
                # 格式为
                """
                ({
                    "question_text": question,
                    "answer1": student_response1,
                    "answer2": student_response2,
                    "answer3": student_response3,
                    ....
                    "check_result1": check_response1,
                    "check_result2": check_response2,
                    "check_result3": check_response3,
                    ...
                })
                """
                # 需要根据 NUM_STUDENT_LOOPS 来动态生成 answer 字段
                if attempt == 0:
                    # 如果是第一个问题，初始化字典
                    all_answers.append({
                        "question_text": question,
                        "answer1": student_response,
                        "check_result1": check_response
                    })
                else:
                    # 如果不是第一个问题，更新字典
                    all_answers[-1][f"answer{attempt + 1}"] = student_response
                    all_answers[-1][f"check_result{attempt + 1}"] = check_response
                
            # student_user_prompt = query_prompt("student_prompt", prompt1=question)
            # student_response = student_agent.run(student_user_prompt)
            # print(f"Agent 返回的答案: {student_response}")
            
            # # 将问题和答案配对，存入结果列表
            # all_answers.append({
            #     "question_text": question,
            #     "answer": student_response
            # })

    # 将所有结果一次性写入新的JSON文件
    if all_answers:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 使用 json.dump 来美化输出 (indent=2)
            json.dump(all_answers, f, ensure_ascii=False, indent=2)
        print(f"\n--- ✅ 全部作答完毕 ---")
        print(f"所有结果已保存至: {output_file_path}")
    else:
        print("\n--- ⚠️ 未处理任何问题 ---")

def main():
    # test
    # process_single("Iron Gwazi")
    answer = get_key_from_file(file_path = "/data1/lz/loop_QA/dataset/random_entries_sample.txt")
    with ThreadPoolExecutor(max_workers=NUM_PARALLEL) as pool:
        list(pool.map(process_single, answer))
      
def process_single(now_answer: str):
    sanitized_answer_name = now_answer.replace(" ", "_").lower()
    current_result_dir = os.path.join(RESULT_DIR, sanitized_answer_name)

    # 用 agent 检查文件中的问题和答案是否正确
    # now_answer 是真实答案，question_text 是问题，answer是模型做出来的答案，需要检查now_answer的语义和answer的语义是否一致
    # 一个 json 中，有多个问题和答案对
    output_file_path = f"{current_result_dir}/student_loop.json"

    # 如果output_file_path存在，就return
    # if os.path.exists(output_file_path):
    #     print(f"--- ✅ 已存在检查结果文件: {output_file_path}，跳过检查 ---")
    #     return
    
    student_task(current_result_dir, now_answer)

if __name__ == "__main__":
    main()