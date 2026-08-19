import asyncio
import edge_tts

async def generate_audio_stream(text: str, voice: str = "en-US-AriaNeural", output_path: str = "output.mp3"):
    """Generates an MP3 audio file from text using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test Taglish TTS generation
    ph_text = "Hi po! Thank you for applying for a business loan with Salita."
    ph_voice = "fil-PH-AngeloNeural"
    
    print("Testing edge-tts generation...")
    asyncio.run(generate_audio_stream(ph_text, voice=ph_voice, output_path="ph_test.mp3"))
    print("Audio file saved to ph_test.mp3")