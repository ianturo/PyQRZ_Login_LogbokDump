# QRZ.com ADIF Export  without subscription based on PyQrzComLogbookDump

This work is derived from <https://github.com/lasek0/PyQrzComLogbookDump> and makes it easier to obtain the `xf_session` variable.

Export your QRZ.com logbook to an ADIF file without copying the `xf_session` cookie by hand.

`qrz_login_export.py` opens a browser window at <https://logbook.qrz.com/>, waits for you to log in, captures the `xf_session` cookie automatically and then runs `qrzdump.py` to download every QSO.

## Requirements

- Python 3.8+
- Microsoft Edge or Google Chrome installed (Playwright drives the existing browser, no extra download needed). If neither is found, run `playwright install chromium`.
- A QRZ.com account with logbook access (the dump script targets subscriber logbooks).

## Installation

```
pip install -r requirements.txt
```

## Usage

```
python qrz_login_export.py [output.adif]
```

1. A browser window opens at `logbook.qrz.com`.
2. Log in as usual (you have up to 10 minutes).
3. Once the logbook loads, the script captures the session, closes the browser and starts the export.
4. Progress is printed to the terminal, one QSO at a time.
5. The ADIF file is written when it finishes.

If you omit `output.adif`, the file is named `qrz_log_YYYYMMDD.adif` and saved in the current directory.

### Running the dump manually

If you already have an `xf_session` value you can skip the browser step:

```
python qrzdump.py <xf_session> <output.adif>
```

## Files

| File | Purpose |
| --- | --- |
| `qrz_login_export.py` | Browser login, cookie capture, launches the dump |
| `qrzdump.py` | Scrapes the logbook and writes the ADIF file |
| `requirements.txt` | Python dependencies (`requests`, `playwright`) |

## Notes and troubleshooting

- **Slow export:** `qrzdump.py` requests one QSO at a time, so large logbooks take a while.
- **Browser closed early:** the script exits with "Browser was closed before login completed." Run it again.
- **Timed out:** if login isn't detected within 10 minutes, the script exits. Run it again.
- **Non-ASCII characters:** the launcher sets `PYTHONUTF8=1` so names with accents are written correctly on Windows. Set it yourself if you run `qrzdump.py` directly.
- **Privacy:** your session cookie is only used locally, to talk to qrz.com. Treat it like a password and don't share it. The ADIF file contains your log data.
- **Fragility:** `qrzdump.py` scrapes QRZ's HTML, so changes to the QRZ site can break it.

![GitHub Stats](https://ghstats.dev/api/card?username=ianturo)
