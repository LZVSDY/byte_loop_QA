import wikipedia
import backoff
import requests
import time


# 定义可能需要重试的异常类型
EXCEPTIONS_TO_RETRY = (
    requests.exceptions.RequestException,  # 网络请求相关错误
    wikipedia.exceptions.WikipediaException,  # Wikipedia API错误, 想办法排除 PageError 和 DisambiguationError
    ConnectionError,  # 连接错误
    TimeoutError,  # 超时错误
)


# 使用backoff装饰器为Wikipedia API添加重试功能
search_with_retry = backoff.on_exception(
    backoff.expo,  # 使用指数退避策略
    EXCEPTIONS_TO_RETRY,  # 需要重试的异常
    max_tries=1800,  # 最大重试次数
    max_time=1800,  # 最大重试时间(秒)
    jitter=backoff.full_jitter,  # 添加随机抖动以避免同时重试
)(wikipedia.search)


get_summary_with_retry = backoff.on_exception(
    backoff.expo,
    EXCEPTIONS_TO_RETRY,
    max_tries=30,
    max_time=30,
    jitter=backoff.full_jitter,
)(wikipedia.summary)


def search_wikipedia(query: str, num_results: int = 5, language: str = "en", loop_id: int = 0, save_dir: str = "/data1/lz/loop_QA/result") -> list:
    """
    Search Wikipedia for a given query and return a list of summaries.

    Args:
        query (str): The search term to look up on Wikipedia.
        num_results (int): The number of results to return. Default is 5.
        language (str): 使用的Wikipedia语言版本，默认为英文(en)
        loop_id (int): 循环ID，用于命名保存文件
        save_dir (str): 保存结果的目录

    Returns:
        list: A list of summaries for the top search results.
    """
    wikipedia.set_lang(language)  # Set the language for Wikipedia search
    
    search_results = search_with_retry(query, results=num_results)
    print(f"Found {len(search_results)} results for '{query}': {search_results}")
    summaries = []
    for title in search_results:
        if title == query:
            continue
        try:
            summary = get_summary_with_retry(title, sentences=1)
        except Exception as e:
            print(f"Error retrieving summary for '{title}' after multiple retries: {e}")
            continue
        # print(f"Summary for '{title}': {summary}")
        summaries.append(summary)
    
    # save summaries to a file
    with open(f"{save_dir}/wikipedia_summaries_{loop_id}.txt", "a") as f:
        for summary in summaries:
            f.write(summary + "\n")
    return summaries
    
if __name__ == "__main__":
    # Example usage
    query = "Python programming"
    summaries = search_wikipedia(query, num_results=3, language="en")
    for i, summary in enumerate(summaries):
        print(f"Result {i+1}: {summary}")