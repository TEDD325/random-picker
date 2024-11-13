import random
import csv
import os
from datetime import datetime
import math

BASE_PATH = "/Users/dohk/Dropbox/codespace/code/Python/random-picker"  # 절대 경로 설정

def get_history_file(course_name):
    # 절대 경로를 기반으로 파일 경로 생성
    return os.path.join(BASE_PATH, f"selection_history_{course_name}.csv")

def load_history(course_name):
    history_file = get_history_file(course_name)
    if not os.path.exists(history_file):
        return [], [], None
    
    with open(history_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_data = list(reader)
        if not all_data:
            return [], [], None
        
        members = all_data[0]  # 첫 번째 줄은 전체 멤버 리스트
        initial_time = all_data[1][0] if len(all_data) > 1 else None  # 두 번째 줄의 첫 번째 컬럼은 최초 실행 시간
        history = all_data[2:]  # 나머지는 선택 이력
        return members, history, initial_time

def save_history(course_name, members, selected_person, is_first_run=False, initial_time=None):
    history_file = get_history_file(course_name)
    mode = 'w' if is_first_run else 'a'
    with open(history_file, mode, encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if is_first_run:
            writer.writerow(members)  # 첫 줄: 멤버 리스트
            writer.writerow([initial_time])  # 두 번째 줄: 최초 실행 시간
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_person])  # 선택된 멤버 기록

def reset_history(course_name, keep_members=True):
    members, _, initial_time = load_history(course_name)
    history_file = get_history_file(course_name)
    if keep_members and members:
        with open(history_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(members)  # 첫 줄: 멤버 리스트
            writer.writerow([initial_time])  # 두 번째 줄: 최초 실행 시간 유지
    else:
        if os.path.exists(history_file):
            os.remove(history_file)

def get_weeks_passed(history, initial_time):
    if not initial_time:
        return 0
    first_date = datetime.strptime(initial_time, '%Y-%m-%d %H:%M:%S')
    current_date = datetime.now()
    days_passed = (current_date - first_date).days
    return math.ceil(days_passed / 7)

def initialize_members():
    course_name = input("과정명을 입력하세요: ").strip()
    print("\n멤버 초기화를 시작합니다.")
    members = []
    while True:
        name = input("멤버 이름을 입력하세요 (입력 완료시 엔터 두 번): ").strip()
        if not name and members:
            break
        elif name:
            members.append(name)
    return course_name, members

def calculate_weights(members, history):
    # 각 멤버의 선택 횟수를 계산
    selection_counts = {member: 0 for member in members}
    for _, selected_person in history:
        if selected_person in selection_counts:
            selection_counts[selected_person] += 1
    
    # 선택되지 않은 사람에게는 기본 가중치 1.0, 선택된 사람에게는 기하급수적으로 감소하는 가중치 부여
    weights = []
    for member in members:
        count = selection_counts[member]
        weight = 1.0 if count == 0 else (0.5 ** count)  # 선택될 때마다 0.5의 비율로 가중치 감소
        weights.append(weight)
    
    return weights

def pick_random_person(course_name):
    members, history, initial_time = load_history(course_name)
    
    # 파일이 없거나 비어있는 경우 (최초 실행)
    if not members:
        course_name, members = initialize_members()
        if not members:
            print("멤버가 입력되지 않았습니다.")
            return None
        initial_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_history(course_name, members, "", is_first_run=True, initial_time=initial_time)
    
    # 주차 확인 및 리셋
    weeks_passed = get_weeks_passed(history, initial_time)
    if weeks_passed >= len(members) and history:
        print(f"\n{len(members)}주가 지나 기록을 리셋합니다.")
        reset_history(course_name, keep_members=True)
        history = []
    
    # 가중치를 계산하여 랜덤 선택
    weights = calculate_weights(members, history)
    selected = random.choices(members, weights=weights, k=1)[0]
    save_history(course_name, members, selected)
    
    return selected, len(history) + 1, weeks_passed + 1

def main():
    course_name = input("과정명을 입력하세요: ").strip()
    selected_person, selection_count, current_week = pick_random_person(course_name)
    
    if selected_person:
        print(f"\n[과정: {course_name}, Week {current_week}] 선택된 사람: {selected_person}")
        print(f"이번 주차의 {selection_count}번째 선택입니다.")

if __name__ == "__main__":
    main()