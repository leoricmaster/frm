#!/usr/bin/env bash
# MinIO 三场景操作脚本（§6.4/§7.2）—— 二阶段验证的可复现入口
# 用法: ./minio-ops.sh <setup|field-upload|dropzone-ls|archive-dropzone|seed-dataset>
#
# 实现说明（相对简报底稿的三处必要技术修正，均经实测验证；凭据/桶名/端口/文案等值逐字未动）：
#  1) mc 别名存在容器内、--rm 即丢：$MC 统一加 `-v /tmp:/tmp` 并固定
#     `--config-dir /tmp/.mc-ops`，让「子命令开头 set 的别名」能被同批后续 $MC 调用
#     共享；该挂载同时满足 field-upload / seed-dataset 读宿主 /tmp 文件的要求
#     （副作用：/tmp/.mc-ops 为容器 root 属主，重跑无害，宿主清理需借容器/sudo）。
#  2) 镜像 ENTRYPOINT 就是 mc：$ALIAS 不能带前缀 "mc"（展开成 `mc mc ...` 是静默
#     no-op，exit 0 但别名没建）；`>/dev/null` 写在调用点而不是塞进 $ALIAS 变量
#     （变量里的重定向符展开后只是字面参数，mc 会报参数错误）。
#  3) policy create 用 /dev/stdin 吃 heredoc，需要 docker run -i 转发 stdin（已内置
#     在 $MC 里，对不读 stdin 的子命令无害）。本版 mc 的 user add / policy create /
#     policy attach 重跑均为覆盖式成功，setup 天然幂等（--ignore-existing flag 不存在，
#     也用不上）。field-upload 按接口约定用 fieldagent 受限凭据上传（§7.2 现场通道），
#     需先跑过 setup。
set -euo pipefail
MC="docker run --rm -i -v /tmp:/tmp --network frm-gitlab_frm-net minio/mc:latest --config-dir /tmp/.mc-ops"
ALIAS="alias set L http://frm-minio:9002 minioadmin Excavator#2026Proto"

case "${1:-}" in
  setup)     # 一次性：建现场受限用户（只能写投放区，不能列目录）
    $MC $ALIAS >/dev/null
    $MC admin user add L fieldagent FieldAgent#2026
    $MC admin policy create L dropzone-write /dev/stdin <<'POL'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:PutObject"],"Resource":["arn:aws:s3:::field-dropzone/*"]}]}
POL
    $MC admin policy attach L dropzone-write --user fieldagent
    echo "[setup] fieldagent 用户就绪（仅 s3:PutObject 到 field-dropzone/*）"
    ;;
  field-upload)   # 现场：传感器数据回传（§7.2 数据向内流）
    shift; F="${1:-/tmp/sensor-$(date +%s).bag}"
    head -c 2097152 /dev/urandom > "$F"   # 2MB 模拟传感器数据
    $MC alias set F http://frm-minio:9002 fieldagent FieldAgent#2026 >/dev/null
    $MC cp "$F" F/field-dropzone/$(basename "$F")
    echo "[field-upload] $(basename "$F") 已进投放区"
    ;;
  dropzone-ls)    # 验证 write-only：fieldagent 列目录应被拒
    $MC alias set F http://frm-minio:9002 fieldagent FieldAgent#2026 >/dev/null
    echo "--- fieldagent 尝试列目录（期望 AccessDenied）:"
    $MC ls F/field-dropzone && echo "!!! 未被拒绝" || echo "[OK] 列目录被拒（write-only 生效）"
    ;;
  archive-dropzone)   # 平台侧：取走投放区数据归档到 dataset-model
    $MC $ALIAS >/dev/null
    $MC mirror --overwrite L/field-dropzone L/dataset-model/field-archive/
    $MC rm --force --recursive L/field-dropzone/
    echo "[archive-dropzone] 投放区已归档并清空"
    ;;
  seed-dataset)  # 平台侧：放示例数据集 + 打印 sha256（CI 校验用）
    $MC $ALIAS >/dev/null
    head -c 5242880 /dev/urandom > /tmp/demo-dataset.bin   # 5MB 假数据集
    SHA=$(sha256sum /tmp/demo-dataset.bin | cut -d' ' -f1)
    $MC cp /tmp/demo-dataset.bin L/dataset-model/datasets/demo-dataset-v1.bin
    echo "{\"path\":\"s3://dataset-model/datasets/demo-dataset-v1.bin\",\"size\":5242880,\"sha256\":\"$SHA\"}"
    ;;
  *) echo "用法: $0 setup|field-upload|dropzone-ls|archive-dropzone|seed-dataset"; exit 2;;
esac
