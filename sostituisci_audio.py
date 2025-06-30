import sys
import os

import moviepy.editor as mp


def replace_audio(video_path: str, audio_path: str, output_path: str | None = None) -> None:
    """Replace the audio track in an MP4 with a new audio file.

    If the audio duration differs from the video duration, it will be trimmed or padded
    with silence to match the video length, ensuring perfect alignment from t=0.
    """

    # Load clips
    print("🔄 Caricamento video e audio…")
    video = mp.VideoFileClip(video_path)
    new_audio = mp.AudioFileClip(audio_path)

    # Allinea durata
    if new_audio.duration < video.duration:
        # Pad with silence
        silence = mp.AudioClip(lambda t: 0, duration=video.duration - new_audio.duration)
        new_audio = mp.concatenate_audioclips([new_audio, silence])
    elif new_audio.duration > video.duration:
        new_audio = new_audio.subclip(0, video.duration)

    # Set new audio
    video = video.set_audio(new_audio)

    # Output path
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_with_new_audio{ext}"

    print(f"💾 Esportazione video con audio sostituito: {output_path}")
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

    video.close()
    new_audio.close()

    print("✅ Completato!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python sostituisci_audio.py <video.mp4> <audio.mp3> [output.mp4]")
        sys.exit(1)

    video_input = sys.argv[1]
    audio_input = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    replace_audio(video_input, audio_input, output_file) 