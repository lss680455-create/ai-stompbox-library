"""
Downloads & caches studio-recorded multi-samples into `sample_vault/`
for 16 Native Acoustic/Electric Instruments + 10 Studio Drum Kit pieces.
"""
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(BASE_DIR, "sample_vault")
FFMPEG = r"C:\Users\李刘爽\AppData\Local\hermes\bin\ffmpeg.exe"
PROXY = "socks5h://127.0.0.1:10808"

NOTE_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# 16 Native Instruments with root MIDI pitches spanning their natural register
INSTRUMENT_ROOTS = {
    "acoustic_guitar_nylon": [48, 55, 60, 67, 72, 79],
    "acoustic_guitar_steel": [48, 55, 60, 67, 72, 79],
    "electric_guitar_jazz": [48, 55, 60, 67, 72, 79],
    "electric_guitar_clean": [48, 55, 60, 67, 72, 79],
    "overdriven_guitar": [48, 55, 60, 67, 72, 79],
    "distortion_guitar": [48, 55, 60, 67, 72, 79],
    "acoustic_grand_piano": [36, 48, 60, 72, 84],
    "electric_piano_1": [48, 60, 72, 84],
    "acoustic_bass": [36, 43, 48, 55],
    "electric_bass_finger": [36, 43, 48, 55],
    "violin": [55, 62, 69, 76, 83],
    "cello": [36, 43, 50, 57, 64],
    "string_ensemble_1": [48, 60, 72, 84],
    "orchestral_harp": [48, 60, 72, 84],
    "flute": [60, 67, 72, 79, 84],
    "vibraphone": [53, 60, 67, 72, 79],
}

DRUM_URLS = {
    "kick_808.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808bd/BD2550.WAV",
    "kick_acoustic.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/bd/BT0A0D0.wav",
    "snare_808.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808sd/SD2550.WAV",
    "snare_acoustic.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/sn/ST0T0S3.wav",
    "snare_ghost.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/sn/ST0T0S0.wav",
    "rimshot.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808/RS.WAV",
    "hat_closed.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808hc/HC10.WAV",
    "hat_open.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808oh/OH25.WAV",
    "clap_808.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808/CP.WAV",
    "tom_low.wav": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/808lt/LT10.WAV",
}


def midi_to_note_str(m: int) -> str:
    return f"{NOTE_NAMES[m % 12]}{(m // 12) - 1}"


def download_one(item):
    url, out_wav = item
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        return True
    os.makedirs(os.path.dirname(out_wav), exist_ok=True)
    tmp = out_wav + ".tmp"
    r = subprocess.run(["curl.exe", "-s", "-L", "--fail", "-x", PROXY, "-o", tmp, url])
    if r.returncode != 0 or not os.path.exists(tmp):
        return False
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-ar", "44100", "-ac", "2", out_wav])
    if os.path.exists(tmp):
        os.remove(tmp)
    return os.path.exists(out_wav)


def main():
    os.makedirs(VAULT_DIR, exist_ok=True)
    tasks = []
    base_sf = "https://gleitz.github.io/midi-js-soundfonts/MusyngKite"
    for inst, roots in INSTRUMENT_ROOTS.items():
        for p in roots:
            nstr = midi_to_note_str(p)
            url = f"{base_sf}/{inst}-mp3/{nstr}.mp3"
            out = os.path.join(VAULT_DIR, inst, f"{p}.wav")
            tasks.append((url, out))
    for fname, url in DRUM_URLS.items():
        tasks.append((url, os.path.join(VAULT_DIR, "drums", fname)))

    with ThreadPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(download_one, tasks))
    print(f"Vault populated: {sum(res)}/{len(tasks)} studio root samples ready.")


if __name__ == "__main__":
    main()
