import os
import json

def clean_student_loop_files(base_dir, entry_list_path):
    """
    遍历指定目录下的 student_loop.json 文件。
    如果任何一个 student_loop.json 文件中的字典缺失 check_result{id} 字段，
    那么该 student_loop.json 文件将被删除。

    Args:
        base_dir (str): 存储结果文件的基础目录，例如 '/data1/lz/loop_QA/test1'。
        entry_list_path (str): 包含文件列表名字的文本文件路径，例如 '/data1/lz/loop_QA/dataset/random_entries_sample.txt'。
    """
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
                        # 检查每个字典是否包含所有的 check_result{id}
                        # 我们假设需要 check_result1 到 check_result5
                        is_valid = True
                        for entry in data:
                            for i in range(1, 6): # 检查 check_result1 到 check_result5
                                if f"check_result{i}" not in entry:
                                    is_valid = False
                                    break # 只要一个缺失就标记为无效
                            if not is_valid:
                                break # 整个文件无效

                        # import pdb
                        # pdb.set_trace()

                        if not is_valid:
                            print(f"Warning: Deleting {student_loop_path} because some 'check_result' fields are missing.")
                            os.remove(student_loop_path)

                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {student_loop_path}. Deleting file.")
                    os.remove(student_loop_path)
                except FileNotFoundError:
                    print(f"Warning: {student_loop_path} not found. Skipping.")
            else:
                print(f"Info: {student_loop_path} does not exist. Skipping.")

if __name__ == "__main__":
    base_directory = "/data1/lz/loop_QA/test1"
    entry_file = "/data1/lz/loop_QA/dataset/random_entries_sample.txt"

    clean_student_loop_files(base_directory, entry_file)
    print("\n清理完成。")