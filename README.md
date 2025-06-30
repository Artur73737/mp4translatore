# Doppiaggio automatico in italiano

Questo progetto consente di:
1. Estrarre i sottotitoli da un video MP4 tramite Whisper.
2. Tradurli automaticamente in italiano.
3. Generare un audio parlato in italiano sincronizzato con i sottotitoli.
4. Sostituire la traccia audio originale del video con quella doppiata.

## Requisiti

1. **Python 3.9+**
2. **FFmpeg** installato e presente nel `PATH` (necessario per *moviepy* e *pydub*).
3. Dipendenze Python:
   ```bash
   pip install -r requirements.txt
   ```
   Se non usi `requirements.txt`, installa manualmente:
   ```bash
   pip install whisper moviepy deep_translator gTTS pydub colorama
   ```
   > Nota: il pacchetto `whisper` richiede PyTorch. Se hai una GPU, installa la versione compatibile con CUDA.

## File principali

| Script | Descrizione |
| ------ | ----------- |
| `srt.py` | Flusso completo: MP4 ➜ SRT (EN) ➜ SRT (IT) ➜ MP3 (IT) ➜ MP4 finale con nuovo audio |
| `traduttore.py` | Traduce un file SRT da una lingua sorgente a una di destinazione |
| `sintetizzatore.py` | Genera un file MP3 da un SRT usando gTTS |
| `sostituisci_audio.py` | Rimpiazza la traccia audio di un MP4 con un nuovo file audio |

## Utilizzo rapido

1. Posiziona nella cartella di lavoro un video, ad esempio `video.mp4`.
2. Esegui:
   ```bash
   python srt.py video.mp4
   ```
3. Output generato:
   - `video.srt`      → sottotitoli in inglese
   - `video_it.srt`   → sottotitoli tradotti in italiano
   - `video.mp3`      → audio italiano sintetizzato
   - `video_it.mp4`   → video con il nuovo audio incorporato

Durante l'esecuzione vedrai messaggi colorati che indicano lo stato dei vari step.

## Utilizzo dei singoli script

- Traduzione autonoma di un SRT:
  ```bash
  python traduttore.py input.srt output_it.srt
  ```

- Sintesi vocale da SRT:
  ```bash
  python sintetizzatore.py output_it.srt audio_it.mp3
  ```

- Sostituzione audio nel video:
  ```bash
  python sostituisci_audio.py video.mp4 audio_it.mp3 video_finale.mp4
  ```

## Suggerimenti

- Whisper richiede tempo; modelli più grandi (e più precisi) impiegano di più. Puoi cambiare la riga in `srt.py`:
  ```python
  model = whisper.load_model("base")  # small | medium | large
  ```
- gTTS è soggetto a limiti di rate‐limit: lo script gestisce gli errori e suddivide frasi lunghe se necessario.
- Se disponi di un TTS locale puoi sostituire gTTS dentro `sintetizzatore.py`.

---

Buon doppiaggio! 🎬🎙️ 