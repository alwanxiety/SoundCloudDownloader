import os
import sys
import subprocess
import yt_dlp


def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_external_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


def download_soundcloud_track(url: str, output_path: str = "%(title)s.%(ext)s"):
    wireproxy_exe = get_resource_path("wireproxy.exe")
    config_path = get_external_path("config.conf")

    proxy_process = None

    if os.path.exists(wireproxy_exe) and os.path.exists(config_path):
        try:
            print("Подключение к VPN через wireproxy...")
            proxy_process = subprocess.Popen(
                [wireproxy_exe, "-c", config_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception as e:
            print(f"Не удалось запустить wireproxy: {e}")
    else:
        print("⚠️ Файл config.conf не найден рядом с программой! Скачивание пойдет без VPN.")
        print(f"Ожидается файл по пути: {config_path}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'ffmpeg_location': get_resource_path(""),
    }

    if proxy_process:
        ydl_opts['proxy'] = 'socks5://127.0.0.1:1080'

    ydl_opts.update({
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            },
        ],
        'writethumbnail': True,
        'quiet': False,
    })

    try:
        print("Начало загрузки...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Загрузка успешно завершена.")
    except Exception as e:
        print(f"Произошла ошибка при скачивании: {e}")
    finally:
        if proxy_process:
            proxy_process.terminate()
            proxy_process.wait()


if __name__ == "__main__":
    track_url = input("Введите ссылку на трек или плейлист SoundCloud: ").strip()
    if track_url:
        download_soundcloud_track(track_url)
    input("\nНажмите Enter, чтобы выйти...")