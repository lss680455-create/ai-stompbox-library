"""
Filter, Wah & Studio EQ Stompboxes (stomp_filter_eq.py)
Includes: CryBabyAutoWah, MoogLadderFilter, SmokyBubbleFilter, StudioParametricEQ, LoFiRadioTelephone
"""
import numpy as np
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass, biquad_bandpass, peaking_eq


class CryBabyAutoWah(Stompbox):
    """Dunlop CryBaby / Mu-Tron Envelope & LFO Auto-Wah Stompbox."""
    name = "CryBaby_Auto_Wah"
    category = "Filter_EQ"

    def __init__(self, rate_hz: float = 1.4, sensitivity: float = 0.65, resonance_db: float = 9.5, **kw):
        super().__init__(rate_hz=rate_hz, sensitivity=sensitivity, resonance_db=resonance_db, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        b1 = peaking_eq(x, 520.0, self.params["resonance_db"], q=2.8)
        b2 = peaking_eq(x, 1180.0, self.params["resonance_db"], q=3.2)
        b3 = peaking_eq(x, 2150.0, self.params["resonance_db"], q=3.5)
        w = 0.5 + 0.5 * np.sin(2 * np.pi * self.params["rate_hz"] * t)
        return (1.0 - w)[:, None] * b1 + (0.5 * b2) + w[:, None] * b3


class MoogLadderFilter(Stompbox):
    """24dB/Octave 4-Pole Resonant Lowpass Filter with Warm Transistor Drive."""
    name = "Moog_24dB_Ladder_Filter"
    category = "Filter_EQ"

    def __init__(self, cutoff_hz: float = 1650.0, resonance: float = 0.45, drive: float = 1.35, **kw):
        super().__init__(cutoff_hz=cutoff_hz, resonance=resonance, drive=drive, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        fc = float(np.clip(self.params["cutoff_hz"], 60.0, 12000.0))
        res_db = self.params["resonance"] * 12.0
        y = np.tanh(x * self.params["drive"])
        y = peaking_eq(y, fc, res_db, q=2.6)
        return biquad_lowpass(y, fc, order=4)


class SmokyBubbleFilter(Stompbox):
    """Denki Groove / Yoshinori Sunahara 'Smoky Bubbles' Liquid Resonant Filter Modulator."""
    name = "SmokyBubble_Liquid_Filter"
    category = "Filter_EQ"

    def __init__(self, bubble_rate_hz: float = 3.2, depth: float = 0.72, mix: float = 0.65, **kw):
        super().__init__(mix=mix, bubble_rate_hz=bubble_rate_hz, depth=depth, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        r = self.params["bubble_rate_hz"]
        f_low = biquad_bandpass(x, 320.0, 880.0, order=2)
        f_mid = biquad_bandpass(x, 780.0, 1950.0, order=2)
        f_hi = biquad_bandpass(x, 1650.0, 3800.0, order=2)
        w1 = 0.5 + 0.5 * np.sin(2 * np.pi * r * t)
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (r * 1.37) * t)
        return np.tanh((w1[:, None] * f_low + 0.8 * f_mid + w2[:, None] * f_hi) * 2.1)


class StudioParametricEQ(Stompbox):
    """4-Band Studio Parametric Equalizer + High/Low Cut."""
    name = "Studio_Parametric_EQ"
    category = "Filter_EQ"

    def __init__(self, hpf_hz: float = 40.0, low_db: float = 0.0, mid_hz: float = 1000.0, mid_db: float = 0.0, high_db: float = 0.0, lpf_hz: float = 16000.0, **kw):
        super().__init__(hpf_hz=hpf_hz, low_db=low_db, mid_hz=mid_hz, mid_db=mid_db, high_db=high_db, lpf_hz=lpf_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        y = biquad_highpass(x, self.params["hpf_hz"], 2)
        y = peaking_eq(y, 120.0, self.params["low_db"], q=0.7)
        y = peaking_eq(y, self.params["mid_hz"], self.params["mid_db"], q=1.1)
        y = peaking_eq(y, 4800.0, self.params["high_db"], q=0.7)
        return biquad_lowpass(y, self.params["lpf_hz"], 2)


class LoFiRadioTelephone(Stompbox):
    """Nostalgic AM Radio / Vinyl Intro Bandpass & Warm Saturation Box."""
    name = "LoFi_Radio_Telephone"
    category = "Filter_EQ"

    def __init__(self, low_hz: float = 380.0, high_hz: float = 2850.0, drive: float = 1.6, **kw):
        super().__init__(low_hz=low_hz, high_hz=high_hz, drive=drive, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(biquad_bandpass(x, self.params["low_hz"], self.params["high_hz"], order=2) * self.params["drive"])
