"""
Native Acoustic & Electric Instruments Engine (native_instruments.py)
Copy-on-Use: Can be copied into any song project folder. Automatically reads studio samples
from the master `sample_vault/` (or falls back to physical modeling if offline) and renders
any MIDI pitch 0..127 with natural pitch-interpolation and articulation envelopes.
"""
import os
import glob
import numpy as np
from scipy.io import wavfile

SR = 44100
_LOCAL_VAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_vault")
DEFAULT_VAULT = _LOCAL_VAULT if os.path.isdir(_LOCAL_VAULT) else r"C:\Users\李刘爽\.gemini\antigravity\scratch\ai_stompbox_library\sample_vault"
_WAV_CACHE = {}


def _load_wav(path: str) -> np.ndarray:
    if path in _WAV_CACHE:
        return _WAV_CACHE[path]
    _, data = wavfile.read(path)
    sig = data.astype(np.float64) / (32768.0 if data.dtype == np.int16 else 1.0)
    if sig.ndim == 1:
        sig = np.column_stack([sig, sig])
    pk = np.max(np.abs(sig)) + 1e-9
    sig = sig * (0.9 / pk)
    _WAV_CACHE[path] = sig
    return sig


class NativeInstrument:
    """
    Play any MIDI note on 16 studio-sampled native instruments:
      - Guitars: 'acoustic_guitar_nylon', 'acoustic_guitar_steel', 'electric_guitar_jazz',
                 'electric_guitar_clean', 'overdriven_guitar', 'distortion_guitar'
      - Keys/Mallets: 'acoustic_grand_piano', 'electric_piano_1', 'vibraphone', 'orchestral_harp'
      - Bass: 'acoustic_bass', 'electric_bass_finger'
      - Strings/Winds: 'violin', 'cello', 'string_ensemble_1', 'flute'
    """
    def __init__(self, instrument_name: str = "electric_guitar_clean", vault_dir: str = DEFAULT_VAULT):
        self.instrument_name = instrument_name
        self.inst_dir = os.path.join(vault_dir, instrument_name)
        self.roots = {}
        if os.path.isdir(self.inst_dir):
            for p in glob.glob(os.path.join(self.inst_dir, "*.wav")):
                try:
                    midi_num = int(os.path.splitext(os.path.basename(p))[0])
                    self.roots[midi_num] = p
                except ValueError:
                    pass

    def render_note(
        self,
        midi_pitch: int,
        duration_sec: float,
        velocity: float = 0.85,
        pan: float = 0.0,
        articulation: str = "normal",
        vibrato_cents: float = 0.0,
    ) -> np.ndarray:
        if self.roots:
            nearest_root = min(self.roots.keys(), key=lambda r: abs(r - midi_pitch))
            raw = _load_wav(self.roots[nearest_root])
            ratio = 2.0 ** ((midi_pitch - nearest_root) / 12.0)
            n_out = max(64, int(round(len(raw) / ratio)))
            idx_out = np.linspace(0, len(raw) - 1, n_out)
            src_idx = np.arange(len(raw), dtype=np.float64)
            sig_l = np.interp(idx_out, src_idx, raw[:, 0])
            sig_r = np.interp(idx_out, src_idx, raw[:, 1])
            sig = np.column_stack([sig_l, sig_r])
        else:
            # Physical modeling fallback if sample vault is not present
            n_out = int((duration_sec + 0.8) * SR)
            t = np.arange(n_out) / SR
            f0 = 440.0 * (2.0 ** ((midi_pitch - 69.0) / 12.0))
            mono = (np.sin(2 * np.pi * f0 * t) + 0.4 * np.sin(4 * np.pi * f0 * t)) * np.exp(-t * 2.2)
            sig = np.column_stack([mono, mono])

        n = len(sig)
        t = np.arange(n) / SR
        if vibrato_cents > 0.1:
            depth = (2.0 ** (vibrato_cents / 1200.0) - 1.0) * 0.008 * SR
            mod = np.clip(np.arange(n) - depth * (1.0 + np.sin(2 * np.pi * 4.8 * t)), 0, n - 1)
            sig = np.column_stack([np.interp(mod, np.arange(n), sig[:, 0]), np.interp(mod, np.arange(n), sig[:, 1])])

        if articulation == "swell":
            atk = min(duration_sec * 0.68, (n / SR) * 0.65)
            env = np.where(t < atk, (t / max(0.04, atk)) ** 2.3, np.exp(-(t - atk) * 2.4))
        elif articulation == "staccato":
            env = np.exp(-t * 12.0)
        else:
            rel_t = min(duration_sec, (n / SR) * 0.85)
            env = np.where(t <= rel_t, 1.0, np.exp(-(t - rel_t) * 5.5))

        l_gain = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.95, 0.95))) * velocity
        r_gain = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.95, 0.95))) * velocity
        return np.column_stack([sig[:, 0] * env * l_gain, sig[:, 1] * env * r_gain])


class NativeDrumKit:
    """Studio Acoustic + Vintage Analog TR-808 Drum Kit Sampler."""
    def __init__(self, vault_dir: str = DEFAULT_VAULT):
        self.drum_dir = os.path.join(vault_dir, "drums")

    def hit(self, piece: str = "kick_acoustic", velocity: float = 0.85, pan: float = 0.0, pitch_semitones: float = 0.0) -> np.ndarray:
        fname = piece if piece.endswith(".wav") else f"{piece}.wav"
        path = os.path.join(self.drum_dir, fname)
        sig = _load_wav(path)
        if abs(pitch_semitones) > 0.05:
            ratio = 2.0 ** (pitch_semitones / 12.0)
            n_out = max(32, int(round(len(sig) / ratio)))
            idx = np.linspace(0, len(sig) - 1, n_out)
            s0 = np.arange(len(sig), dtype=np.float64)
            sig = np.column_stack([np.interp(idx, s0, sig[:, 0]), np.interp(idx, s0, sig[:, 1])])
        l_gain = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.95, 0.95))) * velocity
        r_gain = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.95, 0.95))) * velocity
        return np.column_stack([sig[:, 0] * l_gain, sig[:, 1] * r_gain])
