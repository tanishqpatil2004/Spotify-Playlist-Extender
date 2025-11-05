import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from collections import Counter

# Configuration - UPDATE THESE WITH YOUR CREDENTIALS
SPOTIFY_CLIENT_ID = 'c9514b20921f472cb4754bdda5da2a64'
SPOTIFY_CLIENT_SECRET = '2078a049b3324e2c8b72b6183a5ee144'
GENIUS_ACCESS_TOKEN = '8bK0YJEakZZ4rKNFt0GNzVY36Dqs3vNfaoi49YwIHjDDGyYy8DkUG1mgR8igwGkf'

# Spotify OAuth setup - this will open a browser for authentication
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-modify-public playlist-modify-private'

class PlaylistExtender:
    def __init__(self):
        self.setup_clients()
        self.lyrics_cache = {}
        
    def setup_clients(self):
        """Setup API clients with comprehensive error handling"""
        try:
            # Setup Spotify client with OAuth for write permissions
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SCOPE,
                cache_path=".spotify_cache"
            ))
            print("✅ Spotify OAuth client configured successfully")
            
            # Test authentication by getting current user
            user = self.sp.current_user()
            print(f"✅ Authenticated as: {user['display_name']}")
            
        except Exception as e:
            print(f"❌ Spotify OAuth setup failed: {e}")
            print("Please make sure your redirect URI is set to: http://127.0.0.1:8888/callback")
            self.sp = None
            
        self.genius_headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
        print("✅ Genius client configured successfully")
    
    def extract_playlist_id(self, playlist_uri):
        """Extract playlist ID from various URI formats"""
        if 'spotify:playlist:' in playlist_uri:
            return playlist_uri.split(':')[-1]
        elif 'open.spotify.com/playlist/' in playlist_uri:
            return playlist_uri.split('/')[-1].split('?')[0]
        else:
            return playlist_uri
    
    def get_playlist_tracks_safe(self, playlist_uri):
        """Safely get playlist tracks with extensive error handling"""
        if not self.sp:
            print("❌ Spotify client not available")
            return []
            
        try:
            playlist_id = self.extract_playlist_id(playlist_uri)
            print(f"🎵 Fetching playlist: {playlist_id}")
            
            # Get playlist info
            playlist = self.sp.playlist(playlist_id)
            print(f"📋 Playlist: {playlist['name']}")
            print(f"👤 Owner: {playlist['owner']['display_name']}")
            if playlist.get('description'):
                print(f"📝 {playlist['description']}")
            
            # Check if we can modify this playlist
            current_user = self.sp.current_user()
            can_modify = (playlist['owner']['id'] == current_user['id'] or playlist['collaborative'])
            
            if not can_modify:
                print("❌ Cannot modify this playlist (not owner and not collaborative)")
                return [], playlist, False
            
            # Get all tracks with pagination
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            
            while results['next']:
                time.sleep(0.2)  # Rate limiting
                results = self.sp.next(results)
                tracks.extend(results['items'])
            
            print(f"✅ Found {len(tracks)} tracks")
            return tracks, playlist, True
            
        except Exception as e:
            print(f"❌ Error fetching playlist: {e}")
            return [], None, False
    
    def clean_track_name(self, name):
        """Clean track name for better search results"""
        # Remove content in parentheses and brackets
        name = re.sub(r'[\(\[].*?[\)\]]', '', name)
        # Remove special characters but keep spaces
        name = re.sub(r'[^\w\s]', '', name)
        # Remove common prefixes
        name = re.sub(r'^(official|original|acoustic|remastered|remix)\s+', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def get_genius_lyrics(self, artist, title, max_retries=2):
        """Get lyrics from Genius with robust error handling and retries"""
        cache_key = f"{artist}_{title}"
        if cache_key in self.lyrics_cache:
            return self.lyrics_cache[cache_key]
            
        for attempt in range(max_retries):
            try:
                # Clean inputs
                clean_title = self.clean_track_name(title)
                clean_artist = re.sub(r'[^\w\s]', '', artist).strip()
                
                # Search for song on Genius
                search_url = "https://api.genius.com/search"
                params = {'q': f"{clean_title} {clean_artist}"}
                
                response = requests.get(
                    search_url, 
                    headers=self.genius_headers, 
                    params=params,
                    timeout=10
                )
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return ""
                
                data = response.json()
                
                if not data['response']['hits']:
                    return ""
                
                # Get the most relevant result
                song_path = data['response']['hits'][0]['result']['path']
                song_url = f"https://genius.com{song_path}"
                
                # Scrape lyrics from the song page
                page_response = requests.get(song_url, timeout=10)
                if page_response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return ""
                
                soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # Try multiple selectors for lyrics
                lyrics_selectors = [
                    'div[class*="Lyrics__Container"]',
                    'div.lyrics',
                    '.lyrics-container',
                    '[data-lyrics-container="true"]'
                ]
                
                lyrics_text = ""
                for selector in lyrics_selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        lyrics_text += element.get_text(separator='\n') + '\n'
                
                if lyrics_text.strip():
                    self.lyrics_cache[cache_key] = lyrics_text.strip()
                    return lyrics_text.strip()
                    
            except requests.RequestException as e:
                print(f"   ⚠️ Network error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            except Exception as e:
                print(f"   ⚠️ Unexpected error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        return ""
    
    def analyze_lyrics_sentiment(self, lyrics):
        """Simple sentiment analysis based on lyrical content"""
        if not lyrics:
            return "neutral"
        
        positive_words = {
            'love', 'beautiful', 'happy', 'amazing', 'wonderful', 'perfect', 'better',
            'smile', 'laugh', 'joy', 'peace', 'heaven', 'angel', 'dream', 'hope'
        }
        
        negative_words = {
            'sad', 'hurt', 'pain', 'cry', 'tears', 'broken', 'lonely', 'miss',
            'death', 'die', 'lost', 'wrong', 'bad', 'hate', 'regret', 'sorry'
        }
        
        words = set(re.findall(r'\b[a-z]+\b', lyrics.lower()))
        
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        
        if positive_count > negative_count + 2:
            return "positive"
        elif negative_count > positive_count + 2:
            return "negative"
        else:
            return "neutral"
    
    def extract_lyrical_themes(self, lyrics):
        """Extract common themes from lyrics"""
        if not lyrics:
            return []
        
        # Theme keywords
        themes = {
            'romance': {'love', 'heart', 'baby', 'darling', 'kiss', 'hold', 'touch'},
            'longing': {'miss', 'wait', 'need', 'want', 'wish', 'dream'},
            'heartbreak': {'break', 'hurt', 'pain', 'tears', 'cry', 'lost'},
            'hope': {'hope', 'better', 'future', 'light', 'heal'},
            'nostalgia': {'remember', 'memory', 'past', 'old', 'time'}
        }
        
        words = set(re.findall(r'\b[a-z]+\b', lyrics.lower()))
        detected_themes = []
        
        for theme, keywords in themes.items():
            if len(words.intersection(keywords)) >= 2:
                detected_themes.append(theme)
        
        return detected_themes
    
    def get_track_analysis(self, tracks):
        """Analyze tracks using Genius lyrics"""
        print("\n🔍 Analyzing tracks with Genius...")
        
        analyzed_tracks = []
        lyrics_found = 0
        
        for i, item in enumerate(tracks):
            track = item['track']
            if not track:
                continue
                
            print(f"  {i+1}. Analyzing: {track['name'][:35]}... - {track['artists'][0]['name']}")
            
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms']
            }
            
            # Get lyrics
            lyrics = self.get_genius_lyrics(track['artists'][0]['name'], track['name'])
            if lyrics:
                lyrics_found += 1
                track_info['lyrics'] = lyrics
                track_info['sentiment'] = self.analyze_lyrics_sentiment(lyrics)
                track_info['themes'] = self.extract_lyrical_themes(lyrics)
            else:
                track_info['lyrics'] = ""
                track_info['sentiment'] = "unknown"
                track_info['themes'] = []
            
            analyzed_tracks.append(track_info)
            
            # Rate limiting
            if (i + 1) % 3 == 0:
                time.sleep(1)
        
        print(f"✅ Lyrics found for {lyrics_found}/{len(analyzed_tracks)} tracks")
        return analyzed_tracks
    
    def get_playlist_insights(self, analyzed_tracks):
        """Generate insights from the analyzed tracks"""
        if not analyzed_tracks:
            return {}
        
        # Count artists
        artists = [track['artist'] for track in analyzed_tracks]
        top_artists = Counter(artists).most_common(3)
        
        # Analyze sentiments
        sentiments = [track['sentiment'] for track in analyzed_tracks if track['sentiment'] != 'unknown']
        sentiment_dist = Counter(sentiments)
        
        # Collect all themes
        all_themes = []
        for track in analyzed_tracks:
            all_themes.extend(track['themes'])
        common_themes = Counter(all_themes).most_common(5)
        
        # Calculate average popularity
        popularities = [track['popularity'] for track in analyzed_tracks]
        avg_popularity = sum(popularities) / len(popularities) if popularities else 0
        
        return {
            'top_artists': top_artists,
            'sentiment_distribution': sentiment_dist,
            'common_themes': common_themes,
            'avg_popularity': avg_popularity,
            'total_tracks': len(analyzed_tracks),
            'tracks_with_lyrics': len([t for t in analyzed_tracks if t['lyrics']])
        }
    
    def find_recommendations_via_genius(self, analyzed_tracks, limit=15):
        """Find recommendations using Genius API search"""
        print("\n🎯 Finding recommendations via Genius...")
        
        recommendations = []
        original_artists = set(track['artist'] for track in analyzed_tracks)
        
        # Use top artists and themes for search
        insights = self.get_playlist_insights(analyzed_tracks)
        
        # Strategy 1: Similar artists
        for artist, count in insights['top_artists']:
            try:
                print(f"  Searching artists similar to: {artist}")
                
                # Search for related content on Genius
                search_queries = [
                    f"{artist}",
                    f"songs like {artist}",
                    f"artists similar to {artist}"
                ]
                
                for query in search_queries[:2]:
                    search_url = "https://api.genius.com/search"
                    params = {'q': query}
                    
                    response = requests.get(
                        search_url, 
                        headers=self.genius_headers, 
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        for hit in data['response']['hits'][:3]:
                            song = hit['result']
                            if (song['primary_artist']['name'] not in original_artists and
                                not any(r['artist'] == song['primary_artist']['name'] and 
                                       r['title'] == song['title'] for r in recommendations)):
                                
                                rec = {
                                    'title': song['title'],
                                    'artist': song['primary_artist']['name'],
                                    'url': song['url'],
                                    'reason': f"Similar to {artist}",
                                    'source': 'genius_search'
                                }
                                recommendations.append(rec)
                                
                    time.sleep(0.5)  # Rate limiting
                    
            except Exception as e:
                print(f"    ⚠️ Error searching {artist}: {e}")
                continue
        
        # Strategy 2: Theme-based recommendations
        for theme, count in insights['common_themes'][:3]:
            try:
                print(f"  Searching {theme} themed songs...")
                
                search_url = "https://api.genius.com/search"
                params = {'q': f"{theme} love song acoustic"}
                
                response = requests.get(
                    search_url, 
                    headers=self.genius_headers, 
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for hit in data['response']['hits'][:2]:
                        song = hit['result']
                        if not any(r['artist'] == song['primary_artist']['name'] and 
                                  r['title'] == song['title'] for r in recommendations):
                            
                            rec = {
                                'title': song['title'],
                                'artist': song['primary_artist']['name'],
                                'url': song['url'],
                                'reason': f"{theme.capitalize()} theme",
                                'source': 'theme_search'
                            }
                            recommendations.append(rec)
                            
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ⚠️ Error searching theme {theme}: {e}")
                continue
        
        return recommendations[:limit]
    
    def enhance_with_spotify_info(self, genius_recommendations):
        """Enhance Genius recommendations with Spotify data and get track IDs"""
        if not self.sp:
            return genius_recommendations
            
        print("\n🎵 Enhancing recommendations with Spotify data...")
        
        enhanced_recommendations = []
        
        for rec in genius_recommendations:
            try:
                # Search for the track on Spotify
                query = f"{rec['title']} {rec['artist']}"
                results = self.sp.search(q=query, type='track', limit=1)
                
                if results['tracks']['items']:
                    spotify_track = results['tracks']['items'][0]
                    rec['spotify_id'] = spotify_track['id']
                    rec['spotify_uri'] = spotify_track['uri']  # This is needed for adding to playlist
                    rec['popularity'] = spotify_track['popularity']
                    rec['preview_url'] = spotify_track.get('preview_url')
                    rec['duration_ms'] = spotify_track['duration_ms']
                    rec['album'] = spotify_track['album']['name']
                else:
                    rec['spotify_id'] = None
                    rec['spotify_uri'] = None
                    rec['popularity'] = 0
                    rec['preview_url'] = None
                
                enhanced_recommendations.append(rec)
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Couldn't enhance {rec['title']}: {e}")
                rec['spotify_id'] = None
                rec['spotify_uri'] = None
                rec['popularity'] = 0
                enhanced_recommendations.append(rec)
        
        return enhanced_recommendations
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Add tracks to the playlist"""
        if not self.sp:
            print("❌ Spotify client not available for adding tracks")
            return False
            
        if not track_uris:
            print("❌ No track URIs to add")
            return False
            
        try:
            print(f"\n📤 Adding {len(track_uris)} tracks to playlist...")
            
            # Add tracks in batches of 100 (Spotify API limit)
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i+100]
                self.sp.playlist_add_items(playlist_id, batch)
                print(f"  ✅ Added batch {i//100 + 1} ({len(batch)} tracks)")
                time.sleep(1)  # Rate limiting
            
            print(f"🎉 Successfully added {len(track_uris)} tracks to the playlist!")
            return True
            
        except Exception as e:
            print(f"❌ Error adding tracks to playlist: {e}")
            return False
    
    def display_insights(self, insights, analyzed_tracks):
        """Display beautiful insights about the playlist"""
        print("\n" + "="*60)
        print("🎻 PLAYLIST INSIGHTS")
        print("="*60)
        
        print(f"\n📊 Basic Stats:")
        print(f"   • Total tracks: {insights['total_tracks']}")
        print(f"   • Tracks with lyrics: {insights['tracks_with_lyrics']}")
        print(f"   • Average popularity: {insights['avg_popularity']:.0f}/100")
        
        print(f"\n👨‍🎤 Top Artists:")
        for artist, count in insights['top_artists']:
            print(f"   • {artist} ({count} tracks)")
        
        if insights['sentiment_distribution']:
            print(f"\n🎭 Sentiment Analysis:")
            for sentiment, count in insights['sentiment_distribution'].items():
                percentage = (count / insights['total_tracks']) * 100
                print(f"   • {sentiment.capitalize()}: {count} tracks ({percentage:.1f}%)")
        
        if insights['common_themes']:
            print(f"\n💭 Common Themes:")
            for theme, count in insights['common_themes'][:5]:
                print(f"   • {theme.capitalize()} ({count} occurrences)")
        
        # Show most emotional tracks
        emotional_tracks = [t for t in analyzed_tracks if t['sentiment'] in ['positive', 'negative']]
        if emotional_tracks:
            print(f"\n💖 Most Emotional Tracks:")
            for track in emotional_tracks[:3]:
                print(f"   • {track['name'][:25]}... - {track['artist']} ({track['sentiment']})")
    
    def run(self, playlist_uri):
        """Main method to run the playlist extender"""
        print("🚀 Starting Genius-Powered Playlist Extender")
        print("="*50)
        
        # Step 1: Get playlist tracks and check permissions
        tracks, playlist_info, can_modify = self.get_playlist_tracks_safe(playlist_uri)
        if not tracks:
            print("❌ No tracks found or error accessing playlist")
            return
        
        if not can_modify:
            print("❌ Cannot auto-add tracks to this playlist")
            print("💡 Make sure you own the playlist or it's set to collaborative")
            return
        
        # Step 2: Analyze tracks with Genius
        analyzed_tracks = self.get_track_analysis(tracks)
        
        # Step 3: Generate insights
        insights = self.get_playlist_insights(analyzed_tracks)
        self.display_insights(insights, analyzed_tracks)
        
        # Step 4: Find recommendations via Genius
        genius_recommendations = self.find_recommendations_via_genius(analyzed_tracks, limit=10)
        
        # Step 5: Enhance with Spotify data and get track URIs
        final_recommendations = self.enhance_with_spotify_info(genius_recommendations)
        
        # Filter out recommendations without Spotify URIs
        valid_recommendations = [rec for rec in final_recommendations if rec.get('spotify_uri')]
        
        if not valid_recommendations:
            print("❌ No valid Spotify tracks found to add")
            return
        
        # Step 6: Display final recommendations
        print(f"\n🎵 Recommended Tracks to Add ({len(valid_recommendations)} tracks):")
        print("="*60)
        
        for i, rec in enumerate(valid_recommendations, 1):
            print(f"{i}. {rec['title']} - {rec['artist']}")
            print(f"   💡 {rec['reason']}")
            if rec.get('popularity', 0) > 0:
                print(f"   📊 Popularity: {rec['popularity']}/100")
            print()
        
        # Step 7: Auto-add tracks to playlist
        playlist_id = self.extract_playlist_id(playlist_uri)
        track_uris = [rec['spotify_uri'] for rec in valid_recommendations]
        
        success = self.add_tracks_to_playlist(playlist_id, track_uris)
        
        if success:
            print(f"\n✨ Successfully extended your playlist with {len(track_uris)} new tracks!")
            print(f"📋 Check your Spotify playlist: {playlist_info['name']}")
        else:
            print("\n❌ Failed to add tracks to playlist")

def main():
    """Main function"""
    # Your playlist
    PLAYLIST_URI = 'https://open.spotify.com/playlist/78FWGjRZk2N1BfwkiKnuOq?si=c9e37fb849854324'
    
    # Create and run the extender
    extender = PlaylistExtender()
    extender.run(PLAYLIST_URI)

if __name__ == "__main__":
    main()