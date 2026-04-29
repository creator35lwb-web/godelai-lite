"""Build godelai-mem-sweep-v1.ipynb for Kaggle."""
import json, os

def code(source): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":source}
def md(source):   return {"cell_type":"markdown","metadata":{},"source":source}

cells = []

# -- 1. Title -----------------------------------------------------------------
cells.append(md(
"# GodelReplay: Memory Buffer Sweep\n"
"### Does GodelPlugin's contribution grow as replay buffer shrinks?\n\n"
"> **Hypothesis:** The forgetting reduction delta (Replay-only - GodelReplay)\n"
"> increases as mem_size decreases, proving GodelPlugin provides complementary\n"
"> protection when replay alone is insufficient.\n\n"
"| mem_size | Replay-only forgetting | GodelReplay forgetting | Delta |\n"
"|----------|----------------------|----------------------|-------|\n"
"| 500 | 0.1500 (known) | 0.1487 (known) | +0.87% |\n"
"| 200 | ? | ? | ? |\n"
"| 50 | ? | ? | ? |\n\n"
"*Prior result (mem_size=500): GodelReplay marginally better. At smaller buffers, gap should widen.*\n\n"
"**Part of the Two-Layer GodelAI Architecture paper.**\n"
"*FLYWHEEL TEAM | MACP v2.3.1 | April 2026*"
))

# -- 2. Install ---------------------------------------------------------------
cells.append(md("## 1. Install Dependencies"))
cells.append(code(
    "import subprocess, sys\n"
    "\n"
    "def _install(*pkgs):\n"
    "    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', *pkgs])\n"
    "\n"
    "_install('avalanche-lib', 'torch', 'torchvision')\n"
    "print('avalanche-lib installed.')\n"
))

# -- 3. Clone -----------------------------------------------------------------
cells.append(md("## 2. Load GodelAI Repository"))
cells.append(code(
    "import subprocess, os, sys\n"
    "\n"
    "GODELAI_DIR = '/kaggle/working/godelai-repo'\n"
    "\n"
    "if not os.path.exists(GODELAI_DIR):\n"
    "    print('Cloning creator35lwb-web/godelai...')\n"
    "    result = subprocess.run(\n"
    "        ['git', 'clone', '--depth', '1',\n"
    "         'https://github.com/creator35lwb-web/godelai.git', GODELAI_DIR],\n"
    "        capture_output=True, text=True\n"
    "    )\n"
    "    if result.returncode != 0:\n"
    "        raise RuntimeError('Clone failed: ' + result.stderr)\n"
    "    print('Cloned successfully.')\n"
    "else:\n"
    "    print('godelai-repo already present.')\n"
    "\n"
    "if GODELAI_DIR not in sys.path:\n"
    "    sys.path.insert(0, GODELAI_DIR)\n"
    "\n"
    "from godelai.avalanche_plugin import GodelPlugin\n"
    "from godelai.strategies.godel_replay import create_godel_replay_strategy\n"
    "print('GodelPlugin and GodelReplay imported successfully.')\n"
))

# -- 4. Config ----------------------------------------------------------------
_config_cell = (
    "import torch\n"
    "\n"
    "def _resolve_device():\n"
    "    if not torch.cuda.is_available():\n"
    "        return 'cpu'\n"
    "    major, minor = torch.cuda.get_device_capability(0)\n"
    "    if major >= 7:\n"
    "        return 'cuda'\n"
    "    print('[Warning] GPU sm_' + str(major) + str(minor) + ' < sm_70 -- using CPU.')\n"
    "    return 'cpu'\n"
    "\n"
    "BASE_CONFIG = {\n"
    "    'n_experiences': 10,\n"
    "    'seed': 42,\n"
    "    'train_epochs': 5,\n"
    "    'train_mb_size': 128,\n"
    "    'eval_mb_size': 256,\n"
    "    'lr': 0.001,\n"
    "    'device': _resolve_device(),\n"
    "    'ewc_lambda': 400.0,\n"
    "    'fisher_scaling': 'global_max',\n"
    "    'propagation_gamma': 2.0,\n"
    "    't_score_window': 50,\n"
    "}\n"
    "MEM_SIZES = [50, 200, 500]\n"
    "\n"
    "print('Device: ' + BASE_CONFIG['device'])\n"
    "print('Buffer sizes to test: ' + str(MEM_SIZES))\n"
    "print('Strategies: replay_only, godel_replay')\n"
    "print('Total runs: ' + str(len(MEM_SIZES) * 2))\n"
    "if torch.cuda.is_available():\n"
    "    cap = torch.cuda.get_device_capability(0)\n"
    "    vram = torch.cuda.get_device_properties(0).total_memory / 1e9\n"
    "    print('GPU: ' + torch.cuda.get_device_name(0) + ' | sm_' + str(cap[0]) + str(cap[1]) + ' | VRAM: ' + str(round(vram,1)) + ' GB')\n"
)

cells.append(md("## 3. Configuration"))
cells.append(code(_config_cell))

# -- 5. Run sweep -------------------------------------------------------------
cells.append(md(
    "## 4. Run -- Buffer Size Sweep\n"
    "> 6 runs total: mem_size=[50, 200, 500] x [replay_only, godel_replay]\n"
    "> Estimated runtime: 90-150 min on CPU."
))
cells.append(code(
    "import sys\n"
    "sys.path.insert(0, GODELAI_DIR)\n"
    "\n"
    "from experiments.permutedmnist_mem_sweep import run_one, MEM_SIZES, BASE_CONFIG\n"
    "\n"
    "results = []\n"
    "\n"
    "for mem_size in MEM_SIZES:\n"
    "    for strategy in ['replay_only', 'godel_replay']:\n"
    "        r = run_one(strategy, mem_size, BASE_CONFIG)\n"
    "        results.append(r)\n"
    "        forg = '{:.4f}'.format(r['avg_forgetting']) if r['avg_forgetting'] is not None else 'N/A'\n"
    "        acc  = '{:.4f}'.format(r['final_accuracy'])  if r['final_accuracy']  is not None else 'N/A'\n"
    "        print('DONE: ' + strategy + ' mem=' + str(mem_size) + ' | forgetting=' + forg + ' acc=' + acc)\n"
    "\n"
    "print('All runs complete.')\n"
))

# -- 6. Results ---------------------------------------------------------------
cells.append(md("## 5. Results"))
_results_cell = (
    "print('\\n' + '='*72)\n"
    "print('  MEMORY BUFFER SWEEP -- PermutedMNIST (10 tasks, seed=42)')\n"
    "print('='*72)\n"
    "print('  ' + 'mem_size'.ljust(10) + 'Strategy'.ljust(16) +\n"
    "      'Forgetting'.rjust(12) + 'Accuracy'.rjust(10) + 'Delta'.rjust(12))\n"
    "print('  ' + '-'*60)\n"
    "\n"
    "for mem_size in MEM_SIZES:\n"
    "    r_replay = next((r for r in results if r['strategy'] == 'replay_only' and r['mem_size'] == mem_size), None)\n"
    "    r_godel  = next((r for r in results if r['strategy'] == 'godel_replay' and r['mem_size'] == mem_size), None)\n"
    "    if r_replay:\n"
    "        print('  ' + str(mem_size).ljust(10) + 'replay_only'.ljust(16) +\n"
    "              '{:.4f}'.format(r_replay['avg_forgetting']).rjust(12) +\n"
    "              '{:.4f}'.format(r_replay['final_accuracy']).rjust(10) + '  --'.rjust(12))\n"
    "    if r_godel and r_replay:\n"
    "        delta = r_replay['avg_forgetting'] - r_godel['avg_forgetting']\n"
    "        pct   = delta / r_replay['avg_forgetting'] * 100 if r_replay['avg_forgetting'] else 0\n"
    "        sign  = '+' if pct >= 0 else ''\n"
    "        print('  ' + str(mem_size).ljust(10) + 'godel_replay'.ljust(16) +\n"
    "              '{:.4f}'.format(r_godel['avg_forgetting']).rjust(12) +\n"
    "              '{:.4f}'.format(r_godel['final_accuracy']).rjust(10) +\n"
    "              (sign + '{:.1f}%'.format(pct)).rjust(12))\n"
    "        print()\n"
    "\n"
    "print('='*72)\n"
    "\n"
    "# Known mem_size=500 results for reference\n"
    "print('\\nReference (from prior run, mem_size=500):')\n"
    "print('  replay_only   forgetting=0.1500  acc=0.8416')\n"
    "print('  godel_replay  forgetting=0.1487  acc=0.8418  delta=+0.87%')\n"
    "print('\\nHypothesis: delta should INCREASE as mem_size DECREASES.')\n"
)
cells.append(code(_results_cell))

# -- 7. Conclusion ------------------------------------------------------------
cells.append(md(
    "## 6. Interpretation\n\n"
    "**What this sweep proves:**\n\n"
    "If delta grows as mem_size shrinks, then GodelPlugin and Replay are **complementary**:\n"
    "- Replay handles distribution shift (what examples to show)\n"
    "- GodelPlugin handles weight identity (which weights to protect)\n"
    "- When replay budget is constrained, GodelPlugin fills the gap\n\n"
    "**Paper implication:**\n"
    "> *GodelReplay is most valuable in memory-constrained continual learning settings.\n"
    "> At large buffer sizes, replay saturates protection and GodelPlugin's contribution\n"
    "> is marginal. At small buffer sizes, GodelPlugin provides meaningful additional\n"
    "> forgetting reduction, validating the Two-Layer Architecture complementarity claim.*\n\n"
    "---\n"
    "- [GodelAI GitHub](https://github.com/creator35lwb-web/godelai)\n"
    "- [GodelAI-Lite Notebook](https://www.kaggle.com/code/creator35lwb/godelai-lite-memory-for-gemma-4)\n\n"
    "*creator35lwb | FLYWHEEL TEAM | MACP v2.3.1*"
))

# -- Build --------------------------------------------------------------------
nb = {
    "nbformat": 4, "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": cells
}

out_path = "godelai-mem-sweep-v1.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

size = os.path.getsize(out_path)
print("Written: {} | {} cells | {:,} bytes".format(out_path, len(cells), size))
