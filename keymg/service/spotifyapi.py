import base64
from requests import post, get
import json
import os
from dotenv import load_dotenv

dicc_camelotkey = {(0,1):'8B',
		(1,1):'3B',
		(2,1):'10B',
		(3,1):'5B',
		(4,1):'12B',
		(5,1):'7B',
		(6,1):'2B',
		(7,1):'9B',
		(8,1):'4B',
		(9,1):'11B',
		(10,1):'6B',
		(11,1):'1B',
		(0,0):'5A',
		(1,0):'12A',
		(2,0):'7A',
		(3,0):'2A',
		(4,0):'9A',
		(5,0):'4A',
		(6,0):'11A',
		(7,0):'6A',
		(8,0):'1A',
		(9,0):'8A',
		(10,0):'3A',
		(11,0):'10A',}

dicc_camelotkey_inverted = {v: k for k, v in dicc_camelotkey.items()}

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_id_track(token, name_song):

    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    name_song = name_song.strip().replace(" ", "%20")

    query = f"?q=track:{name_song}&type=track&limit=10"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    list_songs = list()

    for i in range(len(json_result['tracks']['items'])):
        dicc_song = dict()
        dicc_song['id_song'] = json_result['tracks']['items'][i]['id']
        dicc_song['name_song'] = json_result['tracks']['items'][i]['name']
        dicc_song['name_album'] = json_result['tracks']['items'][i]['album']['name']
        dicc_song['name_artist'] = list()
        for j in range(len(json_result['tracks']['items'][i]['artists'])):
                dicc_song['name_artist'].append(json_result['tracks']['items'][i]['artists'][j]['name'])

        list_songs.append(dicc_song)

    return list_songs


def get_info_song(token, id_song):
    search_info_song = dict()

    query_url = f"https://api.spotify.com/v1/tracks/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    json_song = json.loads(result.content)
    
    search_info_song['id_song'] = id_song
    search_info_song['name_song'] = json_song['name']
    search_info_song['name_album'] = json_song['album']['name']

    search_info_song['artists'] = list()
    for j in range(len(json_song['artists'])):
            search_info_song['artists'].append(json_song['artists'][j]['name'])

    
    search_info_song['url'] = json_song['external_urls']['spotify']
    search_info_song['image'] = json_song['album']['images'][0]['url']
    duration_seconds = json_song['duration_ms'] / 1000
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    search_info_song['duration'] = str(minutes) + ":" + str(seconds)
    return search_info_song



def search_for_audio_features(token, id_song):
    query_url = f"https://api.spotify.com/v1/audio-features/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    tracks_features = json.loads(result.content)

    key = tracks_features['key']
    mode = tracks_features['mode']
    bpm = tracks_features['tempo']
    camelot_key = dicc_camelotkey[(key, mode)]
    
    print("Key: {}, Mode: {}, Camelot Key: {},  BPM (tempo): {}".format(key, mode, camelot_key, bpm))
    return key, mode, bpm, camelot_key


def search_songs_for_key_bpm(token, list_harmonic_key_mode, min_bpm, max_bpm, genre):
    for i in range(len(list_harmonic_key_mode)):
        url = "https://api.spotify.com/v1/recommendations"
        headers = get_auth_header(token)
        key = list_harmonic_key_mode[i][0]
        mode = list_harmonic_key_mode[i][1]
        query = f"?seed_genres={genre}&target_key={key}&min_tempo={min_bpm}&max_tempo={max_bpm}&mode={mode}&limit=10"

        query_url = url + query
        result = get(query_url, headers=headers)
        result = json.loads(result.content)
        print("For {}:".format(dicc_camelotkey.get(list_harmonic_key_mode[i])))
        for i in range(len(result['tracks'])):
            name_song = result['tracks'][i]['name']
            print("Song {}: {}".format(i, name_song))
            # search_for_audio_features(token, result['tracks'][i]['id'])


def search_genres(token):
    query_url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)


def armonic_search_key_bpm(token, key, mode, bpm, accepted_bpm):
    harmonic_camelot_key = []
    harmonic_key_mode = []
    camelot_key = dicc_camelotkey[(key, mode)]
    numeric_key = camelot_key[:-1]
    letter_key = camelot_key[-1]
    harmonic_camelot_key.append(camelot_key)
    if numeric_key == '12':
        harmonic_camelot_key.append(str(1) + letter_key)
    else:
        harmonic_camelot_key.append(str(int(numeric_key) + 1) + letter_key)

    if numeric_key == '1':
        harmonic_camelot_key.append(str(12) + letter_key)
    else:
        harmonic_camelot_key.append(str(int(numeric_key) - 1) + letter_key)

    if letter_key == "A":
        harmonic_camelot_key.append(numeric_key + "B")
    else:
        harmonic_camelot_key.append(numeric_key + "A")
    print(harmonic_camelot_key)

    min_bpm = bpm - accepted_bpm
    max_bpm = bpm + accepted_bpm

    for i in range(len(harmonic_camelot_key)):
        harmonic_key_mode.append(dicc_camelotkey_inverted.get(harmonic_camelot_key[i]))
    

    return harmonic_camelot_key, harmonic_key_mode, min_bpm, max_bpm


def get_info_track(token, id_song):
    query_url = f"https://api.spotify.com/v1/tracks/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    track_info = json.loads(result.content)

    print(track_info)

    # key = tracks_features['key']
    # mode = tracks_features['mode']
    # bpm = tracks_features['tempo']
    
    # print("Key: {}, Mode: {}, BPM (tempo): {}".format(key, mode, bpm))
    # return key, mode, bpm


def get_songs_of_playlist(token, id_playlist):
    songs = list()
    info_song = dict()
    query_url = f"https://api.spotify.com/v1/playlists/{id_playlist}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    info_playlist = json.loads(result.content)
    # print(info_playlist)

    tracks = info_playlist['tracks']['items']
    for i in range(len(tracks)):
        info_song = dict()

        info_song['name_song'] = tracks[i]['track']['name']
        info_song['id_song'] = tracks[i]['track']['id']

        info_song['name_album'] = tracks[i]['track']['album']['name']
        info_song['artists'] = list()
        
        for j in range(len(tracks[i]['track']['artists'])):
            info_song['artists'].append(tracks[i]['track']['artists'][j]['name'])

        key, mode, bpm, camelot_key = search_for_audio_features(token, info_song['id_song'])
        info_song['key'] = key
        info_song['mode'] = mode
        info_song['bpm'] = bpm
        info_song['camelot_key'] = camelot_key

        songs.append(info_song)

    return songs


def harmonic_songs_of_playlist(token, songs):
    combinations = list()
    for i in range(len(songs)):
        if i < len(songs) - 1:
            key = songs[i]['key']
            mode = songs[i]['mode']
            bpm = songs[i]['bpm']
            harmonic_camelot_key, harmonic_key_mode, min_bpm, max_bpm = armonic_search_key_bpm(token, key, mode, bpm, 5)
            
            key_next = songs[i+1]['key']
            mode_next = songs[i+1]['mode']
            bpm_next = songs[i+1]['bpm']
            if ((key_next, mode_next) in harmonic_key_mode) and (bpm_next <= max_bpm and bpm_next >= min_bpm):
                print("YES - Harmonic mixing between song {} ({}) and {} ({})".format(i+1, songs[i]['name_song'], i+2, songs[i+1]['name_song']))
                combinations.append(1)
            else:
                print("NO - Harmonic mixing between song {} ({}) and {} ({})".format(i+1, songs[i]['name_song'], i+2, songs[i+1]['name_song']))
                combinations.append(0)

            print("Harmonic mixed: Actual song camelot key: {}".format(songs[i]['camelot_key']))
            print("Camelot key allowed: ")
            print(harmonic_camelot_key)
            print("Next song camelot key: {}".format(songs[i+1]['camelot_key']))




def get_info_song(token, id_song):
    search_info_song = dict()

    query_url = f"https://api.spotify.com/v1/tracks/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    json_song = json.loads(result.content)
    
    search_info_song['id_song'] = id_song
    search_info_song['name_song'] = json_song['name']
    search_info_song['name_album'] = json_song['album']['name']

    search_info_song['artists'] = list()
    for j in range(len(json_song['artists'])):
            search_info_song['artists'].append(json_song['artists'][j]['name'])

    
    search_info_song['url'] = json_song['external_urls']['spotify']
    search_info_song['image'] = json_song['album']['images'][0]['url']
    duration_seconds = json_song['duration_ms'] / 1000
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    search_info_song['duration'] = str(minutes) + ":" + str(seconds)

    search_info_song['key'], search_info_song['mode'], search_info_song['bpm'], search_info_song['camelot_key'] = search_for_audio_features(token, id_song)

    return search_info_song


#-----------------------------------------------------------------------------------------------

token = get_token()
# id_song, name_song, name_album, name_artist = search_for_id_track(token, "Animals")
songs = search_for_id_track(token, "Levels")
print(songs)
# info_song = get_info_song(token, id_song)
# print(info_song)
# key, mode, bpm = search_for_audio_features(token, id_song)

# get_info_track(token, id_song)

# harmonic_camelot_key, harmonic_key_mode, min_bpm, max_bpm = armonic_search_key_bpm(token, info_song['key'], info_song['mode'], info_song['bpm'], 5)
# search_songs_for_key_bpm(token, harmonic_key_mode, min_bpm, max_bpm, 'progressive-house')
# armonic_search_key_bpm(token, 5, 0, 120, 5)

# songs = get_songs_of_playlist(token, "6N4xnJocR3kV4JF37mtqXu")
# get_songs_of_playlist(token, "6ViSThD6IjBMKBnmtzDipB")
# harmonic_songs_of_playlist(token, songs)
