# Makefile для Python проекта

# Имя виртуального окружения
VENV = venv

# Основной Python-скрипт для запуска
MAIN = main.py
INIT = init_db.py

# Пути к файлам зависимостей
REQUIREMENTS_DIR = requirements
REQUIREMENTS = $(REQUIREMENTS_DIR)/requirements.txt
DEV_REQUIREMENTS = $(REQUIREMENTS_DIR)/dev.txt

# Проверка операционной системы
ifeq ($(OS),Windows_NT)
	PYTHON = python
	ACTIVATE = $(VENV)\Scripts\activate
	RM = rmdir /s /q $(VENV)
else
	PYTHON = python3
	ACTIVATE = source $(VENV)/bin/activate
	RM = rm -rf $(VENV)
endif

# Цель: setup - Создание виртуального окружения и установка зависимостей
setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install -r $(REQUIREMENTS)

# Цель: setup-dev - Установка зависимостей для разработки
setup-dev:
	$(ACTIVATE) && pip install -r $(DEV_REQUIREMENTS)
    
dev:
	$(ACTIVATE) && $(PYTHON) $(MAIN) --debug

# Цель: run - Запуск основного Python-скрипта
run:
	$(ACTIVATE) && $(PYTHON) $(MAIN)

# Цель: lint - Проверка качества кода
lint:
	black $(MAIN)
    
# Очистка виртуального окружения
clean:
	$(RM)

# Цель: init-db - Инициализация базы данных
init:
	$(ACTIVATE) && $(PYTHON) $(INIT)

# Цель clean-bd - Удаление базы данных
clean-bd:
ifeq ($(OS),Windows_NT)
	del shortener\shortener.sqlite
else
	rm shortener/shortener.sqlite
endif