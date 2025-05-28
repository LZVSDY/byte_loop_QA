import os
import json
from utils.agent import ArkAgent
from utils.wiki import search_wikipedia
from utils.utils import get_system_prompt, query_prompt, get_key_from_file, filter_keywords, save_string_as_json

NUM_LOOPS = 3
NUM_RESULTS = 3
MODEL_ENDPOINT_ID = "doubao-1-5-pro-256k-250115" 
LANGUAGE = "en"

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
    check_suit_agent = init_agent("check_suit_prompt")
    check_suit_user_prompt = query_prompt("check_suit_prompt", prompt1 = read_answer, prompt2 = read_wiki_summary) # "你是一个严谨的内容匹配分析师。你的任务是判断下面提供的 [维基百科摘要] 是否与给定的 [关键词] 紧密相关且内容有效。\n\n所谓“有效”指的是，摘要内容不是错误页面、消歧义页或空洞无物的描述。\n\n如果内容相关且有效，请只回答 'yes'。\n如果内容不相关或无效，请只回答 'no'。\n\n不要添加任何其他解释或文字。\n\n---\n\n[关键词]:\nPython program\n\n[维基百科摘要]:\nPython is a high-level, general-purpose programming language."
    check_suit_response = check_suit_agent.run(check_suit_user_prompt)
    
    if check_suit_response == "no":
        return None
    
    sumary_agent = init_agent("summary_prompt")
    sumary_user_prompt = query_prompt("summary_prompt", prompt1 = read_wiki_summary)
    sumary_response = sumary_agent.run(sumary_user_prompt)
    
    # save the summary response for the loop
    sumary_response = filter_keywords(sumary_response)
    save_string_as_json(sumary_response, f"/data1/lz/langchain/result/summary_response_{loop_id}.json")
    
    
    # print(sumary_response)
        
    # branch_agent1 = init_agent("branch_prompt1")
    # branch_agent2 = init_agent("branch_prompt2")
    # branch_user_prompt1 = query_prompt("branch_prompt1", prompt1 = sumary_response)
    # branch_user_prompt2 = query_prompt("branch_prompt2", prompt1 = sumary_response)
    # branch_response1 = branch_agent1.run(branch_user_prompt1)
    # branch_response2 = branch_agent2.run(branch_user_prompt2)
    
    relation_agent = init_agent("relation_prompt")
    relation_user_prompt = query_prompt("relation_prompt", prompt1 = read_answer, prompt2 = sumary_response)
    relation_response = relation_agent.run(relation_user_prompt)
    
    # save the relation response for the loop
    save_string_as_json(relation_response, f"/data1/lz/langchain/result/relation_response_{loop_id}.json")
    
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
    read_wiki_summary = search_wikipedia(read_answer, num_results=NUM_RESULTS, language=LANGUAGE) # read_wiki_summary = ['Python is a high-level, general-purpose programming language.'], NUM_RESULTS = 1, LANGUAGE = 'en'
    
    tmp_read_answer = read_answer
    tmp_read_wiki_summary = read_wiki_summary
    # tmp_read_answer = "Python program"
    # tmp_read_wiki_summary = ['Python is a high-level, general-purpose programming language.']    
    
    for i in range(NUM_LOOPS):
        print(f"Loop {i+1}/{NUM_LOOPS}")
        
        read_wiki_summary_raw = loop_over_prompts(tmp_read_answer, tmp_read_wiki_summary, i)
        
        for j, summary in enumerate(read_wiki_summary_raw):
            print(f"Summary {j+1}: {summary}")
            search_wikipedia(summary, num_results=1, language=LANGUAGE)
            
            
    student_agent = init_agent("student_prompt")
    check_response = student_agent.run(tmp_read_answer, tmp_read_wiki_summary)
    
    print(f"Check Response: {check_response}")