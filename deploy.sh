#!/usr/bin/env bash
# CD 远程部署脚本(在服务器上执行):宿主机端口固定 8888,幂等可重跑。
# 用法:bash deploy.sh <服务器地址>
set -e

# ssh 调用脚本时工作目录是用户主目录,先切到脚本所在目录,否则相对路径构建找不到 Dockerfile
cd "$(dirname "$0")"

APP="banksys_szai4"
IMAGE="${APP}:latest"
PREFERRED_PORT=8888   # 首选宿主机公网端口(见 standards/00 占位符取值)
PORT_MAX=8899         # 预留区间上限:共享服务器可能被其他项目占用,自动顺延空闲端口
CONTAINER_PORT=8501   # 容器内 Streamlit 监听端口,与 Dockerfile CMD 一致
HEALTHCHECK="/_stcore/health"  # Streamlit 官方健康端点(Streamlit 不支持自定义路由)

# 国内服务器用清华源加速依赖下载
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t "${IMAGE}" .

# 只停删本项目自己的旧容器,不碰其他同学的容器/镜像/服务
docker rm -f "${APP}" 2>/dev/null || true

port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}

# 选空闲端口:首选 8888,被占用则顺延(05 规范 §4;共享服务器场景,不删除他人容器)
HOST_PORT=""
for p in $(seq "${PREFERRED_PORT}" "${PORT_MAX}"); do
  if ! port_in_use "${p}"; then
    HOST_PORT="${p}"
    break
  fi
done
if [ -z "${HOST_PORT}" ]; then
  echo ">> 预留端口区间 ${PREFERRED_PORT}-${PORT_MAX} 已全部占用,部署中止" >&2
  exit 1
fi
echo ">> 部署到主机端口 ${HOST_PORT}"

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
