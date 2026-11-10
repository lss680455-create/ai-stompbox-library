"""
AI Stompbox & Native Instrument Library — Core Architecture (stomp_core.py)
Copy-on-Use Design: Copy this file and any stomp_*.py / native_instruments.py
into a song project folder to tweak parameters freely without altering the master vault.
"""
from typing import List, Dict, Any
import numpy as np
from scipy import signal

SR = 44100


def ensure_stereo(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return np.column_stack([audio.astype(np.float64), audio.astype(np.float64)])
    return audio.astype(np.float64, copy=True)


def biquad_lowpass(sig: np.ndarray, cutoff_hz: float, order: int = 2) -> np.ndarray:
    nyq = 0.5 * SR
    w = max(0.0005, min(0.99, cutoff_hz / nyq))
    b, a = signal.butter(order, w, btype="low")
    return signal.lfilter(b, a, sig, axis=0)


def biquad_highpass(sig: np.ndarray, cutoff_hz: float, order: int = 2) -> np.ndarray:
    nyq = 0.5 * SR
    w = max(0.0005, min(0.99, cutoff_hz / nyq))
    b, a = signal.butter(order, w, btype="high")
    return signal.lfilter(b, a, sig, axis=0)


def biquad_bandpass(sig: np.ndarray, low_hz: float, high_hz: float, order: int = 2) -> np.ndarray:
    nyq = 0.5 * SR
    w1 = max(0.0005, min(0.98, low_hz / nyq))
    w2 = max(w1 + 0.002, min(0.99, high_hz / nyq))
    b, a = signal.butter(order, [w1, w2], btype="band")
    return signal.lfilter(b, a, sig, axis=0)


def peaking_eq(sig: np.ndarray, freq_hz: float, gain_db: float, q: float = 1.0) -> np.ndarray:
    if abs(gain_db) < 0.05:
        return sig
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * freq_hz / SR
    alpha = np.sin(w0) / (2.0 * max(0.1, q))
    cos_w0 = np.cos(w0)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * cos_w0
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return signal.lfilter(b, a, sig, axis=0)


class Stompbox:
    """Base class for all AI-callable guitar/instrument stompbox pedals."""
    name: str = "BaseStompbox"
    category: str = "Utility"

    def __init__(self, bypass: bool = False, mix: float = 1.0, level: float = 1.0, **kwargs):
        self.bypass = bypass
        self.mix = float(np.clip(mix, 0.0, 1.0))
        self.level = float(level)
        self.params: Dict[str, Any] = dict(kwargs)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        return x

    def __call__(self, audio: np.ndarray) -> np.ndarray:
        x = ensure_stereo(audio)
        if self.bypass:
            return x
        wet = self._render_wet(x)
        out = (1.0 - self.mix) * x + self.mix * wet
        return out * self.level


class PedalboardChain:
    """Serial stompbox chain (like a physical pedalboard)."""
    def __init__(self, pedals: List[Stompbox]):
        self.pedals = list(pedals)

    def __call__(self, audio: np.ndarray) -> np.ndarray:
        x = ensure_stereo(audio)
        for p in self.pedals:
            x = p(x)
        return x
