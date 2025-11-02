# Quality-First Testing Plan: ControlNet → Quality Tuning → LoRA

**Created**: 2025-11-01
**Goal**: Maximum quality fabric-accurate suit generation with zero deformation
**Budget**: <90 seconds per image on 4090 GPU

---

## 🎯 Executive Summary

**The Correct Approach:**
1. **ControlNet Baseline** (Phase 1) - Establish PERFECT suit structure with ZERO deformation
2. **Quality Tuning** (Phase 2) - Maximize quality within 90s budget
3. **Identify Gap** (Phase 3) - Confirm generic textures (expected)
4. **LoRA Training** (Phase 4) - Teach SDXL specific fabric textures from catalog photos

**Why This Order?**
- ✅ ControlNet provides geometric foundation (structure)
- ✅ Quality tuning polishes the foundation
- ✅ LoRA adds fabric-specific textures WITHOUT fighting ControlNet
- ❌ IP-Adapter FIGHTS with ControlNet and causes deformation

**Critical Understanding:**
> **Baseline images (Phase 1-3) must ALREADY be perfect** (structure, quality, lighting).
> **LoRA ONLY teaches fabric textures** - it does NOT fix quality problems.

---

## 🚫 Why NOT IP-Adapter?

**We tested IP-Adapter and discovered:**
- Scale 0.8+ = All texture, deformed suit structure
- Scale 0.3 = Better structure but no precise pattern matching
- **Fundamental conflict**: IP-Adapter visual style transfer FIGHTS with ControlNet geometric control

**IP-Adapter is the WRONG tool for this use case.**

**LoRA is the RIGHT tool because:**
- Teaches new concepts: "algodon-tech-negro-001 looks like THIS"
- Works HARMONIOUSLY with ControlNet (no conflict)
- Precise pattern/texture replication from catalog photos
- Standard industry approach for specific object/texture learning

---

## 📋 Phase-by-Phase Testing Plan

### Phase 1: ControlNet Baseline - Zero Deformation (20 minutes)

**Goal**: Find ControlNet weights that produce PERFECT suit structure

**Test Commands:**
```bash
# Use single cut for faster iteration
--cuts=recto

# Test 1.1: Depth ControlNet weights (prevents body/pose warping)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=0.8
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.5

# Test 1.2: Canny ControlNet weights (sharp lapels/buttons)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.9
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=1.1

# Test 1.3: Verify winning combo with second seed
python -m scripts.quick_gen --preset=baseline --seed=1234 --cuts=recto --override depth_weight=<WINNER>,canny_weight=<WINNER>
```

**Evaluation Checklist:**
- [ ] Zero warping in suit body/sleeves
- [ ] Sharp, straight lapel edges
- [ ] Aligned button rows
- [ ] Professional tailoring drape
- [ ] No deformation at all (most critical!)

**Decision Point**: Document winning ControlNet weights (e.g., `depth_weight=1.2, canny_weight=0.7`)

---

### Phase 2: Quality Ceiling - Maximum Quality (15 minutes)

**Goal**: Find best quality settings within 90s budget

**Starting Config**: Use winning ControlNet weights from Phase 1

**Test Commands:**
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

# Test 2.4: Verify timing (ensure < 90s on 4090)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=<WINNER>,guidance=<WINNER>,refiner=<WINNER>
```

**Evaluation Checklist:**
- [ ] Best overall image quality (sharpness, detail, coherence)
- [ ] Clean white background
- [ ] Professional studio lighting
- [ ] Within 90s generation budget
- [ ] Maintains zero deformation from Phase 1

**Decision Point**: Document optimal quality config (e.g., `steps=100, guidance=6.5, refiner=true`)

---

### Phase 3: Identify the Gap - Fabric Texture Analysis (5 minutes)

**Goal**: Confirm that baseline has generic (not fabric-specific) textures

**Test Commands:**
```bash
# Generate with 2-3 different fabrics using optimized config
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=lana-super-150 --color=azul-marino
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=cashmere-blend --color=gris-carbon
```

**Expected Results:**
- ❌ Fabric patterns DON'T match catalog (as expected)
- ❌ Textures are generic SDXL "suit fabric"
- ✅ Suit structure is perfect (from Phase 1)
- ✅ Overall quality is excellent (from Phase 2)

**Critical Insight:**
> This is NOT a failure - this is the expected baseline.
> We have perfect structure + quality, but generic textures.
> **This is where LoRA comes in** to close the texture gap.

---

### Phase 4: LoRA Training - Precise Fabric Texture Transfer

**Prerequisites:**
- ✅ Phase 1-3 complete with perfect baseline
- ✅ Baseline produces 5-star images with generic textures
- ✅ ControlNet weights documented and locked in

**LoRA Training Workflow:**

#### Step 1: Data Collection (Per Fabric - 1 hour per fabric)

Collect 15-20 high-quality catalog photos of each fabric:

```
Requirements:
- High resolution (2048px+ preferred)
- Clear fabric texture visible
- Consistent lighting
- Various angles/folds showing fabric behavior
- Minimal background (crop to fabric if needed)

Directory structure:
/workspace/lora_training/
├── algodon-tech-negro-001/
│   ├── IMG_0001.jpg  (15-20 images)
├── lana-super-150-azul-marino/
│   ├── IMG_0001.jpg  (15-20 images)
└── cashmere-blend-gris-carbon/
    ├── IMG_0001.jpg  (15-20 images)
```

#### Step 2: Training Environment Setup (30 minutes)

Install Kohya_ss on RunPod:

```bash
cd /workspace
git clone https://github.com/bmaltais/kohya_ss
cd kohya_ss
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Launch GUI
python kohya_gui.py
# Access at http://localhost:7860
```

#### Step 3: Train First LoRA (30-60 minutes per fabric)

**Recommended SDXL LoRA parameters:**
- Base model: `stabilityai/stable-diffusion-xl-base-1.0`
- Resolution: `1024`
- Learning rate: `1e-4`
- Batch size: `1`
- Epochs: `10-15`
- Network dim: `64`
- Network alpha: `32`
- Optimizer: `AdamW8bit`

**Caption example** (`algodon-tech-negro-001_001.txt`):
```
algodon-tech-negro-001, black technical cotton fabric, fine weave texture, matte finish, professional suit material
```

**Training time**: ~20-30 minutes on 4090, ~40-60 minutes on L4

#### Step 4: Integration with Generator (15 minutes)

1. Copy trained LoRA to models directory:
```bash
mkdir -p /workspace/app/backend/models/lora
cp /workspace/kohya_ss/output/algodon-tech-negro-001.safetensors /workspace/app/backend/models/lora/
```

2. Update `.env`:
```bash
USE_LORA=1
LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
LORA_SCALE=0.8
```

3. Test LoRA + ControlNet baseline:
```bash
export USE_LORA=1
export LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
export LORA_SCALE=0.8

# Test with optimized baseline from Phase 1-2
python -m scripts.quick_gen --preset=production-baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001

# Test different LoRA strengths
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.6
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.8
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=1.0
```

**Evaluation:**
- ✅ Fabric texture matches catalog photo
- ✅ Suit structure remains perfect (ControlNet maintained)
- ✅ Overall quality remains high

**Optimal LoRA scale**: Usually 0.7-0.85 for fabric textures

#### Step 5: Train Remaining 4 LoRAs

Repeat Steps 1-4 for each of the 5 required fabrics.

**Total time estimate**: ~3-5 hours for all 5 LoRAs (sequential training)

---

## 📊 Success Criteria by Phase

### Phase 1 Success:
- ✅ Zero deformation in suit structure
- ✅ Sharp lapels, aligned buttons, professional drape
- ❌ Fabric texture is generic (expected at this stage)

### Phase 2 Success:
- ✅ Maximum quality within 90s budget
- ✅ Clean backgrounds, professional lighting
- ✅ Maintains zero deformation from Phase 1
- ❌ Fabric texture still generic (expected)

### Phase 3 Success:
- ✅ Confirmed: baseline produces perfect images
- ✅ Confirmed: fabric textures are generic
- ✅ Gap identified: need fabric-specific textures

### Phase 4 Success (Final Goal):
- ✅ Fabric texture precisely matches catalog photo
- ✅ Suit structure remains perfect (ControlNet maintained)
- ✅ Overall quality remains excellent
- ✅ **Holy Grail**: Structure + Quality + Specific Texture

---

## 🎓 Key Learnings from IP-Adapter Testing

**What We Learned:**
1. IP-Adapter visual style transfer CONFLICTS with ControlNet geometric control
2. High IP-Adapter scale (0.8+) → deformed suit structure
3. Low IP-Adapter scale (0.3) → no precise texture matching
4. IP-Adapter cannot balance both structure AND precise texture

**Why LoRA is Better:**
1. LoRA teaches concepts, doesn't transfer styles
2. LoRA works WITH ControlNet, not against it
3. LoRA is standard approach for specific object/texture learning
4. Industry-proven for fabric/material texture replication

**IP-Adapter Use Cases** (not ours):
- General style transfer (artistic styles)
- Low-precision texture hints
- Quick prototyping without training

**LoRA Use Cases** (our use case):
- Specific object/concept learning
- Precise texture/pattern replication
- Working alongside ControlNet structural controls
- Production-ready fabric texture matching

---

## 📁 Updated File Structure

```
backend/scripts/
├── quick_gen.py                    # Rapid testing script
├── quick_defaults.json             # Updated with ControlNet-first presets
├── README.md                       # Updated with ControlNet → LoRA workflow
└── QUALITY_FIRST_PLAN.md          # This document

Updated Presets in quick_defaults.json:
- baseline                          # Phase 1 starting point
- controlnet-test-1,2,3            # Phase 1 ControlNet weight testing
- quality-baseline-80              # Phase 2 starting point
- quality-100, quality-120         # Phase 2 quality ceiling testing
- [IP-Adapter presets deprecated]  # Marked as experimental, not recommended
```

---

## 🚀 Immediate Next Steps

### 1. Start Phase 1 Testing (20 minutes)

```bash
# SSH to RunPod
ssh root@<pod-ip> -p <pod-port> -i ~/.ssh/id_ed25519

# Activate environment
source /workspace/py311/bin/activate
cd /workspace/app/backend

# Pull latest changes
git pull origin main

# Start Phase 1.1: Depth ControlNet testing
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=0.8
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.5

# Download results to local machine
# (From NEW terminal on Windows)
scp -i ~/.ssh/id_ed25519 -P <port> -r root@<pod-ip>:/workspace/app/backend/outputs/ ./phase1_depth_tests/
```

**Evaluate outputs visually:**
- Which depth weight has zero deformation?
- Which produces sharpest suit structure?

### 2. Complete Phase 1 (40 minutes total)

Continue with Phase 1.2 (Canny testing) and Phase 1.3 (verification).

Document winning ControlNet weights in `quick_defaults.json` under new preset:
```json
"production-baseline": {
  "description": "Optimized ControlNet baseline - zero deformation",
  "controlnet_weight": <WINNER>,
  "controlnet2_weight": <WINNER>,
  ...
}
```

### 3. Phase 2-3 Testing (30 minutes)

Test quality ceiling with winning ControlNet weights locked in.

### 4. Data Collection for LoRA (1-2 hours)

Photograph/collect 15-20 catalog images per fabric while testing continues.

### 5. LoRA Training Setup (30 minutes)

Install Kohya_ss on RunPod during downtime.

### 6. Train First LoRA (1 hour)

Start with one fabric to validate the approach.

---

## 📈 Expected Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | 40 min | ControlNet weights for zero deformation |
| **Phase 2** | 30 min | Quality config within 90s budget |
| **Phase 3** | 10 min | Baseline validation, gap confirmed |
| **Phase 4 Setup** | 2 hours | Data collected, Kohya_ss installed |
| **Phase 4 Training** | 3-5 hours | 5 LoRAs trained and tested |
| **Total** | **7-9 hours** | Production-ready system with 5 fabric LoRAs |

**Can be parallelized:**
- Data collection during Phase 1-3 testing
- Multiple LoRA training sessions (sequential on single GPU)

---

## ✅ Commit and Deploy

Once Phase 1-3 are complete:

```bash
# Commit optimized baseline to git
cd /workspace/app/backend
git add scripts/quick_defaults.json scripts/README.md scripts/QUALITY_FIRST_PLAN.md
git commit -m "feat: ControlNet-first testing approach with LoRA roadmap

- Updated testing workflow: ControlNet → Quality → LoRA
- Deprecated IP-Adapter presets (fights with ControlNet)
- Added comprehensive LoRA training plan
- New baseline presets for Phase 1-3 testing"

git push origin main
```

---

## 📖 Reference Documentation

- **Testing Workflow**: `backend/scripts/README.md` (sections: "Technology Stack", "Workflow: Quality-First Testing Plan", "Comprehensive LoRA Training Plan")
- **Preset Configurations**: `backend/scripts/quick_defaults.json`
- **This Plan**: `backend/scripts/QUALITY_FIRST_PLAN.md`

---

## 💡 Pro Tips

1. **Use Fixed Seeds**: Always use `--seed=42` and `--seed=1234` for A/B testing
2. **Single Cut Testing**: Use `--cuts=recto` during Phase 1-2 for 2x faster iteration
3. **Visual Comparison**: Open outputs side-by-side at 100% zoom to check fabric detail
4. **Document Everything**: Note winning parameters in `quick_defaults.json` immediately
5. **Don't Skip Phases**: Each phase builds on the previous - order is critical

---

**Ready to start Phase 1?** Pull latest changes on RunPod and run the first depth ControlNet test! 🚀
