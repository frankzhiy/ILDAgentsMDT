#!/bin/bash

# 定义清理函数，用于在脚本退出时杀死子进程
cleanup() {
    echo -e "\n正在停止所有服务..."
    # 检查进程是否还在运行并杀死它们
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
    fi
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
    fi
    exit
}

# 捕获 SIGINT 信号 (Ctrl+C)
trap cleanup SIGINT

echo "=================================================="
echo "   🚀 正在启动 ILD Agents MDT 开发环境..."
echo "=================================================="

# --- 自动激活 Conda 环境 (MDTAgent) ---
# 检查当前环境是否已经是 MDTAgent
if [[ "$CONDA_DEFAULT_ENV" != "MDTAgent" ]]; then
    echo "🔍 当前未激活 MDTAgent 环境，正在尝试自动激活..."
    
    # 尝试初始化 Conda (适配常见的安装路径)
    # 注意：脚本是在子 shell 中运行，需要 source conda.sh 才能使用 conda activate
    CONDA_BASE=$(conda info --base 2>/dev/null)
    
    if [ -n "$CONDA_BASE" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
        source "$CONDA_BASE/etc/profile.d/conda.sh"
        conda activate MDTAgent
        
        if [[ "$CONDA_DEFAULT_ENV" == "MDTAgent" ]]; then
            echo "✅ 已成功激活环境: MDTAgent"
        else
            echo "⚠️ 激活失败或环境不存在。将尝试使用当前环境的 Python..."
        fi
    else
        echo "⚠️ 未找到 Conda 基础路径，将使用当前环境的 Python..."
    fi
else
    echo "✅ 检测到当前已在 MDTAgent 环境中"
fi

# 打印 Python 版本以供确认
echo "🐍 使用的 Python: $(which python)"
python --version

# 1. 启动后端 (FastAPI)
echo "正在启动后端 (FastAPI)..."
python server.py &
BACKEND_PID=$!
echo "✅ 后端 PID: $BACKEND_PID"

# 等待几秒确保后端开始初始化
sleep 2

# 2. 启动前端 (Vue)
echo "正在启动前端 (Vue)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端 PID: $FRONTEND_PID"

echo "=================================================="
echo "   🎉 服务已启动! 按 Ctrl+C 停止所有服务"
echo "   👉 访问地址: http://localhost:15173"
echo "=================================================="

# 等待所有后台进程结束
wait $BACKEND_PID $FRONTEND_PID
