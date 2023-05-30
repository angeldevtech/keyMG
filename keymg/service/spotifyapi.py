import base64
from requests import post, get
import json

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

client_id = "dd8b1ed2c16844d18485ecc80fde5979"
client_secret = "444234464fd14f74bdc51a96c31253a9"

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


def search_for_id_track(token, name_song, name_artist):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q=track:{name_song}%20artist:{name_artist}&type=track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    id_song = json_result['tracks']['items'][0]['id']
    
    return id_song

def search_for_audio_features(token, id_song):
    query_url = f"https://api.spotify.com/v1/audio-features/{id_song}"
    headers = get_auth_header(token)

    result = get(query_url, headers=headers)
    tracks_features = json.loads(result.content)

    key = tracks_features['key']
    mode = tracks_features['mode']
    bpm = tracks_features['tempo']
    
    print("Key: {}, Mode: {}, Camelot Key: {},  BPM (tempo): {}".format(key, mode, dicc_camelotkey[(key, mode)], bpm))
    return key, mode, bpm


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
    

    return harmonic_key_mode, min_bpm, max_bpm


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


token = get_token()
id_song = search_for_id_track(token, "Animals", "Garrix")
key, mode, bpm = search_for_audio_features(token, id_song)

# get_info_track(token, id_song)

harmonic_key_mode, min_bpm, max_bpm = armonic_search_key_bpm(token, key, mode, bpm, 5)
search_songs_for_key_bpm(token, harmonic_key_mode, min_bpm, max_bpm, 'progressive-house')
# armonic_search_key_bpm(token, 5, 0, 120, 5)