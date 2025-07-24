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
        print("\nChoose an option:")
        print("1. List all albums")
        print("2. List songs in an album")
        print("3. Get duration of a song")
        print("4. Get lyrics of a song")
        print("5. Find album of a song")
        print("6. Search songs by title")
        print("7. Search songs by lyrics")
        print("8. Exit")

        choice = input("Enter your choice (1–8): ")

        if choice == "1":
            print("\nAlbums:")
            for album in df['album'].unique():
                print(f"- {album}")
        elif choice == "2":
            name = input("Enter album name: ")
            songs = df[df['album'].str.lower() == name.lower()]
            if songs.empty:
                print("Album not found.")
            else:
                print(f"Songs in '{name}':")
                for title in songs['title']:
                    print(f"- {title}")
        elif choice == "3":
            name = input("Enter song name: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['duration'].values[0] if not result.empty else "Song not found.")
        elif choice == "4":
            name = input("Enter song name: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['lyrics'].values[0] if not result.empty else "Song not found.")
        elif choice == "5":
            name = input("Enter song name: ")
            result = df[df['title_lower'] == name.lower()]
            print(result['album'].values[0] if not result.empty else "Song not found.")
        elif choice == "6":
            word = input("Enter word to search in song titles: ")
            matches = df[df['title_lower'].str.contains(word.lower())]['title'].tolist()
            if matches:
                print("Songs found:")
                for title in matches:
                    print(f"- {title}")
            else:
                print("No matching songs found.")
        elif choice == "7":
            word = input("Enter word to search in lyrics: ")
            matches = df[df['lyrics_lower'].str.contains(word.lower())]['title'].tolist()
            if matches:
                print("Songs found:")
                for title in matches:
                    print(f"- {title}")
            else:
                print("No matching songs found.")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

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
