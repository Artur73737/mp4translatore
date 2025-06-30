from deep_translator import GoogleTranslator
import sys
import os

# Colori per output
try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)

    INFO = Fore.CYAN + Style.BRIGHT
    OK = Fore.GREEN + Style.BRIGHT
    WARN = Fore.YELLOW + Style.BRIGHT
    ERR = Fore.RED + Style.BRIGHT
except ImportError:
    # Colorama non installato: definisco stringhe vuote
    INFO = OK = WARN = ERR = ""


def translate_srt(input_path: str, output_path: str, src_lang: str = "en", dest_lang: str = "it") -> None:
    """Translate an SRT file from src_lang to dest_lang while preserving timing and indices.

    Args:
        input_path (str): Path to the input .srt file (source language).
        output_path (str): Path where the translated .srt file will be saved.
        src_lang (str, optional): Source language code. Defaults to "en".
        dest_lang (str, optional): Destination language code. Defaults to "it".
    """

    translator = GoogleTranslator(source=src_lang, target=dest_lang)

    print(f"{INFO}⏳ Avvio traduzione file SRT...")

    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    total_lines = len(lines)

    translated_lines = []
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Keep index numbers, timestamps, and empty lines unchanged
        if stripped == "" or stripped.isdigit() or "-->" in stripped:
            translated_lines.append(line)
            continue

        # Translate subtitle text line
        try:
            translated_text = translator.translate(stripped)
            translated_lines.append(translated_text + "\n")
        except Exception as e:
            print(f"{WARN}[WARN] Impossibile tradurre: {stripped[:50]}... -> {e}")
            translated_lines.append(line)  # Mantieni originale se errore

        # Stampa progresso ogni 50 righe
        if idx % 50 == 0 or idx == total_lines:
            print(f"{INFO}   Tradotte {idx}/{total_lines} righe")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(translated_lines)

    print(f"{OK}✔ Traduzione completata → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python traduttore.py <input.srt> [output.srt]")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_srt = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.path.splitext(input_srt)[0] + "_it.srt"
    )

    translate_srt(input_srt, output_srt)