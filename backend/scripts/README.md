# Quick Generation Scripts for Rapid SDXL Testing

This directory contains tools for **fast iteration** on SDXL generation parameters without the overhead of the full API/DB stack.

## Speed Comparison

| Workflow | Time per Test | Notes |
|----------|---------------|-------|
| **Full Stack** (Frontend → Railway → RunPod) | ~25-30s | Includes API, DB, polling delays |
| **API Only** (curl → worker.py) | ~20-25s | 5s polling delay + generation |
| **quick_gen.py** | **~2-3s** | Direct generation, models stay in RAM ⚡ |

**~8-10x faster iteration** for parameter testing!

---

## Files

- **`quick_defaults.json`** - Preset configurations (version controlled)
- **`quick_gen.py`** - Standalone generation script
- **`README.md`** - This file

---

## Quick Start on RunPod

### 1. SSH into RunPod GPU Pod

```bash
ssh root@<pod-ip> -p <pod-port> -i ~/.ssh/id_ed25519
```

### 2. Activate Environment

```bash
source /workspace/py311/bin/activate
cd /workspace/app/backend
```

### 3. List Available Presets

```bash
python -m scripts.quick_gen --list-presets
```

Output:
```
[Available Presets]

  baseline             - Current production config - dual ControlNet with refiner
  fast-no-refiner      - Skip refiner for speed - test if quality is acceptable
  aggressive-depth     - Heavy depth ControlNet for stronger pose guidance
  aggressive-canny     - Heavy canny ControlNet for sharper lapel/button edges
  balanced-60          - Balanced config with reduced steps for speed
  ultra-fast           - Minimal steps for rapid testing - quality may suffer
  ...
```

### 4. Run a Single Test

```bash
python -m scripts.quick_gen \
  --preset=aggressive-depth \
  --fabric=algodon-tech \
  --color=negro-001
```

**First run**: ~8-10s (loads SDXL models into VRAM)
**Subsequent runs**: ~2-3s (models cached)

### 5. Compare Multiple Presets

```bash
python -m scripts.quick_gen \
  --compare baseline,aggressive-depth,ultra-fast \
  --fabric=algodon-tech \
  --color=negro-001
```

Generates images for all 3 presets in under 10 seconds total.

### 6. Override Specific Parameters

```bash
python -m scripts.quick_gen \
  --preset=baseline \
  --override guidance=6.0,steps=100 \
  --fabric=algodon-tech
```

### 7. Test Single Cut

```bash
python -m scripts.quick_gen \
  --preset=ultra-fast \
  --cuts=recto \
  --fabric=algodon-tech
```

### 8. Download Outputs to Local Machine

**Open a NEW terminal on your local Windows machine** (keep RunPod SSH open):

```bash
# Navigate to backend directory
cd /d/OneDrive/Escritorio/Dev/hf-virtual-stylist/backend

# Download all outputs (replace IP and port with your RunPod details)
scp -i ~/.ssh/id_ed25519 -P 10079 -r root@203.57.40.119:/workspace/app/backend/outputs/ ./runpod_outputs/

# View images
explorer runpod_outputs/generated/
```

**Important:**
- Use uppercase `-P` for scp (lowercase `-p` is for ssh)
- Ensure there's a **space** between `outputs/` and `./runpod_outputs/`
- Type the command manually if copy-paste removes the space

**Download specific generation only:**
```bash
# Replace the run ID with yours (e.g., 2253b3fece)
scp -i ~/.ssh/id_ed25519 -P 10079 -r root@203.57.40.119:/workspace/app/backend/outputs/generated/algodon-tech/negro-001/2253b3fece/ ./test1/
```

---

## Workflow: Finding Optimal Parameters

### Phase 1: Baseline Testing (15 minutes)

Test current production config vs speed-optimized variants **with fixed seeds for reproducibility**:

```bash
# Test baseline vs no-refiner (seed 42)
python -m scripts.quick_gen --compare baseline,fast-no-refiner --seed=42

# Test step counts
python -m scripts.quick_gen --compare balanced-60,baseline,quality-100 --seed=42

# Test single ControlNets
python -m scripts.quick_gen --compare depth-only,canny-only,baseline --seed=42
```

**Goal**: Determine if refiner is worth the time, optimal step count, ControlNet impact.

**Why use `--seed=42`?** Same seed = same base randomness across all presets, isolating the effect of parameter changes.

### Phase 2: ControlNet Weight Tuning (10 minutes)

```bash
# Test depth weights
python -m scripts.quick_gen --preset=baseline --override depth_weight=0.7
python -m scripts.quick_gen --preset=baseline --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --override depth_weight=1.3

# Test canny weights
python -m scripts.quick_gen --preset=baseline --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --override canny_weight=0.8
python -m scripts.quick_gen --preset=baseline --override canny_weight=1.0
```

**Goal**: Find sweet spot for pose guidance vs fabric flexibility.

### Phase 3: Guidance Scale Testing (5 minutes)

```bash
python -m scripts.quick_gen --compare low-cfg,baseline,high-cfg
```

**Goal**: Balance prompt adherence vs creative freedom.

### Phase 4: Document Findings (5 minutes)

Edit `quick_defaults.json` to add winning configs:

```json
{
  "production-v2": {
    "description": "Optimized config after testing - faster, better quality",
    "guidance": 5.5,
    "total_steps": 60,
    "use_refiner": false,
    "controlnet_weight": 1.1,
    "controlnet2_weight": 0.7,
    ...
  }
}
```

Commit to git for team sharing.

---

## Using Fixed Seeds for Reproducibility

### Why Use Seeds?

**Fixed seeds enable:**
- ✅ **A/B testing** - Isolate parameter changes
- ✅ **Reproducibility** - Same seed = same image structure
- ✅ **Systematic comparison** - Test multiple presets on same base image

### Recommended Workflow

#### Step 1: Find Good Seeds (5 minutes)

```bash
# Try different seeds to find good base images
python -m scripts.quick_gen --preset=baseline --seed=42
python -m scripts.quick_gen --preset=baseline --seed=1234
python -m scripts.quick_gen --preset=baseline --seed=9999
```

Pick 2-3 seeds that produce good starting points (clean background, good pose, etc.)

#### Step 2: Test All Presets with Fixed Seeds

```bash
# Test all presets with your chosen seed
python -m scripts.quick_gen \
  --compare baseline,aggressive-depth,fast-no-refiner,ultra-fast \
  --seed=42

# Verify consistency with second seed
python -m scripts.quick_gen \
  --compare baseline,aggressive-depth,fast-no-refiner,ultra-fast \
  --seed=1234
```

#### Step 3: Fine-tune Winners

```bash
# Found aggressive-depth looks best? Tweak it with same seed
python -m scripts.quick_gen --preset=aggressive-depth --seed=42 --override guidance=5.5
python -m scripts.quick_gen --preset=aggressive-depth --seed=42 --override guidance=6.0
python -m scripts.quick_gen --preset=aggressive-depth --seed=42 --override depth_weight=1.3

# Verify on second seed
python -m scripts.quick_gen --preset=aggressive-depth --seed=1234 --override guidance=5.5
```

### Seed Tips

**Use meaningful seeds:**
```bash
--seed=20241101  # Today's date
--seed=42        # The answer to everything
--seed=100       # Simple incrementing numbers
```

**Batch testing:**
```bash
# Test 3 seeds × 4 presets = 12 images
for seed in 42 1234 9999; do
  python -m scripts.quick_gen \
    --compare baseline,aggressive-depth,fast-no-refiner,ultra-fast \
    --seed=$seed
done
```

---

## Adding New Presets

Edit `scripts/quick_defaults.json`:

```json
{
  "my-custom-preset": {
    "description": "Brief description of what this tests",
    "guidance": 4.5,
    "total_steps": 60,
    "use_refiner": true,
    "refiner_split": 0.7,
    "controlnet_enabled": true,
    "controlnet_weight": 0.9,
    "controlnet_guidance_start": 0.0,
    "controlnet_guidance_end": 0.5,
    "controlnet2_enabled": true,
    "controlnet2_weight": 0.65,
    "controlnet2_guidance_start": 0.05,
    "controlnet2_guidance_end": 0.88,
    "ip_adapter_enabled": false
  }
}
```

Then test immediately:

```bash
python -m scripts.quick_gen --preset=my-custom-preset
```

---

## Parameter Reference

### Available Override Keys

| Short Name | Full Config Key | Type | Description |
|------------|-----------------|------|-------------|
| `guidance` | `guidance` | float | CFG scale (2.0-8.0 typical) |
| `steps` | `total_steps` | int | Inference steps (40-100) |
| `refiner` | `use_refiner` | bool | Enable SDXL refiner |
| `refiner_split` | `refiner_split` | float | Base→Refiner transition (0.0-1.0) |
| `depth_weight` | `controlnet_weight` | float | Depth ControlNet strength |
| `canny_weight` | `controlnet2_weight` | float | Canny ControlNet strength |
| `ip_adapter` | `ip_adapter_enabled` | bool | Enable IP-Adapter |
| `ip_scale` | `ip_adapter_scale` | float | IP-Adapter blend strength |

### Example Override Combinations

```bash
# Faster, lighter depth guidance
--override steps=50,depth_weight=0.8,refiner=false

# Maximum quality
--override steps=120,guidance=5.0,refiner=true,refiner_split=0.8

# Test without any ControlNet
--override controlnet_enabled=false,controlnet2_enabled=false
```

---

## Output Location

Images saved to: `backend/outputs/`

Filename pattern: `{fabric_id}_{color_id}_{cut}_{timestamp}.png`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

**Fix**: Run from `backend/` directory:
```bash
cd /workspace/app/backend
python -m scripts.quick_gen ...
```

### "CUDA out of memory"

**Fix**: Models too large for GPU. Check:
```bash
nvidia-smi  # Should show <20GB VRAM usage with L4
```

If still OOM, try `ultra-fast` preset (single ControlNet, no refiner).

### "Control image not found"

**Fix**: Verify ControlNet images exist:
```bash
ls -la /workspace/app/backend/assets/control/
```

Should contain:
- `recto_depth.png`
- `cruzado_depth.png`
- `recto_canny.png`
- `cruzado_canny.png`

### Models downloading slowly

**Fix**: First run downloads ~12GB of models from HuggingFace. Subsequent runs use cache at `/workspace/.cache/huggingface`.

---

## Next Steps After Testing

Once you've found optimal parameters:

1. **Update `quick_defaults.json`** with winning preset
2. **Port to production**: Update `app/services/generator.py` or environment variables
3. **Update `devops/runpod/deploy.sh`** with new defaults
4. **Test end-to-end**: Frontend → Railway → RunPod with new config
5. **Deploy to production**

---

## Tips

- **Keep models loaded**: Don't restart Python between tests (10s reload penalty)
- **Test systematically**: Change one parameter at a time
- **Document findings**: Update preset descriptions with notes
- **Version control**: Commit winning presets to git
- **Compare visually**: Open `outputs/` in image viewer side-by-side
- **Use fixed seed**: Add `--seed=42` for reproducible tests

---

## Example Session

**On RunPod (SSH terminal):**

```bash
# Start RunPod, SSH in
ssh -i ~/.ssh/id_ed25519 root@203.57.40.119 -p 10079
source /workspace/py311/bin/activate
cd /workspace/app/backend

# List presets
python -m scripts.quick_gen --list-presets

# Test baseline with fixed seed (first run, loads models ~55s)
python -m scripts.quick_gen --preset=baseline --seed=42

# Compare 3 presets with same seed (~80s total, models already loaded)
python -m scripts.quick_gen --compare baseline,fast-no-refiner,ultra-fast --seed=42

# Tweak winner with same seed
python -m scripts.quick_gen --preset=fast-no-refiner --seed=42 --override guidance=5.5,steps=70

# Test with different fabric (still using seed 42)
python -m scripts.quick_gen --preset=fast-no-refiner --seed=42 --fabric=lana-super-150 --color=azul-marino

# Verify with different seed
python -m scripts.quick_gen --preset=fast-no-refiner --seed=1234 --override guidance=5.5,steps=70
```

**On Windows (new terminal, keep RunPod SSH open):**

```bash
# Navigate to backend
cd /d/OneDrive/Escritorio/Dev/hf-virtual-stylist/backend

# Download all outputs (note: uppercase -P, space before ./runpod_outputs/)
scp -i ~/.ssh/id_ed25519 -P 10079 -r root@203.57.40.119:/workspace/app/backend/outputs/ ./runpod_outputs/

# View images
explorer runpod_outputs/generated/

# Compare images side-by-side, document findings
# Update quick_defaults.json with winning preset
```

**Total time**: ~3 minutes for complete testing + download cycle 🚀
