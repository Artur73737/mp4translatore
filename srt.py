import whisper
import moviepy.editor as mp
from datetime import timedelta
import re

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

def create_srt_from_video_whisper(video_path, output_srt_path, language='it'):
    """
    Crea file SRT da video MP4 usando OpenAI Whisper
    """
    
    # 1. Estrai audio dal video
    print(f"{INFO}🎞  Estraendo audio dal video…")
    video = mp.VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path, verbose=False, logger=None)
    
    # 2. Carica il modello Whisper
    print(f"{INFO}🤖 Caricando modello Whisper…")
    model = whisper.load_model("base")  # Puoi usare "small", "medium", "large" per maggiore precisione
    
    # 3. Trascrivi l'audio
    print(f"{INFO}📝 Trascrivendo audio… (potrebbe richiedere alcuni minuti)")
    result = model.transcribe(audio_path, language=language)
    
    # 4. Crea il file SRT
    print(f"{INFO}💾 Creando file SRT…")
    create_srt_file(result['segments'], output_srt_path)
    
    # 5. Pulizia
    import os
    os.remove(audio_path)
    video.close()
    
    print(f"{OK}✔ File SRT creato: {output_srt_path}")

def create_srt_file(segments, output_path):
    """
    Crea il file SRT dai segmenti trascritti
    """
    with open(output_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

def format_timestamp(seconds):
    """
    Converte i secondi nel formato SRT (HH:MM:SS,mmm)
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    milliseconds = int((seconds - total_seconds) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

# --- Uso da linea di comando ---
# Esecuzione completa:
#   1. Estrae l'audio e crea un file SRT dall'MP4.
#   2. Traduce il file SRT in italiano.
#   3. Genera l'MP3 in italiano con la stessa durata del video.

if __name__ == "__main__":
    import sys
    from pathlib import Path

    from traduttore import translate_srt
    from sintetizzatore import srt_to_mp3
    from sostituisci_audio import replace_audio

    if len(sys.argv) < 2:
        print("Uso: python srt.py <video.mp4>")
        sys.exit(1)

    video_file = sys.argv[1]
    base_path = Path(video_file).with_suffix("")  # senza estensione

    # 1. Genera SRT dal video
    raw_srt = f"{base_path}.srt"
    print(f"{INFO}[1/3] Generazione SRT: {raw_srt}")
    create_srt_from_video_whisper(video_file, raw_srt, language="en")

    # 2. Traduce SRT in italiano
    it_srt = f"{base_path}_it.srt"
    print(f"{INFO}[2/3] Traduzione in italiano: {it_srt}")
    translate_srt(raw_srt, it_srt, src_lang="en", dest_lang="it")

    # 3. Sintetizza audio
    mp3_output = f"{base_path}.mp3"
    print(f"{INFO}[3/4] Sintesi vocale: {mp3_output}")
    srt_to_mp3(it_srt, mp3_output, lang="it")

    # 4. Incorpora l'audio nel video
    output_video = f"{base_path}_it.mp4"
    print(f"{INFO}[4/4] Creazione MP4 finale con nuovo audio: {output_video}")
    replace_audio(video_file, mp3_output, output_video)

    print(f"{OK}🎉 Processo completato! File finale: {output_video}")