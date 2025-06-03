#!/bin/bash

TARGET_FILE="/data1/lz/loop_QA/finished_tasks.txt"
TIMEOUT_SECONDS=300 # 5分钟 = 300秒
CHECK_INTERVAL=30   # 每60秒检查一次

# --- 您需要配置的命令 ---
# 请确保这里的路径和conda环境名正确
# CONDA_BASE_PATH=$(conda info --base 2>/dev/null) # 尝试自动获取 conda 基础路径
# 如果自动获取失败，或者您想指定特定路径，请取消下面一行的注释并修改为你conda的实际安装路径的上一级目录
# 例如，如果 conda.sh 在 /opt/anaconda3/etc/profile.d/conda.sh, 那么 CONDA_BASE_PATH="/opt/anaconda3"
# CONDA_BASE_PATH="/path/to/your/conda_installation" 

# 如果上面自动获取 CONDA_BASE_PATH 的命令因权限或其他原因失败，脚本会尝试继续，但conda可能不会被激活。
# 确保 conda 初始化脚本的路径正确
# COMMAND_TO_RUN="bash -c 'source \"${CONDA_BASE_PATH}/etc/profile.d/conda.sh\" && conda activate test && cd /data1/lz/loop_QA && python run.py'"
# --- 更健壮的 COMMAND_TO_RUN 定义方式（推荐） ---
# 将实际的 conda 环境中的 python 解释器路径找出，例如在激活 test 环境后执行 which python
# PYTHON_EXEC_PATH="/path/to/your/conda/envs/test/bin/python" # <--- 修改这里为你环境中python的真实路径
PYTHON_EXEC_PATH="/data1/miniconda3/envs/test/bin/python" # <--- 这是一个示例，请务必修改为你的conda环境中 'test' 环境的python解释器路径
                                    # 例如: /data1/lz/miniconda3/envs/test/bin/python
CD_PATH="/data1/lz/loop_QA"
SCRIPT_TO_RUN="run.py"
COMMAND_TO_RUN="cd \"$CD_PATH\" && export https_proxy=http://127.0.0.1:7890 && export http_proxy=http://127.0.0.1:7890 && \"$PYTHON_EXEC_PATH\" \"$SCRIPT_TO_RUN\""
# ---结束命令配置 ---

LOG_FILE="/tmp/task_file_monitor.log" # 监控脚本自身的日志文件

echo "-----------------------------------------------------" >> "$LOG_FILE"
echo "$(date): Monitor script started." >> "$LOG_FILE"
echo "$(date): Watching file: $TARGET_FILE" >> "$LOG_FILE"
echo "$(date): Timeout: $TIMEOUT_SECONDS seconds. Check interval: $CHECK_INTERVAL seconds." >> "$LOG_FILE"
echo "$(date): Command to run on timeout: $COMMAND_TO_RUN" >> "$LOG_FILE"
echo "-----------------------------------------------------" >> "$LOG_FILE"


while true; do
    CURRENT_TIMESTAMP=$(date +%s)
    FILE_MOD_TIMESTAMP=0 # 默认为纪元时间（很久以前）

    if [ -f "$TARGET_FILE" ]; then
        # 对于 Linux 系统:
        FILE_MOD_TIMESTAMP=$(stat -c %Y "$TARGET_FILE")
        # 对于 macOS 系统，请使用:
        # FILE_MOD_TIMESTAMP=$(stat -f %m "$TARGET_FILE")
        echo "$(date): File '$TARGET_FILE' exists. Last modified: $(date -d "@$FILE_MOD_TIMESTAMP")." >> "$LOG_FILE"
    else
        echo "$(date): File '$TARGET_FILE' does not exist. Assuming stale to trigger run." >> "$LOG_FILE"
        # FILE_MOD_TIMESTAMP 保持为 0 (或设置为 CURRENT_TIMESTAMP - TIMEOUT_SECONDS - 1 来确保超时)
        # 这将确保如果文件丢失，我们会尝试启动程序
    fi

    TIME_DIFF=$((CURRENT_TIMESTAMP - FILE_MOD_TIMESTAMP))

    echo "$(date): Current time: $(date -d "@$CURRENT_TIMESTAMP"). File mtime: $(date -d "@$FILE_MOD_TIMESTAMP"). Difference: $TIME_DIFF seconds." >> "$LOG_FILE"

    if [ "$TIME_DIFF" -ge "$TIMEOUT_SECONDS" ]; then
        echo "$(date): TIMEOUT! File '$TARGET_FILE' has not been updated for $TIME_DIFF seconds (threshold is $TIMEOUT_SECONDS)." >> "$LOG_FILE"
        echo "$(date): Attempting to run command: $COMMAND_TO_RUN" >> "$LOG_FILE"
        
        # 在后台执行命令
        # 为了避免 COMMAND_TO_RUN 中的 conda activate 等环境问题，推荐直接使用 conda 环境中的 python 解释器路径
        # (如 COMMAND_TO_RUN 的推荐定义方式所示)
        # 同时，我们将 python run.py 的输出也记录到日志中，方便排查其自身问题
        eval "$COMMAND_TO_RUN >> \"$LOG_FILE\" 2>&1" &
        COMMAND_PID=$!
        
        echo "$(date): Command executed with PID $COMMAND_PID. Output/errors will be appended to $LOG_FILE." >> "$LOG_FILE"
        echo "$(date): Waiting for $CHECK_INTERVAL seconds before next check cycle to allow process to start." >> "$LOG_FILE"
        # 这里可以加一个更长的等待时间，或者在python run.py启动后由它自己touch一下目标文件来重置计时器
        # 不过，python run.py 第一次写入文件时，FILE_MOD_TIMESTAMP 会被更新，从而自动重置计时。
    else
        echo "$(date): File '$TARGET_FILE' is fresh. No action needed." >> "$LOG_FILE"
    fi

    sleep "$CHECK_INTERVAL"
done