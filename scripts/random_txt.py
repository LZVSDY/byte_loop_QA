import random

def save_random_lines(input_path, output_path, num_lines=1000, seed=4):
    """
    从输入文件随机抽取指定行数并保存到新文件
    
    参数:
        input_path (str): 输入文件路径
        output_path (str): 输出文件路径
        num_lines (int): 要抽取的行数，默认为50
        seed (int): 随机种子，默认为42
    """
    # 设置固定随机种子
    random.seed(seed)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
            
            if len(lines) < num_lines:
                raise ValueError(f"输入文件至少需要{num_lines}行，当前只有{len(lines)}行")
                
            selected_lines = random.sample(lines, num_lines)
            
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(selected_lines)
            
        print(f"成功保存 {num_lines} 行到 {output_path}")
        
    except FileNotFoundError:
        print(f"错误：输入文件 {input_path} 未找到")
    except Exception as e:
        print(f"发生错误：{str(e)}")

# 使用示例
if __name__ == "__main__":
    input_file = "/data1/lz/loop_QA/dataset/random_entries.txt"  # 原始文件
    output_file = "/data1/lz/loop_QA/dataset/random_entries_sample.txt"  # 输出文件
    
    save_random_lines(input_file, output_file)
    
    # 验证输出文件行数（可选）
    with open(output_file, 'r', encoding='utf-8') as f:
        print(f"输出文件实际行数：{len(f.readlines())}")
