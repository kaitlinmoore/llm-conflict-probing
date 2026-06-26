#!/usr/bin/env bash
set -euo pipefail

pip install transformer_lens transformers accelerate huggingface-hub anthropic \
    scikit-learn pandas numpy matplotlib seaborn tqdm ipywidgets nbformat sentencepiece
pip uninstall -y torchaudio || true   # install drags it back; ABI clash crashes TL import

export HF_HOME=/workspace/hf_cache    # persist weights on the volume

python - <<'PY'
import torch
torch.zeros(1, device="cuda").cpu()   # the real test: can we ALLOCATE, not just enumerate
print("cuda ok:", torch.cuda.get_device_name(0))
PY

echo "Setup OK. Now run:  hf auth login   (then: source scripts/env.sh in each new shell)"