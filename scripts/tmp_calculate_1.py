# import csv

# def analyze_answer_correctness(file_path, column_name="is_answer_correct"):
#     """
#     统计CSV文件中指定列的总行数，以及其中包含数字 '0' 的行数。

#     Args:
#         file_path (str): CSV 文件的路径。
#         column_name (str): 需要统计的列名，默认为 "is_answer_correct"。

#     Returns:
#         tuple: 一个元组，包含 (总行数, 包含 '0' 的行数)。
#                如果文件不存在或列不存在，则返回 (0, 0)。
#     """
#     total_rows = 0
#     rows_with_zero = 0

#     try:
#         with open(file_path, mode='r', encoding='utf-8') as infile:
#             reader = csv.DictReader(infile)

#             # 检查列是否存在
#             if column_name not in reader.fieldnames:
#                 print(f"错误：CSV 文件中不包含列 '{column_name}'。可用列为：{reader.fieldnames}")
#                 return (0, 0)

#             for row in reader:
#                 total_rows += 1
#                 cell_value = row.get(column_name) # 使用 .get() 避免 KeyError
                
#                 # 检查单元格值是否包含数字 '0'
#                 # 这里假设 '0' 是字符串形式，例如 '0', 'True0False', 'Value0' 等
#                 # 如果 '0' 特指布尔值 False 或者表示不正确，可能需要更精确的匹配，例如 `str(cell_value).strip() == '0'`
#                 if cell_value is not None and '0' in str(cell_value):
#                     rows_with_zero += 1
        
#         print(f"文件 '{file_path}' 中列 '{column_name}' 的统计结果：")
#         print(f"总行数：{total_rows}")
#         print(f"包含数字 '0' 的行数：{rows_with_zero}")
        
#         return (total_rows, rows_with_zero)

#     except FileNotFoundError:
#         print(f"错误：文件 '{file_path}' 未找到。")
#         return (0, 0)
#     except Exception as e:
#         print(f"读取 CSV 文件时发生错误：{e}")
#         return (0, 0)

# if __name__ == "__main__":
#     csv_path = "/data1/lz/loop_QA/dataset/rl_output_lzCheck.csv"
#     total_actual, zeros_actual = analyze_answer_correctness(csv_path, "is_answer_correct")
#     print(f"\n你的实际文件统计结果：总行数 {total_actual}, 包含 '0' 的行数 {zeros_actual}")

import csv
from collections import defaultdict

def calculate_bo5_accuracy(file_path, question_col='question', answer_col='answer', correct_col='is_answer_correct'):
    """
    根据 'bo 5' 规则计算 (question, answer) 对的正确率。
    如果一个 (question, answer) 对的 5 条记录中，至少有一条的 correct_col 包含 '1'，
    则认为该 (question, answer) 对是正确的。

    Args:
        file_path (str): 输入 CSV 文件的路径。
        question_col (str): CSV 中问题所在的列名。
        answer_col (str): CSV 中答案所在的列名。
        correct_col (str): CSV 中判断正确性结果所在的列名。

    Returns:
        float: (question, answer) 对的正确率 (0.0 到 1.0 之间)。
               如果无法处理，则返回 0.0。
    """
    qa_groups = defaultdict(list) # 用于存储每个 (question, answer) 对的所有 is_answer_correct 值

    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            # 检查必要的列是否存在
            required_cols = [question_col, answer_col, correct_col]
            if not all(col in fieldnames for col in required_cols):
                print(f"错误：CSV 文件中缺少一个或多个必要列：{required_cols}。可用列为：{fieldnames}")
                return 0.0

            for row in reader:
                question = row.get(question_col, '').strip()
                answer = row.get(answer_col, '').strip()
                correct_status = row.get(correct_col, '').strip()

                if question and answer: # 确保 question 和 answer 不为空
                    qa_key = (question, answer)
                    qa_groups[qa_key].append(correct_status)
                else:
                    print(f"警告：跳过缺少问题或答案的行: {row}")

        if not qa_groups:
            print("未从文件中读取到有效的 (question, answer) 对。")
            return 0.0

        total_unique_qa_pairs = len(qa_groups)
        correct_qa_pairs = 0

        print(f"\n正在分析 {total_unique_qa_pairs} 个独特的 (question, answer) 对...")

        for qa_key, correct_statuses in qa_groups.items():
            # 检查这个 (question, answer) 对的 is_answer_correct 值中是否有任何一个包含 '1'
            # 假设 '1' 表示正确，且可能以字符串形式存在，例如 "1", "True1False"
            # 如果你的 'is_answer_correct' 严格是 "1" 或 "0"，则可以简化为 '1' in correct_statuses
            is_bo5_correct = any('1' in status for status in correct_statuses)
            
            # 打印每个组的判断结果（可选，用于调试）
            # print(f"QA Pair: {qa_key}, Statuses: {correct_statuses}, BO5 Correct: {is_bo5_correct}")

            if is_bo5_correct:
                correct_qa_pairs += 1

        accuracy = correct_qa_pairs / total_unique_qa_pairs
        print(f"\nBO 5 规则下统计结果：")
        print(f"总共独特的 (question, answer) 对数量: {total_unique_qa_pairs}")
        print(f"被判定为正确的 (question, answer) 对数量: {correct_qa_pairs}")
        print(f"BO 5 正确率: {accuracy:.4f}") # 格式化输出到小数点后4位

        return accuracy

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
        return 0.0
    except Exception as e:
        print(f"读取或处理 CSV 文件时发生错误：{e}")
        return 0.0

# --- 如何使用它 ---
if __name__ == "__main__":
    # 实际应用中，你会使用你之前代码生成的 CSV 文件路径
    your_generated_csv_path = "/data1/lz/loop_QA/dataset/rl_output_lzCheck.csv" # 替换为你的实际文件路径

    print("\n" + "="*50 + "\n") # 分隔线

    print("--- 针对实际生成文件的 BO 5 统计 (请确保文件存在) ---")
    bo5_accuracy_actual = calculate_bo5_accuracy(your_generated_csv_path,
                                                 question_col='\ufeffquestion',
                                                 answer_col='answer',
                                                 correct_col='is_answer_correct')

    print(f"总计：实际文件 BO 5 正确率: {bo5_accuracy_actual:.4f}")