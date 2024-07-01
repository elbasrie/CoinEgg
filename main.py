import requests
import json
import time
import urllib.parse

# Konstanta dan Konfigurasi
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'id;q=0.8',  # Mengubah bahasa menjadi Bahasa Indonesia
    'content-type': 'application/json',
    'origin': 'https://app-coop.rovex.io',
    'priority': 'u=1, i',
    'referer': 'https://app-coop.rovex.io/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Membaca data TG_WEB_APP_DATA dari file token.txt
def read_tg_web_app_data(filename='token.txt'):
    with open(filename, 'r') as file:
        tg_web_app_data_list = file.read().splitlines()
    # Mengabaikan baris kosong dan memeriksa entri URL yang valid
    tg_web_app_data_list = [data for data in tg_web_app_data_list if data.strip()]
    return tg_web_app_data_list

# Memperoleh username dari TG_WEB_APP_DATA
def extract_username(tg_web_app_data):
    try:
        # Decode URL
        decoded_data = urllib.parse.parse_qs(tg_web_app_data)
        # Mendapatkan user JSON
        user_json = decoded_data['user'][0]
        # Memparsing JSON untuk mendapatkan username
        user_data = json.loads(urllib.parse.unquote(user_json))
        return user_data['username']
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Kesalahan saat memparsing TG_WEB_APP_DATA: {e}")
        return "Username Tidak Diketahui"

# Fungsi untuk mendapatkan token
def get_token(tg_web_app_data):
    url = 'https://egg-api.hivehubs.app/api/login/tg'
    data = {
        "token": "",
        "egg_uid": '',
        "init_data": tg_web_app_data,
        "referrer": ""
    }
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        token = response.json()['data']['token']['token']
        return token
    except requests.exceptions.RequestException as error:
        print("Kesalahan saat mendapatkan Token!!!", error)
        raise

# Fungsi untuk mendapatkan aset
def get_assets(token):
    url = 'https://egg-api.hivehubs.app/api/user/assets'
    data = {
        "token": token
    }
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        assets = response.json()['data']
        print(f"Dompet memiliki: {assets['diamond']['amount']} 💎 | {assets['egg']['amount']} 🥚 | {assets['usdt']['amount']} 💲")
    except requests.exceptions.RequestException as error:
        print("Kesalahan saat mendapatkan aset. Abaikan", error)

# Fungsi untuk mengumpulkan telur
def collect(token, eggs_id, is_last=False):
    url = 'https://egg-api.hivehubs.app/api/scene/egg/reward'
    data = {
        "token": token,
        "egg_uid": eggs_id
    }
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        reward = response.json()['data']
        icon = "🥚" if reward['a_type'] == 'egg' else "💎" if reward['a_type'] == 'diamond' else "💲"
        print(f"Telur {eggs_id} berhasil dikumpulkan! Mendapatkan: {reward['amount']} {icon}")
        if is_last:
            get_assets(token)
    except requests.exceptions.RequestException as error:
        print(f"Kesalahan saat mengumpulkan telur {eggs_id}. Abaikan", error)

# Fungsi untuk mendapatkan semua telur di dalam "scene"
def get_eggs(token):
    url = 'https://egg-api.hivehubs.app/api/scene/info'
    data = {
        "token": token
    }
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        scenes = response.json()['data']
        for scene_index, scene in enumerate(scenes):
            for egg_index, egg in enumerate(scene['eggs']):
                is_last = (scene_index == len(scenes) - 1) and (egg_index == len(scene['eggs']) - 1)
                collect(token, egg['uid'], is_last)
    except requests.exceptions.RequestException as error:
        if 'token' in str(error):
            print("Token tidak valid atau sudah kadaluarsa. Mengulangi proses...")
        else:
            print("Kesalahan saat mendapatkan telur. Abaikan", error)

# Fungsi untuk memulai proses pengumpulan untuk satu TG_WEB_APP_DATA
def start_collecting(tg_web_app_data):
    try:
        token = get_token(tg_web_app_data)
        get_eggs(token)
    except Exception as error:
        print('Kesalahan saat memulai!!!', error)

# Fungsi utama untuk memproses setiap token satu per satu
def process_tokens():
    tg_web_app_data_list = read_tg_web_app_data()
    for index, tg_web_app_data in enumerate(tg_web_app_data_list):
        username = extract_username(tg_web_app_data)
        if username != "Username Tidak Diketahui":
            print(f"Mulai proses untuk pengguna: {username}")
            start_collecting(tg_web_app_data)
            # Menambah jeda 60 detik setelah semua token diproses
            if index == len(tg_web_app_data_list) - 1:
                print("Semua token telah diproses. Menunggu 60 detik sebelum memulai ulang...")
                time.sleep(60)
        else:
            print("Mengabaikan TG_WEB_APP_DATA yang tidak valid")

if __name__ == "__main__":
    process_tokens()
