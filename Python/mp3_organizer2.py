import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def extract_mp3_info():
    # 1. 폴더 선택 창 띄우기
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="최상위 MP3 폴더를 선택하세요")

    if not folder_path:
        messagebox.showwarning("알림", "폴더가 선택되지 않았습니다. 프로그램을 종료합니다.")
        return

    music_data = []

    # 2. 최상위 폴더 및 모든 하위 폴더 탐색
    for current_dir, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith('.mp3'):
                file_path = os.path.join(current_dir, file_name)
                
                relative_folder = os.path.relpath(current_dir, folder_path)
                if relative_folder == '.':
                    relative_folder = '최상위 폴더 기본 위치'

                try:
                    audio = MP3(file_path, ID3=ID3)
                    tags = audio.tags if audio.tags else {}

                    title = tags['TIT2'].text[0] if 'TIT2' in tags else ''
                    artist = tags['TPE1'].text[0] if 'TPE1' in tags else ''
                    album = tags['TALB'].text[0] if 'TALB' in tags else ''

                    has_lyrics = 'O' if any(key.startswith('USLT') or key.startswith('SYLT') for key in tags.keys()) else 'X'

                    year = tags['TDRC'].text[0] if 'TDRC' in tags else (tags['TYER'].text[0] if 'TYER' in tags else '')
                    genre = tags['TCON'].text[0] if 'TCON' in tags else ''
                    length_sec = int(audio.info.length)
                    bitrate = audio.info.bitrate // 1000 

                    music_data.append({
                        '폴더 위치': relative_folder,
                        '파일명': file_name,
                        '곡명': str(title),
                        '아티스트명': str(artist),
                        '앨범명': str(album),
                        '가사 유무': has_lyrics,
                        '발매연도': str(year),
                        '장르': str(genre),
                        '재생시간(초)': length_sec,
                        '비트레이트(kbps)': bitrate
                    })

                except Exception:
                    pass

    # 3. 추출한 데이터를 엑셀 파일로 저장 및 결과 알림
    if music_data:
        df = pd.DataFrame(music_data)
        output_file = os.path.join(folder_path, 'MP3_하위폴더포함_정리목록.xlsx')
        df.to_excel(output_file, index=False)
        messagebox.showinfo("완료", f"🎉 성공적으로 엑셀 파일이 생성되었습니다!\n\n저장 경로:\n{output_file}")
    else:
        messagebox.showerror("오류", "선택한 폴더 및 하위 폴더에 MP3 파일이 없거나 정보를 추출할 수 없습니다.")

if __name__ == "__main__":
    extract_mp3_info()