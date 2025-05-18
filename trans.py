import os
import subprocess
import sys
import threading
from collections import deque
from pathlib import Path
from dotenv import load_dotenv, set_key
from tafrigh import Config, TranscriptType, farrigh

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

LAST_FOLDER_FILE = "./../config/last_folder"
ENV_FILE = "./../config/.env"

load_dotenv()

LANGUAGE_API_KEYS = {
    'EN': os.getenv('WIT_API_KEY_EN', ''),
    'AR': os.getenv('WIT_API_KEY_AR', ''),
    'FR': os.getenv('WIT_API_KEY_FR', ''),
}

def save_api_keys():
    for lang, key in LANGUAGE_API_KEYS.items():
        env_key = f'WIT_API_KEY_{lang.upper()}'
        set_key(ENV_FILE, env_key, key)

def get_last_folder():
    if os.path.exists(LAST_FOLDER_FILE):
        with open(LAST_FOLDER_FILE, "r") as f:
            last_folder = f.read().strip()
            if os.path.isdir(last_folder):
                return last_folder
    return os.getcwd()

def save_last_folder(folder_path):
    with open(LAST_FOLDER_FILE, "w") as f:
        f.write(folder_path)

def convert_to_wav(input_path: Path) -> Path:
    output_path = input_path.with_suffix('.wav')
    
    cmd = ['ffmpeg', '-i', str(input_path), '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', str(output_path)]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path

def is_valid_wav(file_path: Path) -> bool:
    try:
        with file_path.open('rb') as f:
            return f.read(4) == b'RIFF'
    except IOError:
        return False

def transcribe(file_path: Path, lang: str) -> None:
    if not is_valid_wav(file_path):
        file_path = convert_to_wav(file_path)

    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / "download"
    output_dir.mkdir(parents=True, exist_ok=True)

    config = Config(
        urls_or_paths=[str(file_path)],
        wit_client_access_tokens=[LANGUAGE_API_KEYS[lang.upper()]],
        output_dir=str(output_dir),
        output_formats=[TranscriptType.TXT, TranscriptType.SRT],
        model_name_or_path='tiny',
        language=lang.lower(),
        skip_if_output_exist=False,
        playlist_items=[],
        verbose=False,
        task='transcribe',
        use_faster_whisper=False,
        beam_size=5,
        ct2_compute_type='float32',
        max_cutting_duration=300,
        min_words_per_segment=3,
        save_files_before_compact=False,
        save_yt_dlp_responses=False,
        output_sample=False,
    )

    deque(farrigh(config), maxlen=0)
    print(f"Transcription terminée dans : {output_dir}")

def open_download_dir():
    try:
        script_dir = Path(__file__).resolve().parent
        output_dir = script_dir / "download"
        
        if sys.platform == "win32":
            os.startfile(output_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", output_dir])
        else:
            subprocess.Popen(["xdg-open", output_dir])
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier : {str(e)}")

def configure_api_keys():
    config_window = tk.Toplevel()
    config_window.title("Configuration des clés API")

    def save_keys():
        for lang, entry in api_entries.items():
            LANGUAGE_API_KEYS[lang] = entry.get().strip()
        save_api_keys()
        messagebox.showinfo("Succès", "Clés API mises à jour avec succès !")
        config_window.destroy()
    
    api_entries = {}
    for i, lang in enumerate(LANGUAGE_API_KEYS.keys()):
        tk.Label(config_window, text=f"Clé {lang}:").grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(config_window, width=50)
        entry.insert(0, LANGUAGE_API_KEYS[lang])
        entry.grid(row=i, column=1, padx=5, pady=5)
        api_entries[lang] = entry
    
    save_button = tk.Button(config_window, text="Enregistrer", command=save_keys)
    save_button.grid(row=len(LANGUAGE_API_KEYS), column=0, columnspan=2, pady=10)

def main_gui():
    root = tk.Tk()
    root.title("Transcripteur Audio/Video")
    
    tk.Button(root, text="Configurer les API", command=configure_api_keys).grid(row=0, column=0, columnspan=3, pady=5)
    
    file_label = tk.Label(root, text="Fichier:")
    file_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    
    file_entry = tk.Entry(root, width=50)
    file_entry.grid(row=1, column=1, padx=5, pady=5)
    
    def browse_file():
        initial_dir = get_last_folder()
        file_path = filedialog.askopenfilename(title="Choisir un fichier", initialdir=initial_dir)
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)
            save_last_folder(str(Path(file_path).parent))
    
    browse_button = tk.Button(root, text="Parcourir", command=browse_file)
    browse_button.grid(row=1, column=2, padx=5, pady=5)
    
    lang_label = tk.Label(root, text="Langue:")
    lang_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    
    lang_var = tk.StringVar(value="FR")
    lang_menu = ttk.Combobox(root, textvariable=lang_var, values=list(LANGUAGE_API_KEYS.keys()), state="readonly", width=10)
    lang_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    status_label = tk.Label(root, text="", fg="blue")
    status_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
    
    def start_transcription():
        def run_transcription():
            try:
                file_path = Path(file_entry.get().strip())
                lang = lang_var.get().upper().strip()
                
                transcribe(file_path.resolve(), lang)
                
                root.after(0, lambda: status_label.config(text="Transcription terminée !"))
                root.after(0, lambda: messagebox.showinfo("Succès", f"Transcription terminée : {file_path.stem}"))
            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur : {str(e)}"))
                root.after(0, lambda: status_label.config(text="Erreur lors de la transcription."))
            finally:
                root.after(0, lambda: transcribe_button.config(state=tk.NORMAL))
        
        if not file_entry.get().strip():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier.")
            return
        
        file_path = Path(file_entry.get().strip())
        if not file_path.exists():
            messagebox.showerror("Erreur", f"Fichier introuvable : {file_path}")
            return
        
        transcribe_button.config(state=tk.DISABLED)
        status_label.config(text="Transcription en cours...")
        threading.Thread(target=run_transcription, daemon=True).start()
    
    transcribe_button = tk.Button(root, text="Transcrire", command=start_transcription)
    transcribe_button.grid(row=3, column=1, padx=5, pady=10)
    
    open_button = tk.Button(root, text="Ouvrir le dossier Download", command=open_download_dir)
    open_button.grid(row=5, column=1, padx=5, pady=10)
    
    root.mainloop()

if __name__ == '__main__':
    main_gui()