#!/bin/bash
# Запуск всех тестов
python -m pytest tests/ -v --cov=src

# Запуск только unit-тестов
python -m pytest tests/unit/ -v

# Запуск только интеграционных тестов
python -m pytest tests/integration/ -v

# Запуск с генерацией отчета о покрытии
python -m pytest tests/ -v --cov=src --cov-report=html