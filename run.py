import os
import json
import time
from utils.agent import ArkAgent
from utils.wiki import search_wikipedia
from utils.utils import get_system_prompt, query_prompt, filter_keywords, \
    save_string_as_json, load_question_indices, prepare_student_task, get_keywords_from_summary

NUM_LOOPS = 2
NUM_RESULTS = 3
MODEL_ENDPOINT_ID = "doubao-1-5-pro-256k-250115" 
LANGUAGE = "en"
RESULT_DIR = "/data1/lz/loop_QA/result"

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
    
    # save the summary response for the loop
    # sumary_response = filter_keywords(sumary_response)
    save_string_as_json(sumary_response, f"{RESULT_DIR}/summary_response_{loop_id}.json")
    
    return sumary_response

def init_agent(choose_prompt: str = "system_prompt") -> ArkAgent:
    """
    Initialize the agent with the system prompt.
    """
    system_prompt = get_system_prompt(choose_prompt)
    return ArkAgent(model_id=MODEL_ENDPOINT_ID, system_prompt=system_prompt)

def get_pair_of_keyworks_wiki_summary(query: str, loop_id: int) -> tuple[str, list[str]]:
    """
    Get a pair of keywords and their corresponding Wikipedia summary.
    
    Args:
        query (str): The query to search for.
        
    Returns:
        tuple: A tuple containing the query and a list of Wikipedia summaries.
    """
    wiki_summary = search_wikipedia(query, num_results=NUM_RESULTS, language=LANGUAGE, loop_id=loop_id)
    return query, wiki_summary


if __name__ == "__main__":
    # read_answer = get_key_from_file()
    answer = ["Python program"]
    
    for now_answer in answer:
        answer_all = [answer_all]
        for i in range(NUM_LOOPS):
            print(f"Loop {i+1}/{NUM_LOOPS}")
            
            for answer_raw in answer_all:
                query, wiki_summary = get_pair_of_keyworks_wiki_summary(answer_raw, loop_id=i + 1)
                loop_over_prompts(query, wiki_summary, i + 1)
            
            if i == NUM_LOOPS - 1:
                break
            
            # 在每次循环中，根据{RESULT_DIR}/summary_response_{i}.json，再次调用 search_wikipedia，生成 tmp_read_wiki_summary
            print(f"\n--- 准备第 {i+1} 轮循环的输入 ---")
            
            summary_file_path = os.path.join(RESULT_DIR, f"summary_response_{i + 1}.json")
            new_keywords = get_keywords_from_summary(summary_file_path)
            
            if not new_keywords:
                print("🔴 错误: 未能从 summary 文件中提取到任何关键词，无法进行下一次搜索。循环终止。")
                break
                
            print(f"从 summary_response_{i}.json 中提取到 {len(new_keywords)} 个新关键词: {new_keywords}")
            
            answer_all = new_keywords
            time.sleep(1)

        sumary_all_response = []
        # 3.1. 读取所有 summary_response_{i}.json 文件，并将其内容合并到 sumary_all_response 列表中
        for i in range(NUM_LOOPS):
            summary_file_path = os.path.join(RESULT_DIR, f"summary_response_{i + 1}.json")
            if os.path.exists(summary_file_path):
                with open(summary_file_path, 'r') as file:
                    summary_data = json.load(file)
                    sumary_all_response.append(summary_data)
            summary_all_response_str = json.dumps(sumary_all_response, indent=2, ensure_ascii=False)

        relation_agent = init_agent("relation_prompt")
        relation_user_prompt = query_prompt("relation_prompt", prompt1 = now_answer, prompt2 = summary_all_response_str)
        relation_response = relation_agent.run(relation_user_prompt)
        
        # save the relation response for the loop
        save_string_as_json(relation_response, f"{RESULT_DIR}/relation_response.json")

        print("\n--- 启动 Student Agent 进行最终解答 ---")
        student_agent = init_agent("student_prompt")
        student_user_prompt = query_prompt("student_prompt", prompt1 = relation_response)
        student_response = student_agent.run(student_user_prompt)
        print(f"Student Agent 返回: {student_response}")
        save_string_as_json(student_response, f"{RESULT_DIR}/student_response.json")