![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)


## Документация по развертыванию проекта


1. Клонируйте репозиторий

2. Создайте виртуальное окружение
    ``` 
    python3 -m venv venv
    ``` 
3. Активируйте виртуальное окружение
    ``` 
    source venv/bin/activate
    ``` 
4. Установите зависимотсти
    ```
    pip install -r requirements.txt 
    ```

5. Запустите скрипт
    ```
    python3 main.py --file example1.log --report average
    ``` 
6. Запуск тестов
    ```
    pytest -v test_log.py
    ```
7. Покрытие тестов
    ```
    pytest --cov=main --cov-report=term-missing
    ```
    ```
    pytest --cov=main --cov-report=html
    ```
   