"""
Reverb, Shimmer & Shoegaze Wall Stompboxes (stomp_reverb.py)
Includes: FenderSpringReverb, EMT140PlateReverb, HallRoomReverb, CathedralShimmerReverb,
          ReverseReverbMBV, ShoegazeDistortedReverb, GatedReverb80s
"""
import numpy as np
from scipy import signal
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass, biquad_bandpass


def _convolve_stereo(x: np.ndarray, ir_l: np.ndarray, ir_r: np.ndarray) -> np.ndarray:
    n = len(x)
    ir_l = ir_l / (np.sqrt(np.sum(ir_l ** 2)) + 1e-9)
    ir_r = ir_r / (np.sqrt(np.sum(ir_r ** 2)) + 1e-9)
    wl = signal.fftconvolve(x[:, 0], ir_l, mode="full")[:n]
    wr = signal.fftconvolve(x[:, 1], ir_r, mode="full")[:n]
    return np.column_stack([wl, wr])


class FenderSpringReverb(Stompbox):
    """'63 Fender Tube Spring Tank Reverb with metallic drip & dispersion."""
    name = "Fender_63_Spring_Reverb"
    category = "Reverb"

    def __init__(self, dwell: float = 0.65, tone_hz: float = 3600.0, mix: float = 0.35, **kw):
        super().__init__(mix=mix, dwell=dwell, tone_hz=tone_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(63)
        ir_len = int(SR * (1.2 + self.params["dwell"] * 1.4))
        t = np.arange(ir_len) / SR
        drip = np.sin(2 * np.pi * (1800.0 * np.exp(-t * 14.0)) * t) * np.exp(-t * 18.0) * 0.4
        env = np.exp(-t / (0.35 + self.params["dwell"] * 0.55))
        ir_l = biquad_bandpass(rng.standard_normal(ir_len) * env + drip, 180.0, self.params["tone_hz"])
        ir_r = biquad_bandpass(rng.standard_normal(ir_len) * env + drip, 180.0, self.params["tone_hz"])
        return _convolve_stereo(x, ir_l, ir_r)


class EMT140PlateReverb(Stompbox):
    """Dense, lush studio Plate Reverb for vocals, snares, and lead guitars."""
    name = "EMT140_Studio_Plate_Reverb"
    category = "Reverb"

    def __init__(self, decay_sec: float = 2.2, predelay_ms: float = 18.0, mix: float = 0.36, **kw):
        super().__init__(mix=mix, decay_sec=decay_sec, predelay_ms=predelay_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(140)
        pre = int(self.params["predelay_ms"] * 0.001 * SR)
        ir_len = int(SR * min(4.5, self.params["decay_sec"] * 1.5))
        t = np.arange(ir_len) / SR
        env = np.exp(-t / max(0.2, self.params["decay_sec"] * 0.65)) * (1.0 - np.exp(-t * 95.0))
        ir_l = np.pad(biquad_bandpass(rng.standard_normal(ir_len) * env, 140.0, 7200.0), (pre, 0))
        ir_r = np.pad(biquad_bandpass(rng.standard_normal(ir_len) * env, 140.0, 7200.0), (pre, 0))
        return _convolve_stereo(x, ir_l, ir_r)


class CathedralShimmerReverb(Stompbox):
    """Strymon BigSky / Eno style Cathedral Hall + Octave-Up Shimmer Feedback."""
    name = "Cathedral_Shimmer_Reverb"
    category = "Reverb"

    def __init__(self, decay_sec: float = 3.8, shimmer: float = 0.28, high_damp_hz: float = 5200.0, mix: float = 0.48, **kw):
        super().__init__(mix=mix, decay_sec=decay_sec, shimmer=shimmer, high_damp_hz=high_damp_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(1997)
        ir_len = int(SR * min(5.5, self.params["decay_sec"]))
        t = np.arange(ir_len) / SR
        env = np.exp(-t / (self.params["decay_sec"] * 0.45)) * (1.0 - np.exp(-t * 32.0))
        ir_l = biquad_bandpass(rng.standard_normal(ir_len) * env, 150.0, self.params["high_damp_hz"])
        ir_r = biquad_bandpass(rng.standard_normal(ir_len) * env, 150.0, self.params["high_damp_hz"])
        wet = _convolve_stereo(x, ir_l, ir_r)
        sh = self.params["shimmer"]
        if sh > 0.01:
            n = len(wet)
            half = wet[::2]
            oct_up = np.zeros_like(wet)
            oct_up[: len(half)] = half
            oct_wet = _convolve_stereo(biquad_bandpass(oct_up, 550.0, 6200.0), ir_r, ir_l)
            wet = wet + sh * oct_wet
        return wet


class ReverseReverbMBV(Stompbox):
    """My Bloody Valentine / Yamaha SPX90 Reverse Envelope Early-Reflections Reverb."""
    name = "MBV_Reverse_Reverb"
    category = "Reverb"

    def __init__(self, swell_ms: float = 380.0, mix: float = 0.65, **kw):
        super().__init__(mix=mix, swell_ms=swell_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(1991)
        ir_len = max(512, int(self.params["swell_ms"] * 0.001 * SR))
        t = np.linspace(0.0, 1.0, ir_len)
        env = (t ** 2.6) * np.exp(-(1.0 - t) * 1.5)
        ir_l = biquad_bandpass(rng.standard_normal(ir_len) * env, 180.0, 4800.0)
        ir_r = biquad_bandpass(rng.standard_normal(ir_len) * env, 180.0, 4800.0)
        return _convolve_stereo(x, ir_l, ir_r)


class ShoegazeDistortedReverb(Stompbox):
    """Complete Pre-Reverb -> Asymmetrical Tube/Fuzz Saturation -> 2x12 Cabinet -> Post Shimmer Wall."""
    name = "Shoegaze_Distorted_Reverb_Wall"
    category = "Reverb"

    def __init__(self, drive: float = 2.4, pre_reverb_mix: float = 0.42, post_reverb_mix: float = 0.58, shimmer: float = 0.25, **kw):
        super().__init__(mix=1.0, drive=drive, pre_reverb_mix=pre_reverb_mix, post_reverb_mix=post_reverb_mix, shimmer=shimmer, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        pre = ReverseReverbMBV(swell_ms=340.0, mix=self.params["pre_reverb_mix"])(x)
        g = self.params["drive"]
        sat = np.tanh(g * (pre + 0.14 * (pre ** 2)))
        cab = biquad_lowpass(biquad_highpass(sat, 85.0, 2), 4450.0, 2)
        return CathedralShimmerReverb(decay_sec=3.8, shimmer=self.params["shimmer"], mix=self.params["post_reverb_mix"])(cab)


class GatedReverb80s(Stompbox):
    """Non-linear Gated Reverb for Cocteau Twins / 80s Dream Pop Snares & Toms."""
    name = "Gated_NonLinear_Reverb"
    category = "Reverb"

    def __init__(self, hold_ms: float = 240.0, mix: float = 0.42, **kw):
        super().__init__(mix=mix, hold_ms=hold_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(1985)
        ir_len = max(512, int(self.params["hold_ms"] * 0.001 * SR))
        t = np.linspace(0.0, 1.0, ir_len)
        env = np.where(t < 0.82, 1.0, np.exp(-(t - 0.82) * 28.0))
        ir_l = biquad_bandpass(rng.standard_normal(ir_len) * env, 160.0, 5600.0)
        ir_r = biquad_bandpass(rng.standard_normal(ir_len) * env, 160.0, 5600.0)
        return _convolve_stereo(x, ir_l, ir_r)
