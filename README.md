# 🎸 AI Stompbox & Native Instrument Vault (`ai-stompbox-library`)

一套专为 AI 编曲、MIDI 触发与离线高保真混音设计的**“可按项目复制（Copy-on-Use）硬件建模单块效果器 + 录音室多采样原生器乐库”**。

- **38 款经典硬件单块效果器建模（`pedals/`）**：涵盖压缩、瞬态、过载/失真/法兹、经典吉他/贝斯箱头与 6 种箱体 IR、BBD 合唱/颤音/移相/镶边、阶梯低通/液体气泡滤波、模拟/磁带/乒乓/反向延迟、弹簧/板式/微光/MBV 反向混响、盯鞋失真混响音墙一体机与开盘母带磁带机。
- **16 种录音室实录多采样原生器乐 + 10 种真鼓/TR-808 采样（`instruments/` + `sample_vault/`）**：内置 91 个 44.1kHz Stereo 实录多采样根音（来自 Musyng Kite 与 Dirt-Samples），支持 `0–127` 全 MIDI 音域自动变调插值与演奏包络（`normal` / `swell` 慢门渐强 / `staccato` 断奏 / `vibrato_cents` 揉弦）。
- **零读取盲调（No-Analyze）& 按项目克隆（Copy-on-Use）**：通过 [`clone_rig.py`](clone_rig.py) 一键将单块脚本复制到每首歌独立的 `fx_rig/` 目录，一行 `from stomp_hub import *` 即可自由串联与改参，**永不污染母库**。

---

## 📸 建模原型：经典硬件单块、音箱与鼓机实拍图鉴

> 以下实拍照片均取自 Wikimedia Commons / Wikipedia 开源硬件图库，对应本库 `pedals/` 中的核心数字信号处理（DSP）建模模块：

| 硬件实拍图 | 对应本库单块类 (`stomp_hub`) | 核心电路/声学特性建模 |
| :---: | :--- | :--- |
| <img src="assets/pedals/ehx_big_muff_pi.jpg" width="220"/> | **`BigMuffPiFuzz`** / **`ShoegazeDistortedReverb`**<br>(`stomp_drive_fuzz.py` / `stomp_reverb.py`) | Electro-Harmonix Big Muff Pi 四级级联晶体管削波 + 标志性中频凹陷 Tone Stack，搭配前置反向混响构成纯正盯鞋（Shoegaze）失真混响音墙 |
| <img src="assets/pedals/ibanez_tube_screamer.jpg" width="220"/> | **`TubeScreamerTS808`**<br>(`stomp_drive_fuzz.py`) | Ibanez TS-808 经典 `720 Hz` 中频凸起（Mid-Hump）与运算放大器非对称硅二极管软削波温暖过载 |
| <img src="assets/pedals/proco_rat_distortion.jpg" width="220"/> | **`ProCoRatDistortion`**<br>(`stomp_drive_fuzz.py`) | ProCo RAT LM308 压摆率限制硬削波失真 + 反向高切 Filter 旋钮 |
| <img src="assets/pedals/boss_stompbox.jpg" width="220"/> | **`BossCE2Chorus`** / **`DimensionCChorus`** / **`PitchVibratoVB2`**<br>(`stomp_modulation.py`) | Boss / Roland 经典 BBD 斗链式模拟延迟线正交 LFO 调制立体声合唱与摇把纯音高颤音 |
| <img src="assets/pedals/mxr_phase90.jpg" width="220"/> | **`Phase90Phaser`** / **`DynaCompPedal`**<br>(`stomp_modulation.py` / `stomp_dynamics.py`) | MXR M-101 Phase 90 全通移相器与 Dyna Comp 高在位感颗粒压缩 |
| <img src="assets/pedals/dunlop_crybaby_wah.jpg" width="220"/> | **`CryBabyAutoWah`**<br>(`stomp_filter_eq.py`) | Dunlop CryBaby 经典谐振峰扫频哇音与包络跟随自动哇音 |
| <img src="assets/pedals/roland_re201_space_echo.jpg" width="220"/> | **`SpaceEchoRE201`**<br>(`stomp_delay.py`) | Roland RE-201 Space Echo 三磁头循环磁带回声（含磁带饱和、高低切老化与 Wow/Flutter 抖动） |
| <img src="assets/pedals/roland_jc120_amp.jpg" width="220"/> | **`RolandJC120Amp`** + **`CabinetSimulatorIR("2x12_JC120")`**<br>(`stomp_amp_cab.py`) | Roland JC-120 Jazz Chorus 晶体管高动态清音箱头与 2x12 银盆喇叭箱体模拟（Dream Pop 标准清音底座） |
| <img src="assets/pedals/fender_twin_reverb.jpg" width="220"/> | **`FenderTwinAmp`** + **`FenderSpringReverb`**<br>(`stomp_amp_cab.py` / `stomp_reverb.py`) | Fender '65 Twin Reverb Blackface 中频凹陷电子管清音与 '63 弹簧混响水滴感色散建模 |
| <img src="assets/pedals/vox_ac30_amp.jpg" width="220"/> | **`VoxAC30TopBoost`** + **`CabinetSimulatorIR("2x12_Celestion_Blue")`**<br>(`stomp_amp_cab.py`) | Vox AC30 甲类阴极偏置闪烁英式清音/微过载与 Celestion Blue 铝镍钴喇叭频响 |
| <img src="assets/pedals/roland_tr808.jpg" width="220"/> | **`NativeDrumKit`** (`kick_808`, `snare_808`, `rimshot`, `hat_closed`, `hat_open`)<br>(`instruments/native_instruments.py`) | Roland TR-808 经典模拟鼓机实录采样与真实原声 Breakbeat 鼓组叠层触发器 |

---

## 🎧 完整示例工程：《Smoky Bubble Dream Pop》（致敬 電気グルーヴ《SMOKY BUBBLES》）

仓库内置了一首完全使用本库 **原生器乐多采样 + 单块效果器板串联** 制作并渲染的 98 BPM Dream Pop 示范曲（位于 [`examples/smoky_bubble_dreampop/`](examples/smoky_bubble_dreampop/)）：

- **🎵 完整母带试听与下载**：
  - 无损 WAV 母带：[`examples/smoky_bubble_dreampop/smoky_bubble_STOMPBOX_SKILL_MASTER.wav`](examples/smoky_bubble_dreampop/smoky_bubble_STOMPBOX_SKILL_MASTER.wav)
  - 320kbps MP3 母带：[`examples/smoky_bubble_dreampop/smoky_bubble_STOMPBOX_SKILL_MASTER.mp3`](examples/smoky_bubble_dreampop/smoky_bubble_STOMPBOX_SKILL_MASTER.mp3)
- **🎚️ 7 条单块渲染分轨（320kbps MP3 预览）**：[`examples/smoky_bubble_dreampop/audio_stems_mp3/`](examples/smoky_bubble_dreampop/audio_stems_mp3/)
  1. `01_Drums_Stompbox_Groove.mp3` — TR-808 + 真鼓叠层 → `MoogLadderFilter`（前奏/间奏水下低通滤波）→ `TransientDesignerPedal` → `DynaCompPedal` → `EMT140PlateReverb`
  2. `02_Smoky_Bubble_Filter_Synth.mp3` — 原生颤音琴 + Rhodes 电钢 → `SmokyBubbleFilter`（砂原良徳式液体气泡共振）→ `PingPongStereoDelay` → `CathedralShimmerReverb`
  3. `03_Guitar_Rhythm_JC120_Chorus.mp3` — 原生爵士电吉他 + 25% 钢弦木吉他 → `DynaCompPedal` → `BluesbreakerDrive` → `RolandJC120Amp` → `DimensionCChorus(mode=3)` → `CathedralShimmerReverb`
  4. `04_Guitar_Arp_CE2_PingPong.mp3` — 原生清音电吉他 → `DynaCompPedal` → `RolandJC120Amp` → `BossCE2Chorus` → `PingPongStereoDelay`（附点八分）→ `CathedralShimmerReverb`
  5. `05_Guitar_Lead_SpaceEcho_Shoegaze.mp3` — 过载+清音双层电吉他 → `TubeScreamerTS808` → `FenderTwinAmp` → `PitchVibratoVB2` → `SpaceEchoRE201` → `ShoegazeDistortedReverb`
  6. `06_Guitar_Swell_BigMuff_MBV.mp3` — 慢门包络失真吉他 + 30% 交响弦乐群 → `ReverseReverbMBV`（前置反向混响）→ `BigMuffPiFuzz` → `CabinetSimulatorIR("2x12_JC120")` → `MicroPitchDetune` → `CathedralShimmerReverb`
  7. `07_Bass_Fingered_LA2A_Ampeg.mp3` — 原生指弹电贝斯 + 25% 原声木贝斯 → `OpticalLA2APedal` → `CabinetSimulatorIR("1x15_Bass_Ampeg")`
- **🎹 宿主软件多轨与分轨 MIDI**：[`examples/smoky_bubble_dreampop/midi/`](examples/smoky_bubble_dreampop/midi/)（含合并总轨 `smoky_bubble_dreampop_all_tracks.mid` 与 7 条独立乐器 `.mid`）
- **📜 编曲与单块渲染源码**：
  - 编曲乐谱生成：[`examples/smoky_bubble_dreampop/composition.py`](examples/smoky_bubble_dreampop/composition.py)
  - 单块串联渲染主脚本：[`examples/smoky_bubble_dreampop/render_via_stompbox_skill.py`](examples/smoky_bubble_dreampop/render_via_stompbox_skill.py)
  - DAW 导入与混音指南：[`examples/smoky_bubble_dreampop/README_DAW_GUIDE.md`](examples/smoky_bubble_dreampop/README_DAW_GUIDE.md)

---

## 🚀 快速开始（Copy-on-Use 克隆工作流）

### 1. 将单块与原生器乐库克隆到你的新歌曲工程
```bash
python clone_rig.py --target "./my_new_song/fx_rig" --modules all
```

### 2. 一行导入并像真实单块踏板一样串联调用
```python
import sys

sys.path.insert(0, "./my_new_song/fx_rig")
from stomp_hub import *  # 一行导入全部 38 款单块、PedalboardChain、NativeInstrument、NativeDrumKit

# 1. 调用原生器乐（支持 16 种旋律乐器 + 10 种真鼓/808 采样）
guitar = NativeInstrument("electric_guitar_jazz")
dry_chord = guitar.render_note(
    midi_pitch=64, duration_sec=2.0, velocity=0.9, vibrato_cents=10.0
)

# 2. 自由串联单块效果器板（例如：MBV 反向混响 -> Big Muff 法兹 -> JC-120 箱体 -> 四键合唱 -> 大教堂微光混响）
board = PedalboardChain([
    ReverseReverbMBV(swell_ms=380.0, mix=0.45),
    BigMuffPiFuzz(sustain=0.70, tone=0.55, mix=0.80),
    CabinetSimulatorIR("2x12_JC120"),
    DimensionCChorus(mode=3, mix=0.50),
    CathedralShimmerReverb(decay_sec=4.2, shimmer=0.28, mix=0.58),
])

wet_audio = board(dry_chord)
```
