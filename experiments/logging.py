import json
import os
from datetime import datetime

def save_experiment_log(shared_state_dict: dict, experiment_name: str = "default"):
    """
    保存实验记录到本地 JSON 文件 (占位)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiments/log_{experiment_name}_{timestamp}.json"
    
    # 确保目录存在
    os.makedirs("experiments", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(shared_state_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Experiment log saved to {filename}")
