"""
Unified One-Line Import Hub for AI Stompbox & Native Instrument Vault (stomp_hub.py)
Allows AI agents to simply write: `from stomp_hub import *` without inspecting individual files.
"""
from stomp_core import SR, Stompbox, PedalboardChain, ensure_stereo, biquad_lowpass, biquad_highpass, biquad_bandpass, peaking_eq
from stomp_dynamics import DynaCompPedal, OpticalLA2APedal, NoiseGatePedal, TransientDesignerPedal, SidechainPumperPedal
from stomp_drive_fuzz import TubeScreamerTS808, BluesbreakerDrive, ProCoRatDistortion, BigMuffPiFuzz, OctaviaFuzz, LoFiBitcrusher
from stomp_amp_cab import CabinetSimulatorIR, RolandJC120Amp, FenderTwinAmp, VoxAC30TopBoost
from stomp_modulation import BossCE2Chorus, DimensionCChorus, PitchVibratoVB2, ElectricMistressFlanger, Phase90Phaser, OpticalTremolo
from stomp_filter_eq import CryBabyAutoWah, MoogLadderFilter, SmokyBubbleFilter, StudioParametricEQ, LoFiRadioTelephone
from stomp_delay import AnalogBBDDelay, SpaceEchoRE201, PingPongStereoDelay, ReverseDelay
from stomp_reverb import FenderSpringReverb, EMT140PlateReverb, CathedralShimmerReverb, ReverseReverbMBV, ShoegazeDistortedReverb, GatedReverb80s
from stomp_pitch_master import PolyOctavePOG, MicroPitchDetune, ReelToReelTapeMaster
from native_instruments import NativeInstrument, NativeDrumKit
