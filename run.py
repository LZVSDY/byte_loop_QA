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
QUESTION_INDEX_FILE = "/data1/lz/loop_QA/questions_to_answer.txt" # 假设您的索引文件叫这个名字

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
    sumary_user_prompt = query_prompt("summary_prompt", prompt1 = read_wiki_summary, prompt2=str(loop_id))
    sumary_response = sumary_agent.run(sumary_user_prompt)
    
    # save the summary response for the loop
    # sumary_response = filter_keywords(sumary_response)
    save_string_as_json(sumary_response, f"/data1/lz/loop_QA/result/summary_response_{loop_id}.json")
    
    return sumary_response

def init_agent(choose_prompt: str = "system_prompt") -> ArkAgent:
    """
    Initialize the agent with the system prompt.
    """
    system_prompt = get_system_prompt(choose_prompt)
    return ArkAgent(model_id=MODEL_ENDPOINT_ID, system_prompt=system_prompt)

if __name__ == "__main__":
    # read_answer = get_key_from_file()
    read_answer = "Python program"
    read_wiki_summary = search_wikipedia(read_answer, num_results=NUM_RESULTS, language=LANGUAGE, loop_id = 1) # read_wiki_summary = ['Python is a high-level, general-purpose programming language.'], NUM_RESULTS = 1, LANGUAGE = 'en'
    
    tmp_read_answer = read_answer
    tmp_read_wiki_summary = read_wiki_summary
    # tmp_read_answer = "Python program"
    # tmp_read_wiki_summary = ['Python is a high-level, general-purpose programming language.']    
    
    for i in range(NUM_LOOPS):
        print(f"Loop {i+1}/{NUM_LOOPS}")
        
        loop_over_prompts(tmp_read_answer, tmp_read_wiki_summary, i + 1)
        
        if i == NUM_LOOPS - 1:
            break
        
        # 在每次循环中，根据/data1/lz/loop_QA/result/summary_response_{i}.json，再次调用 search_wikipedia，生成 tmp_read_wiki_summary
        print(f"\n--- 准备第 {i+1} 轮循环的输入 ---")
        
        # 2.1. 定义刚刚生成的 summary 文件路径
        summary_file_path = os.path.join(RESULT_DIR, f"summary_response_{i + 1}.json")
        
        # 2.2. 从该文件中提取所有关键词
        new_keywords = get_keywords_from_summary(summary_file_path)
        
        if not new_keywords:
            print("🔴 错误: 未能从 summary 文件中提取到任何关键词，无法进行下一次搜索。循环终止。")
            break
            
        print(f"从 summary_response_{i}.json 中提取到 {len(new_keywords)} 个新关键词: {new_keywords}")
        
        # 2.3. 使用提取出的关键词进行新的维基百科搜索
        all_new_summaries = [] # 创建一个空列表，用于收集所有新的摘要
        print("--- 针对每个关键词进行独立的维基百科搜索 ---")
        for keyword in new_keywords:
            print(f"正在搜索关键词: '{keyword}'")
            # 为当前关键词搜索维基百科
            # 注意：search_wikipedia 本身返回的是一个列表
            individual_summary_list = search_wikipedia(keyword, num_results=1, language=LANGUAGE, loop_id=i + 2)
            
            if individual_summary_list:
                # 将本次搜索到的摘要（列表）合并到总的摘要列表（all_new_summaries）中
                all_new_summaries.extend(individual_summary_list)
                print(f"  -> 成功获取摘要: '{individual_summary_list[0][:50]}...'")
            else:
                print(f"  -> 未能获取到 '{keyword}' 的摘要。")
            
            # 暂停一下，避免对API的请求过于频繁
            time.sleep(1) 
        
        tmp_read_wiki_summary = all_new_summaries

    relation_agent = init_agent("relation_prompt")
    relation_user_prompt = query_prompt("relation_prompt", prompt1 = read_answer, prompt2 = sumary_response)
    relation_response = relation_agent.run(relation_user_prompt)
    
    # save the relation response for the loop
    save_string_as_json(relation_response, f"/data1/lz/loop_QA/result/relation_response.json")
    

    print("\n--- 启动 Student Agent 进行最终解答 ---")