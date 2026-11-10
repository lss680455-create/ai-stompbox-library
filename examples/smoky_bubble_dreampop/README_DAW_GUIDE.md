# Smoky Bubble Dream Pop — DAW 工程导入与制作说明

## 1. 工程全局参数
- **BPM（速度）**：`98.0 BPM`（带 16 分音符微醺 Swing `+2.4%`）
- **拍号**：`4/4`
- **调性**：**E Lydian / B Major**（核心和弦循环：`Emaj9` → `F#6/9` → `D#m11` → `G#m9`，每和弦 2 小节，8 小节一轮）
- **总长度**：48 小节 + 混响尾音（约 `2:03`，采样率 `44.1 kHz / 16-bit Stereo`）

## 2. 文件清单
- **母带总轨 (Master WAV)**：`smoky_bubble_dreampop_master.wav`
- **音频分轨 (`stems/` 目录)**：
  1. `01_Drums_Smoky_Groove.wav`：参考電気グルーヴ《SMOKY BUBBLES》（石野卓球 & 砂原良徳 1997《A》）的松弛 Breakbeat 鼓组（含前奏与间奏水下低通滤波动态、Rimshot 边击、幽灵军鼓 Ghost Notes 与摇摆踩镲）
  2. `02_Smoky_Bubble_Perc_Synth.wav`：砂原良徳式模拟滤波器气泡共振点缀（挂附点八分音符 Ping-Pong Delay）
  3. `03_Guitar_Rhythm_Jazzmaster.wav`：左声道（`-28%`）Jazzmaster 风格扩展和弦扫弦（含弦间真实扫弦时间差与摇把微颤音）
  4. `04_Guitar_Arp_Chorus.wav`：右声道（`+32%`）清亮 Chorus + 附点八分延迟分解和弦吉他
  5. `05_Guitar_Lead_Dream.wav`：副歌（第 17–24 小节）与高潮（第 33–44 小节）漂浮感主音吉他旋律线
  6. `06_Guitar_Shoegaze_Swells.wav`：反向包络（Reverse Volume Swell）与八度泛音氛围音墙吉他
  7. `07_Bass_Warm.wav`：与底鼓咬合的温暖指弹/模拟合成低音
- **MIDI 分轨与总轨 (`midi/` 目录)**：
  - `smoky_bubble_dreampop_all_tracks.mid`（Type 1 多轨合并 MIDI，拖入 Ableton Live / Logic / Cubase / FL Studio 自动分轨并读取 98 BPM 速度轨）
  - 各独立乐器单轨 `.mid`（`01_Drums_Smoky_Groove.mid` 至 `07_Bass_Warm.mid`）

## 3. 宿主软件（DAW）替换音源与效果器链建议
1. **鼓组轨 (`01_Drums_Smoky_Groove.mid`)**：
   - 映射遵循标准 GM Drum Map：`C1(36)` 底鼓、`C#1(37)` 边击 Rimshot、`D1(38)` 主军鼓、`E1(40)` 幽灵音 Ghost Snare、`F#1(42)` 闭镲、`A#1(46)` 开镲。
   - 建议选用 **TR-808/909 混搭 Lo-Fi 采样鼓** 或 **Addictive Drums (Indie / Breakbeat 预设)**，总线加轻度磁带饱和与约 `1800 Hz` 的自动化低通滤波（第 1–4 小节、第 25–28 小节）。
2. **节奏与分解吉他 (`03` / `04`)**：
   - 推荐 **Jazzmaster / Strat 颈拾音器清音** → **Boss CE-2 / Roland Dimension D 合唱**（Rate `0.6–0.85 Hz`, Depth `45%`）→ **附点八分乒乓延迟**（约 `459 ms`, Feedback `42%`）→ **Valhalla VintageVerb / Shimmer**（Decay `3.5s`, Mix `35–42%`）。
3. **主音与音墙吉他 (`05` / `06`)**：
   - `06_Guitar_Shoegaze_Swells` 可挂载 **反向混响 (Reverse Reverb)** 或 **Slow Gear 慢门包络 + 大教堂八度微光混响 (Shimmer Reverb)**。
