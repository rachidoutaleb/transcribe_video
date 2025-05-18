# transcribe
Un projet open source permettant la transcription automatique de fichiers audio et vidéo en texte à l’aide de wit.ai  Il prend en charge plusieurs formats (MP3, WAV, MP4…) et langues, avec export en TXT, SRT

# Installation:
1. Install Python dependencies:
```
   pip install -r requirements.txt
```

2. Install FFmpeg:

Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z
Extract the downloaded file
Rename the extracted folder to "ffmpeg"
Move the "ffmpeg" folder to C:\
Add C:\ffmpeg\bin to your system's PATH environment variable

# Usage:
```
git clone https://github.com/rachidoutaleb/transcribe
cd transcribe
python trans.py
```

dans PowerShell avec privilège admin exécute :
```
Set-ExecutionPolicy RemoteSigned
Set-ExecutionPolicy Restricted
```

Exécution:
```
python -Xfrozen_modules=off trans.py
```

# Requirements:
- FFmpeg
- Python 3.11
