"""
Musical Arrangement & Score Generator for 'Smoky Bubble Dream Pop'
BPM: 98.0 | Time Signature: 4/4 | Total Bars: 48 (~1m58s + reverb tail)
Key: E Lydian / B Major (Emaj9 -> F#6/9 -> D#m11 -> G#m9)
"""
from dataclasses import dataclass
from typing import List
import numpy as np

BPM = 98.0
BEAT_SEC = 60.0 / BPM
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * 4


@dataclass
class NoteEvent:
    beat: float
    dur: float
    pitch: int
    vel: int
    pan: float = 0.0
    tag: str = ""


# 4-bar chord cycle (2 bars per chord = 8-bar harmonic phrase, or 1 bar per chord = 4-bar phrase)
# Here each chord lasts 2 bars (8 beats) -> 8-bar lush cycle:
# Cycle A: Emaj9 (2 bars) -> F#6/9 (2 bars) -> D#m11 (2 bars) -> G#m9 (2 bars)
CHORD_CYCLE = [
    {
        "name": "Emaj9",
        "bass": 40,  # E2
        "bass_alt": 47,  # B2
        "guitar_voicing": [52, 56, 59, 63, 66],  # E3, G#3, B3, D#4, F#4
        "arp_notes": [64, 66, 71, 66, 63, 66, 71, 75],  # E4, F#4, B4, F#4, D#4, F#4, B4, D#5
        "swell_notes": [64, 71, 75],  # E4, B4, D#5
        "bubble_notes": [76, 78, 83, 75],
    },
    {
        "name": "F#6/9",
        "bass": 42,  # F#2
        "bass_alt": 49,  # C#3
        "guitar_voicing": [54, 58, 61, 63, 68],  # F#3, A#3, C#4, D#4, G#4
        "arp_notes": [66, 68, 73, 68, 63, 68, 73, 78],  # F#4, G#4, C#5, G#4, D#4, G#4, C#5, F#5
        "swell_notes": [66, 73, 78],  # F#4, C#5, F#5
        "bubble_notes": [78, 80, 85, 75],
    },
    {
        "name": "D#m11",
        "bass": 39,  # D#2
        "bass_alt": 46,  # A#2
        "guitar_voicing": [51, 54, 58, 61, 66],  # D#3, F#3, A#3, C#4, F#4
        "arp_notes": [63, 66, 70, 66, 61, 66, 73, 75],  # D#4, F#4, A#4, F#4, C#4, F#4, C#5, D#5
        "swell_notes": [63, 70, 75],  # D#4, A#4, D#5
        "bubble_notes": [75, 78, 82, 73],
    },
    {
        "name": "G#m9",
        "bass": 44,  # G#2
        "bass_alt": 51,  # D#3
        "guitar_voicing": [56, 59, 63, 66, 70],  # G#3, B3, D#4, F#4, A#4
        "arp_notes": [63, 66, 71, 66, 59, 66, 70, 75],  # D#4, F#4, B4, F#4, B3, F#4, A#4, D#5
        "swell_notes": [68, 71, 75],  # G#4, B4, D#5
        "bubble_notes": [80, 78, 83, 75],
    },
]


def chord_at_bar(bar: int) -> dict:
    return CHORD_CYCLE[(bar // 2) % len(CHORD_CYCLE)]


def build_drum_events() -> List[NoteEvent]:
    """
    Smoky Bubbles + Dream Pop breakbeat drum pattern:
    - Laid-back swung 16th groove (swing = +0.025 beat on odd 16th steps)
    - Cushiony kick on 1, 2-and-a, 3-and
    - Rimshot / Snare on 2 and 4, plus ghost notes on 1-a, 2-e, 3-a, 4-e
    - Smoky bubble resonant percussive pops woven into offbeats
    """
    rng = np.random.default_rng(101)
    events: List[NoteEvent] = []
    for bar in range(TOTAL_BARS):
        b0 = bar * 4.0
        ch = chord_at_bar(bar)
        is_intro = bar < 8
        is_breakdown = 24 <= bar < 32
        is_outro = bar >= 40

        # Kick pattern (MIDI 36)
        if not is_outro or bar < 44:
            kick_steps = [(0.0, 96), (1.75, 76), (2.5, 88)] if not is_intro else [(0.0, 82), (2.5, 74)]
            if bar % 2 == 1 and not is_intro:
                kick_steps.append((3.5, 72))
            for pos, vel in kick_steps:
                events.append(NoteEvent(b0 + pos, 0.25, 36, vel + int(rng.integers(-3, 4)), 0.0, "kick"))

        # Snare (38) & Rimshot (37) & Ghost Snare (40)
        if not is_outro or bar < 46:
            use_rim = is_intro or is_breakdown
            main_pitch = 37 if use_rim else 38
            events.append(NoteEvent(b0 + 1.0, 0.25, main_pitch, 86, 0.0, "rim" if use_rim else "snare"))
            events.append(NoteEvent(b0 + 3.0, 0.25, main_pitch, 90, 0.0, "rim" if use_rim else "snare"))
            # Ghost notes
            for gpos, gvel in [(0.75, 52), (1.25, 46), (2.75, 56), (3.75, 60)]:
                if not is_intro or gpos in (1.25, 3.75):
                    events.append(NoteEvent(b0 + gpos + 0.02, 0.2, 40, gvel, 0.05, "ghost"))

        # Swung Hi-Hats (42 closed, 46 open)
        if bar < 44:
            for step16 in range(16):
                swing = 0.024 if (step16 % 2 == 1) else 0.0
                pos = step16 * 0.25 + swing
                if is_intro and step16 % 2 == 1:
                    continue
                is_open = (step16 == 14 and bar % 2 == 1 and not is_intro)
                pitch = 46 if is_open else 42
                base_v = 74 if step16 % 4 == 0 else (56 if step16 % 2 == 0 else 44)
                events.append(NoteEvent(b0 + pos, 0.2 if not is_open else 0.45, pitch, base_v, 0.18, "open_hat" if is_open else "hat"))

        # Smoky Bubble Resonant Perc Blips (mapped to 62/63/64 in MIDI, pitched in synth)
        bubble_pitches = ch["bubble_notes"]
        for idx, bpos in enumerate([0.5, 1.5, 2.25, 3.25]):
            if (bar + idx) % 2 == 0 or is_breakdown or is_intro:
                bp = bubble_pitches[idx % len(bubble_pitches)]
                pan = -0.35 if idx % 2 == 0 else 0.35
                events.append(NoteEvent(b0 + bpos, 0.3, bp, 66, pan, "bubble"))

    return events


def build_guitar_rhythm_events() -> List[NoteEvent]:
    """Jazzmaster Chorus Rhythm Guitar — realistic strummed extended chords."""
    events: List[NoteEvent] = []
    # Strum pattern inside each bar: beat 0.0 (down), 1.5 (up), 2.5 (down), 3.5 (up-soft)
    strum_hits = [
        (0.0, 1.35, 80, False),
        (1.5, 0.85, 68, True),
        (2.5, 0.90, 74, False),
        (3.5, 0.45, 58, True),
    ]
    for bar in range(4, TOTAL_BARS - 2):
        if 24 <= bar < 28:
            # Let breakdown breathe for 4 bars
            continue
        b0 = bar * 4.0
        voicing = chord_at_bar(bar)["guitar_voicing"]
        for pos, dur, base_vel, is_up in strum_hits:
            notes = list(reversed(voicing)) if is_up else voicing
            for idx, p in enumerate(notes):
                strum_offset = idx * 0.018
                vel = base_vel - idx * 2
                events.append(NoteEvent(b0 + pos + strum_offset, dur, p, vel, -0.28, "rhythm"))
    return events


def build_guitar_arp_events() -> List[NoteEvent]:
    """Shimmering 8th-note Dream Pop Arpeggio Guitar (right-panned)."""
    events: List[NoteEvent] = []
    for bar in range(0, TOTAL_BARS):
        b0 = bar * 4.0
        arp = chord_at_bar(bar)["arp_notes"]
        for i in range(8):
            pos = i * 0.5 + (0.015 if i % 2 == 1 else 0.0)
            vel = 76 if i in (0, 3, 6) else 62
            if bar >= 44:
                vel = int(vel * 0.65)
            events.append(NoteEvent(b0 + pos, 0.65, arp[i], vel, 0.32, "arp"))
    return events


def build_guitar_lead_events() -> List[NoteEvent]:
    """Floating Dream Pop Lead Guitar Hook (enters in Chorus bars 16-24 & Climax bars 32-44)."""
    events: List[NoteEvent] = []
    # 8-bar melodic motif in E Lydian / B Major (relative to bar start of 8-bar cycle)
    motif = [
        # Bar 0-1 (Emaj9): B4 -> D#5 -> F#5 -> G#5 -> F#5 -> D#5
        (0.0, 1.5, 71, 88), (1.5, 1.0, 75, 84), (2.5, 1.5, 78, 92),
        (4.0, 2.0, 80, 90), (6.0, 1.0, 78, 82), (7.0, 1.0, 75, 78),
        # Bar 2-3 (F#6/9): C#5 -> D#5 -> F#5 -> G#5 -> A#5 -> F#5
        (8.0, 1.5, 73, 86), (9.5, 1.0, 75, 84), (10.5, 1.5, 78, 90),
        (12.0, 1.5, 80, 92), (13.5, 1.0, 82, 88), (14.5, 1.5, 78, 84),
        # Bar 4-5 (D#m11): A#4 -> C#5 -> D#5 -> F#5 -> D#5 -> B4
        (16.0, 1.5, 70, 85), (17.5, 1.0, 73, 83), (18.5, 1.5, 75, 90),
        (20.0, 2.0, 78, 92), (22.0, 1.0, 75, 82), (23.0, 1.0, 71, 78),
        # Bar 6-7 (G#m9): B4 -> D#5 -> F#5 -> D#5 -> C#5 -> B4
        (24.0, 1.5, 71, 86), (25.5, 1.0, 75, 88), (26.5, 1.5, 78, 90),
        (28.0, 2.5, 75, 86), (30.5, 1.5, 71, 78),
    ]
    for start_bar in [16, 32, 40]:
        b0 = start_bar * 4.0
        for rel_b, dur, pitch, vel in motif:
            if start_bar == 40 and rel_b >= 16.0:
                break
            events.append(NoteEvent(b0 + rel_b, dur, pitch, vel, -0.08, "lead"))
    return events


def build_guitar_swell_events() -> List[NoteEvent]:
    """Shoegaze / Smoky Bubbles reverse-envelope guitar swells & harmonics."""
    events: List[NoteEvent] = []
    for bar in range(8, TOTAL_BARS, 2):
        b0 = bar * 4.0
        swells = chord_at_bar(bar)["swell_notes"]
        for idx, p in enumerate(swells):
            pan = -0.45 if idx == 0 else (0.45 if idx == 2 else 0.0)
            events.append(NoteEvent(b0, 6.5, p, 72, pan, "swell"))
    return events


def build_bass_events() -> List[NoteEvent]:
    """Warm melodic Dream Pop bassline locking with the kick."""
    events: List[NoteEvent] = []
    for bar in range(8, TOTAL_BARS - 4):
        b0 = bar * 4.0
        ch = chord_at_bar(bar)
        root = ch["bass"]
        fifth = ch["bass_alt"]
        pattern = [
            (0.0, 1.6, root, 88),
            (1.75, 0.7, root, 76),
            (2.5, 1.0, fifth, 82),
            (3.5, 0.45, root + 12 if bar % 2 == 1 else fifth, 74),
        ]
        for pos, dur, p, vel in pattern:
            events.append(NoteEvent(b0 + pos, dur, p, vel, 0.0, "bass"))
    return events
