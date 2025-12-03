# 结构化输出指令
STRUCTURING_INSTRUCTION = """
请阅读上述病历，提取信息并以严格的 JSON 格式输出。
JSON 结构应包含以下字段：

{
    "basic_info": "患者基本概况字符串",
    "symptoms": "主要症状及病史摘要",
    "signs": "体格检查阳性体征",
    "lab_results": "实验室检查关键结果",
    "imaging": "影像学检查描述",
    "pathology": "病理检查描述 (如无则填'未提及')",
    "diagnosis_history": "既往诊断与治疗反应",
    "key_questions": "本次 MDT 需要解决的主要问题"
}

注意：
1. 如果某项信息缺失，请填 "未提及"。
2. 直接返回 JSON 字符串，不要包含 Markdown 代码块标记（如 ```json）。
"""

# 增量更新指令
UPDATING_INSTRUCTION = """
你是一个专业的医疗病例整理员。
你的任务是根据【用户最新输入】，更新已有的【结构化病例信息】，并识别出【本轮新增证据】。

请遵循以下原则：
1. **保留**：已有的信息如果未被新输入否定或修改，请原样保留。
2. **更新**：如果新输入提供了更准确或更新的信息（例如更正了吸烟史，或补充了新的检查结果），请更新对应字段。
3. **追加**：将新出现的症状、检查结果追加到对应字段中。
4. **冲突解决**：如果新输入与旧信息冲突，以【用户最新输入】为准。

请输出一个包含两个部分的 JSON 对象：
{
    "updated_case": {
        "basic_info": "...",
        "symptoms": "...",
        "signs": "...",
        "lab_results": "...",
        "imaging": "...",
        "pathology": "...",
        "diagnosis_history": "...",
        "key_questions": "..."
    },
    "new_evidence": {
        "new_lab_results": ["..."],
        "new_symptoms_info": ["..."],
        "new_imaging_info": ["..."],
        "new_pathology_info": ["..."],
        "answers_to_team_questions": ["..."]
    }
}

关于 `new_evidence`：
- 请将用户本次输入中包含的新信息分类提取到列表中。
- 如果某类没有新信息，请返回空列表 []。
- 这部分信息将用于决定下一轮需要邀请哪些专家。

注意：直接返回 JSON 字符串，不要包含 Markdown 代码块标记。
"""
