# ILD Agents MDT (间质性肺病多学科会诊智能体系统)

这是一个基于大语言模型（LLM）的多智能体协作系统，旨在模拟间质性肺病（ILD）的多学科会诊（MDT）过程。

项目采用前后端分离架构，通过 **FastAPI** 提供后端服务，**LangGraph** 编排智能体工作流，前端使用 **Vue 3** 构建专业的医疗会诊界面。

## ✨ 主要功能

*   **多角色智能体协作**：包含病例整理员、影像科、病理科、呼吸科、风湿免疫科及主持专家（Moderator）等多个专业角色。
*   **实时流式传输**：支持 WebSocket 双向通信，实时流式输出医生的详细分析意见和总结。
*   **双重输出机制**：专科医生同时生成“详细分析报告”和“精简总结”，分别展示在不同的 UI 面板中。
*   **多轮会诊支持**：支持多轮对话和追问，系统会自动维护会诊历史和上下文。
*   **灵活的模型配置**：支持在界面上为不同角色配置不同的 LLM 模型（如 GPT-5.1, DeepSeek V3, Claude Haiku 等），并支持配置持久化。
*   **专业医疗界面**：基于 Element Plus 设计的现代化界面，包含聊天面板、结构化信息展示、专科意见折叠面板等。

## 🛠 技术栈

### Backend (后端)
*   **Python 3.10+**
*   **FastAPI**: 高性能 Web 框架，提供 REST API 和 WebSocket 服务。
*   **LangGraph**: 用于构建有状态、多角色的智能体工作流。
*   **OpenAI SDK**: 统一的大模型调用接口（兼容 DeepSeek, Claude 等）。

### Frontend (前端)
*   **Vue 3**: 渐进式 JavaScript 框架。
*   **Vite**: 下一代前端构建工具。
*   **Pinia**: 状态管理库。
*   **Element Plus**: 基于 Vue 3 的组件库。
*   **Tailwind CSS**: 原子化 CSS 框架。

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.10+ 和 Node.js 18+。

### 2. 后端设置

```bash
# 1. 克隆项目并进入目录
git clone <repository_url>
cd ILDAgentsMDT

# 2. 创建并激活虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 复制 .env.example 为 .env 并填入你的 API Key
cp .env.example .env
```

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 4. 启动项目

你需要同时启动后端和前端服务。

**终端 1 (后端):**
```bash
# 在项目根目录下
python server.py
# 服务将运行在 http://localhost:18000
```

**终端 2 (前端):**
```bash
# 在 frontend 目录下
npm run dev
# 页面将运行在 http://localhost:15173
```

**同步启动:**
```bash
# 在项目根目录下
./start.sh
# 页面将运行在 http://localhost:15173
```

## 📂 目录结构

```
ILDAgentsMDT/
├── agents/                 # 智能体实现
│   ├── case_organizer/     # 病例整理员
│   ├── moderator/          # 主持专家
│   ├── radiologist/        # 影像科医生
│   ├── ...                 # 其他专科医生
│   └── base.py             # Agent 基类
├── config/                 # 配置文件
│   ├── llm_config.py       # 模型配置定义
│   └── settings.py         # 环境变量加载
├── core/                   # 核心逻辑
│   ├── pipeline.py         # LangGraph 工作流构建
│   ├── pipeline_api.py     # API 适配层
│   ├── shared_state.py     # 共享状态定义
│   └── nodes/              # 图节点工厂函数
├── frontend/               # Vue 3 前端项目
│   ├── src/
│   │   ├── api/            # Axios & WebSocket 封装
│   │   ├── components/     # Vue 组件 (ChatPanel, InfoPanel, Sidebar...)
│   │   ├── stores/         # Pinia 状态管理
│   │   └── App.vue         # 根组件
│   └── ...
├── llm/                    # LLM 客户端封装
├── server.py               # FastAPI 入口文件
└── requirements.txt        # Python 依赖
```

## ⚙️ 模型配置

项目支持多种大模型配置。你可以在 `config/llm_config.py` 中定义预设模型，或者在前端界面的“配置面板”中动态选择。

支持的模型预设包括：
- GPT-5.1
- DeepSeek V3
- Claude Haiku
- Gemini 2.5 Pro
- Grok 4
- Qwen 3

## 📝 开发指南

- **添加新角色**：
  1. 在 `agents/` 下创建新角色的文件夹。
  2. 继承 `BaseAgent` 实现 `run` 方法。
  3. 在 `core/pipeline.py` 中注册新节点。
  4. 在 `frontend/src/components/Sidebar.vue` 中添加选项。

- **修改 Prompt**：
  每个 Agent 的 Prompt 位于其目录下的 `prompts/` 文件夹中。

## 📄 License

MIT License
