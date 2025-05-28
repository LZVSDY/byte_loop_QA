import os
import json

SYSTEM_PROMPT_PARH = "/data1/lz/langchain/system_prompt"
USR_PROMPT_PARH = "/data1/lz/langchain/user_prompt_fomat"
THRESHOLD = 0.7

def get_system_prompt(file_name: str = "system_prompt", defult_path: str = SYSTEM_PROMPT_PARH) -> str:
    file_path = os.path.join(defult_path, f"{file_name}.txt")
    with open(file_path, "r") as file:
        prompt = file.read()
    return prompt

# def query_prompt(file_name: str = "system_prompt", prompt1: str = "", prompt2: str = "") -> str:
#     usr_prompt_format = get_system_prompt(file_name, defult_path=USR_PROMPT_PARH)
#     usr_prompt = usr_prompt_format.format(prompt1=prompt1, prompt2=prompt2)
#     return usr_prompt

def query_prompt(file_name: str, prompt1: any = "", prompt2: any = None) -> str:
    """
    Generates a user prompt by formatting a template file with provided data.
    This version intelligently handles if prompt2 is a list of strings.
    """
    # --- Start of Changes ---
    # If prompt2 is None, we can still format the string without it
    if isinstance(prompt1, list):
        # If prompt1 is a list, join its elements into a single string
        prompt1_str = "\n".join(prompt1)
    else:
        # If prompt1 is already a string, use it as is
        prompt1_str = prompt1
    
    # Intelligently handle the format of prompt2
    if prompt2 is not None:
        if isinstance(prompt2, list):
            # If the input is a list (like from search_wikipedia),
            # join its elements into a single, clean string separated by newlines.
            # This handles cases where you might get multiple summary paragraphs.
            prompt2_str = "\n".join(prompt2)
        else:
            # If it's not a list, assume it's already a string or can be converted.
            prompt2_str = str(prompt2)
            
        # --- End of Changes ---
        
        usr_prompt_format = get_system_prompt(file_name, defult_path=USR_PROMPT_PARH)
        
        # Use the processed string in the format call
        usr_prompt = usr_prompt_format.format(prompt1=prompt1_str, prompt2=prompt2_str)
    else:
        usr_prompt_format = get_system_prompt(file_name, defult_path=USR_PROMPT_PARH)
        usr_prompt = usr_prompt_format.format(prompt1=prompt1_str)
    
    return usr_prompt

def get_key_from_file(file_path: str = "/data1/lz/langchain/key.txt") -> str:
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
        # encoding='utf-8' 对于处理中文等非英文字符至关重要。
        with open(output_file_path, 'w', encoding='utf-8') as f:
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