#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(command):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_path)
        if result.returncode != 0:
            print(f"Ошибка выполнения команды: {command}")
            print(f"Stderr: {result.stderr}")
            return False
        print(f"✓ {command}")
        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"Исключение при выполнении команды {command}: {e}")
        return False

# Путь к проекту
project_path = r"C:\Users\fonsh\Downloads\coachapp"

print("=" * 50)
print("  Обновление GitHub репозитория")
print("=" * 50)

# Проверка существования папки
if not os.path.exists(project_path):
    print(f"Ошибка: Папка {project_path} не найдена!")
    sys.exit(1)

# Переход в папку проекта
os.chdir(project_path)

print("1. Проверка Git репозитория...")
if not run_command("git status"):
    print("Ошибка: Не удается получить статус Git")
    sys.exit(1)

print("\n2. Удаление всех файлов из индекса Git...")
run_command("git rm -r --cached . || echo 'Нечего удалять'")

print("\n3. Добавление всех файлов из текущей папки...")
if not run_command("git add ."):
    print("Ошибка при добавлении файлов")
    sys.exit(1)

print("\n4. Создание коммита...")
if not run_command('git commit -m "Полная очистка и обновление репозитория"'):
    print("Ошибка при создании коммита")
    sys.exit(1)

print("\n5. Отправка на GitHub...")
if not run_command("git push origin main --force"):
    print("Ошибка при отправке на GitHub")
    sys.exit(1)

print("\n" + "=" * 50)
print("  Готово! Репозиторий успешно обновлен")
print("=" * 50)
