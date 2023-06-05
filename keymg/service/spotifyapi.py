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
    """
    Obtener el token para request a la API de Spotify
    """

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
    """
    Obtiene una lista de posibles canciones que coinciden con el nombre de la canción
    """

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
    """
    Obtiene información de la canción
    """

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

    search_info_song['key'], search_info_song['mode'], search_info_song['bpm'], search_info_song['camelot_key'], tracks_features = search_for_audio_features(token, id_song)

    return search_info_song



def search_for_audio_features(token, id_song):
    """
    Obtiene el key, mode, bpm y el camelot key de una canción por el id_song
    """

    query_url = f"https://api.spotify.com/v1/audio-features/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    tracks_features = json.loads(result.content)

    key = tracks_features['key']
    mode = tracks_features['mode']
    bpm = tracks_features['tempo']
    camelot_key = dicc_camelotkey[(key, mode)]
    
    print("Key: {}, Mode: {}, Camelot Key: {},  BPM (tempo): {}".format(key, mode, camelot_key, bpm))
    return key, mode, bpm, camelot_key, tracks_features


def search_songs_for_key_bpm(token, list_harmonic_key_mode, min_bpm, max_bpm, genre):
    """
    Busca las canciones que coinciden con los criterios de key y bpm para que combinen armónicamente
    """
    songs = list()
    for j in range(len(list_harmonic_key_mode)):
        url = "https://api.spotify.com/v1/recommendations"
        headers = get_auth_header(token)
        key = list_harmonic_key_mode[j][0]
        mode = list_harmonic_key_mode[j][1]
        query = f"?seed_genres={genre}&target_key={key}&min_tempo={min_bpm}&max_tempo={max_bpm}&mode={mode}&limit=10"

        query_url = url + query
        result = get(query_url, headers=headers)
        result = json.loads(result.content)
        # print("--------------------------------------------------------------------------------------------------------------")
        # print(result)
        print("For {}:".format(dicc_camelotkey.get(list_harmonic_key_mode[j])))
        for i in range(len(result['tracks'])):
            info_song = dict()
            name_song = result['tracks'][i]['name']
            print("Song {}: {}".format(i+1, name_song))

            info_song['id_song'] = result['tracks'][i]['id']
            info_song['name_song'] = result['tracks'][i]['name']
            
            info_song['key'], info_song['mode'], info_song['bpm'], info_song['camelot_key'], tracks_features = search_for_audio_features(token, info_song['id_song'])

            if (info_song['key'] == key) and (info_song['mode'] == mode):

                info_song['name_album'] = result['tracks'][i]['album']['name']

                info_song['artists'] = list()
                for j in range(len(result['tracks'][i]['artists'])):
                        info_song['artists'].append(result['tracks'][i]['artists'][j]['name'])

                
                info_song['url'] = result['tracks'][i]['external_urls']['spotify']
                info_song['image'] = result['tracks'][i]['album']['images'][0]['url']
                duration_seconds = result['tracks'][i]['duration_ms'] / 1000
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                info_song['duration'] = str(minutes) + ":" + str(seconds)

            
                songs.append(info_song)
            else:
                pass

    return songs



def search_genres(token):
    """
    Busca los géneros posibles en Spotify
    """

    query_url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)


def harmonic_search_key_bpm(token, key, mode, bpm, accepted_bpm):
    """
    Busca las tonalidades y bpm posibles para que combinen armónicamente con la canción solicitada
    """

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



def get_songs_of_playlist(token, id_playlist):
    """
    Obtiene la info de las canciones de una playlist
    """

    songs = list()
    playlist = dict()
    query_url = f"https://api.spotify.com/v1/playlists/{id_playlist}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    info_playlist = json.loads(result.content)
    # print(info_playlist)

    playlist['name'] = id_playlist
    playlist['name'] = info_playlist['name']
    playlist['owner'] = info_playlist['owner']['display_name']
    playlist['description'] = info_playlist['description']
    playlist['url'] = info_playlist['href']
    playlist['num_songs'] = len(info_playlist['tracks']['items'])
    total_duration = 0

    tracks = info_playlist['tracks']['items']
    for i in range(len(tracks)):
        info_song = dict()

        info_song['id_song'] = tracks[i]['track']['id']
        info_song['name_song'] = tracks[i]['track']['name']
        info_song['name_album'] = tracks[i]['track']['album']['name']

        info_song['artists'] = list()
        for j in range(len(tracks[i]['track']['artists'])):
            info_song['artists'].append(tracks[i]['track']['artists'][j]['name'])

        
        info_song['url'] = tracks[i]['track']['external_urls']['spotify']
        info_song['image'] = tracks[i]['track']['album']['images'][0]['url']
        duration_seconds = tracks[i]['track']['duration_ms'] / 1000
        total_duration = total_duration + duration_seconds
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        info_song['duration'] = str(minutes) + ":" + str(seconds)

        info_song['key'], info_song['mode'], info_song['bpm'], info_song['camelot_key'], tracks_features = search_for_audio_features(token, info_song['id_song'])


        songs.append(info_song)

    playlist['duration_min'] = total_duration / 60
    
    return playlist, songs


def harmonic_songs_of_playlist(token, songs):
    """
    Valida que las canciones consecutivas combinen armónicamente
    """
    
    combinations = list()
    for i in range(len(songs)):
        if i < len(songs) - 1:
            key = songs[i]['key']
            mode = songs[i]['mode']
            bpm = songs[i]['bpm']
            harmonic_camelot_key, harmonic_key_mode, min_bpm, max_bpm = harmonic_search_key_bpm(token, key, mode, bpm, 5)
            
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

    return combinations



#-----------------------------------------------------------------------------------------------

token = get_token()
# id_song, name_song, name_album, name_artist = search_for_id_track(token, "Animals")
# songs = search_for_id_track(token, "Levels")
# print(songs)
# id_song = songs[1]['id_song']
# info_song = get_info_song(token, id_song)
# print(info_song)
# key, mode, bpm = search_for_audio_features(token, id_song)

# get_info_track(token, id_song)

# harmonic_camelot_key, harmonic_key_mode, min_bpm, max_bpm = harmonic_search_key_bpm(token, info_song['key'], info_song['mode'], info_song['bpm'], 5)
# songs_harmonic = search_songs_for_key_bpm(token, harmonic_key_mode, min_bpm, max_bpm, 'progressive-house')
# print(songs_harmonic)
# harmonic_search_key_bpm(token, 5, 0, 120, 5)

# playlist, songs = get_songs_of_playlist(token, "6N4xnJocR3kV4JF37mtqXu")
# print(playlist)
# get_songs_of_playlist(token, "6ViSThD6IjBMKBnmtzDipB")
# combinations = harmonic_songs_of_playlist(token, songs)
# print("----------------------------")
# print(combinations)
