import os
import json

SYSTEM_PROMPT_PARH = "/data1/lz/loop_QA/system_prompt"
USR_PROMPT_PARH = "/data1/lz/loop_QA/user_prompt_fomat"
THRESHOLD = 0.8

def get_system_prompt(file_name: str = "system_prompt", defult_path: str = SYSTEM_PROMPT_PARH) -> str:
    file_path = os.path.join(defult_path, f"{file_name}.txt")
    with open(file_path, "r") as file:
        prompt = file.read()
    return prompt

# def query_prompt(file_name: str = "system_prompt", prompt1: str = "", prompt2: str = "") -> str:
#     usr_prompt_format = get_system_prompt(file_name, defult_path=USR_PROMPT_PARH)
#     usr_prompt = usr_prompt_format.format(prompt1=prompt1, prompt2=prompt2)
#     return usr_prompt

def turn_prompt_to_string(prompt: any) -> str:
    if prompt is None:
        return None
    
    if isinstance(prompt, list):
        # 如果是列表，将其元素连接成一个字符串
        return "\n".join(prompt)
    elif isinstance(prompt, str):
        # 如果是字符串，直接返回
        return prompt
    else:
        # 如果是其他类型，尝试转换为字符串
        return str(prompt)

def query_prompt(file_name: str, prompt1: any = "", prompt2: any = None, prompt3: any = None) -> str:
    """
    Generates a user prompt by formatting a template file with provided data.
    This version intelligently handles if prompt2 is a list of strings.
    """
    usr_prompt_format = get_system_prompt(file_name, defult_path=USR_PROMPT_PARH)

    prompt1_str = turn_prompt_to_string(prompt1)
    prompt2_str = turn_prompt_to_string(prompt2)
    prompt3_str = turn_prompt_to_string(prompt3)
    if prompt3_str is not None:
        usr_prompt = usr_prompt_format.format(prompt1=prompt1_str, prompt2=prompt2_str, prompt3=prompt3_str)
    elif prompt2_str is not None:
        usr_prompt = usr_prompt_format.format(prompt1=prompt1_str, prompt2=prompt2_str)
    else:
        usr_prompt = usr_prompt_format.format(prompt1=prompt1_str)                    
    
    return usr_prompt

def get_key_from_file(file_path: str = "/data1/lz/loop_QA/key.txt") -> str:
    """
    Read a key from a file.
    
    Args:
        file_path (str): The path to the file containing the key.
        
    Returns:
        str: The key read from the file.
    """
    with open(file_path, "r") as file:
        key = file.read().strip()
    return key

def filter_keywords(json_string: str, threshold: float = THRESHOLD) -> str:
    """
    接收一个 JSON 字符串，过滤其中的 'keywords' 列表，并返回一个过滤后的 JSON 字符串。

    这是一个 "字符串进，字符串出" 的函数，封装了所有处理逻辑。

    Args:
        json_string (str): 应当是 JSON 格式的原始字符串。
        threshold (float): 保留关键词的相关性分数阈值（包含此值）。

    Returns:
        str: 过滤后的、格式化的 JSON 字符串。如果输入无效，则返回原始字符串。
    """
    try:
        # 1. 将输入的字符串解析成 Python 字典
        data_dict = json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        # 如果解析失败（例如字符串不是合法的JSON），则不进行任何操作，
        # 直接返回原始的、有问题的字符串，以便后续步骤（如save_string_as_json）可以记录错误。
        print(f"⚠️ 警告: filter_keywords 收到的输入不是有效JSON，将返回原始字符串。")
        return json_string

    # 2. 检查解析后的字典结构是否符合预期
    if 'keywords' not in data_dict or not isinstance(data_dict.get('keywords'), list):
        # 如果没有 'keywords' 键或其值不是列表，也返回原始字符串
        return json_string

    # 3. 过滤 'keywords' 列表
    filtered_list = [
        keyword for keyword in data_dict['keywords']
        if isinstance(keyword, dict) and keyword.get('relevance', 0) >= threshold
    ]
    
    # 4. 用过滤后的列表更新字典
    data_dict['keywords'] = filtered_list
    
    # 5. 将过滤后的字典【转换回】格式化的 JSON 字符串并返回
    # indent=2 或 4 使得字符串本身也带有格式，便于调试和查看
    return json.dumps(data_dict, ensure_ascii=False, indent=4)

def save_string_as_json(json_string: str, output_file_path: str):
    """
    解析一个字符串（应为JSON格式），并将其美化后存为 .json 文件。
    
    这个函数是通用的，不关心JSON内部的数据结构。
    它能处理任何合法的JSON字符串（无论是对象{}还是数组[]）。
    包含了错误处理机制，以防输入字符串不是有效的JSON。

    Args:
        json_string (str): 从 Agent 返回的、应为 JSON 格式的原始字符串。
        output_file_path (str): 目标文件的完整路径，例如 'output/agent_response.json'。
    """
    try:
        # 1. 尝试将输入的字符串解析成 Python 对象（字典或列表）
        # 这是从 str 到 dict/list 的关键一步。
        data = json.loads(json_string)
        
        # 2. 将解析后的 Python 对象写入文件
        # 'w' 表示写入模式，如果文件已存在则会覆盖。
        # 'a' 表示追加模式，如果文件不存在则会创建新文件。
        # encoding='utf-8' 对于处理中文等非英文字符至关重要。
        with open(output_file_path, 'a', encoding='utf-8') as f:
            # json.dump() 将 Python 对象序列化成 JSON 格式的字符串并写入文件。
            # indent=4: 添加4个空格的缩进，让文件内容格式优美，易于阅读。
            # ensure_ascii=False: 确保中文字符能被正确写入，而不是被转换成 ASCII 编码。
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ 成功将字符串解析并保存为 JSON 文件: {output_file_path}")
        return True # 返回 True 表示成功

    except json.JSONDecodeError:
        # 如果输入的字符串不是合法的JSON格式，json.loads()会抛出此错误
        print(f"❌ 错误: 无法解析字符串，因为它不是一个有效的JSON格式。")
        print("--- [问题字符串开始] ---")
        print(json_string)
        print("--- [问题字符串结束] ---")
        return False # 返回 False 表示失败

    except Exception as e:
        # 捕获其他可能的错误，例如没有文件写入权限等
        print(f"❌ 发生未知错误: {e}")
        return False
    
def load_question_indices(file_path: str) -> dict[int, list[int]]:
    """
    读取一个指定格式的文本文件，该文件定义了要从哪些结果文件中抽取哪些问题。

    Args:
        file_path (str): 索引文件的路径, 例如 'questions_to_answer.txt'。

    Returns:
        dict[int, list[int]]: 一个字典，键是文件ID (loop_id)，值是要回答的问题索引列表。
                                例如: {0: [0, 1], 1: [0, 2]}
    """
    question_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        file_id = int(parts[0])
                        question_id = int(parts[1])
                        if file_id not in question_map:
                            question_map[file_id] = []
                        question_map[file_id].append(question_id)
                    except ValueError:
                        print(f"⚠️ 警告: 无法解析行 '{line.strip()}'，已跳过。")
    except FileNotFoundError:
        print(f"❌ 错误: 问题索引文件未找到: {file_path}")
    return question_map

def prepare_student_task(question_map: dict[int, list[int]], result_dir: str) -> str | None:
    """
    根据问题映射，从指定的JSON结果文件中抽取问题，并格式化为单个字符串。

    Args:
        question_map (dict[int, list[int]]): `load_question_indices` 函数返回的字典。
        result_dir (str): 存储 relation_response_X.json 文件的目录路径。

    Returns:
        str | None: 一个包含所有待回答问题的、格式化好的字符串。如果出错则返回 None。
    """
    all_questions = []
    question_number = 1
    
    # 按文件ID排序，确保问题顺序稳定
    for file_id in sorted(question_map.keys()):
        file_path = os.path.join(result_dir, f"relation_response_{file_id}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确保 'related_concepts' 存在且为列表
            related_concepts = data.get("related_concepts", [])
            if not isinstance(related_concepts, list):
                continue

            # 抽取指定索引的问题
            for question_id in question_map[file_id]:
                if 0 <= question_id < len(related_concepts):
                    question_text = related_concepts[question_id].get("question")
                    if question_text:
                        all_questions.append(f"{question_number}. {question_text}")
                        question_number += 1
                else:
                    print(f"⚠️ 警告: 在文件 {file_path} 中找不到索引为 {question_id} 的问题。")

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"❌ 错误: 处理文件 {file_path} 时出错: {e}")
            continue
            
    if not all_questions:
        return None
        
    return "\n".join(all_questions)

def get_keywords_from_summary(file_path: str) -> list[str]:
    """
    从一个新版格式的 summary_response.json 文件中读取并提取所有专有名词/关键词。

    新版JSON格式是一个对象列表，例如:
    [
        {"proper_noun": "专有名词1", ...},
        {"keywords": "关键词2", ...}
    ]

    Args:
        file_path (str): summary_response_{i}.json 文件的路径。

    Returns:
        list[str]: 一个包含所有专有名词/关键词字符串的列表。
                   如果文件不存在或格式不正确，则返回空列表。
    """
    keywords = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 直接将整个文件内容解析为列表
            data_list = json.load(f)
        
        # 1. 确保加载的数据是一个列表
        if not isinstance(data_list, list):
            print(f"⚠️ 警告: 文件 {file_path} 的内容不是一个列表，无法提取关键词。")
            return []

        # 2. 遍历列表中的每一个字典元素
        for item in data_list:
            # 3. 确保每个元素都是字典
            if isinstance(item, dict):
                # 4. 尝试从 'proper_noun' 或 'keywords' 键中获取值
                #    使用 .get(key) 方法比直接用 [key] 更安全，如果键不存在不会报错
                keyword = item.get("proper_noun") or item.get("keywords")
                
                if keyword:
                    keywords.append(keyword)

    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到: {file_path}")
    except json.JSONDecodeError:
        print(f"❌ 错误: 文件 {file_path} 的内容不是有效的JSON格式。")
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时发生未知错误: {e}")
    
    return keywords