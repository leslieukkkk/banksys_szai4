#!/usr/bin/env bash
# CD 远程部署脚本(在服务器上执行):宿主机端口固定 8888,幂等可重跑。
# 用法:bash deploy.sh <服务器地址>
set -e

# ssh 调用脚本时工作目录是用户主目录,先切到脚本所在目录,否则相对路径构建找不到 Dockerfile
cd "$(dirname "$0")"

APP="banksys_szai4"
IMAGE="${APP}:latest"
HOST_PORT=8888        # 宿主机公网端口:用户要求固定 8888,不回退(见 standards/00)
CONTAINER_PORT=8501   # 容器内 Streamlit 监听端口,与 Dockerfile CMD 一致;映射 8888:8501
HEALTHCHECK="/_stcore/health"  # Streamlit 官方健康端点(Streamlit 不支持自定义路由)

# 国内服务器用清华源加速依赖下载
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t "${IMAGE}" .

# 只停删本项目自己的旧容器,不碰其他同学的容器/镜像/服务
docker rm -f "${APP}" 2>/dev/null || true

if ! docker run -d --name "${APP}" --restart unless-stopped -p "${HOST_PORT}:${CONTAINER_PORT}" "${IMAGE}"; then
  echo ">> docker run 失败,当前占用 ${HOST_PORT} 的容器:" >&2
  docker ps --format "table {{.Names}}\t{{.Ports}}" >&2
  exit 1
fi

# 本机健康检查:Streamlit 首启要导入 pandas/pyarrow 等依赖,服务就绪可达十几秒,
# 立即 curl 会收到 connection reset(exit 56,curl 默认不重试),故改为等待就绪循环。
HEALTH_OK=0
for i in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:${HOST_PORT}${HEALTHCHECK}"; then
    HEALTH_OK=1
    break
  fi
  echo ">> 等待服务就绪(${i}/20)..."
  sleep 3
done

# 仍失败则输出容器状态与本项目日志便于诊断
if [ "${HEALTH_OK}" != "1" ]; then
  echo ">> 健康检查失败,容器状态:" >&2
  docker ps --filter "name=${APP}" >&2
  echo ">> ${APP} 容器日志:" >&2
  docker logs --tail 50 "${APP}" >&2
  exit 1
fi
echo ""
echo ">> 部署成功:http://${1}:${HOST_PORT}"
