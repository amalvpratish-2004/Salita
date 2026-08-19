import asyncio
import os
import platform
import edge_tts

async def generate_audio_stream(text: str, voice: str = "en-US-AriaNeural", output_path: str = "output.mp3"):
    """Generates an MP3 audio file from text using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

async def generate_and_play_audio(text: str, voice: str = "en-US-AriaNeural", output_path: str = "output.mp3"):
    """Generates an MP3 audio file from text and plays it locally."""
    await generate_audio_stream(text, voice=voice, output_path=output_path)
    print(f"Audio saved to: {output_path}")

    if platform.system() == "Windows":
        os.system(f'start "" "{output_path}"')
    elif platform.system() == "Darwin":
        os.system(f'afplay "{output_path}"')
    else:
        os.system(f'xdg-open "{output_path}"')

if __name__ == "__main__":
    # Quick sanity check
    asyncio.run(generate_audio_stream("Testing TTS stream generation.", output_path="test_stream.mp3"))
    print("TTS module initialized cleanly.")