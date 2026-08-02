# 生产镜像:只装运行依赖(开发依赖仅 CI/本地安装,见 05 规范)
FROM python:3.11-slim

# 国内服务器构建时可用清华源覆盖,如 --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 先复制依赖文件再安装,利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 应用与公开数据(模型产物 models/ 不进 Git,由训练生成,见 standards/00)
COPY app.py .
COPY data/ data/

EXPOSE 8501

# headless:容器内无 TTY;健康端点 /_stcore/health(Streamlit 官方)
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"]
