"""
Copy-on-Use Rig Cloner & Catalog for AI Stompbox & Native Instrument Library
Usage:
  1. List all available stompboxes & native instruments:
     python clone_rig.py --list
  2. Clone stompbox scripts & native instrument engine into a new song project folder:
     python clone_rig.py --target "C:/path/to/new_song_project/fx_rig" --modules all
"""
import os
import shutil
import argparse

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
PEDALS_DIR = os.path.join(LIB_DIR, "pedals")
INST_DIR = os.path.join(LIB_DIR, "instruments")

CATALOG = {
    "stomp_dynamics.py": ["DynaCompPedal", "OpticalLA2APedal", "NoiseGatePedal", "TransientDesignerPedal", "SidechainPumperPedal"],
    "stomp_drive_fuzz.py": ["TubeScreamerTS808", "BluesbreakerDrive", "ProCoRatDistortion", "BigMuffPiFuzz", "OctaviaFuzz", "LoFiBitcrusher"],
    "stomp_amp_cab.py": ["RolandJC120Amp", "FenderTwinAmp", "VoxAC30TopBoost", "CabinetSimulatorIR (6 speaker/body models)"],
    "stomp_modulation.py": ["BossCE2Chorus", "DimensionCChorus", "PitchVibratoVB2", "Phase90Phaser", "ElectricMistressFlanger", "OpticalTremolo"],
    "stomp_filter_eq.py": ["CryBabyAutoWah", "MoogLadderFilter", "SmokyBubbleFilter", "StudioParametricEQ", "LoFiRadioTelephone"],
    "stomp_delay.py": ["AnalogBBDDelay", "SpaceEchoRE201", "PingPongStereoDelay", "ReverseDelay"],
    "stomp_reverb.py": ["FenderSpringReverb", "EMT140PlateReverb", "CathedralShimmerReverb", "ReverseReverbMBV", "ShoegazeDistortedReverb", "GatedReverb80s"],
    "stomp_pitch_master.py": ["PolyOctavePOG", "MicroPitchDetune", "ReelToReelTapeMaster"],
    "stomp_mixer_console.py": ["AudioTriggeredSidechainDucker", "MidSideProcessorPedal", "SSLBusGlueCompressor", "MultibandLimiter3Band", "StudioMixingConsole"],
    "native_instruments.py": [
        "16 Melodic Studio Instruments: acoustic_guitar_nylon, acoustic_guitar_steel, electric_guitar_jazz, electric_guitar_clean, overdriven_guitar, distortion_guitar, acoustic_grand_piano, electric_piano_1, acoustic_bass, electric_bass_finger, violin, cello, string_ensemble_1, orchestral_harp, flute, vibraphone",
        "10 Studio Drums: kick_808, kick_acoustic, snare_808, snare_acoustic, snare_ghost, rimshot, hat_closed, hat_open, clap_808, tom_low",
    ],
}


def print_catalog():
    print("=== AI Stompbox & Native Instrument Vault Catalog ===")
    for mod, items in CATALOG.items():
        print(f"\n[{mod}]")
        for it in items:
            print(f"  - {it}")


def clone_to_project(target_dir: str, modules: list):
    os.makedirs(target_dir, exist_ok=True)
    # Always copy stomp_core.py and native_instruments.py
    shutil.copy2(os.path.join(PEDALS_DIR, "stomp_core.py"), os.path.join(target_dir, "stomp_core.py"))
    shutil.copy2(os.path.join(INST_DIR, "native_instruments.py"), os.path.join(target_dir, "native_instruments.py"))

    all_pedal_files = [f for f in os.listdir(PEDALS_DIR) if f.startswith("stomp_") and f.endswith(".py")]
    selected = all_pedal_files if ("all" in modules or not modules) else [
        f if f.endswith(".py") else f"stomp_{f}.py" for f in modules
    ]
    copied = ["stomp_core.py", "native_instruments.py"]
    for fname in selected:
        src = os.path.join(PEDALS_DIR, fname)
        if os.path.exists(src) and fname not in copied:
            shutil.copy2(src, os.path.join(target_dir, fname))
            copied.append(fname)

    print(f"Cloned {len(copied)} standalone script(s) into project '{target_dir}':")
    for c in copied:
        print(f"  -> {c}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List all pedals and native instruments")
    parser.add_argument("--target", type=str, default="", help="Target song project folder to copy scripts into")
    parser.add_argument("--modules", nargs="*", default=["all"], help="Specific pedal modules or 'all'")
    args = parser.parse_args()
    if args.list or not args.target:
        print_catalog()
    if args.target:
        clone_to_project(args.target, args.modules)
