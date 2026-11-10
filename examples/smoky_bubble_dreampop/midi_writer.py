"""
Pure-Python Standard MIDI File (SMF Type 1) Writer
Supports multi-track export, individual stem MIDI export, tempo, time signature,
control change (CC), pitch bend, and humanized note events.
"""
import struct
from typing import List, Tuple, Optional


def _vlq(val: int) -> bytes:
    """Encode integer as MIDI Variable-Length Quantity."""
    val = max(0, int(val))
    buf = [val & 0x7F]
    val >>= 7
    while val > 0:
        buf.append((val & 0x7F) | 0x80)
        val >>= 7
    buf.reverse()
    return bytes(buf)


class MidiTrackBuilder:
    def __init__(self, name: str, channel: int = 0, program: Optional[int] = None, ppq: int = 480):
        self.name = name
        self.channel = channel & 0x0F
        self.program = program
        self.ppq = ppq
        # Events stored as (tick, sort_priority, raw_bytes)
        self.events: List[Tuple[int, int, bytes]] = []

    def add_meta(self, tick: int, meta_type: int, data: bytes, priority: int = 0):
        raw = b"\xFF" + bytes([meta_type]) + _vlq(len(data)) + data
        self.events.append((int(round(tick)), priority, raw))

    def add_note(self, start_beat: float, duration_beats: float, pitch: int, velocity: int = 90):
        start_tick = max(0, int(round(start_beat * self.ppq)))
        dur_tick = max(10, int(round(duration_beats * self.ppq)))
        end_tick = start_tick + dur_tick
        pitch = max(0, min(127, int(pitch)))
        vel = max(1, min(127, int(velocity)))
        # Note On (priority 20), Note Off (priority 10 so note-off precedes simultaneous note-on)
        self.events.append((start_tick, 20, bytes([0x90 | self.channel, pitch, vel])))
        self.events.append((end_tick, 10, bytes([0x80 | self.channel, pitch, 0])))

    def add_cc(self, beat: float, cc_num: int, cc_val: int):
        tick = max(0, int(round(beat * self.ppq)))
        self.events.append((
            tick,
            15,
            bytes([0xB0 | self.channel, max(0, min(127, int(cc_num))), max(0, min(127, int(cc_val)))])
        ))

    def add_pitch_bend(self, beat: float, bend_norm: float):
        """bend_norm in [-1.0, 1.0], where 0.0 is center (8192)."""
        tick = max(0, int(round(beat * self.ppq)))
        val = max(0, min(16383, int(round(8192 + bend_norm * 8191))))
        lsb = val & 0x7F
        msb = (val >> 7) & 0x7F
        self.events.append((tick, 16, bytes([0xE0 | self.channel, lsb, msb])))

    def to_track_chunk(self, include_tempo_bpm: Optional[float] = None) -> bytes:
        all_events = list(self.events)
        # Track name meta event
        name_bytes = self.name.encode("utf-8")
        all_events.append((0, 0, b"\xFF\x03" + _vlq(len(name_bytes)) + name_bytes))

        if include_tempo_bpm is not None:
            mpqn = int(round(60_000_000.0 / include_tempo_bpm))
            tempo_bytes = struct.pack(">I", mpqn)[1:]
            all_events.append((0, 1, b"\xFF\x51\x03" + tempo_bytes))
            # 4/4 Time signature
            all_events.append((0, 2, b"\xFF\x58\x04\x04\x02\x18\x08"))

        if self.program is not None and self.channel != 9:
            all_events.append((0, 5, bytes([0xC0 | self.channel, self.program & 0x7F])))

        all_events.sort(key=lambda e: (e[0], e[1]))

        body = bytearray()
        last_tick = 0
        for tick, _, raw in all_events:
            delta = max(0, tick - last_tick)
            body.extend(_vlq(delta))
            body.extend(raw)
            last_tick = tick

        # End of Track
        body.extend(_vlq(0))
        body.extend(b"\xFF\x2F\x00")
        return b"MTrk" + struct.pack(">I", len(body)) + bytes(body)


def write_midi_file(path: str, tracks: List[MidiTrackBuilder], bpm: float = 98.0, ppq: int = 480):
    """Write SMF Type 1 MIDI file with a dedicated tempo conductor track + instrument tracks."""
    conductor = MidiTrackBuilder("Conductor_Tempo_Map", channel=0, ppq=ppq)
    chunks = [conductor.to_track_chunk(include_tempo_bpm=bpm)]
    for t in tracks:
        chunks.append(t.to_track_chunk(include_tempo_bpm=None))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), ppq)
    with open(path, "wb") as f:
        f.write(header)
        for ch in chunks:
            f.write(ch)
