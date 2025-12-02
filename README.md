# ILD Agents MDT

这是一个用于“多大语言模型智能体 + MDT 虚拟诊室”科研实验的项目骨架。

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   复制 `.env.example` 为 `.env` 并填入 API Key。

3. 运行项目：
   ```bash
   streamlit run app.py
   ```
4. 项目可视化：
   ```bash
   langgraph dev
   ```

## 目录结构

- `agents/`: 智能体实现，每个智能体独立文件夹。
- `core/`: 核心逻辑，包括共享状态和调度流水线。
- `ui/`: Streamlit 界面代码，按页面和组件拆分。
- `llm/`: 大模型接口封装。
- `config/`: 配置文件。
- `experiments/`: 实验记录与日志。
