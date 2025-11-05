# 🎧 Genius-Powered Spotify Playlist Extender

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Spotify API](https://img.shields.io/badge/Spotify-API-success)
![Genius API](https://img.shields.io/badge/Genius-API-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

A Python-based tool that enhances your Spotify playlists by analyzing song lyrics and suggesting new tracks using the **Genius API** and **Spotify Web API**.  
This project automatically fetches lyrical data, performs **sentiment and theme analysis**, and extends your playlist with new songs that match the mood and style of your existing tracks.

---

## 🚀 Features

- 🔐 **OAuth Authentication** with Spotify  
- 🎵 **Lyrics Extraction** using Genius API  
- 🧠 **Sentiment Analysis** of songs (positive, neutral, negative)  
- 💭 **Theme Detection** (romance, heartbreak, nostalgia, etc.)  
- 🧩 **Smart Recommendations** from Genius and Spotify  
- 📊 **Playlist Insights Dashboard** in Command Prompt  
- 🎯 **Auto-adds new recommendations** directly to your Spotify playlist  

---

## 🖼️ Screenshots

### 🧩 1. Script Execution & Analysis
Analyzes tracks, fetches lyrics from Genius, and performs theme and sentiment analysis.

![Playlist Analysis Screenshot](./Screenshot%202025-11-04%20211708.png)

---

### 📊 2. Playlist Insights & Emotional Overview
Displays playlist-level analytics including top artists, sentiment breakdown, and recurring themes.

![Playlist Insights Screenshot](./Screenshot%202025-11-04%20211716.png)

---

### 🔍 3. Smart Recommendations from Genius
Finds similar or thematically linked songs using Genius search and sentiment matching.

![Recommendations Screenshot](./Screenshot%202025-11-04%20211723.png)

---

### 🎉 4. Final Additions to Spotify Playlist
Automatically adds selected recommendations to your playlist.

![Playlist Extended Screenshot](./Screenshot%202025-11-04%20211727.png)

---

## 🧠 How It Works

1. **Authenticate with Spotify**  
   The script uses Spotify OAuth to access and modify your playlists.

2. **Fetch Playlist Data**  
   Retrieves all tracks from your chosen playlist.

3. **Analyze Lyrics via Genius**  
   Scrapes and analyzes song lyrics for themes, sentiment, and emotional cues.

4. **Generate Insights**  
   Displays summary stats like:
   - Average popularity  
   - Common lyrical themes  
   - Emotional track highlights  

5. **Recommend New Songs**  
   Uses Genius to find similar or thematic tracks, enhances them with Spotify data, and adds them to your playlist.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Spotify Developer Account
- Genius API Token

### Installation Steps
```bash
# Clone this repository
git clone https://github.com/<your-username>/spotify-playlist-extender.git
cd spotify-playlist-extender

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root and add:
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GENIUS_ACCESS_TOKEN=your_genius_access_token
```

### Run the Script
```bash
python spotify.py
```

Once authenticated, the tool will:
- Analyze your playlist  
- Display lyrical insights  
- Recommend and auto-add new tracks 🎶  

---

## 📊 Example Insights Output

```
🎻 PLAYLIST INSIGHTS
========================================

📊 Basic Stats:
 • Total tracks: 32
 • Tracks with Lyrics: 32
 • Average popularity: 37/100

👨‍🎤 Top Artists:
 • Arctic Monkeys (4 tracks)
 • Leslie Kritzer (3 tracks)
 • not dvr (3 tracks)

🎭 Sentiment Analysis:
 • Neutral: 25 tracks (78.1%)
 • Negative: 5 tracks (15.6%)
 • Positive: 2 tracks (6.2%)

💭 Common Themes:
 • Romance (15)
 • Longing (8)
 • Heartbreak (6)
```

---

## 📦 Technologies Used
- **Python 3.9+**
- **Spotipy (Spotify Web API Wrapper)**
- **Genius API**
- **BeautifulSoup4**
- **Requests**
- **JSON / Regex / Counter**

---

## 🧩 Folder Structure
```
├── spotify.py               # Main script
├── requirements.txt          # Python dependencies
├── .spotify_cache            # Auth cache file
├── screenshots/              # Project visuals
└── README.md                 # Documentation
```

---

## 📄 License
This project is licensed under the **MIT License** — free to use and modify.

---

## 💡 Future Improvements
- Integrate machine learning-based sentiment analysis (BERT/T5)
- Add GUI dashboard for interactive playlist visualization
- Support for Apple Music and YouTube Music APIs

---

## 👤 Author
**Tanishq Patil**  
🎓 AIML Student | Manipal University Jaipur  
📧 [LinkedIn](https://linkedin.com/in/tanishq-patil)
