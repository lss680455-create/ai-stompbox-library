"""
Modulation Stompboxes (stomp_modulation.py)
Includes: BossCE2Chorus, DimensionCChorus, PitchVibratoVB2, Phase90Phaser,
          ElectricMistressFlanger, OpticalTremolo, RotaryLeslieSpeaker
"""
import numpy as np
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass


def _mod_delay_line(sig_1d: np.ndarray, delay_samples: np.ndarray) -> np.ndarray:
    n = len(sig_1d)
    idx = np.arange(n, dtype=np.float64)
    read_pos = np.clip(idx - delay_samples, 0.0, n - 1.0)
    return np.interp(read_pos, idx, sig_1d)


class BossCE2Chorus(Stompbox):
    """Boss CE-2 BBD Analog Bucket-Brigade Stereo Chorus."""
    name = "Boss_CE2_Analog_Chorus"
    category = "Modulation"

    def __init__(self, rate_hz: float = 0.65, depth_ms: float = 3.2, mix: float = 0.48, **kw):
        super().__init__(mix=mix, rate_hz=rate_hz, depth_ms=depth_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        base = 0.011 * SR
        depth = self.params["depth_ms"] * 0.001 * SR
        r = self.params["rate_hz"]
        dl_l = base + depth * np.sin(2 * np.pi * r * t)
        dl_r = base + depth * np.cos(2 * np.pi * (r * 1.05) * t)
        wl = _mod_delay_line(biquad_lowpass(x[:, 0], 6800.0, 1), dl_l)
        wr = _mod_delay_line(biquad_lowpass(x[:, 1], 6800.0, 1), dl_r)
        return np.column_stack([wl, wr])


class DimensionCChorus(Stompbox):
    """Roland DC-2 Dimension C / SDD-320 Dual Cross-Phase Wide Chorus (Modes 1-4)."""
    name = "Roland_DimensionC_Chorus"
    category = "Modulation"

    def __init__(self, mode: int = 3, mix: float = 0.52, **kw):
        super().__init__(mix=mix, mode=mode, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        m = max(1, min(4, int(self.params["mode"])))
        rates = {1: 0.35, 2: 0.48, 3: 0.62, 4: 0.82}[m]
        depths = {1: 1.8, 2: 2.5, 3: 3.4, 4: 4.5}[m]
        c1 = BossCE2Chorus(rate_hz=rates, depth_ms=depths, mix=1.0)._render_wet(x)
        c2 = BossCE2Chorus(rate_hz=rates * 0.77, depth_ms=depths * 0.85, mix=1.0)._render_wet(x[:, ::-1])
        return 0.6 * c1 + 0.4 * c2


class PitchVibratoVB2(Stompbox):
    """Boss VB-2 / Jazzmaster Tremolo Arm True Pitch Vibrato (100% wet pitch glide)."""
    name = "Boss_VB2_Pitch_Vibrato"
    category = "Modulation"

    def __init__(self, rate_hz: float = 3.6, depth_ms: float = 1.65, **kw):
        super().__init__(mix=1.0, rate_hz=rate_hz, depth_ms=depth_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        mod = (0.004 + self.params["depth_ms"] * 0.001 * (1.0 + np.sin(2 * np.pi * self.params["rate_hz"] * t))) * SR
        return np.column_stack([_mod_delay_line(x[:, 0], mod), _mod_delay_line(x[:, 1], mod)])


class ElectricMistressFlanger(Stompbox):
    """EHX Deluxe Electric Mistress Liquid/Jet Flanger with resonant comb feedback."""
    name = "ElectricMistress_Flanger"
    category = "Modulation"

    def __init__(self, rate_hz: float = 0.28, range_ms: float = 3.2, color: float = 0.55, mix: float = 0.5, **kw):
        super().__init__(mix=mix, rate_hz=rate_hz, range_ms=range_ms, color=color, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        dl = (0.0012 + self.params["range_ms"] * 0.001 * (0.5 + 0.5 * np.sin(2 * np.pi * self.params["rate_hz"] * t))) * SR
        w1 = np.column_stack([_mod_delay_line(x[:, 0], dl), _mod_delay_line(x[:, 1], dl * 1.04)])
        w2 = np.column_stack([_mod_delay_line(w1[:, 0], dl), _mod_delay_line(w1[:, 1], dl * 1.04)])
        return w1 + self.params["color"] * w2


class Phase90Phaser(Stompbox):
    """MXR Phase 90 / Small Stone Sweeping Notch Phaser."""
    name = "MXR_Phase90_Phaser"
    category = "Modulation"

    def __init__(self, rate_hz: float = 0.42, depth: float = 0.75, mix: float = 0.5, **kw):
        super().__init__(mix=mix, rate_hz=rate_hz, depth=depth, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * self.params["rate_hz"] * t)
        dl1 = (0.0004 + 0.0018 * self.params["depth"] * lfo) * SR
        dl2 = (0.0009 + 0.0026 * self.params["depth"] * (1.0 - lfo)) * SR
        s1 = np.column_stack([_mod_delay_line(x[:, 0], dl1), _mod_delay_line(x[:, 1], dl2)])
        s2 = np.column_stack([_mod_delay_line(s1[:, 0], dl2), _mod_delay_line(s1[:, 1], dl1)])
        return x - 0.65 * s1 + 0.45 * s2


class OpticalTremolo(Stompbox):
    """Fender Opto-Tremolo & Harmonic Tremolo."""
    name = "Fender_Optical_Tremolo"
    category = "Modulation"

    def __init__(self, rate_hz: float = 4.2, depth: float = 0.65, harmonic_mode: bool = False, stereo_pan: float = 0.3, **kw):
        super().__init__(mix=1.0, rate_hz=rate_hz, depth=depth, harmonic_mode=harmonic_mode, stereo_pan=stereo_pan, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        d = self.params["depth"]
        phi = 2 * np.pi * self.params["rate_hz"] * t
        if self.params["harmonic_mode"]:
            low = biquad_lowpass(x, 600.0, 2)
            high = biquad_highpass(x, 600.0, 2)
            m1 = 1.0 - d * (0.5 + 0.5 * np.sin(phi))
            m2 = 1.0 - d * (0.5 - 0.5 * np.sin(phi))
            return low * m1[:, None] + high * m2[:, None]
        l_mod = 1.0 - d * (0.5 + 0.5 * np.sin(phi))
        r_mod = 1.0 - d * (0.5 + 0.5 * np.sin(phi + self.params["stereo_pan"] * np.pi))
        return np.column_stack([x[:, 0] * l_mod, x[:, 1] * r_mod])
