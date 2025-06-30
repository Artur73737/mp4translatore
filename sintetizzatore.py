import os
import sys
import re
from io import BytesIO
from datetime import timedelta
from typing import List, Tuple

from gtts import gTTS  # Google Text-to-Speech
from pydub import AudioSegment  # Requires ffmpeg installed
from gtts import gTTSError

# Colori output
try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)

    INFO = Fore.CYAN + Style.BRIGHT
    OK = Fore.GREEN + Style.BRIGHT
    WARN = Fore.YELLOW + Style.BRIGHT
    ERR = Fore.RED + Style.BRIGHT
except ImportError:
    INFO = OK = WARN = ERR = ""

TIMESTAMP_PATTERN = re.compile(
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}),(?P<milli>\d{3})"
)


def parse_timestamp(ts: str) -> int:
    """Convert SRT timestamp (HH:MM:SS,mmm) to milliseconds."""
    match = TIMESTAMP_PATTERN.match(ts)
    if not match:
        raise ValueError(f"Timestamp non valido: {ts}")
    parts = {k: int(v) for k, v in match.groupdict().items()}
    td = timedelta(
        hours=parts["hour"],
        minutes=parts["minute"],
        seconds=parts["second"],
        milliseconds=parts["milli"],
    )
    return int(td.total_seconds() * 1000)


def read_srt(path: str) -> List[Tuple[int, int, str]]:
    """Parse SRT file and return list of (start_ms, end_ms, text)."""
    segments: List[Tuple[int, int, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().splitlines()

    i = 0
    while i < len(content):
        if content[i].strip().isdigit():
            # index line
            if i + 1 >= len(content):
                break
            time_line = content[i + 1].strip()
            if "-->" not in time_line:
                i += 1
                continue
            start_ts, end_ts = [s.strip() for s in time_line.split("-->")]
            start_ms = parse_timestamp(start_ts)
            end_ms = parse_timestamp(end_ts)
            # accumulate text lines until empty line
            text_lines = []
            j = i + 2
            while j < len(content) and content[j].strip() != "":
                text_lines.append(content[j].strip())
                j += 1
            text = " ".join(text_lines).strip()
            segments.append((start_ms, end_ms, text))
            i = j
        else:
            i += 1
    return segments


def synthesize_text(text: str, lang: str = "it") -> AudioSegment:
    """Generate speech audio for given text and return as AudioSegment."""
    def _synthesize(chunk: str) -> AudioSegment:
        tts = gTTS(text=chunk, lang=lang)
        _fp = BytesIO()
        tts.write_to_fp(_fp)
        _fp.seek(0)
        return AudioSegment.from_file(_fp, format="mp3")

    try:
        return _synthesize(text)
    except gTTSError as e:
        print(f"{WARN}[WARN] gTTS errore, provo a suddividere il testo: {e}")

        # Split text into smaller chunks (<= 100 char) preserving words
        words = text.split()
        chunks = []
        current = []
        for word in words:
            if sum(len(w) + 1 for w in current) + len(word) > 90:
                chunks.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            chunks.append(" ".join(current))

        audio = AudioSegment.silent(duration=0)
        for chunk in chunks:
            try:
                audio += _synthesize(chunk)
            except Exception as inner_err:
                print(f"{ERR}[ERR] Impossibile sintetizzare il chunk: {chunk[:30]}… -> {inner_err}")
        if len(audio) == 0:
            # Fallback: return 500ms silence to keep timing
            return AudioSegment.silent(duration=500)
        return audio


def srt_to_mp3(srt_path: str, mp3_output: str, lang: str = "it") -> None:
    """Create an MP3 from SRT using TTS, matching overall duration to SRT end time."""
    segments = read_srt(srt_path)
    if not segments:
        raise ValueError("Nessun segmento trovato nel file SRT.")

    print(f"{INFO}⏳ Sintesi vocale in corso ({len(segments)} segmenti)...")

    last_end = segments[-1][1]  # milliseconds

    final_audio = AudioSegment.silent(duration=0)

    for idx, (start_ms, end_ms, text) in enumerate(segments, 1):
        # Add silence to align start
        if start_ms > len(final_audio):
            silence_dur = start_ms - len(final_audio)
            final_audio += AudioSegment.silent(duration=silence_dur)
        # Synthesize speech for this subtitle
        speech = synthesize_text(text, lang)
        final_audio += speech
        # If speech shorter than allotted time, we will add silence in next loop iteration

        if idx % 20 == 0 or idx == len(segments):
            print(f"{INFO}   Sintetizzati {idx}/{len(segments)} segmenti")

    # Pad or trim to exact duration
    if len(final_audio) < last_end:
        final_audio += AudioSegment.silent(duration=last_end - len(final_audio))
    elif len(final_audio) > last_end:
        final_audio = final_audio[:last_end]

    final_audio.export(mp3_output, format="mp3")
    print(f"{OK}✔ MP3 generato: {mp3_output} (durata: {len(final_audio)/1000:.2f}s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python sintetizzatore.py <input.srt> [output.mp3]")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_mp3 = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.path.splitext(input_srt)[0] + ".mp3"
    )

    srt_to_mp3(input_srt, output_mp3, lang="it") 