# Quick Generation Scripts for Maximum Quality SDXL Testing

This directory contains tools for **rapid iteration** on SDXL parameters to achieve **maximum quality fabric-accurate suit generation**.

## 🎯 Primary Goal: QUALITY FIRST

**Objective**: Generate photorealistic suit images with **precise fabric texture transfer** from catalog photos.

**Key Requirements**:
- ✅ **Maximum quality** - Realistic fabric patterns, forms, and textures
- ✅ **No deformation** - Professional suit structure (lapels, buttons, tailoring)
- ✅ **Fast iteration** - Quick parameter testing (NOT optimizing generation speed)
- ✅ **Budget**: <90 seconds per image on 4090 GPU

**Critical Technology**: **IP-Adapter** for direct fabric texture transfer from catalog product photos.

---

## Iteration Speed Comparison

| Workflow | Setup Time | Iteration Speed | Use Case |
|----------|------------|-----------------|----------|
| **Full Stack** (Frontend → Railway → RunPod) | N/A | One test every 2-3 min | End-to-end validation |
| **API Only** (curl → worker.py) | ~10s | One test every 90-120s | API testing |
| **quick_gen.py** | ~55s (first run) | **New test every 60-90s** | **Quality parameter tuning** ⚡ |

**Why quick_gen.py is faster for iteration:**
- Models load once (~55s), stay in VRAM
- No API/DB overhead
- Direct parameter changes via CLI
- **Result**: Test 10+ parameter combinations in 15 minutes

---

## Files

- **`quick_defaults.json`** - Preset configurations (version controlled)
- **`quick_gen.py`** - Standalone generation script
- **`README.md`** - This file

---

## 🔑 IP-Adapter: Key Technology for Fabric Texture Transfer

**What is IP-Adapter?**
IP-Adapter allows SDXL to use a reference image (your fabric catalog photo) as an "image prompt" to guide texture/pattern generation. This is **far more precise** than text prompts for capturing fabric details.

**Why It's Critical for Your Use Case:**
- ✅ **Direct texture transfer** from catalog photos to generated suits
- ✅ **Captures subtle patterns** (weaves, threads, texture) that text can't describe
- ✅ **Consistent fabric appearance** across different suit styles

**How It Works:**
1. You provide a high-res fabric catalog photo as input
2. IP-Adapter extracts visual features from the photo
3. These features guide SDXL to replicate the fabric texture on the generated suit
4. **IP-Adapter scale** (0.0-1.0) controls how strongly the fabric texture is applied

**IP-Adapter Scale Guide:**
- `0.5-0.7` - Subtle fabric influence, more creative freedom
- `0.7-0.8` - **Recommended** - Strong fabric transfer, balanced with suit structure
- `0.8-0.95` - Very strong fabric transfer, may override some prompt details
- `0.95-1.0` - Maximum fabric similarity, minimal deviation

**Setup:**
Currently, IP-Adapter reads fabric images from the path set in `IP_ADAPTER_IMAGE` environment variable. To use with your catalog photos:

```bash
# In your .env file on RunPod
IP_ADAPTER_ENABLED=1
IP_ADAPTER_IMAGE=/workspace/app/backend/assets/fabric_swatches/algodon-tech-negro-001.jpg
IP_ADAPTER_SCALE=0.8
```

**Testing IP-Adapter Impact:**
```bash
# Compare without vs with IP-Adapter
python -m scripts.quick_gen --preset=quality-100 --seed=42  # No IP-Adapter
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42  # With IP-Adapter

# Test different IP-Adapter strengths
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --override ip_scale=0.7
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --override ip_scale=0.9
```

**Expected Results:**
- **Without IP-Adapter**: SDXL guesses fabric texture from text prompts
- **With IP-Adapter**: Fabric texture closely matches your catalog photo

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

## Workflow: Quality-First Testing Plan

**Budget**: 90 seconds per image on 4090 GPU
**Goal**: Maximum quality with precise fabric texture transfer
**Use fixed seeds** (42, 1234) for all tests to isolate parameter effects

---

### Test 1: IP-Adapter Baseline (MOST CRITICAL - 15 minutes)

**Goal**: Verify IP-Adapter improves fabric texture accuracy

```bash
# Single cut for faster iteration
--cuts=recto

# Without IP-Adapter (baseline)
python -m scripts.quick_gen --preset=quality-100 --seed=42 --cuts=recto
python -m scripts.quick_gen --preset=quality-100 --seed=1234 --cuts=recto

# With IP-Adapter (recommended strength)
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=1234 --cuts=recto

# Heavy IP-Adapter (stronger texture transfer)
python -m scripts.quick_gen --preset=quality-ip-heavy --seed=42 --cuts=recto
python -m scripts.quick_gen --preset=quality-ip-heavy --seed=1234 --cuts=recto
```

**Download and compare**: Does IP-Adapter accurately transfer fabric pattern? Which scale is optimal?

---

### Test 2: Steps & Refiner for Quality Ceiling (10 minutes)

**Goal**: Find quality ceiling within 90s budget

```bash
# Test step counts (with IP-Adapter enabled)
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override steps=80
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override steps=100
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override steps=120

# Test refiner impact
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override refiner=false
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override refiner=true
```

**Decision**: Optimal steps for best texture? Does refiner help or blur fabric details?

---

### Test 3: Guidance Scale for Quality (10 minutes)

**Goal**: Balance fabric texture detail vs professional suit structure

```bash
# Test guidance scales (higher = more prompt adherence, sharper details)
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override guidance=5.0
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override guidance=6.5
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override guidance=8.0
```

**Decision**: Which guidance gives cleanest fabric texture + best suit structure?

---

### Test 4: ControlNet Tuning to Prevent Deformation (10 minutes)

**Goal**: Maintain suit structure without deformation while preserving fabric accuracy

```bash
# Test depth ControlNet weights (pose/structure guidance)
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override depth_weight=1.3
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override depth_weight=1.6

# Test canny ControlNet (sharp edges for lapels/buttons)
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override canny_weight=0.5
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override canny_weight=0.8
python -m scripts.quick_gen --preset=ultra-quality-ip --seed=42 --cuts=recto --override canny_weight=1.0
```

**Decision**: Optimal ControlNet weights for structure without warping?

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

## 📊 Quality Evaluation Criteria

Use these criteria when comparing test outputs to systematically evaluate quality:

### ⭐⭐⭐⭐⭐ Excellent (Production Ready)
- ✅ **Fabric Texture**: Precisely matches catalog photo - pattern, weave, and material texture clearly visible
- ✅ **Suit Structure**: Perfect tailoring - sharp lapels, aligned buttons, crisp edges, professional drape
- ✅ **No Deformation**: Zero warping or distortion in suit shape, lapels, or sleeves
- ✅ **Background**: Pure white seamless background, no artifacts or shadows
- ✅ **Lighting**: Consistent, professional studio lighting with subtle shadows
- ✅ **Overall**: Indistinguishable from professional product photography

### ⭐⭐⭐⭐ Good (Acceptable)
- ✅ **Fabric Texture**: Clearly recognizable from catalog photo, minor detail differences acceptable
- ✅ **Suit Structure**: Professional tailoring, sharp details, minimal imperfections
- ✅ **No Deformation**: Slight geometric inconsistencies but not noticeable without zooming
- ⚠️ **Background**: Clean white but may have very subtle artifacts
- ✅ **Lighting**: Professional, minor shadow variations acceptable

### ⭐⭐⭐ Acceptable (Needs Improvement)
- ⚠️ **Fabric Texture**: Fabric type recognizable but pattern/texture not precise
- ⚠️ **Suit Structure**: Generally good but some details blurry or soft
- ⚠️ **Minor Deformation**: Some warping visible (lapel edges, button rows) but within tolerance
- ⚠️ **Background**: Some artifacts or light inconsistencies
- ⚠️ **Lighting**: Usable but not perfect

### ⭐⭐ Poor (Not Production Ready)
- ❌ **Fabric Texture**: Pattern doesn't match catalog, texture generic
- ❌ **Suit Structure**: Blurry details, soft edges, unprofessional look
- ❌ **Deformation**: Visible warping in suit shape or structural elements
- ❌ **Background**: Noticeable artifacts, shadows, or color inconsistencies
- ❌ **Lighting**: Flat or inconsistent

### ⭐ Unusable
- ❌ **Severe Issues**: Major deformation, unrecognizable fabric, background ruined, severe artifacts

---

## Systematic Quality Comparison

When comparing outputs from different presets:

1. **Open images side-by-side** in image viewer (Windows Photos, IrfanView, etc.)
2. **Zoom to 100%** to check fabric detail and texture accuracy
3. **Check against catalog photo**: Does fabric pattern/texture match?
4. **Inspect suit structure**: Are lapels sharp? Buttons aligned? No warping?
5. **Check background**: Pure white? No artifacts?
6. **Document findings**: Note which preset scores highest on each criterion

**Quick quality checklist:**
```
[ ] Fabric texture matches catalog photo (most important!)
[ ] No deformation in suit structure
[ ] Sharp lapels and crisp tailoring
[ ] Clean white background
[ ] Professional lighting
[ ] Within 90s generation budget on 4090
```

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
