import os
import openai 
from typing import Dict, List, Optional

class ArkAgent:
    """
    一个与火山引擎方舟大模型交互的 Agent 类。
    它直接使用火山引擎提供的 API 端点和模型。
    """
    def __init__(self, 
                 model_id: str, 
                 system_prompt: Optional[str] = "你是人工智能助手",
                 base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
                #  api_key_env_var: str = "75a7a2b3-c147-4005-8c14-45a65fe2da90"): # 1.5 pro
                 api_key_env_var: str = "6d6f26d9-4bad-4280-8972-347815f959b2"): # deepseek r1
        """
        初始化 Agent。

        Args:
            model_id (str): 你在方舟平台上创建的推理接入点 ID。
            system_prompt (Optional[str]): 可选的系统提示词，定义助手的角色。
            base_url (str): 方舟 API 的基础 URL。
            api_key_env_var (str): 存储方舟 API Key 的环境变量名称。
        """
        self.model_id = model_id
        self.system_prompt = system_prompt
        
        api_key = api_key_env_var
        if not api_key:
            raise ValueError(f"错误：环境变量 {api_key_env_var} 未设置或为空。请确保 API Key 已正确配置。")

        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def _construct_messages(self, user_prompt: str) -> List[Dict[str, str]]:
        """
        构建发送给 API 的消息列表。
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def run(self, user_prompt: str, stream: bool = False) -> str:
        """
        执行 Agent，向方舟大模型发送请求并获取响应。

        Args:
            user_prompt (str): 用户输入的提示词。
            stream (bool): 是否使用流式响应。如果为 True，将逐块打印响应内容；
                           如果为 False，将一次性返回完整响应。

        Returns:
            str: 如果 stream 为 False，返回模型的完整响应文本。
                 如果 stream 为 True，逐块打印响应并返回一个空字符串（或可以修改为收集完整流式输出）。
        """
        messages = self._construct_messages(user_prompt)

        try:
            if stream:
                full_response_content = []
                response_stream = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    stream=True,
                )
                # print("----- 流式响应 -----")
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content_piece = chunk.choices[0].delta.content
                        # print(content_piece, end="", flush=True)
                        full_response_content.append(content_piece)
                # print() # 换行
                return "".join(full_response_content) # 返回拼接后的完整流式响应
            else:
                # print("----- 标准请求 -----")
                completion = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                )
                response_content = completion.choices[0].message.content
                # print(f"模型响应: {response_content}")
                return response_content
        except Exception as e:
            print(f"与方舟 API 交互时发生错误: {e}")
            return f"错误: API 调用失败 - {e}"

if __name__ == "__main__":
    # MODEL_ENDPOINT_ID = "doubao-1-5-pro-256k-250115" 
    MODEL_ENDPOINT_ID = "deepseek-r1-250120" 
    

    try:
        # 1. 创建一个 Agent 实例
        my_agent = ArkAgent(model_id=MODEL_ENDPOINT_ID, system_prompt="你是一个乐于助人的代码助手。")

        # 2. 测试标准（非流式）请求
        print("\n--- 测试标准请求 ---")
        prompt1 = "你好，请用 Python 写一个快速排序算法。"
        response1 = my_agent.run(prompt1)
        print(f"Agent 返回 (标准): {response1}") # run 方法内部已经打印

        print("\n--- 测试另一个标准请求 ---")
        prompt2 = "解释一下什么是 Docker。"
        response2 = my_agent.run(prompt2)
        print(f"Agent 返回 (标准): {response2}")

        # 3. 测试流式请求
        print("\n--- 测试流式请求 ---")
        prompt3 = "给我讲一个关于程序员的笑话。"
        streamed_response = my_agent.run(prompt3, stream=True)
        print(f"\n流式传输结束后收集到的完整内容: {streamed_response[:100]}...") # 打印部分收集到的内容

    except ValueError as ve:
        print(f"初始化 Agent 失败: {ve}")
    except Exception as e:
        print(f"在示例中发生未预料的错误: {e}")
        
'''
模型响应: 
以下是用 Python 实现的快速排序算法，包含详细注释和两种常见版本（原地排序版和简洁版）：


### 版本1：原地排序（空间复杂度 O(log n)，更节省内存）
快速排序的核心是**分治思想**：选择一个基准值（pivot），将数组分为“小于基准”和“大于基准”的两部分，递归对两部分排序。原地排序通过交换元素直接在原数组上操作，节省额外空间。

```python
def quick_sort(arr):
    def partition(low, high):
        """分区函数：将数组分为两部分，返回基准的正确位置"""
        pivot = arr[high]  # 选择最后一个元素作为基准
        i = low - 1  # 记录小于基准的元素的右边界
        
        # 遍历数组（不包含基准本身）
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1  # 找到一个小于基准的元素，右边界右移
                arr[i], arr[j] = arr[j], arr[i]  # 交换到左半部分
        
        # 将基准交换到正确位置（i+1 是基准的最终位置）
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1  # 返回基准的位置

    def _quick_sort(low, high):
        """递归排序函数"""
        if low < high:
            # 分区并获取基准位置
            pivot_idx = partition(low, high)
            # 递归排序左半部分（小于基准）
            _quick_sort(low, pivot_idx - 1)
            # 递归排序右半部分（大于基准）
            _quick_sort(pivot_idx + 1, high)

    # 初始调用：排序整个数组（low=0，high=len(arr)-1）
    _quick_sort(0, len(arr) - 1)
    return arr
```


### 版本2：简洁版（利用列表推导式，易理解但额外空间 O(n)）
适合教学演示，通过列表推导式将数组分为三部分（小于/等于/大于基准），递归合并结果。

```python
def quick_sort_simple(arr):
    if len(arr) <= 1:
        return arr  # 基线条件：空或单元素数组已有序
    
    # 选择中间元素作为基准（避免极端情况性能下降）
    pivot = arr[len(arr) // 2]
    
    # 分为三部分：小于、等于、大于基准
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # 递归排序左右部分，合并结果
    return quick_sort_simple(left) + middle + quick_sort_simple(right)
```


### 测试示例
```python
# 测试原地排序版
arr = [3, 6, 8, 10, 1, 2, 1]
quick_sort(arr)
print(arr)  # 输出: [1, 1, 2, 3, 6, 8, 10]

# 测试简洁版
arr = [3, 6, 8, 10, 1, 2, 1]
sorted_arr = quick_sort_simple(arr)
print(sorted_arr)  # 输出: [1, 1, 2, 3, 6, 8, 10]
```


### 关键说明
- **时间复杂度**：平均 O(n log n)，最坏 O(n²)（如完全逆序数组且总选第一个元素为基准）。实际中可通过随机选择基准避免最坏情况。
- **空间复杂度**：原地排序版为 O(log n)（递归栈空间），简洁版为 O(n)（额外列表）。
- **稳定性**：快速排序是**不稳定排序**（相同元素的相对顺序可能改变）。

选择原地排序版以节省内存，适合处理大规模数据；简洁版适合学习和理解核心逻辑。
Agent 返回 (标准): 
以下是用 Python 实现的快速排序算法，包含详细注释和两种常见版本（原地排序版和简洁版）：


### 版本1：原地排序（空间复杂度 O(log n)，更节省内存）
快速排序的核心是**分治思想**：选择一个基准值（pivot），将数组分为“小于基准”和“大于基准”的两部分，递归对两部分排序。原地排序通过交换元素直接在原数组上操作，节省额外空间。

```python
def quick_sort(arr):
    def partition(low, high):
        """分区函数：将数组分为两部分，返回基准的正确位置"""
        pivot = arr[high]  # 选择最后一个元素作为基准
        i = low - 1  # 记录小于基准的元素的右边界
        
        # 遍历数组（不包含基准本身）
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1  # 找到一个小于基准的元素，右边界右移
                arr[i], arr[j] = arr[j], arr[i]  # 交换到左半部分
        
        # 将基准交换到正确位置（i+1 是基准的最终位置）
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1  # 返回基准的位置

    def _quick_sort(low, high):
        """递归排序函数"""
        if low < high:
            # 分区并获取基准位置
            pivot_idx = partition(low, high)
            # 递归排序左半部分（小于基准）
            _quick_sort(low, pivot_idx - 1)
            # 递归排序右半部分（大于基准）
            _quick_sort(pivot_idx + 1, high)

    # 初始调用：排序整个数组（low=0，high=len(arr)-1）
    _quick_sort(0, len(arr) - 1)
    return arr
```


### 版本2：简洁版（利用列表推导式，易理解但额外空间 O(n)）
适合教学演示，通过列表推导式将数组分为三部分（小于/等于/大于基准），递归合并结果。

```python
def quick_sort_simple(arr):
    if len(arr) <= 1:
        return arr  # 基线条件：空或单元素数组已有序
    
    # 选择中间元素作为基准（避免极端情况性能下降）
    pivot = arr[len(arr) // 2]
    
    # 分为三部分：小于、等于、大于基准
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # 递归排序左右部分，合并结果
    return quick_sort_simple(left) + middle + quick_sort_simple(right)
```


### 测试示例
```python
# 测试原地排序版
arr = [3, 6, 8, 10, 1, 2, 1]
quick_sort(arr)
print(arr)  # 输出: [1, 1, 2, 3, 6, 8, 10]

# 测试简洁版
arr = [3, 6, 8, 10, 1, 2, 1]
sorted_arr = quick_sort_simple(arr)
print(sorted_arr)  # 输出: [1, 1, 2, 3, 6, 8, 10]
```


### 关键说明
- **时间复杂度**：平均 O(n log n)，最坏 O(n²)（如完全逆序数组且总选第一个元素为基准）。实际中可通过随机选择基准避免最坏情况。
- **空间复杂度**：原地排序版为 O(log n)（递归栈空间），简洁版为 O(n)（额外列表）。
- **稳定性**：快速排序是**不稳定排序**（相同元素的相对顺序可能改变）。

选择原地排序版以节省内存，适合处理大规模数据；简洁版适合学习和理解核心逻辑。
'''

'''
--- 测试另一个标准请求 ---
----- 标准请求 -----
模型响应: 
Docker 是一个**开源的容器化平台工具**，核心目标是帮助开发者将应用及其依赖环境“打包”成一个**轻量级、可移植、自包含的容器**，从而实现“一次打包，到处运行”（Write Once, Run Anywhere），解决传统开发中“环境不一致”和“部署复杂”的痛点。


### 一、核心概念：容器（Container）
容器是 Docker 的核心。简单理解，容器是一个**独立运行的软件环境**，它将应用程序代码、运行时（如 Java、Python 环境）、依赖库、配置文件等所有需要的资源“打包”在一起，确保应用在不同的物理机、云服务器或开发机上都能**一致、可靠地运行**。

**对比传统虚拟机（VM）**：  
虚拟机通过“Hypervisor”模拟硬件，运行完整的操作系统（如 Linux、Windows），资源占用高、启动慢；  
而 Docker 容器**共享宿主机的操作系统内核**（如宿主机是 Linux，容器直接使用其内核），仅包含应用所需的最小运行环境，因此更轻量（通常几 MB 到几百 MB）、启动更快（毫秒级）、资源利用率更高。


### 二、Docker 的关键组件
1. **镜像（Image）**  
   镜像是容器的“模板”或“快照”，是一个**只读的文件包**，包含应用运行所需的所有依赖和配置（如代码、运行时、库、环境变量等）。  
   例如：一个 Python 应用的镜像可能包含 Python 解释器、项目代码、`requirements.txt` 中的依赖库。

2. **容器（Container）**  
   容器是镜像的**运行实例**（类似“类的实例化”）。通过镜像启动一个容器，就得到一个独立、隔离的运行环境。容器可以启动、停止、删除，修改容器不会影响原镜像（除非提交为新镜像）。

3. **Dockerfile**  
   Dockerfile 是一个**文本格式的脚本**，用于定义如何构建镜像。通过编写一系列指令（如安装依赖、复制代码、设置启动命令），可以自动化生成镜像。  
   示例 Dockerfile：  
   ```dockerfile
   FROM python:3.9  # 基础镜像（Python 3.9 环境）
   WORKDIR /app     # 设置工作目录
   COPY requirements.txt .  # 复制依赖文件
   RUN pip install -r requirements.txt  # 安装依赖
   COPY . .          # 复制当前目录代码到容器
   CMD ["python", "app.py"]  # 启动命令
   ```

4. **仓库（Registry）**  
   仓库是存储和分享镜像的“云盘”，类似代码托管平台（如 GitHub）。公开仓库如 **Docker Hub**（默认仓库），企业可搭建私有仓库（如 Harbor）。开发者可上传自己的镜像，或拉取他人的镜像直接使用（如 `nginx`、`mysql` 官方镜像）。


### 三、Docker 的核心优势
- **环境一致性**：彻底解决“本地能跑，线上报错”的问题，容器打包了完整运行环境，部署时无需重新配置。  
- **轻量高效**：共享宿主机内核，资源占用远低于虚拟机，单台服务器可运行数百个容器。  
- **快速迭代**：镜像可复用（如基于 `python:3.9` 镜像开发自己的应用），容器秒级启动，适合微服务架构和 CI/CD 流程。  
- **隔离性**：容器间相互隔离（通过 Linux 的 Namespace 和 Cgroup 技术），避免应用间资源冲突。  


### 四、典型应用场景
- **开发环境管理**：开发者只需 `docker run` 命令即可启动预配置的数据库（如 MySQL）、缓存（如 Redis）等服务，无需本地安装。  
- **微服务部署**：每个微服务打包为独立容器，通过 Docker Compose 或 Kubernetes 协调多个容器，实现弹性扩展。  
- **持续集成/持续部署（CI/CD）**：在流水线中通过 Docker 镜像确保测试、预发布、生产环境完全一致。  
- **云原生应用**：与 Kubernetes（K8s）结合，实现容器的自动化调度、故障恢复和负载均衡。  


总结来说，Docker 是**容器化技术的标杆工具**，通过“镜像-容器”的模式，彻底简化了应用的开发、测试和部署流程，是现代云计算和 DevOps 体系的核心基础设施之一。
Agent 返回 (标准): 
Docker 是一个**开源的容器化平台工具**，核心目标是帮助开发者将应用及其依赖环境“打包”成一个**轻量级、可移植、自包含的容器**，从而实现“一次打包，到处运行”（Write Once, Run Anywhere），解决传统开发中“环境不一致”和“部署复杂”的痛点。


### 一、核心概念：容器（Container）
容器是 Docker 的核心。简单理解，容器是一个**独立运行的软件环境**，它将应用程序代码、运行时（如 Java、Python 环境）、依赖库、配置文件等所有需要的资源“打包”在一起，确保应用在不同的物理机、云服务器或开发机上都能**一致、可靠地运行**。

**对比传统虚拟机（VM）**：  
虚拟机通过“Hypervisor”模拟硬件，运行完整的操作系统（如 Linux、Windows），资源占用高、启动慢；  
而 Docker 容器**共享宿主机的操作系统内核**（如宿主机是 Linux，容器直接使用其内核），仅包含应用所需的最小运行环境，因此更轻量（通常几 MB 到几百 MB）、启动更快（毫秒级）、资源利用率更高。


### 二、Docker 的关键组件
1. **镜像（Image）**  
   镜像是容器的“模板”或“快照”，是一个**只读的文件包**，包含应用运行所需的所有依赖和配置（如代码、运行时、库、环境变量等）。  
   例如：一个 Python 应用的镜像可能包含 Python 解释器、项目代码、`requirements.txt` 中的依赖库。

2. **容器（Container）**  
   容器是镜像的**运行实例**（类似“类的实例化”）。通过镜像启动一个容器，就得到一个独立、隔离的运行环境。容器可以启动、停止、删除，修改容器不会影响原镜像（除非提交为新镜像）。

3. **Dockerfile**  
   Dockerfile 是一个**文本格式的脚本**，用于定义如何构建镜像。通过编写一系列指令（如安装依赖、复制代码、设置启动命令），可以自动化生成镜像。  
   示例 Dockerfile：  
   ```dockerfile
   FROM python:3.9  # 基础镜像（Python 3.9 环境）
   WORKDIR /app     # 设置工作目录
   COPY requirements.txt .  # 复制依赖文件
   RUN pip install -r requirements.txt  # 安装依赖
   COPY . .          # 复制当前目录代码到容器
   CMD ["python", "app.py"]  # 启动命令
   ```

4. **仓库（Registry）**  
   仓库是存储和分享镜像的“云盘”，类似代码托管平台（如 GitHub）。公开仓库如 **Docker Hub**（默认仓库），企业可搭建私有仓库（如 Harbor）。开发者可上传自己的镜像，或拉取他人的镜像直接使用（如 `nginx`、`mysql` 官方镜像）。


### 三、Docker 的核心优势
- **环境一致性**：彻底解决“本地能跑，线上报错”的问题，容器打包了完整运行环境，部署时无需重新配置。  
- **轻量高效**：共享宿主机内核，资源占用远低于虚拟机，单台服务器可运行数百个容器。  
- **快速迭代**：镜像可复用（如基于 `python:3.9` 镜像开发自己的应用），容器秒级启动，适合微服务架构和 CI/CD 流程。  
- **隔离性**：容器间相互隔离（通过 Linux 的 Namespace 和 Cgroup 技术），避免应用间资源冲突。  


### 四、典型应用场景
- **开发环境管理**：开发者只需 `docker run` 命令即可启动预配置的数据库（如 MySQL）、缓存（如 Redis）等服务，无需本地安装。  
- **微服务部署**：每个微服务打包为独立容器，通过 Docker Compose 或 Kubernetes 协调多个容器，实现弹性扩展。  
- **持续集成/持续部署（CI/CD）**：在流水线中通过 Docker 镜像确保测试、预发布、生产环境完全一致。  
- **云原生应用**：与 Kubernetes（K8s）结合，实现容器的自动化调度、故障恢复和负载均衡。  


总结来说，Docker 是**容器化技术的标杆工具**，通过“镜像-容器”的模式，彻底简化了应用的开发、测试和部署流程，是现代云计算和 DevOps 体系的核心基础设施之一。
'''