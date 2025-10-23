import tkinter as tk
from tkinter import scrolledtext, messagebox
from collections import Counter
import re
import itertools
import time

# 예쁜 다크모드 색상 정의
BG_MAIN = '#0d1117'          # GitHub 다크 배경
BG_SECTION = '#161b22'       # 섹션 배경
BG_INPUT = '#21262d'         # 입력 필드
BG_BUTTON = '#238636'        # GitHub 그린 버튼
FG_PRIMARY = '#f0f6fc'       # 밝은 흰색
FG_SECONDARY = '#8b949e'     # 회색 텍스트
FG_ACCENT = '#58a6ff'        # 파란색 강조

def parse_skills(text):
    """텍스트에서 스킬명을 추출하는 함수 (공백, 탭, 콤마 구분자 자동 인식)"""
    # 콤마를 공백으로 변환하고, 연속된 공백/탭을 하나의 공백으로 변환
    text = re.sub(r'[,，]', ' ', text)  # 콤마 제거
    text = re.sub(r'\s+', ' ', text)    # 연속된 공백을 하나로
    return [skill.strip() for skill in text.split() if skill.strip()]

def find_optimal_combination():
    """완전탐색으로 최적 코어 조합 찾기"""
    targets_text = target_entry.get().strip()
    cores_text = core_text.get("1.0", tk.END).strip()
    
    # 최대 탐색 코어 수
    try:
        max_cores = int(max_cores_entry.get().strip())
        if max_cores <= 0:
            max_cores = 6
    except ValueError:
        max_cores = 6

    if not targets_text or not cores_text:
        messagebox.showerror("입력 오류", "목표 스킬과 코어 목록을 모두 입력해주세요.")
        return

    # 목표 스킬 파싱
    targets = parse_skills(targets_text)
    
    # 코어 목록 파싱 (한 줄당 2-3개 스킬)
    core_lines = []
    for line in cores_text.split("\n"):
        if line.strip():
            skills = parse_skills(line)
            if len(skills) >= 2:
                core_lines.append(skills)

    if not targets or not core_lines:
        messagebox.showerror("입력 오류", "올바른 형식으로 입력해주세요.")
        return

    # 유효한 코어 필터링 (목표 스킬 2개 이상 포함)
    valid_cores = []
    for i, core in enumerate(core_lines):
        target_count = sum(1 for skill in core if skill in targets)
        if target_count >= 2:  # 목표 스킬 2개 이상 포함
            valid_cores.append(core)

    if not valid_cores:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "⚠️ 유효한 코어가 없습니다.\n")
        result_box.insert(tk.END, "목표 스킬이 2개 이상 포함된 코어만 유효합니다.\n")
        return

    # 완전탐색 시작
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, "🔍 완전탐색 시작...\n")
    result_box.insert(tk.END, f"목표 스킬: {targets}\n")
    result_box.insert(tk.END, f"유효한 코어 수: {len(valid_cores)}\n")
    result_box.insert(tk.END, f"최대 탐색 코어 수: {max_cores}\n\n")
    result_box.update()

    start_time = time.time()
    total_combinations = 0
    optimal_combination = None
    optimal_size = float('inf')

    # r=1부터 max_cores까지 모든 조합 탐색
    for r in range(1, min(max_cores + 1, len(valid_cores) + 1)):
        result_box.insert(tk.END, f"🔍 {r}개 코어 조합 탐색 중...\n")
        result_box.update()
        
        combinations_count = 0
        for combination in itertools.combinations(valid_cores, r):
            combinations_count += 1
            total_combinations += 1
            
            # 중복 첫 스킬 체크
            first_skills = [core[0] for core in combination]
            if len(first_skills) != len(set(first_skills)):
                continue  # 첫 스킬 중복 있으면 제외
            
            # 스킬 등장 횟수 계산
            skill_counter = Counter()
            for core in combination:
                for skill in core:
                    if skill in targets:
                        skill_counter[skill] += 1
            
            # 모든 목표 스킬이 2회 이상 등장하는지 확인
            if all(skill_counter[s] >= 2 for s in targets):
                optimal_combination = combination
                optimal_size = r
                result_box.insert(tk.END, f"✅ 최적 조합 발견! ({r}개 코어)\n")
                result_box.update()
                break
        
        if optimal_combination:
            break
        
        result_box.insert(tk.END, f"   {combinations_count}개 조합 탐색 완료\n")
        result_box.update()

    end_time = time.time()
    elapsed_time = end_time - start_time

    # 결과 출력
    result_box.insert(tk.END, f"\n📊 탐색 완료!\n")
    result_box.insert(tk.END, f"총 탐색 조합 수: {total_combinations:,}개\n")
    result_box.insert(tk.END, f"소요 시간: {elapsed_time:.2f}초\n")
    result_box.insert(tk.END, f"최적 조합 크기: {optimal_size}개 코어\n\n")

    if optimal_combination:
        result_box.insert(tk.END, "📋 [최적 코어 조합]\n\n")
        for i, core in enumerate(optimal_combination, 1):
            result_box.insert(tk.END, f"{' - '.join(core)}\n")

        # 스킬 등장 횟수 계산
        skill_counter = Counter()
        for core in optimal_combination:
            for skill in core:
                if skill in targets:
                    skill_counter[skill] += 1

        result_box.insert(tk.END, "\n✅ 스킬 등장 횟수\n")
        for skill in targets:
            result_box.insert(tk.END, f"{skill}: {skill_counter[skill]}회\n")

        # 부족하거나 초과된 스킬 확인
        insufficient = [s for s in targets if skill_counter[s] < 2]
        exceeded = [s for s in targets if skill_counter[s] > 2]
        
        if insufficient:
            result_box.insert(tk.END, f"\n⚠️ 부족한 스킬: {', '.join(insufficient)}\n")
        if exceeded:
            result_box.insert(tk.END, f"\n⚠️ 초과된 스킬: {', '.join(exceeded)}\n")
        
        if not insufficient and not exceeded:
            result_box.insert(tk.END, "\n🎯 모든 스킬이 정확히 2회 이상 등장했습니다!\n")
    else:
        result_box.insert(tk.END, "⚠️ 조건을 만족하는 코어 조합을 찾을 수 없습니다.\n")
        result_box.insert(tk.END, "최대 코어 수를 늘리거나 코어 목록을 확인해주세요.\n")

# GUI 생성 및 설정
root = tk.Tk()
root.title("🍁 Maple Core Optimizer (완전탐색)")
root.geometry("900x950")
root.configure(bg=BG_MAIN)

# 메인 프레임
main_frame = tk.Frame(root, bg=BG_MAIN)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# 제목
title_label = tk.Label(main_frame, text="🍁 Maple Core Optimizer", 
                      font=("Arial", 24, "bold"), bg=BG_MAIN, fg=FG_ACCENT)
title_label.pack(pady=(0, 5))

subtitle_label = tk.Label(main_frame, text="완전탐색 기반 최적 코어 조합 찾기", 
                         font=("Arial", 12), bg=BG_MAIN, fg=FG_SECONDARY)
subtitle_label.pack(pady=(0, 20))

# 목표 스킬 입력 섹션
target_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
target_frame.pack(fill=tk.X, pady=10)

target_label = tk.Label(target_frame, text="🎯 목표 스킬 목록", 
         font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
target_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

target_desc = tk.Label(target_frame, text="(공백, 탭, 콤마로 구분)", 
         font=("Arial", 9), bg=BG_SECTION, fg=FG_SECONDARY)
target_desc.pack(anchor=tk.W, padx=10)

target_entry = tk.Entry(target_frame, width=80, font=("Arial", 11), 
                        bg=BG_INPUT, fg=FG_PRIMARY, 
                        insertbackground=FG_PRIMARY,
                        relief=tk.FLAT, bd=5)
target_entry.pack(pady=(5, 10), padx=10, fill=tk.X)

# 최대 탐색 코어 수 입력 섹션
max_cores_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
max_cores_frame.pack(fill=tk.X, pady=10)

max_cores_label = tk.Label(max_cores_frame, text="🔢 최대 탐색 코어 수", 
         font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
max_cores_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

max_cores_entry = tk.Entry(max_cores_frame, width=10, font=("Arial", 11),
                          bg=BG_INPUT, fg=FG_PRIMARY,
                          insertbackground=FG_PRIMARY,
                          relief=tk.FLAT, bd=5)
max_cores_entry.pack(pady=(5, 10), padx=10, anchor=tk.W)
max_cores_entry.insert(0, "6")  # 기본값 설정

# 코어 목록 입력 섹션
core_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
core_frame.pack(fill=tk.BOTH, expand=True, pady=10)

core_label = tk.Label(core_frame, text="🧩 코어 목록", 
         font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
core_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

core_desc = tk.Label(core_frame, text="(한 줄에 3개씩, 엑셀 복붙 가능)", 
         font=("Arial", 9), bg=BG_SECTION, fg=FG_SECONDARY)
core_desc.pack(anchor=tk.W, padx=10)

core_text = scrolledtext.ScrolledText(core_frame, width=80, height=20, 
                                      font=("Consolas", 10), wrap=tk.WORD,
                                      bg=BG_INPUT, fg=FG_PRIMARY, 
                                      insertbackground=FG_PRIMARY,
                                      relief=tk.FLAT, bd=5)
core_text.pack(pady=(5, 10), padx=10, fill=tk.BOTH, expand=True)

# 버튼 섹션
button_frame = tk.Frame(main_frame, bg=BG_MAIN)
button_frame.pack(pady=20)

# 계산 버튼
calc_button = tk.Button(button_frame, text="🔍 최적 조합 찾기", 
                       command=find_optimal_combination,
                       bg=BG_BUTTON, fg=FG_PRIMARY, 
                       font=("Arial", 14, "bold"),
                       relief=tk.FLAT, bd=0, padx=30, pady=10)
calc_button.pack()

# 결과 섹션
result_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

result_label = tk.Label(result_frame, text="📜 탐색 결과", 
         font=("Arial", 12, "bold"), bg=BG_SECTION, fg=FG_ACCENT)
result_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

result_box = scrolledtext.ScrolledText(result_frame, width=80, height=15, 
                                       font=("Consolas", 10), bg=BG_INPUT, 
                                       fg=FG_PRIMARY,
                                       wrap=tk.WORD, relief=tk.FLAT, bd=5,
                                       insertbackground=FG_PRIMARY)
result_box.pack(pady=(5, 10), padx=10, fill=tk.BOTH, expand=True)

# 사용법 안내
help_frame = tk.Frame(main_frame, bg=BG_SECTION, relief=tk.RAISED, bd=2)
help_frame.pack(fill=tk.X, pady=10)

help_text = """
💡 사용법 (완전탐색 버전):
1. 목표 스킬을 입력하세요 (예: 렌드 알파 타이탄 화이트 팽 블래스트 트랩 스컬 커맨드)
2. 최대 탐색 코어 수를 설정하세요 (기본값: 6개)
3. 코어 목록을 입력하세요 (한 줄에 3개씩, 엑셀에서 복사 가능)
4. '최적 조합 찾기' 버튼을 클릭하세요
5. 완전탐색으로 모든 스킬이 2회 이상 등장하는 최소 조합을 찾습니다!

⚠️ 주의: 코어 수가 많을 경우 탐색 시간이 오래 걸릴 수 있습니다.
"""
help_label = tk.Label(help_frame, text=help_text, 
                     font=("Arial", 9), bg=BG_SECTION, fg=FG_SECONDARY,
                     justify=tk.LEFT)
help_label.pack(pady=15, padx=15, fill=tk.X)

# 프로그램 실행
root.mainloop()
