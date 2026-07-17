export HF_HOME=/workspace/hf_cache
# uv: cache + venv on pod-local disk, NOT the network volume (quota; see 2026-07-16 session)
export UV_CACHE_DIR=/root/.cache/uv
export UV_PROJECT_ENVIRONMENT=/root/venv

# Blessed direct interpreter (2026-07-17 env guard): bypasses uv entirely, so
# it can never trigger a silent duplicate-venv build onto the network volume.
# Use when in doubt, or in any shell where env.sh sourcing is uncertain.
runpy() { /root/venv/bin/python "$@"; }
