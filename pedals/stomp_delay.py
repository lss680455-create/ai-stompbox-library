"""
Delay & Echo Stompboxes (stomp_delay.py)
Includes: AnalogBBDDelay, SpaceEchoRE201, PingPongStereoDelay, ReverseDelay
"""
import numpy as np
from stomp_core import Stompbox, SR, biquad_lowpass, biquad_highpass


class AnalogBBDDelay(Stompbox):
    """Boss DM-2 / Memory Man Dark Bucket-Brigade Analog Delay."""
    name = "Boss_DM2_Analog_BBD_Delay"
    category = "Delay"

    def __init__(self, delay_ms: float = 340.0, feedback: float = 0.45, tone_hz: float = 2400.0, mix: float = 0.35, **kw):
        super().__init__(mix=mix, delay_ms=delay_ms, feedback=feedback, tone_hz=tone_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        d = max(1, int(round(self.params["delay_ms"] * 0.001 * SR)))
        fb = float(np.clip(self.params["feedback"], 0.0, 0.92))
        wet = np.zeros_like(x)
        cur = biquad_lowpass(x, self.params["tone_hz"], 1)
        for tap in range(1, 9):
            off = tap * d
            if off >= n:
                break
            cur = np.tanh(biquad_lowpass(cur, self.params["tone_hz"] * (0.88 ** tap), 1) * 1.05)
            wet[off:] += cur[:-off] * (fb ** tap)
        return wet


class SpaceEchoRE201(Stompbox):
    """Roland RE-201 Multi-Head Magnetic Tape Echo with Tape Wow/Flutter & Saturation."""
    name = "Roland_RE201_Space_Echo"
    category = "Delay"

    def __init__(self, base_delay_ms: float = 280.0, feedback: float = 0.52, wow_depth_ms: float = 1.4, mix: float = 0.38, **kw):
        super().__init__(mix=mix, base_delay_ms=base_delay_ms, feedback=feedback, wow_depth_ms=wow_depth_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        t = np.arange(n) / SR
        # 3 playback tape heads (1x, 1.75x, 2.5x)
        heads = [1.0, 1.75, 2.5]
        wet = np.zeros_like(x)
        src = biquad_highpass(biquad_lowpass(np.tanh(x * 1.25), 3400.0, 1), 130.0, 1)
        for h_idx, ratio in enumerate(heads):
            d = max(1, int(round(self.params["base_delay_ms"] * ratio * 0.001 * SR)))
            if d < n:
                wet[d:] += src[:-d] * (self.params["feedback"] ** (h_idx + 1))
        # Apply gentle tape wow/flutter modulation
        idx = np.arange(n, dtype=np.float64)
        wow = (self.params["wow_depth_ms"] * 0.001 * SR) * np.sin(2 * np.pi * 1.15 * t)
        pos = np.clip(idx - wow, 0, n - 1)
        return np.column_stack([np.interp(pos, idx, wet[:, 0]), np.interp(pos, idx, wet[:, 1])])


class PingPongStereoDelay(Stompbox):
    """Stereo Ping-Pong Delay (ideal for Dotted-8th Dream Pop & Post-Rock guitars)."""
    name = "Stereo_PingPong_Delay"
    category = "Delay"

    def __init__(self, delay_ms: float = 459.0, feedback: float = 0.44, damp_hz: float = 3400.0, mix: float = 0.34, **kw):
        super().__init__(mix=mix, delay_ms=delay_ms, feedback=feedback, damp_hz=damp_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        d = max(1, int(round(self.params["delay_ms"] * 0.001 * SR)))
        fb = float(np.clip(self.params["feedback"], 0.0, 0.92))
        src = biquad_lowpass(x, self.params["damp_hz"], 1)
        wl = np.zeros(n, dtype=np.float64)
        wr = np.zeros(n, dtype=np.float64)
        for tap in range(1, 9):
            off = tap * d
            if off >= n:
                break
            g = fb ** tap
            if tap % 2 == 1:
                wl[off:] += src[:-off, 1] * g
                wr[off:] += src[:-off, 0] * g * 0.82
            else:
                wr[off:] += src[:-off, 0] * g
                wl[off:] += src[:-off, 1] * g * 0.82
        return np.column_stack([wl, wr])


class ReverseDelay(Stompbox):
    """Psych / Dream Pop Backwards Grain Delay."""
    name = "Psych_Reverse_Delay"
    category = "Delay"

    def __init__(self, grain_ms: float = 460.0, mix: float = 0.42, **kw):
        super().__init__(mix=mix, grain_ms=grain_ms, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        g_len = max(256, int(round(self.params["grain_ms"] * 0.001 * SR)))
        n = len(x)
        win = np.hanning(g_len)[:, None]
        out = np.zeros_like(x)
        for start in range(0, n - g_len, g_len // 2):
            chunk = x[start : start + g_len][::-1] * win
            out[start : start + g_len] += chunk
        return out
