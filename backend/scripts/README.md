# Quick Generation Scripts for Maximum Quality SDXL Testing

This directory contains tools for **rapid iteration** on SDXL parameters to achieve **maximum quality fabric-accurate suit generation**.

## 🎯 Primary Goal: QUALITY FIRST

**Objective**: Generate photorealistic suit images with **precise fabric texture transfer** from catalog photos.

**Key Requirements**:
- ✅ **Maximum quality** - Realistic fabric patterns, forms, and textures
- ✅ **No deformation** - Professional suit structure (lapels, buttons, tailoring)
- ✅ **Fast iteration** - Quick parameter testing (NOT optimizing generation speed)
- ✅ **Budget**: <90 seconds per image on 4090 GPU

**Critical Technology**: **ControlNet** for structural control + **LoRA** for precise fabric texture transfer.

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

## 🔑 Technology Stack: ControlNet → Quality Tuning → LoRA

**The Right Approach for Fabric-Accurate Suit Generation:**

### Phase 1: ControlNet Baseline (Foundation)
**Goal**: Establish zero-deformation structural control FIRST

**What ControlNet Does:**
- **Depth ControlNet**: Controls pose/body geometry (prevents warping)
- **Canny ControlNet**: Controls sharp edges (lapels, buttons, seams)
- These work TOGETHER to maintain professional suit structure

**Why Start Here:**
- ✅ If suit structure is deformed, fabric texture is irrelevant
- ✅ ControlNet provides the geometric foundation
- ✅ Allows isolated testing of structural controls before adding texture

**Testing ControlNet:**
```bash
# Test depth ControlNet weights (prevent pose deformation)
python -m scripts.quick_gen --preset=baseline --seed=42 --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --override depth_weight=1.5

# Test canny ControlNet weights (sharp lapels/buttons)
python -m scripts.quick_gen --preset=baseline --seed=42 --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --seed=42 --override canny_weight=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --override canny_weight=0.9
```

**Success Criteria**: Zero deformation, sharp professional tailoring, clean suit structure

---

### Phase 2: Quality Tuning (Polish the Foundation)
**Goal**: Maximize quality within 90s budget on 4090 GPU

**Parameters to Test:**
- **Steps** (60-120): More steps = smoother details, diminishing returns after 100
- **Guidance** (4.0-8.0): Higher = more prompt adherence, sharper details
- **Refiner**: SDXL refinement stage for quality boost

**Success Criteria**: Best quality achievable without fabric-specific textures

---

### Phase 3: LoRA Training (Precise Fabric Texture Transfer)
**Goal**: Teach SDXL specific fabric patterns/textures from catalog photos

**Why LoRA Instead of IP-Adapter:**
- ❌ **IP-Adapter**: Transfers visual style, FIGHTS with ControlNet, causes deformation
  - High scale (0.8+) = all texture, deformed suit structure
  - Low scale (0.3) = better structure but no precise pattern matching
  - Cannot balance both structure AND precise texture

- ✅ **LoRA**: Learns new concepts, WORKS WITH ControlNet
  - Teaches SDXL: "this is what 'algodon-tech-negro-001' looks like"
  - Works harmoniously with ControlNet structural controls
  - Precise pattern/texture replication from catalog photos

**LoRA Workflow** (detailed plan below):
1. Collect catalog photos per fabric (10-20 images minimum)
2. Train LoRA on each fabric family
3. Generate with: `<lora:algodon-tech:0.8>` in prompt
4. LoRA adds texture, ControlNet maintains structure

**Success Criteria**: Fabric texture matches catalog photo + zero deformation

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

**CRITICAL**: Test in this EXACT order - each phase builds on the previous

---

### Phase 1: ControlNet Baseline - Zero Deformation (20 minutes)

**Goal**: Find ControlNet weights that produce PERFECT suit structure with ZERO deformation

**Why First**: If suit structure is deformed, nothing else matters. This is the foundation.

```bash
# Use single cut for faster iteration
--cuts=recto

# Test 1.1: Depth ControlNet (prevents body/pose warping)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=0.8
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.5

# Test 1.2: Canny ControlNet (sharp lapels/buttons)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.9
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=1.1

# Test 1.3: Verify winning combo with second seed
python -m scripts.quick_gen --preset=baseline --seed=1234 --cuts=recto --override depth_weight=<WINNER>,canny_weight=<WINNER>
```

**Evaluation Criteria:**
- ✅ Zero warping in suit body/sleeves
- ✅ Sharp, straight lapel edges
- ✅ Aligned button rows
- ✅ Professional tailoring drape

**Decision**: Document winning weights (e.g., depth=1.2, canny=0.7) - this becomes your new baseline

---

### Phase 2: Quality Ceiling - Maximum Quality (15 minutes)

**Goal**: Find best quality settings within 90s budget

**Starting Config**: Use winning ControlNet weights from Phase 1

```bash
# Test 2.1: Step counts (quality vs time tradeoff)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=60
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=80
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=100
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=120

# Test 2.2: Refiner impact (quality boost vs time cost)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=false
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=true,refiner_split=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=true,refiner_split=0.8

# Test 2.3: Guidance scale (prompt adherence vs creativity)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=4.5
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=6.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=7.5

# Test 2.4: Verify timing with full config
# (Ensure total generation time < 90s on 4090)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=<WINNER>,guidance=<WINNER>,refiner=<WINNER>
```

**Evaluation Criteria:**
- ✅ Best overall image quality (sharpness, detail, coherence)
- ✅ Clean white background
- ✅ Professional studio lighting
- ✅ Within 90s budget

**Decision**: Document optimal quality config (e.g., steps=100, guidance=6.5, refiner=true)

---

### Phase 3: Identify the Gap - Fabric Texture Analysis (5 minutes)

**Goal**: Confirm that quality baseline has generic (not fabric-specific) textures

```bash
# Generate with 2-3 different fabrics using optimized config
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=lana-super-150 --color=azul-marino
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=cashmere-blend --color=gris-carbon
```

**Compare against catalog photos:**
- ❌ Fabric patterns DON'T match catalog (as expected)
- ❌ Textures are generic SDXL "suit fabric"
- ✅ Suit structure is perfect (from Phase 1)
- ✅ Overall quality is excellent (from Phase 2)

**The Gap**: We have perfect structure + quality, but generic textures. This is where LoRA comes in.

---

### Phase 4: LoRA Training Setup (See LoRA Plan Below)

**Goal**: Train fabric-specific LoRAs to close the texture gap

This phase requires:
1. Collecting 10-20 catalog photos per fabric
2. Training LoRA models (external tool: Kohya_ss or similar)
3. Integrating LoRAs into generation pipeline
4. Testing LoRA + ControlNet combination

**See "Comprehensive LoRA Training Plan" section below for detailed workflow**

---

### Phase 5: Document Winning Config (5 minutes)

Edit `quick_defaults.json` to add your optimized baseline:

```json
{
  "production-baseline": {
    "description": "Optimized ControlNet baseline - zero deformation, max quality",
    "guidance": 6.5,
    "total_steps": 100,
    "use_refiner": true,
    "refiner_split": 0.7,
    "controlnet_enabled": true,
    "controlnet_weight": 1.2,
    "controlnet_guidance_start": 0.0,
    "controlnet_guidance_end": 0.5,
    "controlnet2_enabled": true,
    "controlnet2_weight": 0.7,
    "controlnet2_guidance_start": 0.05,
    "controlnet2_guidance_end": 0.88,
    "ip_adapter_enabled": false
  }
}
```

**Important**: This baseline should produce **perfect images with generic fabric textures**. Once you have this, you're ready for LoRA training.

Commit to git for team sharing.

---

## 🎓 Comprehensive LoRA Training Plan

**Prerequisites**: You MUST complete Phases 1-3 first and have a **perfect baseline** before starting LoRA training.

**Your baseline should:**
- ✅ Have ZERO deformation (suit structure is perfect)
- ✅ Have maximum quality within 90s budget
- ❌ Have generic fabric textures (this is expected and what LoRA will fix)

---

### What LoRA Does (and Doesn't Do)

**LoRA Teaches New Concepts:**
- "This is what 'algodon-tech-negro-001' fabric looks like"
- "This is the specific weave pattern of 'lana-super-150'"
- "This is the unique texture of 'cashmere-blend-gris'"

**LoRA Does NOT Fix:**
- ❌ Deformation (ControlNet's job)
- ❌ Poor quality (Steps/Guidance/Refiner's job)
- ❌ Bad lighting or backgrounds (Baseline config's job)

**Think of LoRA as:** Teaching SDXL a new vocabulary word with visual examples.

---

### LoRA Training Workflow

### Step 1: Data Collection (Per Fabric Family)

**Goal**: Collect 10-20 high-quality catalog photos of each fabric

**Requirements for Training Images:**
```
Minimum: 10 images per fabric
Recommended: 15-20 images per fabric
Optimal: 25-30 images per fabric

Image Quality:
- High resolution (1024px minimum, 2048px+ preferred)
- Clear fabric texture visible
- Good lighting (consistent across images)
- Minimal background (crop to fabric if needed)
- Various angles/folds showing fabric behavior
```

**Example Directory Structure:**
```
/workspace/lora_training/
├── algodon-tech-negro-001/
│   ├── IMG_0001.jpg
│   ├── IMG_0002.jpg
│   ├── ... (15-20 images)
├── lana-super-150-azul-marino/
│   ├── IMG_0001.jpg
│   ├── ... (15-20 images)
└── cashmere-blend-gris-carbon/
    ├── ... (15-20 images)
```

**Data Collection Tips:**
- Photograph fabric swatches from multiple angles
- Include close-ups showing weave/texture detail
- Include medium shots showing drape/fold behavior
- Maintain consistent lighting across all photos
- Use same camera/settings for consistency

---

### Step 2: Training Environment Setup

**Option A: Kohya_ss (Recommended for SDXL LoRA)**

Install Kohya_ss on RunPod or local machine with GPU:

```bash
# On RunPod
cd /workspace
git clone https://github.com/bmaltais/kohya_ss
cd kohya_ss
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# GUI mode
python kohya_gui.py
# Access at http://localhost:7860
```

**Option B: Auto1111 WebUI with Dreambooth/LoRA Extension**

```bash
cd /workspace
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh --listen --port 7860
```

---

### Step 3: LoRA Training Configuration

**Recommended SDXL LoRA Training Parameters:**

```yaml
# Basic Settings
base_model: stabilityai/stable-diffusion-xl-base-1.0
output_name: algodon-tech-negro-001
resolution: 1024  # SDXL native resolution

# Training Parameters
learning_rate: 1e-4
batch_size: 1  # Adjust based on VRAM
num_epochs: 10-15
save_every_n_epochs: 5

# LoRA Specific
network_dim: 64  # LoRA rank (64-128 for fabric textures)
network_alpha: 32  # Typically half of network_dim
optimizer: AdamW8bit  # Memory efficient

# Regularization
clip_skip: 2
noise_offset: 0.05  # Helps with contrast/detail

# Captions
caption_extension: .txt  # Descriptive captions for each image
```

**Example Caption for Training Image:**
```
# algodon-tech-negro-001_001.txt
algodon-tech-negro-001, black technical cotton fabric, fine weave texture, matte finish, professional suit material
```

**Caption Guidelines:**
- Start with fabric ID (your trigger word)
- Describe texture (weave, knit, smooth, textured)
- Describe color (black, navy blue, charcoal grey)
- Describe material (cotton, wool, cashmere blend)
- Describe appearance (matte, subtle sheen, professional)

---

### Step 4: Training Process (Example with Kohya_ss)

```bash
# Navigate to Kohya_ss directory
cd /workspace/kohya_ss
source venv/bin/activate

# Launch GUI
python kohya_gui.py

# In GUI:
# 1. Source tab: Point to /workspace/lora_training/algodon-tech-negro-001/
# 2. Parameters tab: Set SDXL LoRA parameters (above)
# 3. Training tab: Start training

# Training time estimate:
# - 4090 GPU: ~20-30 minutes for 15 images, 10 epochs
# - L4 GPU: ~40-60 minutes for 15 images, 10 epochs
```

**Monitor Training:**
- Watch loss values (should decrease steadily)
- Check sample images (generated every N steps)
- Stop if overfitting (samples lose variety)

**Optimal Training Signs:**
- Loss converges to 0.05-0.15
- Sample images show fabric texture clearly
- Samples still maintain variety (not memorizing)

---

### Step 5: LoRA Integration with Generator

**After training, you'll have:** `algodon-tech-negro-001.safetensors` (~100-200MB)

**Integration Steps:**

1. **Copy LoRA to models directory:**
```bash
mkdir -p /workspace/app/backend/models/lora
cp /workspace/kohya_ss/output/algodon-tech-negro-001.safetensors /workspace/app/backend/models/lora/
```

2. **Update generator to load LoRA:**

Edit `app/services/generator.py` to add LoRA loading:

```python
# Add at the top
from diffusers import StableDiffusionXLPipeline

# In SdxlTurboGenerator class, after loading ControlNet
if USE_LORA:
    lora_path = os.getenv("LORA_PATH", None)
    lora_scale = float(os.getenv("LORA_SCALE", "0.8"))

    if lora_path and os.path.exists(lora_path):
        cls._base.load_lora_weights(lora_path)
        print(f"[lora] loaded {lora_path} with scale {lora_scale}")
```

3. **Add to .env:**
```bash
USE_LORA=1
LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
LORA_SCALE=0.8
```

4. **Update prompt construction in generator:**
```python
# Add LoRA trigger to prompt
if USE_LORA:
    prompt = f"algodon-tech-negro-001, {prompt}"
```

---

### Step 6: Testing LoRA + ControlNet Baseline

**Test with your optimized baseline config:**

```bash
# Test with LoRA enabled
export USE_LORA=1
export LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
export LORA_SCALE=0.8

python -m scripts.quick_gen --preset=production-baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001

# Test different LoRA strengths
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.6
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.8
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=1.0
```

**Evaluation:**
- ✅ Fabric texture should now match catalog photo
- ✅ Suit structure should remain perfect (ControlNet unchanged)
- ✅ Overall quality should remain high

**If texture is too weak:** Increase `LORA_SCALE` (try 0.9-1.0)
**If structure starts deforming:** Decrease `LORA_SCALE` (try 0.6-0.7)
**Optimal range:** Usually 0.7-0.85 for fabric LoRAs

---

### Step 7: Production Deployment

Once you've trained and tested all 5 required fabric LoRAs:

1. **Organize LoRA models:**
```bash
/workspace/app/backend/models/lora/
├── algodon-tech-negro-001.safetensors
├── lana-super-150-azul-marino.safetensors
├── cashmere-blend-gris-carbon.safetensors
├── ... (5 total)
```

2. **Update generator to dynamically load LoRA based on fabric_id:**

```python
# In generate() method
lora_filename = f"{fabric_id}_{color_id}.safetensors"
lora_path = f"/workspace/app/backend/models/lora/{lora_filename}"

if os.path.exists(lora_path):
    self._base.load_lora_weights(lora_path)
    prompt = f"{fabric_id}-{color_id}, {prompt}"
else:
    print(f"[lora] not found for {fabric_id}_{color_id}, using baseline")
```

3. **Test end-to-end:** Frontend → Railway → RunPod with LoRA

---

### LoRA Training Tips

**Data Quality > Quantity:**
- 15 excellent photos > 30 mediocre photos
- Consistent lighting across all images
- High resolution (2048px+ preferred)

**Prevent Overfitting:**
- Use regularization images (generic fabric photos)
- Don't train for too many epochs (10-15 usually enough)
- Monitor sample outputs during training

**Optimal LoRA Settings for Fabrics:**
- Network Dim: 64-96 (captures texture detail without overfitting)
- Learning Rate: 1e-4 (conservative, prevents mode collapse)
- Batch Size: 1-2 (fabric details need careful learning)

**Training Multiple LoRAs:**
- Train sequentially, not in parallel (resource management)
- Use same base settings for all fabrics (consistency)
- Document training notes per fabric in version control

---

### Expected Results

**Before LoRA (Phase 1-3 Baseline):**
- ✅ Perfect suit structure
- ✅ Professional quality
- ❌ Generic fabric texture (SDXL's default "suit fabric" concept)

**After LoRA (Phase 4):**
- ✅ Perfect suit structure (maintained)
- ✅ Professional quality (maintained)
- ✅ **Precise fabric texture matching catalog photo**

**This is the holy grail:** Structure + Quality + Specific Texture

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
