export HF_HOME=/workspace/hf_cache
# uv: cache + venv on pod-local disk, NOT the network volume (quota; see 2026-07-16 session)
export UV_CACHE_DIR=/root/.cache/uv
export UV_PROJECT_ENVIRONMENT=/root/venv
