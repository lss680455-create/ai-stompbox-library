"""
Overdrive, Distortion & Fuzz Stompboxes (stomp_drive_fuzz.py)
Includes: TubeScreamerTS808, BluesbreakerDrive, ProCoRatDistortion, BigMuffPiFuzz, OctaviaFuzz, LoFiBitcrusher
"""
import numpy as np
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass, peaking_eq


class TubeScreamerTS808(Stompbox):
    """Ibanez TS-808 style mid-hump overdrive with asymmetrical silicon diode soft-clipping."""
    name = "TubeScreamer_TS808"
    category = "Drive_Fuzz"

    def __init__(self, drive: float = 0.55, tone: float = 0.6, **kw):
        super().__init__(drive=drive, tone=tone, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        pre = biquad_highpass(x, 720.0, order=1)
        g = 1.5 + self.params["drive"] * 9.0
        clipped = np.tanh(g * (pre + 0.12 * (pre ** 2)))
        cutoff = 1200.0 + self.params["tone"] * 3800.0
        return biquad_lowpass(clipped, cutoff, order=1) * 0.78


class BluesbreakerDrive(Stompbox):
    """Marshall Bluesbreaker / JHS Morning Glory style transparent edge-of-breakup overdrive."""
    name = "Bluesbreaker_Transparent_OD"
    category = "Drive_Fuzz"

    def __init__(self, drive: float = 0.42, tone: float = 0.65, **kw):
        super().__init__(drive=drive, tone=tone, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        g = 1.2 + self.params["drive"] * 4.2
        y = np.arctan(g * (x + 0.08 * (x ** 2))) * (2.0 / np.pi)
        return biquad_lowpass(y, 2200.0 + self.params["tone"] * 4500.0, order=1)


class ProCoRatDistortion(Stompbox):
    """ProCo RAT style op-amp slew-rate hard clipping + reverse Filter control."""
    name = "ProCo_RAT_Distortion"
    category = "Drive_Fuzz"

    def __init__(self, distortion: float = 0.65, filter_knob: float = 0.45, **kw):
        super().__init__(distortion=distortion, filter_knob=filter_knob, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        pre = peaking_eq(biquad_highpass(x, 120.0, order=1), 1100.0, 5.0, q=0.9)
        g = 2.5 + self.params["distortion"] * 18.0
        hard = np.clip(pre * g, -0.78, 0.82)
        soft = np.tanh(hard * 1.4)
        cutoff = 4800.0 - self.params["filter_knob"] * 3600.0
        return biquad_lowpass(soft, cutoff, order=2) * 0.72


class BigMuffPiFuzz(Stompbox):
    """Electro-Harmonix Big Muff Pi 4-stage cascaded transistor fuzz for Shoegaze / Dream Pop walls."""
    name = "BigMuff_Pi_Fuzz"
    category = "Drive_Fuzz"

    def __init__(self, sustain: float = 0.75, tone: float = 0.55, **kw):
        super().__init__(sustain=sustain, tone=tone, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        g1 = 2.0 + self.params["sustain"] * 7.5
        s1 = np.tanh(biquad_highpass(x, 75.0, order=1) * g1)
        s2 = np.tanh(biquad_lowpass(s1, 3800.0, order=1) * (g1 * 0.9))
        # Iconic Big Muff mid-scooped tone stack (blend of lowpass bass and highpass treble)
        low_branch = biquad_lowpass(s2, 480.0, order=1)
        high_branch = biquad_highpass(s2, 1250.0, order=1)
        t = self.params["tone"]
        voiced = (1.0 - t) * low_branch + t * high_branch
        return biquad_lowpass(voiced, 4400.0, order=2) * 0.85


class OctaviaFuzz(Stompbox):
    """Tycobrahe / Roger Mayer Octavia full-wave rectifier octave-up fuzz."""
    name = "Octavia_Octave_Fuzz"
    category = "Drive_Fuzz"

    def __init__(self, fuzz: float = 0.7, octave_blend: float = 0.65, **kw):
        super().__init__(fuzz=fuzz, octave_blend=octave_blend, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        g = 3.0 + self.params["fuzz"] * 10.0
        driven = np.tanh(x * g)
        rect = biquad_highpass(np.abs(driven) * 2.0 - 0.5, 160.0, order=1)
        blended = (1.0 - self.params["octave_blend"]) * driven + self.params["octave_blend"] * rect
        return biquad_lowpass(blended, 4200.0, order=2) * 0.7


class LoFiBitcrusher(Stompbox):
    """Lo-Fi Sample Rate Reducer & Bit-Depth Crusher for nostalgic indie/electronic textures."""
    name = "LoFi_Bitcrusher"
    category = "Drive_Fuzz"

    def __init__(self, bits: float = 10.0, downsample: int = 3, **kw):
        super().__init__(bits=bits, downsample=downsample, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        step = max(1, int(self.params["downsample"]))
        y = x.copy()
        if step > 1:
            idx = (np.arange(len(x)) // step) * step
            y = y[idx]
        levels = 2.0 ** max(2.0, float(self.params["bits"]))
        return np.round(y * levels) / levels
