import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# Load and Parse DB File
# =======================
def parse_pink_floyd_db(file_path: str) -> pd.DataFrame:
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()

    data = []
    current_album = None
    current_year = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            parts = line[1:].split("::")
            current_album = parts[0].strip()
            current_year = parts[1].strip() if len(parts) > 1 else "Unknown"
        elif line.startswith("*"):
            try:
                parts = line[1:].split("::", 3)
                title, artist, duration, lyrics = [part.strip() for part in parts]
                data.append({
                    "album": current_album,
                    "year": current_year,
                    "title": title,
                    "artist": artist,
                    "duration": duration,
                    "lyrics": lyrics
                })
            except ValueError:
                print("Error parsing line:", line)
    return pd.DataFrame(data)

df = parse_pink_floyd_db("Pink_Floyd_DB.TXT")
df['title_lower'] = df['title'].str.lower()
df['lyrics_lower'] = df['lyrics'].str.lower()

# ==============
# API ENDPOINTS
# ==============

@app.get("/albums")
def get_albums():
    return df['album'].unique().tolist()

@app.get("/albums/{album_name}")
def get_album_songs(album_name: str):
    return df[df['album'].str.lower() == album_name.lower()]['title'].tolist()

@app.get("/songs/{song_name}/duration")
def get_song_duration(song_name: str):
    song = df[df['title_lower'] == song_name.lower()]
    return song['duration'].values[0] if not song.empty else "Song not found"

@app.get("/songs/{song_name}/lyrics")
def get_song_lyrics(song_name: str):
    song = df[df['title_lower'] == song_name.lower()]
    return song['lyrics'].values[0] if not song.empty else "Song not found"

@app.get("/songs/{song_name}/album")
def get_song_album(song_name: str):
    song = df[df['title_lower'] == song_name.lower()]
    return song['album'].values[0] if not song.empty else "Song not found"

@app.get("/search/title")
def search_title(word: str):
    return df[df['title_lower'].str.contains(word.lower())]['title'].tolist()

@app.get("/search/lyrics")
def search_lyrics(word: str):
    return df[df['lyrics_lower'].str.contains(word.lower())]['title'].tolist()

# ====================
# Text UI Interaction
# ====================

def cli_menu():
    while True:
        print("\nבחר פעולה:")
        print("1. רשימת אלבומים")
        print("2. רשימת שירים באלבום")
        print("3. קבלת משך זמן של שיר")
        print("4. קבלת מילים של שיר")
        print("5. באיזה אלבום נמצא השיר?")
        print("6. חיפוש שיר לפי שם")
        print("7. חיפוש שיר לפי מילים בשיר")
        print("8. יציאה")
        choice = input("הכנס מספר בחירה: ")

        if choice == "1":
            print("\nרשימת אלבומים:")
            for album in df['album'].unique():
                print(f"- {album}")
        elif choice == "2":
            name = input("הכנס שם אלבום: ")
            songs = df[df['album'].str.lower() == name.lower()]
            if songs.empty:
                print("האלבום לא נמצא.")
            else:
                print(f"שירים באלבום {name}:")
                for title in songs['title']:
                    print(f"- {title}")
        elif choice == "3":
            name = input("הכנס שם שיר: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['duration'].values[0] if not result.empty else "שיר לא נמצא.")
        elif choice == "4":
            name = input("הכנס שם שיר: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['lyrics'].values[0] if not result.empty else "שיר לא נמצא.")
        elif choice == "5":
            name = input("הכנס שם שיר: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['album'].values[0] if not result.empty else "שיר לא נמצא.")
        elif choice == "6":
            word = input("הכנס מילה לחיפוש בשם: ")
            matches = df[df['title_lower'].str.contains(word.lower())]['title'].tolist()
            print("שירים שנמצאו:", *matches, sep="\n- ")
        elif choice == "7":
            word = input("הכנס מילה לחיפוש במילים: ")
            matches = df[df['lyrics_lower'].str.contains(word.lower())]['title'].tolist()
            print("שירים שנמצאו:", *matches, sep="\n- ")
        elif choice == "8":
            print("להתראות!")
            break
        else:
            print("בחירה לא חוקית, נסה שוב.")

# ===============
# Run Option
# ===============
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run CLI instead of server")
    args = parser.parse_args()
    if args.cli:
        cli_menu()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
