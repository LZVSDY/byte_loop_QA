# env

```bash
conda create -n wiki_loop
conda activate wiki_loop
```

## 实现多 ip 查询 wiki

```bash
git clone https://github.com/LZVSDY/Wikipedia
cd Wikipedia
pip install -e .
cd ..
```

## pip

```bash
pip install openai
```

## 配置 v2ray

### 参考配置教程

[参考配置教程1](https://github.com/v2fly/v2ray-core)

[参考配置教程2](https://github.com/2dust/v2rayN)

### 修改环境

修改 `~/.bashrc`

在文件内部末尾加上两行

```bash
alias proxy_on="export https_proxy=http://127.0.0.1:7890 && export http_proxy=http://127.0.0.1:7890"
alias proxy_off="unset http_proxy https_proxy"
```

### 设置 config.json 文件

`wget` 获得 `base64` 源码，解码成 `json` 文件（这步用 ai 来做就行）

### 终端测试

终端1

```bash
cd v2ray
./v2ray run
```

如果终端1输出了 v2ray 的配置，那么说明梯子启动成功

终端2

```bash
proxy_on
curl google.com
```

如果终端2输出了一段 html 文本，那么说明配置成功

# run

* 在 `run.py` 中的 `add_subscription()` 加入梯子的 URL
* `PATH="<path_v2ray>:$PATH" python run.py`
此处 `<path_v2ray>` 是你本地的 `v2ray` 地址

# 文件解释

* 修改 system prompt 路径：`./system_prompt`
* 修改 user prompt formate 路径：`./user_prompt_fomat`
* 具体代码参数，见 `run.py`