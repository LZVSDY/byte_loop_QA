import re

# 您的JSON字符串
json_string = """
[{"answer":"Isidor Isaac Rabi","question_text":"An American scientist discovered a physical phenomenon related to nuclei in magnetic fields. This discovery is used in medical imaging in radiology. In 1944, this scientist received an award related to physics. What's the name of this scientist?","condition_strategy":{"simple_used":["American","1944"],"complex_used":["physical phenomenon","nuclei","strong constant magnetic field","radiology"],"complex_processed":["Referred to nuclear magnetic resonance as a physical phenomenon","Referred to the nuclei in the description of nuclear magnetic resonance","Mentioned the strong constant magnetic field in the context of nuclear magnetic resonance","Indicated the field where magnetic resonance imaging is used"]},"generated_question":{"validation":{"unique_solution":true,"ambiguity_check":"The combination of being American, having a 1944 physics - related award, and a discovery in physics used in radiology narrows down to Isidor Isaac Rabi.","answer_path":"From the American nationality, the 1944 physics award, and the connection between the physical phenomenon related to nuclei in magnetic fields and medical imaging in radiology, we can conclude it's Isidor Isaac Rabi."}}},{"answer":"Isidor Isaac Rabi","question_text":"A scientist from a country in North America discovered a phenomenon that causes nuclei in a strong magnetic field to respond with an electromagnetic signal. This phenomenon is used in a medical imaging technique. In the year after World War I ended, this scientist got a prize for physics. Who is this scientist?","condition_strategy":{"simple_used":["1944"],"complex_used":["North America","nuclei","strong constant magnetic field","electromagnetic signal"],"complex_processed":["Described the origin area of the scientist as North America","Mentioned nuclei in the context of the discovered phenomenon","Referred to the strong magnetic field in the phenomenon","Pointed out the electromagnetic signal produced by the phenomenon"]},"generated_question":{"validation":{"unique_solution":true,"ambiguity_check":"The details of being from North America, the discovery details, its use in medical imaging, and the 1944 physics prize lead to Isidor Isaac Rabi.","answer_path":"The clues of the North American origin, the details of the physical discovery and its medical application, along with the 1944 physics prize, lead to the identification of Isidor Isaac Rabi."}}}]
"""

# 定义我们的正则表达式
# re.DOTALL 标志让 . 可以匹配换行符，增加一点点健壮性
regex_pattern = r'"question_text"\s*:\s*"(.*?)"'

# 使用 re.findall 寻找所有匹配项
# 它会返回一个列表，其中只包含捕获组(括号里的部分)的内容
extracted_questions = re.findall(regex_pattern, json_string, flags=re.DOTALL)

# 打印结果
print("--- 使用正则表达式提取的结果 ---\n")
if extracted_questions:
    for i, question in enumerate(extracted_questions):
        print(f"问题 {i + 1}: {question}\n")
else:
    print("没有找到匹配 'question_text' 的内容。")

print("\n--- 再次提醒 ---")
print("以上方法仅为技术演示，实际应用中请务必使用 json.loads() 或 json.load()。")