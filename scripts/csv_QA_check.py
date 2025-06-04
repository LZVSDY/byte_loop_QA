import os
import json
import csv
import glob

BASE_RESULT_DIR = "/data1/lz/loop_QA/test1"  # 专业词目录的根路径
SOURCE_TXT_FILE = "/data1/lz/loop_QA/dataset/random_entries_sample.txt"     # 包含原始专业词列表的txt文件路径
FAILURE_LOG_FILE = "/data1/lz/loop_QA/test_final/failure_sample.txt"             # 记录失败专业词的文件
OUTPUT_CSV_FILE = "/data1/lz/loop_QA/test_final/qa_report_sample.csv"            # 输出的CSV文件名

def sanitize_to_dirname(term_name: str) -> str:
    """将原始专业词转换为目录名格式 (小写，空格替换为下划线)。"""
    return term_name.replace(" ", "_").lower()

def dirname_to_original(dirname: str) -> str:
    """将目录名格式转换回原始专业词 (下划线替换为空格，首字母可能需要大写 - 根据原始列表决定)。
       为了更准确地还原，我们从原始txt列表中查找。
    """
    # 注意: 这个函数现在依赖于原始列表来精确还原大小写和原始空格
    # 如果原始列表不可用或不希望依赖它，可以简单地用replace和title()等，但可能不完全一致
    # 例如: return dirname.replace("_", " ").title()
    # 这里我们假设原始列表已经加载到内存中
    global original_terms_map
    return original_terms_map.get(dirname, dirname.replace("_", " "))


def process_directories():
    """
    处理所有专业词目录，记录失败项并提取QA对到CSV。
    """
    failed_terms = []
    csv_data_rows = []

    # 1. 读取原始专业词列表，用于准确还原名称
    global original_terms_map
    original_terms_map = {} # dirname -> original_term
    try:
        with open(SOURCE_TXT_FILE, 'r', encoding='utf-8') as f_source:
            for line in f_source:
                original_term = line.strip()
                if original_term:
                    dir_name_version = sanitize_to_dirname(original_term)
                    original_terms_map[dir_name_version] = original_term
        print(f"✅ 成功从 {SOURCE_TXT_FILE} 加载了 {len(original_terms_map)} 个原始专业词条目。")
    except FileNotFoundError:
        print(f"⚠️ 警告: 原始专业词列表文件 {SOURCE_TXT_FILE} 未找到。将尝试从目录名直接转换。")
        # 如果文件不存在，则map为空，后续转换将使用简单替换

    # 2. 遍历BASE_RESULT_DIR下的所有子目录（这些被认为是专业词目录）
    for term_dirname in os.listdir(BASE_RESULT_DIR):
        current_term_path = os.path.join(BASE_RESULT_DIR, term_dirname)

        if not os.path.isdir(current_term_path):
            continue # 跳过非目录项

        # 还原专业词的原始名称
        original_term_name = dirname_to_original(term_dirname)

        # 检查是否存在 wikipedia*.txt 文件
        """
        student_loop.json 格式示例：
        [
            {
                "question_text": "Which season of an English football club involved competition in a Southern league before the integration of that league into a higher division, occurred when the club was renamed from its original 19th-century name, and took place in the early 20th century?",
                "answer1": "\n\n1919–20",
                "check_result1": "\n\nno",
                "answer2": "\n\n1919-20",
                "check_result2": "\nno",
                "answer3": "\n\n1919-20",
                "check_result3": "\n\nno",
                "answer4": "\n\n1919–20",
                "check_result4": "\n\nno",
                "answer5": "\n\n1900-01",
                "check_result5": "\n\nno"
            }
        ]
        """
        wiki_files_pattern = os.path.join(current_term_path, "wikipedia*.txt")
        if not glob.glob(wiki_files_pattern): # glob.glob返回一个列表，如果为空则表示没找到
            failed_terms.append(original_term_name)
            print(f"📉 专业词 '{original_term_name}' (目录: {term_dirname}) 失败，缺少 wikipedia*.txt 文件。")
            # 对于失败的条目，我们不再尝试读取 student_loop.json

        # 如果存在 wikipedia*.txt 文件，则处理 student_loop.json
        
        
        else:
            student_answers_path = os.path.join(current_term_path, "student_loop.json")
            if os.path.exists(student_answers_path):
                try:
                    with open(student_answers_path, 'r', encoding='utf-8') as f_answers:
                        qa_pairs = json.load(f_answers)
                        if isinstance(qa_pairs, list): # 确保是列表
                            for pair in qa_pairs:
                                qustion = pair.get("question_text")
                                answer1 = pair.get("answer1")
                                answer2 = pair.get("answer2")
                                answer3 = pair.get("answer3")
                                answer4 = pair.get("answer4")
                                answer5 = pair.get("answer5")
                                
                                check_result1 = pair.get("check_result1")
                                check_result2 = pair.get("check_result2")
                                check_result3 = pair.get("check_result3")
                                check_result4 = pair.get("check_result4")
                                check_result5 = pair.get("check_result5")
                                
                                if qustion and answer1 and answer2 and answer3 and answer4 \
                                    and answer5 and check_result1 and check_result2 and check_result3 \
                                    and check_result4 and check_result5: # 确保键存在且值不为空
                                    csv_data_rows.append({
                                        "Answer": original_term_name,
                                        "Question": qustion,
                                        "Model_Answer1": answer1,
                                        "Model_Answer2": answer2,
                                        "Model_Answer3": answer3,
                                        "Model_Answer4": answer4,
                                        "Model_Answer5": answer5,
                                        "Check_Result1": check_result1,
                                        "Check_Result2": check_result2,
                                        "Check_Result3": check_result3,
                                        "Check_Result4": check_result4,
                                        "Check_Result5": check_result5
                                    })
                                else:
                                    print(f"⚠️ 警告: 在 {student_answers_path} 中找到不完整的QA对: {pair}")
                                
                                # question = pair.get("question_text")
                                # model_answer = pair.get("answer")
                                # if question and model_answer: # 确保键存在且值不为空
                                #     csv_data_rows.append({
                                #         "Answer": original_term_name,
                                #         "Question": question,
                                #         "Model_Answer": model_answer
                                #     })
                                # else:
                                #     print(f"⚠️ 警告: 在 {student_answers_path} 中找到不完整的QA对: {pair}")
                        else:
                            print(f"⚠️ 警告: {student_answers_path} 的内容不是预期的列表格式。")
                except json.JSONDecodeError:
                    print(f"❌ 错误: 解析JSON文件失败 {student_answers_path}")
                except Exception as e:
                    print(f"❌ 处理文件 {student_answers_path} 时发生未知错误: {e}")
            else:
                print(f"⚠️ 警告: 专业词 '{original_term_name}' (目录: {term_dirname}) 的 student_answers.json 文件未找到。")


    # 3. 将失败的专业词写入 failure.txt
    if failed_terms:
        with open(FAILURE_LOG_FILE, 'w', encoding='utf-8') as f_failure:
            for term in failed_terms:
                f_failure.write(term + "\n")
        print(f"\n📝 共有 {len(failed_terms)} 个失败的专业词已写入 {FAILURE_LOG_FILE}")
    else:
        print("\n✨ 所有专业词目录均包含 wikipedia*.txt 文件，没有失败项。")

    # 4. 将提取的数据写入CSV文件
    if csv_data_rows:
        csv_fieldnames = ["Answer", "Question", "Model_Answer1", "Model_Answer2", "Model_Answer3", "Model_Answer4", "Model_Answer5",
                          "Check_Result1", "Check_Result2", "Check_Result3", "Check_Result4", "Check_Result5"]
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=csv_fieldnames)
            writer.writeheader()
            writer.writerows(csv_data_rows)
        print(f"📊 成功将 {len(csv_data_rows)} 条QA记录写入 {OUTPUT_CSV_FILE}")
    else:
        print("\nℹ️ 未提取到任何QA数据用于生成CSV报告。")

if __name__ == "__main__":
    # 首先，确保你的原始专业词txt文件存在，或者接受警告并进行后续处理
    # 假设你的原始专业词文件名为 'your_source_list.txt'，请修改下面的 SOURCE_TXT_FILE 变量
    # 如果你没有原始列表，还原的 Answer 名称可能在大小写上与原始词条不完全一致
    
    # 例如，如果你的原始列表是 'terms.txt'，请将上面配置部分的
    # SOURCE_TXT_FILE = "your_source_list.txt" 修改为
    # SOURCE_TXT_FILE = "terms.txt"

    # 运行主处理函数
    process_directories()

    print("\n🚀 处理完成！")