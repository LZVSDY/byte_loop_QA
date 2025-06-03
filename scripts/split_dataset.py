import pandas as pd

csv_file_path = '/data1/lz/loop_QA/dataset/dr_rl.csv'
output_filename = '/data1/lz/loop_QA/dataset/random_entries.txt'
NUM_RESULTS = 6868

try:
    # 第一列是 'Category'，第二列是 'Entry'
    df = pd.read_csv(csv_file_path)

    # 检查 'Entry' 列是否存在
    if 'Entry' not in df.columns:
        print(f"错误：文件中找不到名为 'Entry' 的列。")
        print(f"文件中找到的列是: {list(df.columns)}")
    else:
        # 从DataFrame中随机抽取n行
        # 然后只选择 'Entry' 这一列
        # dropna() 会移除空值，防止空行被选中
        random_entries = df['Entry'].dropna().sample(n=NUM_RESULTS, random_state=4)

        with open(output_filename, 'w', encoding='utf-8') as f:
            for entry in random_entries:
                # str(entry).strip() 将条目转换为字符串并移除前后多余的空格
                # f.write(...) 将清理后的词条写入文件
                # '\n' 确保每个词条占一行
                f.write(str(entry).strip() + '\n')

        print(f"成功! 已从 '{csv_file_path}' 中随机抽取{NUM_RESULTS}个词条并保存到 '{output_filename}'。")

except FileNotFoundError:
    print(f"错误：找不到文件。请确保路径 '{csv_file_path}' 是正确的。")
except Exception as e:
    print(f"处理文件时发生了一个错误: {e}")