# ETHUSDT Analysis

Проект представляет собой систему для анализа и мониторинга фьючерса по
Ethereum/USDT на бирже Binance.

## Стек

- **Язык программирования:** Python
- **Библиотеки:** pandas, SQLAlchemy, websockets, numpy, pytest
- **База данных:** PostgreSQL
- **Управление зависимостями:** pip
- **Система контроля версий:** Git

## Описание проекта:

    FuturesProcessor Class:
        Описание: Класс для получения и обработки данных о фьючерсах.
        Функциональность:
            Подключается к Binance WebSocket.
            Обрабатывает сделки и сохраняет их в базу данных.
            Вызывает функцию для проверки изменения цены Ethereum (ETH).
            Позволяет читать данные из базы данных в формате DataFrame.

    FuturesTrade Model:
        Описание: Модель для таблицы futures_trades в базе данных.
        Содержание:
            id: Уникальный идентификатор сделки.
            symbol: Символ торговой пары (например, "ethusdt").
            price: Цена сделки.
            timestamp: Временная метка сделки.

## Торговля фьючерсами стала важным инструментом для инвесторов и трейдеров в криптовалютном пространстве. Анализ и мониторинг цен на Ethereum с использованием данного проекта позволяют:

    Следить за изменениями цен на рынке ETH/USDT в реальном времени.
    Автоматизировать процесс обработки и хранения данных о сделках.
    Проводить аналитику для выявления тенденций и паттернов.
    C некоторой вероятностью выполнять сделки.

Проект актуален для трейдеров и аналитиков, интересующихся криптовалютной
торговлей, и может быть использован в качестве основы для разработки более
сложных систем анализа и управления портфелем.

## Запуск программы из командной строки:

```shell
pip install -r requirements.txt
python main.py
```

## Запуск тестов из командной строки:

```shell
pytest
```

## Запуск проверки стиля кода:

```shell
flake8 .
```
