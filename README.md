# Trader Tools by ThorLab

<p align="center">
<img width="679" height="189" alt="image" src="https://github.com/user-attachments/assets/3cc64c56-508d-490e-8016-ecfc9f5a7fa0" />
</p>
Софт, автоматически,  по тикеру ищет листинги на биржах, открывает ссылки, отслеживает цены и дельту. Для работы не нужны никакие данные: ни API ключи, ни прокси, построен на PyQt6.
<p>&nbsp;</p>
Поддерживает следующие биржи: <b>Binance, Bitget, Bybit, HyperLiquid, Gate, Mexc, Okx</b>

<p>&nbsp;</p>

<table align="center">
  <tr>
    <td align="center" valign="middle">
      <img src="https://i.imgur.com/9jrRDCj.png" height="380" alt="Главное окно">
    </td>
    <td align="center" valign="middle">
      <img src="https://i.imgur.com/Qg1qXeT.png" height="380" alt="Окно настроек">
    </td>
  </tr>
</table>

### Возможности
- Ищет листинги на фьючах/споте по тикеру 
- Отслеживает актуальные цены и дельту с момента запуска
- Автоматически открывает ссылки в браузере
- Можно запустить через хоткей из буфера обмена
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
git clone https://github.com/th0masi/trader-tools.git
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

2) Запустите сборку:
```powershell
./build.ps1
```
Готовый файл появится в папке `dist` (имя: `Trade Helper.exe`).

---

## Структура

- `app.py` — точка входа
- `core/gui` — GUI-модули (`window.py`, `settings.py`, `styles.py`, `utils.py`)
- `core/exchange` — клиенты бирж
- `core/monitor.py` — агрегатор запросов
- `assets/icons` — иконки (`icon.ico`, `icon.svg`)

---

## Обратная связь

- [Личное сообщение](https://t.me/th0masi)
- [Thor Lab](https://t.me/thor_lab)

🙏 Буду рад вашим идеям и предложениям.


