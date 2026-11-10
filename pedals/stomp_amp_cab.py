"""
Guitar/Bass Amplifiers & Speaker Cabinet Simulators (stomp_amp_cab.py)
Includes: RolandJC120Amp, FenderTwinAmp, VoxAC30TopBoost, MarshallPlexiAmp, CabinetSimulatorIR
"""
import numpy as np
from stomp_core import Stompbox, biquad_lowpass, biquad_highpass, peaking_eq


class CabinetSimulatorIR(Stompbox):
    """
    Speaker Cabinet Frequency & Resonance Modeling.
    Models: '2x12_JC120', '2x12_Jensen_Twin', '2x12_Celestion_Blue', '4x12_Greenback', '1x15_Bass_Ampeg', 'Acoustic_Body'
    """
    name = "Cabinet_Speaker_Simulator"
    category = "Amp_Cab"

    def __init__(self, cab_model: str = "2x12_JC120", air_presence: float = 0.5, **kw):
        super().__init__(cab_model=cab_model, air_presence=air_presence, **kw)

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        m = self.params["cab_model"]
        air = self.params["air_presence"]
        if m == "2x12_JC120":
            y = biquad_highpass(x, 78.0, order=2)
            y = peaking_eq(y, 380.0, -2.5, q=1.1)
            y = peaking_eq(y, 2600.0, 2.2 + air * 2.0, q=1.2)
            return biquad_lowpass(y, 5400.0, order=2)
        elif m == "2x12_Jensen_Twin":
            y = biquad_highpass(x, 82.0, order=2)
            y = peaking_eq(y, 480.0, -4.2, q=1.0)
            y = peaking_eq(y, 2400.0, 3.0 + air * 1.5, q=1.1)
            return biquad_lowpass(y, 4800.0, order=2)
        elif m == "2x12_Celestion_Blue":
            y = biquad_highpass(x, 90.0, order=2)
            y = peaking_eq(y, 1150.0, 3.2, q=0.9)
            y = peaking_eq(y, 3100.0, 2.8, q=1.4)
            return biquad_lowpass(y, 4500.0, order=2)
        elif m == "1x15_Bass_Ampeg":
            y = biquad_highpass(x, 36.0, order=2)
            y = peaking_eq(y, 95.0, 3.5, q=1.1)
            y = peaking_eq(y, 320.0, -2.5, q=1.2)
            return biquad_lowpass(y, 3100.0, order=2)
        elif m == "Acoustic_Body":
            y = biquad_highpass(x, 70.0, order=2)
            y = peaking_eq(y, 115.0, 4.0, q=2.2)
            y = peaking_eq(y, 240.0, 2.5, q=1.8)
            return peaking_eq(y, 3800.0, 2.0 + air * 2.0, q=1.0)
        else:  # 4x12_Greenback
            y = biquad_highpass(x, 88.0, order=2)
            y = peaking_eq(y, 130.0, 2.8, q=1.5)
            y = peaking_eq(y, 550.0, -2.2, q=1.0)
            y = peaking_eq(y, 2250.0, 3.6, q=1.3)
            return biquad_lowpass(y, 4350.0, order=2)


class RolandJC120Amp(Stompbox):
    """Roland JC-120 Jazz Chorus Solid-State Clean Amp — the gold standard for Dream Pop."""
    name = "Roland_JC120_Clean_Amp"
    category = "Amp_Cab"

    def __init__(self, bright: bool = True, bass_db: float = 1.5, mid_db: float = -1.0, treble_db: float = 2.5, **kw):
        super().__init__(bright=bright, bass_db=bass_db, mid_db=mid_db, treble_db=treble_db, **kw)
        self.cab = CabinetSimulatorIR("2x12_JC120")

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        y = peaking_eq(x, 110.0, self.params["bass_db"], q=0.8)
        y = peaking_eq(y, 650.0, self.params["mid_db"], q=1.0)
        y = peaking_eq(y, 3400.0, self.params["treble_db"] + (2.5 if self.params["bright"] else 0.0), q=0.9)
        y = np.tanh(y * 1.15)
        return self.cab(y)


class FenderTwinAmp(Stompbox):
    """Fender '65 Twin Reverb Tube Amp with Blackface mid-scoop & glassy clean headroom."""
    name = "Fender_65_Twin_Amp"
    category = "Amp_Cab"

    def __init__(self, drive: float = 0.25, bass_db: float = 2.0, mid_db: float = -3.5, treble_db: float = 3.0, **kw):
        super().__init__(drive=drive, bass_db=bass_db, mid_db=mid_db, treble_db=treble_db, **kw)
        self.cab = CabinetSimulatorIR("2x12_Jensen_Twin")

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        y = peaking_eq(x, 105.0, self.params["bass_db"], q=0.8)
        y = peaking_eq(y, 480.0, self.params["mid_db"], q=1.1)
        y = peaking_eq(y, 3200.0, self.params["treble_db"], q=0.9)
        g = 1.1 + self.params["drive"] * 2.5
        y = np.tanh(g * (y + 0.07 * (y ** 2)))
        return self.cab(y)


class VoxAC30TopBoost(Stompbox):
    """Vox AC30 Top Boost Class-A Chime & British Jangle Amp."""
    name = "Vox_AC30_TopBoost_Amp"
    category = "Amp_Cab"

    def __init__(self, drive: float = 0.4, cut_knob: float = 0.35, **kw):
        super().__init__(drive=drive, cut_knob=cut_knob, **kw)
        self.cab = CabinetSimulatorIR("2x12_Celestion_Blue")

    def _render_wet(self, x: np.ndarray) -> np.ndarray:
        y = peaking_eq(x, 1400.0, 2.8, q=0.8)
        g = 1.4 + self.params["drive"] * 4.0
        y = np.tanh(g * (y + 0.12 * (y ** 2)))
        y = biquad_lowpass(y, 5800.0 - self.params["cut_knob"] * 2400.0, order=1)
        return self.cab(y)
