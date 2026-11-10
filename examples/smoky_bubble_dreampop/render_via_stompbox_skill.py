"""
Studio Audio Rendering via AI Stompbox & Native Instrument Library
Song: 'Smoky Bubble Dream Pop'
Renders 7 isolated stems using modeled hardware pedals and studio-sampled native instruments,
and mixes the final master bus through Studio Parametric EQ and Studer Reel-to-Reel Tape.
"""
import os
import sys
import numpy as np
from scipy.io import wavfile

# Add local fx_rig to path (Copy-on-Use)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FX_RIG_DIR = os.path.join(SCRIPT_DIR, "fx_rig")
sys.path.insert(0, FX_RIG_DIR)

from stomp_hub import (
    SR,
    PedalboardChain,
    TransientDesignerPedal,
    DynaCompPedal,
    OpticalLA2APedal,
    TubeScreamerTS808,
    BluesbreakerDrive,
    BigMuffPiFuzz,
    RolandJC120Amp,
    FenderTwinAmp,
    CabinetSimulatorIR,
    BossCE2Chorus,
    DimensionCChorus,
    PitchVibratoVB2,
    MoogLadderFilter,
    SmokyBubbleFilter,
    StudioParametricEQ,
    PingPongStereoDelay,
    SpaceEchoRE201,
    EMT140PlateReverb,
    CathedralShimmerReverb,
    ReverseReverbMBV,
    ShoegazeDistortedReverb,
    MicroPitchDetune,
    ReelToReelTapeMaster,
    NativeInstrument,
    NativeDrumKit,
)

from composition import (
    BPM,
    BEAT_SEC,
    TOTAL_BEATS,
    build_drum_events,
    build_guitar_rhythm_events,
    build_guitar_arp_events,
    build_guitar_lead_events,
    build_guitar_swell_events,
    build_bass_events,
)

STEMS_DIR = os.path.join(SCRIPT_DIR, "stems_stompbox_skill")
MASTER_PATH = os.path.join(SCRIPT_DIR, "smoky_bubble_STOMPBOX_SKILL_MASTER.wav")


def place_clip(buf: np.ndarray, clip: np.ndarray, start_beat: float):
    idx = max(0, int(round(start_beat * BEAT_SEC * SR)))
    if idx >= len(buf):
        return
    end = min(len(buf), idx + len(clip))
    buf[idx:end] += clip[: end - idx]


def save_wav(path: str, stereo: np.ndarray, norm_peak: float = 0.90):
    sig = stereo.copy()
    pk = np.max(np.abs(sig)) + 1e-9
    sig = sig * (norm_peak / pk)
    sig = np.clip(sig, -0.99, 0.99)
    wavfile.write(path, SR, (sig * 32767.0).astype(np.int16))


def main():
    os.makedirs(STEMS_DIR, exist_ok=True)
    total_sec = TOTAL_BEATS * BEAT_SEC + 6.0
    n_samples = int(round(total_sec * SR))
    print(f"Allocating {total_sec:.2f}s audio buffers ({n_samples} samples at {SR}Hz)...")

    # Audio buffers for 7 stems
    buf_drums = np.zeros((n_samples, 2), dtype=np.float64)
    buf_bubbles = np.zeros((n_samples, 2), dtype=np.float64)
    buf_rhy = np.zeros((n_samples, 2), dtype=np.float64)
    buf_arp = np.zeros((n_samples, 2), dtype=np.float64)
    buf_lead = np.zeros((n_samples, 2), dtype=np.float64)
    buf_swell = np.zeros((n_samples, 2), dtype=np.float64)
    buf_bass = np.zeros((n_samples, 2), dtype=np.float64)

    # -------------------------------------------------------------
    # TRACK 01: DRUMS & TRACK 02: SMOKY BUBBLES
    # -------------------------------------------------------------
    print("Rendering Track 01 Drums & Track 02 Smoky Bubbles...")
    drum_kit = NativeDrumKit()
    inst_vib = NativeInstrument("vibraphone")
    inst_ep = NativeInstrument("electric_piano_1")

    drum_events = build_drum_events()
    for e in drum_events:
        v = (e.vel / 127.0) ** 1.15
        if e.tag == "kick":
            k1 = drum_kit.hit("kick_808", velocity=v * 0.78, pan=0.0)
            k2 = drum_kit.hit("kick_acoustic", velocity=v * 0.65, pan=0.0)
            place_clip(buf_drums, k1, e.beat)
            place_clip(buf_drums, k2, e.beat)
        elif e.tag == "rim":
            place_clip(buf_drums, drum_kit.hit("rimshot", velocity=v * 0.82, pan=-0.05), e.beat)
        elif e.tag == "snare":
            s1 = drum_kit.hit("snare_808", velocity=v * 0.68, pan=0.0)
            s2 = drum_kit.hit("snare_acoustic", velocity=v * 0.75, pan=0.04)
            place_clip(buf_drums, s1, e.beat)
            place_clip(buf_drums, s2, e.beat)
        elif e.tag == "ghost":
            place_clip(buf_drums, drum_kit.hit("snare_ghost", velocity=v * 0.52, pan=0.08), e.beat)
        elif e.tag == "hat":
            place_clip(buf_drums, drum_kit.hit("hat_closed", velocity=v * 0.58, pan=e.pan), e.beat)
        elif e.tag == "open_hat":
            place_clip(buf_drums, drum_kit.hit("hat_open", velocity=v * 0.62, pan=e.pan), e.beat)
        elif e.tag == "bubble":
            # Track 02: Vibraphone + Electric Piano 1 layered
            dur_sec = max(0.28, e.dur * BEAT_SEC)
            s_vib = inst_vib.render_note(e.pitch, dur_sec, velocity=v * 0.72, pan=e.pan, articulation="staccato")
            s_ep = inst_ep.render_note(e.pitch, dur_sec, velocity=v * 0.60, pan=e.pan, articulation="staccato")
            min_len = min(len(s_vib), len(s_ep))
            s_bub = 0.65 * s_vib[:min_len] + 0.35 * s_ep[:min_len]
            place_clip(buf_bubbles, s_bub, e.beat)

    # Apply MoogLadderFilter on Drum Intro (bars 0-4) and Breakdown (bars 24-28)
    print("Applying MoogLadderFilter automation on Drums Intro & Breakdown...")
    moog = MoogLadderFilter(cutoff_hz=1650.0, resonance=0.45)
    filtered_drums = moog(buf_drums)

    env_filter = np.zeros(n_samples, dtype=np.float64)
    # Intro bars 0-4 (beats 0 to 16)
    b_intro_end = int(16.0 * BEAT_SEC * SR)
    b_fade = int(0.5 * BEAT_SEC * SR)
    env_filter[: b_intro_end - b_fade] = 1.0
    env_filter[b_intro_end - b_fade : b_intro_end] = np.linspace(1.0, 0.0, b_fade)

    # Breakdown bars 24-28 (beats 96 to 112)
    b_bk_start = int(96.0 * BEAT_SEC * SR)
    b_bk_end = int(112.0 * BEAT_SEC * SR)
    env_filter[b_bk_start : b_bk_start + b_fade] = np.linspace(0.0, 1.0, b_fade)
    env_filter[b_bk_start + b_fade : b_bk_end - b_fade] = 1.0
    env_filter[b_bk_end - b_fade : b_bk_end] = np.linspace(1.0, 0.0, b_fade)

    buf_drums = (1.0 - env_filter[:, None]) * buf_drums + env_filter[:, None] * filtered_drums

    # Drum bus chain
    print("Processing Drum Bus through TransientDesigner -> DynaComp -> EMT140PlateReverb...")
    drum_bus_chain = PedalboardChain([
        TransientDesignerPedal(attack_gain=0.25),
        DynaCompPedal(sensitivity=0.5, mix=0.45),
        EMT140PlateReverb(decay_sec=1.4, mix=0.14),
    ])
    buf_drums = drum_bus_chain(buf_drums)

    # Track 02 Smoky Bubble Chain
    print("Processing Smoky Bubble Texture through SmokyBubbleFilter -> PingPongStereoDelay -> CathedralShimmerReverb...")
    bubble_chain = PedalboardChain([
        SmokyBubbleFilter(bubble_rate_hz=3.4, mix=0.75),
        PingPongStereoDelay(delay_ms=459.0, feedback=0.48, mix=0.42),
        CathedralShimmerReverb(decay_sec=3.2, shimmer=0.20, mix=0.38),
    ])
    buf_bubbles = bubble_chain(buf_bubbles)

    # -------------------------------------------------------------
    # TRACK 03: GUITAR RHYTHM
    # -------------------------------------------------------------
    print("Rendering Track 03 Guitar Rhythm (Jazzmaster + Steel Acoustic layer)...")
    inst_jazz = NativeInstrument("electric_guitar_jazz")
    inst_steel = NativeInstrument("acoustic_guitar_steel")
    rhy_events = build_guitar_rhythm_events()
    for e in rhy_events:
        dur_sec = e.dur * BEAT_SEC
        v = e.vel / 127.0
        s_jz = inst_jazz.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan)
        s_st = inst_steel.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan)
        min_len = min(len(s_jz), len(s_st))
        s_rhy = 0.75 * s_jz[:min_len] + 0.25 * s_st[:min_len]
        place_clip(buf_rhy, s_rhy, e.beat)

    print("Processing Guitar Rhythm through DynaComp -> Bluesbreaker -> RolandJC120 -> DimensionC -> CathedralShimmer...")
    rhy_chain = PedalboardChain([
        DynaCompPedal(sensitivity=0.62),
        BluesbreakerDrive(drive=0.28, mix=0.55),
        RolandJC120Amp(bright=True),
        DimensionCChorus(mode=3, mix=0.52),
        CathedralShimmerReverb(decay_sec=3.4, shimmer=0.12, mix=0.36),
    ])
    buf_rhy = rhy_chain(buf_rhy)

    # -------------------------------------------------------------
    # TRACK 04: GUITAR ARPEGGIO
    # -------------------------------------------------------------
    print("Rendering Track 04 Guitar Arpeggio (Strat Clean)...")
    inst_clean = NativeInstrument("electric_guitar_clean")
    arp_events = build_guitar_arp_events()
    for e in arp_events:
        dur_sec = e.dur * BEAT_SEC
        v = e.vel / 127.0
        s_arp = inst_clean.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan)
        place_clip(buf_arp, s_arp, e.beat)

    print("Processing Guitar Arpeggio through DynaComp -> RolandJC120 -> BossCE2 -> PingPong -> CathedralShimmer...")
    arp_chain = PedalboardChain([
        DynaCompPedal(sensitivity=0.68),
        RolandJC120Amp(bright=True),
        BossCE2Chorus(rate_hz=0.78, depth_ms=3.1, mix=0.48),
        PingPongStereoDelay(delay_ms=459.0, feedback=0.46, mix=0.36),
        CathedralShimmerReverb(decay_sec=3.8, shimmer=0.22, mix=0.42),
    ])
    buf_arp = arp_chain(buf_arp)

    # -------------------------------------------------------------
    # TRACK 05: GUITAR LEAD
    # -------------------------------------------------------------
    print("Rendering Track 05 Guitar Lead (Overdriven + Clean vibrato=10 cents)...")
    inst_od = NativeInstrument("overdriven_guitar")
    lead_events = build_guitar_lead_events()
    for e in lead_events:
        dur_sec = e.dur * BEAT_SEC
        v = e.vel / 127.0
        s_od = inst_od.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan, vibrato_cents=10.0)
        s_cl = inst_clean.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan, vibrato_cents=10.0)
        min_len = min(len(s_od), len(s_cl))
        s_lead = 0.65 * s_od[:min_len] + 0.35 * s_cl[:min_len]
        place_clip(buf_lead, s_lead, e.beat)

    print("Processing Guitar Lead through TS808 -> FenderTwin -> PitchVibratoVB2 -> SpaceEchoRE201 -> ShoegazeDistortedReverb...")
    lead_chain = PedalboardChain([
        TubeScreamerTS808(drive=0.45, tone=0.62, mix=0.7),
        FenderTwinAmp(drive=0.3),
        PitchVibratoVB2(rate_hz=3.8, depth_ms=1.2, mix=0.35),
        SpaceEchoRE201(base_delay_ms=306.0, feedback=0.48, mix=0.36),
        ShoegazeDistortedReverb(drive=1.85, pre_reverb_mix=0.28, post_reverb_mix=0.48, shimmer=0.24),
    ])
    buf_lead = lead_chain(buf_lead)

    # -------------------------------------------------------------
    # TRACK 06: GUITAR SHOEGAZE SWELL WALL
    # -------------------------------------------------------------
    print("Rendering Track 06 Guitar Shoegaze Swell Wall (Distortion Guitar + String Ensemble swell)...")
    inst_dist = NativeInstrument("distortion_guitar")
    inst_str = NativeInstrument("string_ensemble_1")
    swell_events = build_guitar_swell_events()
    for e in swell_events:
        dur_sec = e.dur * BEAT_SEC
        v = e.vel / 127.0
        s_dst = inst_dist.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan, articulation="swell")
        s_str = inst_str.render_note(e.pitch, dur_sec, velocity=v, pan=e.pan, articulation="swell")
        min_len = min(len(s_dst), len(s_str))
        s_sw = 0.70 * s_dst[:min_len] + 0.30 * s_str[:min_len]
        place_clip(buf_swell, s_sw, e.beat)

    print("Processing Shoegaze Swell Wall through MBV ReverseReverb -> BigMuffPi -> 2x12 Cab -> MicroPitchDetune -> CathedralShimmer...")
    swell_chain = PedalboardChain([
        ReverseReverbMBV(swell_ms=380.0, mix=0.55),
        BigMuffPiFuzz(sustain=0.68, tone=0.52, mix=0.75),
        CabinetSimulatorIR("2x12_JC120"),
        MicroPitchDetune(cents=9.5, mix=0.48),
        CathedralShimmerReverb(decay_sec=4.5, shimmer=0.36, mix=0.65),
    ])
    buf_swell = swell_chain(buf_swell)

    # -------------------------------------------------------------
    # TRACK 07: BASS
    # -------------------------------------------------------------
    print("Rendering Track 07 Bass (Fingered Electric Bass + Acoustic Bass layer)...")
    inst_ebass = NativeInstrument("electric_bass_finger")
    inst_abass = NativeInstrument("acoustic_bass")
    bass_events = build_bass_events()
    for e in bass_events:
        dur_sec = e.dur * BEAT_SEC
        v = e.vel / 127.0
        s_eb = inst_ebass.render_note(e.pitch, dur_sec, velocity=v, pan=0.0)
        s_ab = inst_abass.render_note(e.pitch, dur_sec, velocity=v, pan=0.0)
        min_len = min(len(s_eb), len(s_ab))
        s_bs = 0.75 * s_eb[:min_len] + 0.25 * s_ab[:min_len]
        place_clip(buf_bass, s_bs, e.beat)

    print("Processing Bass through Optical LA-2A -> Ampeg 1x15 Cabinet...")
    bass_chain = PedalboardChain([
        OpticalLA2APedal(peak_reduction=0.6, makeup_db=3.0),
        CabinetSimulatorIR("1x15_Bass_Ampeg"),
    ])
    buf_bass = bass_chain(buf_bass)

    # -------------------------------------------------------------
    # SAVE ALL 7 STEMS
    # -------------------------------------------------------------
    stems = [
        ("01_Drums_Stompbox_Groove.wav", buf_drums, 0.88),
        ("02_Smoky_Bubble_Filter_Synth.wav", buf_bubbles, 0.74),
        ("03_Guitar_Rhythm_JC120_Chorus.wav", buf_rhy, 0.80),
        ("04_Guitar_Arp_CE2_PingPong.wav", buf_arp, 0.78),
        ("05_Guitar_Lead_SpaceEcho_Shoegaze.wav", buf_lead, 0.82),
        ("06_Guitar_Swell_BigMuff_MBV.wav", buf_swell, 0.76),
        ("07_Bass_Fingered_LA2A_Ampeg.wav", buf_bass, 0.84),
    ]

    print("\nExporting 7 Stems to stems_stompbox_skill/...")
    for filename, sig, norm_pk in stems:
        stem_path = os.path.join(STEMS_DIR, filename)
        save_wav(stem_path, sig, norm_peak=norm_pk)
        print(f"  -> Exported stem: {filename} ({os.path.getsize(stem_path) / 1024 / 1024:.2f} MB)")

    # -------------------------------------------------------------
    # MASTER BUS MIX & MASTERING CHAIN
    # -------------------------------------------------------------
    print("\nMixing Master Bus with musical balance...")
    master = (
        1.00 * buf_drums
        + 0.62 * buf_bubbles
        + 0.78 * buf_rhy
        + 0.76 * buf_arp
        + 0.82 * buf_lead
        + 0.58 * buf_swell
        + 0.82 * buf_bass
    )

    print("Mastering through StudioParametricEQ -> Studer ReelToReelTapeMaster...")
    master_chain = PedalboardChain([
        StudioParametricEQ(hpf_hz=30.0, low_db=1.2, mid_hz=420.0, mid_db=-1.2, high_db=1.5, lpf_hz=16500.0),
        ReelToReelTapeMaster(drive=1.22, head_bump_db=2.0, wow_depth_ms=0.25, tape_hiss=0.0003),
    ])
    master = master_chain(master)

    save_wav(MASTER_PATH, master, norm_peak=0.95)
    print(f"\nSuccessfully created Master WAV: {MASTER_PATH} ({os.path.getsize(MASTER_PATH) / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    main()
