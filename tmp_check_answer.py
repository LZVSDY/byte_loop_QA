# import csv
# import os
# import json
# import time
# import shutil
# import re
# from concurrent.futures import ThreadPoolExecutor
# from utils.agent import ArkAgent
# from utils.wiki import search_wikipedia
# from utils.utils import get_system_prompt, query_prompt, \
#     save_string_as_json, save_list_as_json, \
#     get_key_from_file, get_keywords_from_summary

# from wikipedia import add_subscription

# NUM_PARALLEL = 64
# DEEPSEEK_ENDPOINT_ID = "deepseek-r1-250120" 
# DOUBAO_ENDPOINT_ID = "doubao-1-5-pro-256k-250115"
# DOUBAO_THINKING_ENDPOINT_ID = "doubao-1-5-thinking-pro-250415"
# RESULT_DIR = "/data1/lz/loop_QA/test1"
# NUM_STUDENT_LOOPS = 5

# def init_agent(choose_prompt: str = "system_prompt", is_student: int = 0) -> ArkAgent:
#     """
#     Initialize the agent with the system prompt.
#     """
#     system_prompt = get_system_prompt(choose_prompt)
#     if is_student:
#         return ArkAgent(model_id=DOUBAO_THINKING_ENDPOINT_ID, system_prompt=system_prompt,
#             api_key_env_var = "75a7a2b3-c147-4005-8c14-45a65fe2da90")
#     else:
#         return ArkAgent(model_id=DEEPSEEK_ENDPOINT_ID, system_prompt=system_prompt,
#             api_key_env_var = "6d6f26d9-4bad-4280-8972-347815f959b2")

# def my_processing_logic(row):
#         """
#         示例处理函数：检查 'answer' 和 'model_answer' 是否相同。
#         你可以根据你的实际需求修改这个函数。
#         """
        
#         if row.get('answer') and row.get('model_answer') and row['\ufeffquestion']:
#             check_agent = init_agent("check_suit_prompt")
#             check_user_prompt = query_prompt("check_suit_prompt", prompt1=row.get('answer'), prompt2=row.get('model_answer'), prompt3=row['\ufeffquestion'])
#             check_response = check_agent.run(check_user_prompt)
#             return check_response

# def process_and_write_csv(input_file_path, output_file_path, new_column_name):
#     """
#     读取CSV文件，对每行数据进行处理，并添加一个新列到新的CSV文件。

#     Args:
#         input_file_path (str): 输入CSV文件的路径。
#         output_file_path (str): 输出CSV文件的路径（将创建新文件）。
#         new_column_name (str): 新增列的列名。
#         processing_function (callable): 一个函数，接受一行数据（字典形式），
#                                         返回该行的新列的值。
#     """
#     try:
#         with open(input_file_path, mode='r', encoding='utf-8') as infile, \
#              open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:

#             reader = csv.DictReader(infile)
            
#             # 获取所有现有列名
#             fieldnames = reader.fieldnames
#             if fieldnames is None:
#                 print(f"Error: Input CSV file '{input_file_path}' is empty or has no headers.")
#                 return

#             # 添加新列名到列表末尾
#             new_fieldnames = fieldnames + [new_column_name]
            
#             writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
#             writer.writeheader()  # 写入新文件的标题行

#             for row in reader:
#                 # 调用处理函数获取新列的值
#                 new_value = my_processing_logic(row)
                
#                 # 将新值添加到当前行数据中
#                 row[new_column_name] = new_value
                
#                 # 将更新后的行写入新文件
#                 writer.writerow(row)
        
#         print(f"处理完成！新结果已写入到 '{output_file_path}'。")

#     except FileNotFoundError:
#         print(f"错误：文件 '{input_file_path}' 未找到。")
#     except Exception as e:
#         print(f"发生了一个意外错误：{e}")

# if __name__ == "__main__":

#     input_csv_path = "/data1/lz/loop_QA/dataset/rl_output.csv"

#     output_csv_path = "/data1/lz/loop_QA/dataset/rl_output_lzCheck.csv"
#     new_column_name = "is_answer_correct" # 你想新增的列名

#     # 2. 定义你的处理函数
#     # 这个函数会根据 'answer' 和 'model_answer' 是否匹配来返回 'True' 或 'False'
    

#     # 3. 调用主函数进行处理
#     process_and_write_csv(input_csv_path, output_csv_path, new_column_name)

#     # 4. 可选：验证新生成的文件内容
#     print("\n新生成的文件内容（前几行）：")
#     with open(output_csv_path, 'r', encoding='utf-8') as f:
#         for i, line in enumerate(f):
#             print(line.strip())
#             if i >= 4: # 只打印前5行
#                 break

import csv
import os
import json
import time
import shutil
import re
from concurrent.futures import ThreadPoolExecutor, as_completed # 导入 as_completed
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

# my_processing_logic 将保持不变，因为它处理单行数据
def my_processing_logic(row):
    """
    示例处理函数：检查 'answer' 和 'model_answer' 是否相同。
    你可以根据你的实际需求修改这个函数。
    """

    if row.get('answer') and row.get('model_answer') and row.get('\ufeffquestion'): # 使用 .get() 避免 KeyError
        check_agent = init_agent("check_suit_prompt")
        check_user_prompt = query_prompt("check_suit_prompt", prompt1=row.get('answer'), prompt2=row.get('model_answer'), prompt3=row.get('\ufeffquestion'))
        check_response = check_agent.run(check_user_prompt)
        return check_response
    return "N/A" # 如果关键列缺失，返回默认值

def process_and_write_csv_concurrently(input_file_path, output_file_path, new_column_name):
    """
    读取CSV文件，使用线程池对每行数据进行高并发处理，并添加一个新列到新的CSV文件。

    Args:
        input_file_path (str): 输入CSV文件的路径。
        output_file_path (str): 输出CSV文件的路径（将创建新文件）。
        new_column_name (str): 新增列的列名。
    """
    try:
        # 1. 读取所有输入数据
        rows_to_process = []
        with open(input_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print(f"Error: Input CSV file '{input_file_path}' is empty or has no headers.")
                return

            # 检查必要列是否存在
            # 你的 my_processing_logic 中使用了 'answer', 'model_answer', '\ufeffquestion'
            required_cols_for_processing = ['answer', 'model_answer', '\ufeffquestion']
            if not all(col in fieldnames for col in required_cols_for_processing):
                print(f"Warning: Missing one or more required columns ({required_cols_for_processing}) in input CSV.")
                # 可以选择在这里返回或继续，但处理函数会返回 "N/A"
                
            for row in reader:
                rows_to_process.append(row)

        if not rows_to_process:
            print("No data rows found in the input CSV file.")
            return

        # 2. 使用 ThreadPoolExecutor 并行处理数据
        processed_results = []
        with ThreadPoolExecutor(max_workers=NUM_PARALLEL) as executor:
            # 提交任务到线程池
            # future_to_row_map 存储 future 对象到原始行数据的映射
            future_to_row_map = {executor.submit(my_processing_logic, row): row for row in rows_to_process}

            # 收集结果
            for future in as_completed(future_to_row_map):
                original_row = future_to_row_map[future]
                try:
                    new_value = future.result() # 获取处理函数的返回值
                    original_row[new_column_name] = new_value
                    processed_results.append(original_row)
                except Exception as exc:
                    print(f'Row processing generated an exception: {exc} for row: {original_row}')
                    # 如果处理失败，可以考虑给该行添加一个错误标记或默认值
                    original_row[new_column_name] = f"Error: {exc}"
                    processed_results.append(original_row)

        # 3. 将处理后的数据写入新的CSV文件
        # 重新获取 fieldnames，以防原始文件为空
        # 或者从 processed_results 的第一行获取 keys
        if not processed_results:
            print("No results to write to output file.")
            return

        # 确保新列名在 fieldnames 中，且在最后
        output_fieldnames = list(processed_results[0].keys()) # 获取所有可能的键
        if new_column_name not in output_fieldnames:
            output_fieldnames.append(new_column_name) # 确保新列在
        
        # 保持原始列的顺序，并将新列放在最后
        final_fieldnames = [f for f in fieldnames if f in output_fieldnames] # 原始列顺序
        if new_column_name not in final_fieldnames:
            final_fieldnames.append(new_column_name) # 确保新列在末尾

        with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=final_fieldnames)
            writer.writeheader()
            writer.writerows(processed_results) # 批量写入所有处理后的行

        print(f"处理完成！新结果已写入到 '{output_file_path}'。")

    except FileNotFoundError:
        print(f"错误：文件 '{input_file_path}' 未找到。")
    except Exception as e:
        print(f"发生了一个意外错误：{e}")

if __name__ == "__main__":
    input_csv_path = "/data1/lz/loop_QA/dataset/rl_output.csv"
    output_csv_path = "/data1/lz/loop_QA/dataset/rl_output_lzCheck.csv"
    new_column_name = "is_answer_correct" # 你想新增的列名

    # 3. 调用主函数进行处理
    start_time = time.time()
    process_and_write_csv_concurrently(input_csv_path, output_csv_path, new_column_name)
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f} 秒")

    # 4. 可选：验证新生成的文件内容
    print("\n新生成的文件内容（前几行）：")
    try:
        with open(output_csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                print(line.strip())
                if i >= 4: # 只打印前5行
                    break
    except FileNotFoundError:
        print("输出文件未生成，无法验证。")