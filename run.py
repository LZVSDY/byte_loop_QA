import os
import json
import time
import shutil
import re
from utils.agent import ArkAgent
from utils.wiki import search_wikipedia
from utils.utils import get_system_prompt, query_prompt, \
    save_string_as_json, save_list_as_json, \
    get_key_from_file, get_keywords_from_summary

NUM_LOOPS = 2
NUM_RESULTS = 5
DEEPSEEK_ENDPOINT_ID = "deepseek-r1-250120" 
DOUBAO_ENDPOINT_ID = "doubao-1-5-pro-256k-250115"
DOUBAO_THINKING_ENDPOINT_ID = "doubao-1-5-thinking-pro-250415"
LANGUAGE = "en"
RESULT_DIR = "/data1/lz/loop_QA/test"

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
        
    return sumary_response

def init_agent(choose_prompt: str = "system_prompt", is_student: int = 0) -> ArkAgent:
    """
    Initialize the agent with the system prompt.
    """
    system_prompt = get_system_prompt(choose_prompt)
    if is_student:
        return ArkAgent(model_id=DEEPSEEK_ENDPOINT_ID, system_prompt=system_prompt,
            api_key_env_var = "d6f26d9-4bad-4280-8972-347815f959b2")
    else:
        return ArkAgent(model_id=DOUBAO_ENDPOINT_ID, system_prompt=system_prompt,
            api_key_env_var = "75a7a2b3-c147-4005-8c14-45a65fe2da90")

def get_pair_of_keyworks_wiki_summary(query: str, loop_id: int, save_dir: str) -> tuple[str, list[str]]:
    """
    Get a pair of keywords and their corresponding Wikipedia summary.
    
    Args:
        query (str): The query to search for.
        
    Returns:
        tuple: A tuple containing the query and a list of Wikipedia summaries.
    """
    wiki_summary = search_wikipedia(query, num_results=NUM_RESULTS, language=LANGUAGE, loop_id=loop_id, save_dir = save_dir)
    return query, wiki_summary

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

def student_task(current_result_dir: str):
    source_file_path = f"{current_result_dir}/relation_response.json"
    output_file_path = f"{current_result_dir}/student_answers.json"

    student_agent = init_agent("student_prompt")
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
            student_user_prompt = query_prompt("student_prompt", prompt1=question)
            student_response = student_agent.run(student_user_prompt)
            print(f"Agent 返回的答案: {student_response}")
            
            # 将问题和答案配对，存入结果列表
            all_answers.append({
                "question_text": question,
                "answer": student_response
            })

    # 将所有结果一次性写入新的JSON文件
    if all_answers:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 使用 json.dump 来美化输出 (indent=2)
            json.dump(all_answers, f, ensure_ascii=False, indent=2)
        print(f"\n--- ✅ 全部作答完毕 ---")
        print(f"所有结果已保存至: {output_file_path}")
    else:
        print("\n--- ⚠️ 未处理任何问题 ---")

if __name__ == "__main__":
    answer = get_key_from_file()
    # test
    # answer = ["Python program"]
    
    for now_answer in answer:
        sanitized_answer_name = now_answer.replace(" ", "_").lower()
        current_result_dir = os.path.join(RESULT_DIR, sanitized_answer_name)
        if os.path.exists(current_result_dir):
            shutil.rmtree(current_result_dir)
        
        # Create the directory if it doesn't exist
        os.makedirs(current_result_dir, exist_ok=True)
        
        answer_all = [now_answer]
        for i in range(NUM_LOOPS):
            print(f"Loop {i+1}/{NUM_LOOPS}")
            all_summary_data = [] 
            
            for answer_raw in answer_all:
                query, wiki_summary = get_pair_of_keyworks_wiki_summary(answer_raw, loop_id=i + 1, save_dir=current_result_dir)
                summary_response = loop_over_prompts(query, wiki_summary, i + 1)
                
                # 解析字符串并收集数据
                try:
                    # 解析模型返回的JSON字符串
                    new_data = json.loads(summary_response)
                    # 如果返回的是列表，就合并列表
                    if isinstance(new_data, list):
                        all_summary_data.extend(new_data)
                    # 如果返回的是对象，就添加到列表
                    else:
                        all_summary_data.append(new_data)
                except json.JSONDecodeError:
                    print(f"❌ 警告: 在第 {i+1} 轮循环中未能解析 summary_response，已跳过。")
            
            save_list_as_json(all_summary_data, f"{current_result_dir}/summary_response_{i + 1}.json")
            
            if i == NUM_LOOPS - 1:
                break
            
            # 在每次循环中，根据{current_result_dir}/summary_response_{i}.json 文件中的内容提取关键词
            print(f"\n--- 准备第 {i+1} 轮循环的输入 ---")
            
            summary_file_path = os.path.join(current_result_dir, f"summary_response_{i + 1}.json")
            new_keywords = get_keywords_from_summary(summary_file_path)
            
            if not new_keywords:
                print("🔴 错误: 未能从 summary 文件中提取到任何关键词，无法进行下一次搜索。循环终止。")
                break
                
            print(f"从 summary_response_{i}.json 中提取到 {len(new_keywords)} 个新关键词: {new_keywords}")
            
            answer_all = new_keywords
            # time.sleep(1)

        sumary_all_response = []
        # 读取所有 summary_response_{i}.json 文件，并将其内容合并到 sumary_all_response 列表中
        for i in range(NUM_LOOPS):
            summary_file_path = os.path.join(current_result_dir, f"summary_response_{i + 1}.json")
            if os.path.exists(summary_file_path):
                with open(summary_file_path, 'r') as file:
                    summary_data = json.load(file)
                    sumary_all_response.append(summary_data)
            summary_all_response_str = json.dumps(sumary_all_response, indent=2, ensure_ascii=False)

        relation_agent = init_agent("relation_prompt")
        relation_user_prompt = query_prompt("relation_prompt", prompt1 = now_answer, prompt2 = summary_all_response_str)
        relation_response = relation_agent.run(relation_user_prompt)
        
        # save the relation response for the loop
        save_string_as_json(relation_response, f"{current_result_dir}/relation_response.json")

        print("\n--- 启动 Student Agent 进行最终解答 ---")
        student_task(current_result_dir)