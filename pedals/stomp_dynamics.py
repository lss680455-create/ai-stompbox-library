"""
Dynamics & Envelope Stompboxes (stomp_dynamics.py)
Includes: DynaCompPedal, OpticalLA2APedal, NoiseGatePedal, TransientDesignerPedal, SidechainPumperPedal
"""
import numpy as np
from scipy import signal
from stomp_core import Stompbox, SR


def _envelope_follower(mono_abs: np.ndarray, attack_ms: float, release_ms: float) -> np.ndarray:
    # Fast two-stage exponential smoothing approximation via IIR filter
    tau_rel = max(0.002, release_ms * 0.001)
    alpha = np.exp(-1.0 / (tau_rel * SR))
    b = np.array([1.0 - alpha])
    a = np.array([1.0, -alpha])
    env = signal.lfilter(b, a, mono_abs)
    return np.maximum(env, 1e-7)


class DynaCompPedal(Stompbox):
    """MXR Dyna Comp / Ross Compressor style stompbox for snappy clean guitar sustain."""
    name = "DynaComp_Compressor"
    category = "Dynamics"

    def __init__(self, sensitivity: float = 0.65, ratio: float = 4.5, attack_ms: float = 5.0, release_ms: float = 120.0, makeup_db: float = 4.5, **kw):
        super().__init__(sensitivity=sensitivity, ratio=ratio, attack_ms=attack_ms, release_ms=release_ms, makeup_db=makeup_db, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        sens = self.params["sensitivity"]
        thresh = 0.08 + (1.0 - sens) * 0.35
        ratio = self.params["ratio"]
        peak = np.max(np.abs(x), axis=1)
        env = _envelope_follower(peak, self.params["attack_ms"], self.params["release_ms"])
        gain = np.where(env > thresh, (thresh + (env - thresh) / ratio) / env, 1.0)
        makeup = 10.0 ** (self.params["makeup_db"] / 20.0)
        return np.tanh(x * gain[:, None] * makeup * 1.05)


class OpticalLA2APedal(Stompbox):
    """Smooth electro-optical studio compressor for vocals, bass, and acoustic instruments."""
    name = "Optical_LA2A_Leveler"
    category = "Dynamics"

    def __init__(self, peak_reduction: float = 0.55, makeup_db: float = 3.5, **kw):
        super().__init__(peak_reduction=peak_reduction, makeup_db=makeup_db, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        pr = self.params["peak_reduction"]
        thresh = 0.12 + (1.0 - pr) * 0.38
        rms = np.sqrt(_envelope_follower(np.mean(x ** 2, axis=1), 15.0, 260.0))
        gain = np.where(rms > thresh, (thresh / rms) ** 0.68, 1.0)
        makeup = 10.0 ** (self.params["makeup_db"] / 20.0)
        return x * gain[:, None] * makeup


class NoiseGatePedal(Stompbox):
    """Studio Noise Gate for high-gain fuzz/overdrive rigs."""
    name = "Studio_Noise_Gate"
    category = "Dynamics"

    def __init__(self, threshold_db: float = -45.0, release_ms: float = 80.0, **kw):
        super().__init__(threshold_db=threshold_db, release_ms=release_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        thresh = 10.0 ** (self.params["threshold_db"] / 20.0)
        env = _envelope_follower(np.max(np.abs(x), axis=1), 2.0, self.params["release_ms"])
        gate = np.clip((env - thresh * 0.5) / max(1e-6, thresh), 0.0, 1.0) ** 2
        return x * gate[:, None]


class TransientDesignerPedal(Stompbox):
    """SPL-style Transient Shaper to boost or soften pick attack & drum punch."""
    name = "Transient_Shaper"
    category = "Dynamics"

    def __init__(self, attack_gain: float = 0.4, sustain_gain: float = 0.0, **kw):
        super().__init__(attack_gain=attack_gain, sustain_gain=sustain_gain, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        pk = np.max(np.abs(x), axis=1)
        fast = _envelope_follower(pk, 2.0, 18.0)
        slow = _envelope_follower(pk, 25.0, 180.0)
        diff = (fast - slow) / (slow + 0.01)
        atk_mod = 1.0 + self.params["attack_gain"] * np.clip(diff, 0.0, 2.5)
        sus_mod = 1.0 + self.params["sustain_gain"] * np.clip(-diff, 0.0, 1.5)
        return x * (atk_mod * sus_mod)[:, None]


class SidechainPumperPedal(Stompbox):
    """Tempo-synced rhythmic ducking / sidechain breathing effect."""
    name = "Sidechain_Pumper"
    category = "Dynamics"

    def __init__(self, bpm: float = 98.0, depth: float = 0.55, subdivision: float = 1.0, **kw):
        super().__init__(bpm=bpm, depth=depth, subdivision=subdivision, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        period = (60.0 / self.params["bpm"]) * self.params["subdivision"]
        phase = (t % period) / period
        curve = 1.0 - self.params["depth"] * np.exp(-phase * 5.2)
        return x * curve[:, None]
