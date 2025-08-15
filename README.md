# Trade Helper

Простой помощник для быстрого поиска и отслеживания тикеров на биржах, построен на PyQt6.


Поддерживаемые биржи: **Gate.io**, **Hyperliquid**, **Binance**, **Bitget**, **Bybit**, **Mexc**, **Okex**

### Возможности
- Открывать найденные ссылки на биржи в браузере
- Выбор режима открытия: в новом окне или в текущем
- Режим «Отслеживать цены» с таблицей обновлений
- Отображение дельты цены с момента старта отслеживания
- Выбор бирж для открытия тикеров/отслеживания
- Выбор Интервал обновления цен
- Прозрачность окна и тема (Светлая / Тёмная)
- Always-on-top окно
- Хоткей для быстрого старта
---

## Как запустить (способ 1 — через Git)

1) Установите Python 3.10+ с официального сайта.

2) Откройте PowerShell и создайте папку, куда хотите поставить проект, затем перейдите в неё:
```powershell
mkdir D:\Apps\TradeHelper
cd D:\Apps\TradeHelper
```

3) Склонируйте репозиторий:
```powershell
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> .
```

4) Создайте виртуальное окружение и установите зависимости:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

5) Запустите приложение:
```powershell
python app.py
```

---

## Как запустить (способ 2 — без Git, через скачивание)

1) Скачайте ZIP проекта с GitHub и распакуйте в удобную папку, например `D:\Apps\TradeHelper`.

2) В PowerShell перейдите в папку проекта:
```powershell
cd D:\Apps\TradeHelper
```

3) Создайте виртуальное окружение и установите зависимости:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

4) Запустите приложение:
```powershell
python app.py
```

---

## Сборка в .exe (Windows)

При желании вы можете собрать проект в .exe и запускать софт как обычную программу, без необходимости использовать консоль/IDE.
1) В консоли активируйте окружение и установите зависимости:
```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2) Убедитесь, что в `assets/icons/` есть иконка `icon.ico` (или `trade_helper.ico`).

3) Запустите сборку:
```powershell
./build.ps1
```
Готовый файл появится в папке `dist` (имя: `Trade Helper.exe`).

Подсказка: при желании можно указать параметры:
```powershell
./build.ps1 -OneFile:$true -Entry "app.py"
```

---

## Структура

- `app.py` — точка входа
- `core/gui` — GUI-модули (`window.py`, `settings.py`, `styles.py`, `utils.py`)
- `core/exchange` — клиенты бирж (Gate, Hyperliquid)
- `core/monitor.py` — агрегатор запросов
- `assets/icons` — иконки (`icon.ico`, `icon.svg`)

---

## Обратная связь

- [Личное сообщение](https://t.me/th0masi)
- [Thor Lab](https://t.me/thor_lab)

🙏 Буду рад вашим идеям и предложениям.


