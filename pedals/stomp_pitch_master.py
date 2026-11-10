"""
Pitch Shifting, Harmonizer & Master Tape Stompboxes (stomp_pitch_master.py)
Includes: PolyOctavePOG, MicroPitchDetune, ReelToReelTapeMaster
"""
import numpy as np
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass, peaking_eq


def _resample_pitch_grain(x: np.ndarray, ratio: float, grain_size: int = 2048) -> np.ndarray:
    """Overlap-add synchronous granular pitch shifter (preserves duration)."""
    n = len(x)
    out = np.zeros_like(x)
    hop = grain_size // 2
    win = np.hanning(grain_size)[:, None]
    src_idx = np.linspace(0, grain_size - 1, grain_size)
    read_idx = np.clip(src_idx * ratio, 0, grain_size - 1)
    for start in range(0, n - grain_size, hop):
        chunk = x[start : start + grain_size]
        l_ch = np.interp(src_idx, np.linspace(0, grain_size - 1, int(grain_size / ratio)), chunk[: int(grain_size / ratio), 0]) if ratio < 1.0 else np.interp(read_idx, src_idx, chunk[:, 0])
        r_ch = np.interp(src_idx, np.linspace(0, grain_size - 1, int(grain_size / ratio)), chunk[: int(grain_size / ratio), 1]) if ratio < 1.0 else np.interp(read_idx, src_idx, chunk[:, 1])
        out[start : start + grain_size] += np.column_stack([l_ch, r_ch]) * win
    return out


class PolyOctavePOG(Stompbox):
    """EHX POG / Boss OC-2 Polyphonic Sub-Octave + Octave-Up Generator."""
    name = "EHX_POG_Poly_Octaver"
    category = "Pitch"

    def __init__(self, dry_level: float = 0.8, sub_octave: float = 0.45, up_octave: float = 0.4, **kw):
        super().__init__(mix=1.0, dry_level=dry_level, sub_octave=sub_octave, up_octave=up_octave, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        sub = biquad_lowpass(_resample_pitch_grain(x, 0.5), 900.0, 2) if self.params["sub_octave"] > 0.01 else 0.0
        up = biquad_highpass(_resample_pitch_grain(x, 2.0), 250.0, 1) if self.params["up_octave"] > 0.01 else 0.0
        return self.params["dry_level"] * x + self.params["sub_octave"] * sub + self.params["up_octave"] * up


class MicroPitchDetune(Stompbox):
    """Eventide H910/H3000 Stereo Dual Micro-Pitch Detune Widener (±cents)."""
    name = "Eventide_MicroPitch_Detune"
    category = "Pitch"

    def __init__(self, cents: float = 9.5, delay_ms: float = 14.0, mix: float = 0.45, **kw):
        super().__init__(mix=mix, cents=cents, delay_ms=delay_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        ratio_up = 2.0 ** (self.params["cents"] / 1200.0)
        ratio_dn = 2.0 ** (-self.params["cents"] / 1200.0)
        up = _resample_pitch_grain(x, ratio_up)
        dn = _resample_pitch_grain(x, ratio_dn)
        d = max(1, int(self.params["delay_ms"] * 0.001 * SR))
        wl = np.pad(up[:, 0], (d, 0))[: len(x)]
        wr = np.pad(dn[:, 1], (int(d * 1.25), 0))[: len(x)]
        return np.column_stack([wl, wr])


class ReelToReelTapeMaster(Stompbox):
    """Studer A800 / Ampex ATR-102 Master Reel-to-Reel Tape Saturation, Head Bump & Wow/Flutter."""
    name = "Studer_ReelToReel_Tape_Master"
    category = "Master"

    def __init__(self, drive: float = 1.25, head_bump_db: float = 2.2, wow_depth_ms: float = 0.35, tape_hiss: float = 0.0, **kw):
        super().__init__(mix=1.0, drive=drive, head_bump_db=head_bump_db, wow_depth_ms=wow_depth_ms, tape_hiss=tape_hiss, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        y = biquad_highpass(x, 26.0, 2)
        y = peaking_eq(y, 68.0, self.params["head_bump_db"], q=1.2)
        y = np.tanh(y * self.params["drive"])
        y = biquad_lowpass(y, 16500.0, 1)
        if self.params["wow_depth_ms"] > 0.01:
            idx = np.arange(n, dtype=np.float64)
            mod = (self.params["wow_depth_ms"] * 0.001 * SR) * np.sin(2 * np.pi * 0.85 * t)
            pos = np.clip(idx - mod, 0, n - 1)
            y = np.column_stack([np.interp(pos, idx, y[:, 0]), np.interp(pos, idx, y[:, 1])])
        if self.params["tape_hiss"] > 0.0001:
            rng = np.random.default_rng(800)
            y += biquad_lowpass(rng.standard_normal(y.shape), 9500.0, 1) * self.params["tape_hiss"]
        return y
