import json
import os
from datetime import datetime
from typing import Dict, Any, List
from core.shared_state import SharedState

class SessionLogger:
    def __init__(self, log_dir: str = "logs/sessions"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_file_path(self, session_id: str) -> str:
        return os.path.join(self.log_dir, f"{session_id}.json")

    def _load_log(self, session_id: str) -> Dict[str, Any]:
        file_path = self._get_file_path(session_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading log file {file_path}: {e}")
                return self._create_new_log_structure(session_id)
        return self._create_new_log_structure(session_id)

    def _create_new_log_structure(self, session_id: str) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "rounds": []
        }

    def save_round(self, session_id: str, state: SharedState):
        """
        保存当前轮次的状态到日志文件。
        如果该轮次已存在（例如重试），则更新；否则追加。
        """
        log_data = self._load_log(session_id)
        current_round_index = state.round_count
        
        # 构建当前轮次的数据对象
        round_data = {
            "round_index": current_round_index,
            "timestamp": datetime.now().isoformat(),
            "user_input": state.raw_case_text, # 当前轮的输入
            "new_evidence": state.new_evidence, # 当前轮的新证据
            "process": {
                "structured_info": state.structured_info,
                "specialist_opinions": state.specialist_opinions,
                "specialist_summaries": state.specialist_summaries,
                "conflicts": state.conflicts,
                "discussion_notes": state.discussion_notes,
                "moderator_decision": state.moderator_summary,
                "selected_agents": state.selected_agents
            },
            "output": {
                "summary": state.moderator_summary,
                "questions_to_user": state.questions_to_user
            }
        }

        # 检查是否已经存在该轮次的记录
        round_exists = False
        for i, r in enumerate(log_data["rounds"]):
            if r["round_index"] == current_round_index:
                log_data["rounds"][i] = round_data # 更新
                round_exists = True
                break
        
        if not round_exists:
            log_data["rounds"].append(round_data) # 追加

        # 更新元数据
        log_data["last_updated"] = datetime.now().isoformat()

        # 写入文件
        file_path = self._get_file_path(session_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            print(f"Session log saved to {file_path}")
        except Exception as e:
            print(f"Error saving session log: {e}")

# 全局实例
session_logger = SessionLogger()
