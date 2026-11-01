import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from pathlib import Path

def integrated_mp3_organizer():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("안내", "모든 하위 폴더의 MP3를 하나로 모으면서,\n'Various Artists' 음원은 별도 폴더로 자동 분류합니다.\n\n원본 파일은 안전하게 보존됩니다.", parent=root)

    # 1. 원본 폴더 선택
    source_dir = filedialog.askdirectory(title="1. [원본] MP3 파일이 흩어져 있는 최상위 폴더를 선택하세요")
    if not source_dir:
        root.destroy()
        return
    
    # 2. 대상 폴더 선택
    target_dir = filedialog.askdirectory(title="2. [도착지] 정리된 파일들을 모을 '새 폴더'를 선택하세요")
    if not target_dir:
        root.destroy()
        return

    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    # 원본과 도착지 경로 충돌 방지
    if target_path.is_relative_to(source_path):
        messagebox.showerror("오류", "[도착지] 폴더는 [원본] 폴더의 바깥에 있는 완전히 다른 폴더여야 합니다.", parent=root)
        root.destroy()
        return

    # 3. 원본 폴더 내 모든 MP3 파일 검색
    mp3_files = [p for p in source_path.rglob('*') if p.suffix.lower() == '.mp3']
    total_files = len(mp3_files)

    if total_files == 0:
        messagebox.showerror("오류", "선택한 원본 폴더에 MP3 파일이 없습니다.", parent=root)
        root.destroy()
        return

    #도착지 안에 만들어질 Various Artists 전용 폴더 경로 정의
    va_folder_path = target_path / "Various Artists 모음"

    # 4. GUI 진행 상황 창 생성
    root.deiconify()
    root.title("MP3 통합 정리 진행 상황")
    root.geometry("450x180")
    root.resizable(False, False)

    status_label = tk.Label(root, text="파일 분석 및 정리를 준비 중입니다...", font=("맑은 고딕", 10))
    status_label.pack(pady=15)

    progress = ttk.Progressbar(root, orient="horizontal", length=380, mode="determinate")
    progress.pack(pady=5)
    progress["maximum"] = total_files

    percent_label = tk.Label(root, text="0% (0 / 0)", font=("맑은 고딕", 9))
    percent_label.pack(pady=5)

    normal_count = 0
    va_count = 0

    # 5. MP3 파일 순회 및 분류 복사
    for idx, file_path in enumerate(mp3_files, 1):
        file_name = file_path.name
        
        status_label.config(text=f"정리 중: {file_name[:40]}...")
        progress["value"] = idx
        percent = int((idx / total_files) * 100)
        percent_label.config(text=f"{percent}% ({idx} / {total_files} 곡 처리 중)")
        root.update()

        # Various Artists 여부 판별
        is_various = False
        try:
            audio = MP3(str(file_path), ID3=ID3)
            tags = audio.tags if audio.tags else {}
            artist_name = tags['TPE1'].text[0].lower() if 'TPE1' in tags else ''
            
            if 'various' in artist_name or artist_name in ['v.a.', 'v.a', 'va']:
                is_various = True
        except Exception:
            pass # 태그를 읽을 수 없는 불량 파일은 일반 곡 폴더로 분류하도록 처리

        # 6. 저장될 최종 목적지 폴더 결정
        if is_various:
            # VA 음원이 발견되었을 때만 폴더를 생성하도록 방어 조치
            if not va_folder_path.exists():
                va_folder_path.mkdir(parents=True, exist_ok=True)
            current_target_dir = va_folder_path
        else:
            current_target_dir = target_path

        # 7. 파일명 중복 방어 로직 (동일 파일명 존재 시 번호 부여)
        destination_file = current_target_dir / file_name
        counter = 1
        while destination_file.exists():
            new_name = f"{file_path.stem} ({counter}){file_path.suffix}"
            destination_file = current_target_dir / new_name
            counter += 1

        try:
            # 안전하게 복사 진행
            shutil.copy2(file_path, destination_file)
            if is_various:
                va_count += 1
            else:
                normal_count += 1
        except Exception:
            pass

    # 8. 완료 처리
    status_label.config(text="🎉 모든 MP3 파일 통합 정리가 완료되었습니다!")
    percent_label.config(text=f"일반 곡: {normal_count}곡 / VA 곡: {va_count}곡 복사 완료")

    def on_close():
        os.startfile(str(target_path)) # 최종 정리된 도착지 폴더 열기
        root.destroy()

    close_button = tk.Button(root, text="닫기 및 정리된 폴더 열기", command=on_close, font=("맑은 고딕", 10, "bold"), bg="#e1e1e1")
    close_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    integrated_mp3_organizer()