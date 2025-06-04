import pandas as pd

def select_random_rows_from_csv(input_csv_path: str, output_csv_path: str, num_rows: int = 20, random_seed: int = None):
    """
    从CSV文件中随机选取指定行数，并生成新的CSV文件。

    参数:
        input_csv_path (str): 输入的CSV文件路径。
        output_csv_path (str): 输出的新CSV文件路径。
        num_rows (int): 要随机选取的行数，默认为20。
        random_seed (int, optional): 随机种子，用于确保结果可复现。默认为None。
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(input_csv_path)

        # 检查请求的行数是否超过总行数
        if num_rows > len(df):
            print(f"⚠️ 警告: 请求选取的行数 ({num_rows}) 大于文件总行数 ({len(df)})。将选取所有行。")
            selected_df = df
        elif num_rows <= 0:
            print(f"⚠️ 警告: 请求选取的行数 ({num_rows}) 无效。不会生成新文件。")
            return
        else:
            selected_df = df.sample(n=num_rows, random_state=random_seed)

        # 将选取的行保存到新的CSV文件
        selected_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig') # utf-8-sig 确保Excel打开中文无乱码
        print(f"✅ 成功从 '{input_csv_path}' 中随机选取 {len(selected_df)} 行，并保存到 '{output_csv_path}'")

    except FileNotFoundError:
        print(f"❌ 错误: 输入文件 '{input_csv_path}' 未找到。")
    except pd.errors.EmptyDataError:
        print(f"❌ 错误: 输入文件 '{input_csv_path}' 为空。")
    except Exception as e:
        print(f"❌ 处理CSV文件时发生错误: {e}")

if __name__ == "__main__":
    input_file = "/data1/lz/loop_QA/test_final/qa_report_sample.csv"   
    output_file = "/data1/lz/loop_QA/test_final/random_50_rows_sample.csv" 
    number_of_rows_to_select = 50
    my_seed = 4

    select_random_rows_from_csv(input_file, output_file, num_rows=number_of_rows_to_select, random_seed=my_seed)