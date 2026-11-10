"""
Studio Mixing Console & Mastering Suite (stomp_mixer_console.py)
Includes:
  - AudioTriggeredSidechainDucker (Dynamic Kick-to-Bass / Vocal-to-Pad frequency-selective ducker)
  - MidSideProcessorPedal (Mid/Side width, Side high-frequency air boost, Sub-bass mono maker <130Hz)
  - SSLBusGlueCompressor (SSL G-Series VCA Master Bus Glue Compressor with Sidechain HPF)
  - MultibandLimiter3Band (3-Band Low/Mid/High dynamic tamer + True-Peak Brickwall Ceiling)
  - StudioMixingConsole (Multi-track channel strip summing + LUFS/RMS target loudness normalizer)
"""
import numpy as np
from scipy import signal
from stomp_core import Stompbox, SR, ensure_stereo, biquad_lowpass, biquad_highpass, peaking_eq


def _fast_env(mono_abs: np.ndarray, release_ms: float = 90.0) -> np.ndarray:
    tau = max(0.003, release_ms * 0.001)
    alpha = np.exp(-1.0 / (tau * SR))
    return np.maximum(signal.lfilter([1.0 - alpha], [1.0, -alpha], mono_abs), 1e-7)


class AudioTriggeredSidechainDucker:
    """
    Real Audio-Triggered Sidechain Ducker (e.g., Kick ducks Bass or Vocal ducks Guitars).
    If `crossover_hz > 0`, only ducks frequencies below `crossover_hz` (Dynamic EQ Ducking!).
    """
    def __init__(self, threshold_db: float = -22.0, duck_depth: float = 0.55, release_ms: float = 110.0, crossover_hz: float = 180.0):
        self.threshold = 10.0 ** (threshold_db / 20.0)
        self.duck_depth = float(np.clip(duck_depth, 0.0, 0.95))
        self.release_ms = release_ms
        self.crossover_hz = crossover_hz

    def process(self, target_audio: np.ndarray, trigger_audio: np.ndarray) -> np.ndarray:
        tgt = ensure_stereo(target_audio)
        trig = ensure_stereo(trigger_audio)
        n = min(len(tgt), len(trig))
        trig_pk = np.max(np.abs(trig[:n]), axis=1)
        env = _fast_env(trig_pk, self.release_ms)
        over = np.clip((env - self.threshold) / (1.0 - self.threshold + 1e-6), 0.0, 1.0)
        gain = 1.0 - self.duck_depth * np.tanh(over * 2.2)
        out = tgt.copy()
        if self.crossover_hz > 20.0:
            low = biquad_lowpass(tgt[:n], self.crossover_hz, 2)
            high = biquad_highpass(tgt[:n], self.crossover_hz, 2)
            out[:n] = low * gain[:, None] + high
        else:
            out[:n] = tgt[:n] * gain[:, None]
        return out


class MidSideProcessorPedal(Stompbox):
    """Mid/Side Stereo Imaging, Sub-Bass Mono Maker (<mono_below_hz), and Side Air Enhancer."""
    name = "MidSide_Stereo_Processor"
    category = "Mixer_Master"

    def __init__(self, mid_gain_db: float = 0.0, side_gain_db: float = 1.8, side_air_db: float = 2.0, mono_below_hz: float = 130.0, **kw):
        super().__init__(mix=1.0, mid_gain_db=mid_gain_db, side_gain_db=side_gain_db, side_air_db=side_air_db, mono_below_hz=mono_below_hz, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        mid = 0.5 * (x[:, 0] + x[:, 1])[:, None]
        side = 0.5 * (x[:, 0] - x[:, 1])[:, None]
        if self.params["mono_below_hz"] > 20.0:
            side = biquad_highpass(side, self.params["mono_below_hz"], 2)
        if abs(self.params["side_air_db"]) > 0.1:
            side = peaking_eq(side, 4800.0, self.params["side_air_db"], q=0.75)
        mg = 10.0 ** (self.params["mid_gain_db"] / 20.0)
        sg = 10.0 ** (self.params["side_gain_db"] / 20.0)
        m_out, s_out = mid[:, 0] * mg, side[:, 0] * sg
        return np.column_stack([m_out + s_out, m_out - s_out])


class SSLBusGlueCompressor(Stompbox):
    """SSL 4000 G-Master VCA Bus Glue Compressor with Sidechain High-Pass Filter."""
    name = "SSL_GMaster_Bus_Compressor"
    category = "Mixer_Master"

    def __init__(self, threshold_db: float = -12.0, ratio: float = 4.0, release_ms: float = 110.0, sc_hpf_hz: float = 90.0, makeup_db: float = 2.2, **kw):
        super().__init__(threshold_db=threshold_db, ratio=ratio, release_ms=release_ms, sc_hpf_hz=sc_hpf_hz, makeup_db=makeup_db, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        sc = biquad_highpass(x, self.params["sc_hpf_hz"], 1) if self.params["sc_hpf_hz"] > 20.0 else x
        env = _fast_env(np.max(np.abs(sc), axis=1), self.params["release_ms"])
        thresh = 10.0 ** (self.params["threshold_db"] / 20.0)
        r = max(1.0, float(self.params["ratio"]))
        gain = np.where(env > thresh, (thresh + (env - thresh) / r) / env, 1.0)
        makeup = 10.0 ** (self.params["makeup_db"] / 20.0)
        return np.tanh(x * gain[:, None] * makeup * 1.02)


class MultibandLimiter3Band(Stompbox):
    """3-Band (Low/Mid/High) Dynamic Tamer & Master Brickwall Ceiling Limiter."""
    name = "Multiband_3Band_Limiter"
    category = "Mixer_Master"

    def __init__(self, low_xover_hz: float = 180.0, high_xover_hz: float = 3800.0, drive: float = 1.18, ceiling_peak: float = 0.96, **kw):
        super().__init__(mix=1.0, low_xover_hz=low_xover_hz, high_xover_hz=high_xover_hz, drive=drive, ceiling_peak=ceiling_peak, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        f1, f2 = self.params["low_xover_hz"], self.params["high_xover_hz"]
        low = np.tanh(biquad_lowpass(x, f1, 2) * self.params["drive"])
        mid = np.tanh(biquad_lowpass(biquad_highpass(x, f1, 2), f2, 2) * self.params["drive"])
        high = np.tanh(biquad_highpass(x, f2, 2) * self.params["drive"])
        summed = low + mid + high
        pk = np.max(np.abs(summed)) + 1e-9
        if pk > self.params["ceiling_peak"]:
            summed = summed * (self.params["ceiling_peak"] / pk)
        return summed


class StudioMixingConsole:
    """Complete Multi-Track Studio Mixing & Mastering Console."""
    def __init__(self, target_rms_dbfs: float = -10.8, ceiling_peak: float = 0.96):
        self.target_rms = 10.0 ** (target_rms_dbfs / 20.0)
        self.ceiling_peak = ceiling_peak
        self.channels = {}

    def add_track(self, name: str, audio: np.ndarray, fader_db: float = 0.0, pan: float = 0.0, hpf_hz: float = 0.0, lpf_hz: float = 0.0):
        sig = ensure_stereo(audio)
        if hpf_hz > 15.0:
            sig = biquad_highpass(sig, hpf_hz, 2)
        if 100.0 < lpf_hz < 20000.0:
            sig = biquad_lowpass(sig, lpf_hz, 2)
        gain = 10.0 ** (fader_db / 20.0)
        l_pan = np.sqrt(0.5 * (1.0 - np.clip(pan, -1.0, 1.0))) * gain
        r_pan = np.sqrt(0.5 * (1.0 + np.clip(pan, -1.0, 1.0))) * gain
        self.channels[name] = np.column_stack([sig[:, 0] * l_pan, sig[:, 1] * r_pan])

    def apply_sidechain_ducking(self, target_track: str, trigger_track: str, threshold_db: float = -22.0, duck_depth: float = 0.50, crossover_hz: float = 180.0):
        if target_track in self.channels and trigger_track in self.channels:
            ducker = AudioTriggeredSidechainDucker(threshold_db=threshold_db, duck_depth=duck_depth, crossover_hz=crossover_hz)
            self.channels[target_track] = ducker.process(self.channels[target_track], self.channels[trigger_track])

    def render_master(self, master_chain=None) -> np.ndarray:
        if not self.channels:
            raise ValueError("No tracks added to StudioMixingConsole")
        max_len = max(len(v) for v in self.channels.values())
        bus = np.zeros((max_len, 2), dtype=np.float64)
        for ch in self.channels.values():
            bus[: len(ch)] += ch
        if master_chain is not None:
            bus = master_chain(bus)
        cur_rms = np.sqrt(np.mean(bus ** 2)) + 1e-9
        bus = np.tanh(bus * min(2.2, self.target_rms / cur_rms))
        pk = np.max(np.abs(bus)) + 1e-9
        return bus * (self.ceiling_peak / pk)
