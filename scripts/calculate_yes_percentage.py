import os
import json

def calculate_yes_percentage(base_dir, entry_list_path):
    """
    计算所有文件列表中 'yes' 结果的占比。

    Args:
        base_dir (str): 存储结果文件的基础目录，例如 '/data1/lz/loop_QA/test1'。
        entry_list_path (str): 包含文件列表名字的文本文件路径，例如 '/data1/lz/loop_QA/dataset/random_entries_sample.txt'。

    Returns:
        float: 'yes' 结果的占比。
    """
    total_yes_count = 0
    total_check_results = 0
    
    bo5_yes_count = 0
    bo5_check_results = 0

    with open(entry_list_path, 'r') as f:
        for line in f:
            now_answer = line.strip()
            if not now_answer:
                continue

            sanitized_answer_name = now_answer.replace(" ", "_").lower()
            current_result_dir = os.path.join(base_dir, sanitized_answer_name)
            student_loop_path = os.path.join(current_result_dir, "student_loop.json")

            if os.path.exists(student_loop_path):
                try:
                    with open(student_loop_path, 'r') as student_loop_file:
                        data = json.load(student_loop_file)
                        for entry in data:
                            bo5_check_results += 1
                            tmp = 0
                            for i in range(1, 6):  # check_result1 to check_result5
                                check_result_key = f"check_result{i}"
                                if check_result_key in entry:
                                    total_check_results += 1
                                    # 移除可能的换行符，并进行比较
                                    if entry[check_result_key].strip().lower() == "yes":
                                        total_yes_count += 1
                                        tmp = 1
                            if tmp > 0:
                                bo5_yes_count += 1
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {student_loop_path}")
                except FileNotFoundError:
                    print(f"Warning: {student_loop_path} not found.")
            else:
                print(f"Warning: Directory or student_loop.json not found for {sanitized_answer_name} at {student_loop_path}")

    if total_check_results == 0:
        return 0.0
    else:
        print("Total 'yes' count:", total_yes_count)
        print("Total check results:", total_check_results)
        print("Total 'yes' count in BO5:", bo5_yes_count)
        print("Total BO5 check results:", bo5_check_results)
        return (total_yes_count / total_check_results) * 100, (bo5_yes_count / bo5_check_results) * 100

if __name__ == "__main__":
    base_directory = "/data1/lz/loop_QA/test1"
    entry_file = "/data1/lz/loop_QA/dataset/random_entries_sample.txt"

    percentage, bo5 = calculate_yes_percentage(base_directory, entry_file)
    print(f"'yes' 结果的占比为: {percentage:.2f}%")
    print(f"BO5 'yes' 结果的占比为: {bo5:.2f}%")