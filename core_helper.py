import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from collections import Counter
import itertools
import re
import time
import threading

# 버전 정보 
VERSION = "v1.1"

# 🎨 다크모드 색상
BG_MAIN = '#0d1117'
BG_SECTION = '#161b22'
BG_INPUT = '#21262d'
BG_BUTTON = '#238636'
BG_BUTTON_HOVER = '#2ea043'
FG_PRIMARY = '#f0f6fc'
FG_SECONDARY = '#8b949e'
FG_ACCENT = '#58a6ff'
BORDER_COLOR = '#30363d'

# 🎨 툴팁 클래스
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.tooltip_window:
            return
        
        # 메인 창의 정보 가져오기
        main_window = self.widget.winfo_toplevel()
        window_x = main_window.winfo_rootx()
        window_y = main_window.winfo_rooty()
        window_width = main_window.winfo_width()
        window_height = main_window.winfo_height()
        
        # 툴팁 크기 추정
        text_width = 300  # 고정 너비
        text_height = 150  # 고정 높이
        
        # 창 중앙에서 위로 200픽셀 위치 계산
        x = window_x + (window_width // 2) - (text_width // 2)
        y = window_y + (window_height // 2) - (text_height // 2) - 200
        
        # 창 경계 확인 및 조정
        if x < window_x + 10:
            x = window_x + 10
        elif x + text_width > window_x + window_width - 10:
            x = window_x + window_width - text_width - 10
            
        if y < window_y + 10:
            y = window_y + 10
        elif y + text_height > window_y + window_height - 10:
            y = window_y + window_height - text_height - 10

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, 
                        bg=BG_SECTION, fg=FG_PRIMARY, 
                        font=("Arial", 9), relief=tk.RAISED, bd=1,
                        padx=8, pady=4, justify=tk.LEFT,
                        width=40, wraplength=280)
        label.pack()

    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# 🎨 버튼 호버 효과
def create_hover_button(parent, text, command, **kwargs):
    button = tk.Button(parent, text=text, command=command, 
                      bg=BG_BUTTON, fg=FG_PRIMARY, 
                      font=kwargs.get('font', ("Arial", 12, "bold")),
                      relief=tk.FLAT, bd=0, 
                      padx=kwargs.get('padx', 20), pady=kwargs.get('pady', 8),
                      cursor="hand2")
    
    def on_enter(e):
        button.config(bg=BG_BUTTON_HOVER)
    def on_leave(e):
        button.config(bg=BG_BUTTON)
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    return button

# 🔍 스킬 파싱
def parse_skills(text):
    text = re.sub(r'[,，]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return [s.strip() for s in text.split() if s.strip()]

# 🧮 완전탐색
def find_optimal_combination():
    targets_text = target_entry.get().strip()
    cores_text = core_text.get("1.0", tk.END).strip()

    try:
        max_cores = int(max_core_entry.get().strip())
        if max_cores <= 0:
            max_cores = 6
    except ValueError:
        max_cores = 6

    if not targets_text or not cores_text:
        messagebox.showerror("입력 오류", "목표 스킬과 코어 목록을 모두 입력해주세요.")
        return

    targets = parse_skills(targets_text)
    core_lines = [parse_skills(line) for line in cores_text.split("\n") if line.strip()]
    valid_cores = [core for core in core_lines if sum(1 for s in core if s in targets) >= 2]

    result_box.delete("1.0", tk.END)
    if not valid_cores:
        result_box.insert(tk.END, "⚠️ 유효한 코어가 없습니다.\n")
        return

    # 로딩바 표시
    progress_frame.pack(pady=10)
    progress_bar.start()
    btn.config(state='disabled')

    # 백그라운드에서 탐색 실행
    def search_thread():
        result_box.insert(tk.END, f"🔍 탐색 시작...\n목표 스킬: {targets}\n유효 코어 수: {len(valid_cores)}\n\n")
        result_box.update()

        start = time.time()
        total = 0
        optimal = None

        for r in range(1, min(max_cores + 1, len(valid_cores) + 1)):
            result_box.insert(tk.END, f"▶ {r}개 코어 조합 탐색 중...\n")
            result_box.update()
            for combo in itertools.combinations(valid_cores, r):
                total += 1
                firsts = [c[0] for c in combo]
                if len(firsts) != len(set(firsts)):
                    continue
                counts = Counter()
                for c in combo:
                    for s in c:
                        if s in targets:
                            counts[s] += 1
                if all(counts[t] >= 2 for t in targets):
                    optimal = combo
                    result_box.insert(tk.END, f"✅ 최적 조합 발견! ({r}개)\n")
                    result_box.update()
                    break
            if optimal:
                break

        end = time.time()
        
        # 탐색 완료 후 중간 과정 메시지들 모두 지우고 결과만 표시
        result_box.delete("1.0", tk.END)
        
        if optimal:
            result_box.insert(tk.END, f"📊 탐색 완료 ({total:,} 조합, {end - start:.2f}초)\n\n")
            result_box.insert(tk.END, "📋 [최적 코어 조합]\n\n")
            for c in optimal:
                result_box.insert(tk.END, f" - {' / '.join(c)}\n")

            counts = Counter()
            for c in optimal:
                for s in c:
                    if s in targets:
                        counts[s] += 1

            result_box.insert(tk.END, "\n🎯 스킬 등장 횟수\n")
            for t in targets:
                result_box.insert(tk.END, f"{t}: {counts[t]}회\n")
        else:
            result_box.insert(tk.END, f"📊 탐색 완료 ({total:,} 조합, {end - start:.2f}초)\n\n")
            result_box.insert(tk.END, "⚠️ 조건을 만족하는 조합을 찾지 못했습니다.\n")

        result_box.see(tk.END)
        
        # 로딩바 숨기기
        progress_bar.stop()
        progress_frame.pack_forget()
        btn.config(state='normal')

    # 백그라운드 스레드에서 탐색 실행
    threading.Thread(target=search_thread, daemon=True).start()

# 🪄 도움말 토글 (제거됨 - 툴팁으로 대체)


# 🪟 기본 창
root = tk.Tk()
root.title(f"🍁 Maple Core Optimizer {VERSION}")
root.geometry("650x900")
root.configure(bg=BG_MAIN)

# 🧱 메인 프레임 (스크롤 없음)
main_frame = tk.Frame(root, bg=BG_MAIN)
main_frame.pack(fill="both", expand=True)

# 🏷️ 제목
title_label = tk.Label(main_frame, text=f"🍁 Maple Core Optimizer {VERSION}",
                       font=("Arial", 20, "bold"), bg=BG_MAIN, fg=FG_ACCENT)
title_label.pack(pady=(20, 5))

subtitle = tk.Label(main_frame, text="완전탐색 기반 최적 코어 조합 찾기",
                    font=("Arial", 10), bg=BG_MAIN, fg=FG_SECONDARY)
subtitle.pack(pady=(0, 20))

# ❓ 도움말 버튼 (맨 위쪽에 독립 배치)
help_button = tk.Button(main_frame, text="?", font=("Arial", 10, "bold"),
                        bg=BG_SECTION, fg=FG_ACCENT, width=2, height=1, relief=tk.RAISED, bd=1,
                        cursor="hand2")

def help_hover_enter(e):
    help_button.config(bg=BG_BUTTON_HOVER)
def help_hover_leave(e):
    help_button.config(bg=BG_SECTION)

help_button.bind("<Enter>", help_hover_enter)
help_button.bind("<Leave>", help_hover_leave)
help_button.pack(anchor=tk.NE, pady=(0, 10), padx=20)

# 📋 상단 입력 섹션 (이미지 레이아웃)
top_frame = tk.Frame(main_frame, bg=BG_MAIN)
top_frame.pack(fill=tk.X, padx=20, pady=10)

# 🎯 목표 스킬 (왼쪽)
target_frame = tk.Frame(top_frame, bg=BG_SECTION, relief=tk.RAISED, bd=1)
target_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

target_label = tk.Label(target_frame, text="🎯 목표 스킬 목록 (공백, 탭, 콤마 구분)", 
         font=("Arial", 11, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
target_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

target_entry = tk.Entry(target_frame, width=30, font=("Arial", 10), 
                        bg=BG_INPUT, fg=FG_PRIMARY, 
                        insertbackground=FG_PRIMARY,
                        relief=tk.FLAT, bd=5)
target_entry.pack(pady=(5, 15), padx=15, fill=tk.X)

# 🔢 최대 코어 수 (오른쪽, 세로 길이 늘림)
right_frame = tk.Frame(top_frame, bg=BG_MAIN)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

max_core_frame = tk.Frame(right_frame, bg=BG_SECTION, relief=tk.RAISED, bd=1)
max_core_frame.pack(fill=tk.BOTH, expand=True)

max_core_label = tk.Label(max_core_frame, text="🔢 최대 코어 수", 
         font=("Arial", 11, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
max_core_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

max_core_entry = tk.Entry(max_core_frame, width=10, font=("Arial", 10),
                          bg=BG_INPUT, fg=FG_PRIMARY,
                          insertbackground=FG_PRIMARY,
                          relief=tk.FLAT, bd=5)
max_core_entry.pack(pady=(5, 15), padx=15, fill=tk.X)
max_core_entry.insert(0, "6")

# 🎨 툴팁 추가 (물음표 버튼만)
ToolTip(help_button, """💡 사용법
1. 목표 스킬 입력 (예: 렌드 알파 타이탄 화이트 팽
   스컬 트랩 파이널 에펙)
2. 최대 코어 수 설정 (기본값: 6)
3. 코어 목록 입력 (한 줄에 3개씩)
4. '최적 조합 찾기' 클릭
5. 완전탐색으로 모든 스킬이 2회 이상 등장하는
   조합을 자동 탐색!""")

# 🧩 코어 목록
core_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
core_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

core_label = tk.Label(core_frame, text="🧩 코어 목록 (한 줄에 3개씩, 공백/탭/콤마 구분, 엑셀 복붙 가능)",
                      font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
core_label.pack(anchor="w", padx=15, pady=(15, 10))

core_text = scrolledtext.ScrolledText(core_frame, font=("Consolas", 10),
                                     bg=BG_INPUT, fg=FG_PRIMARY,
                                     height=12, wrap=tk.WORD,
                                     relief=tk.FLAT, bd=5)
core_text.pack(padx=15, pady=(0, 15), fill=tk.BOTH, expand=True)

# 🔍 버튼
btn = tk.Button(main_frame, text="🔍 최적 조합 찾기",
                bg=BG_BUTTON, fg=FG_PRIMARY,
                font=("Arial", 14, "bold"), relief=tk.FLAT,
                command=find_optimal_combination, padx=30, pady=10)
btn.pack(pady=15)

# 📊 로딩바 (숨김 상태로 시작)
progress_frame = tk.Frame(main_frame, bg=BG_MAIN)
progress_label = tk.Label(progress_frame, text="탐색 중...", 
                         font=("Arial", 10), bg=BG_MAIN, fg=FG_ACCENT)
progress_label.pack()

progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', 
                              style='TProgressbar')
progress_bar.pack(pady=5, padx=20, fill=tk.X)

# 📜 결과창
result_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
result_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

result_label = tk.Label(result_frame, text="📜 탐색 결과",
                        font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
result_label.pack(anchor="w", padx=15, pady=(15, 10))

result_box = scrolledtext.ScrolledText(result_frame, font=("Consolas", 10),
                                       bg=BG_INPUT, fg=FG_PRIMARY,
                                       height=8, wrap=tk.WORD,
                                       relief=tk.FLAT, bd=5)
result_box.pack(padx=15, pady=(0, 15), fill=tk.BOTH, expand=True)

# 💡 도움말 (툴팁으로 대체됨)


# 🎨 추가 툴팁

# 🪄 실행
root.mainloop()
