#!/usr/bin/env python3
"""
Log in to QRZ.com in a real browser window, grab the xf_session cookie
automatically and run qrzdump.py to export the logbook to ADIF.

Usage:
    python qrz_login_export.py [out.adif]

Requires:  pip install -r requirements.txt   (uses the installed Edge/Chrome,
           no extra browser download needed)
"""
import os
import re
import subprocess
import sys
import time
from datetime import datetime

import requests
from playwright.sync_api import sync_playwright, Error as PlaywrightError

LOGBOOK_URL = 'https://logbook.qrz.com/logbook'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_SCRIPT = os.path.join(SCRIPT_DIR, 'qrzdump.py')
LOGIN_TIMEOUT = 600  # seconds the user has to finish logging in
POLL_INTERVAL = 2


def is_logged_in(xf_session):
  """Same check qrzdump.py relies on: the logbook page exposes a qhash input."""
  try:
    r = requests.get(LOGBOOK_URL, headers={'Cookie': 'xf_session=' + xf_session}, timeout=15)
  except requests.RequestException:
    return False
  return bool(re.search(r'name="qhash"', r.text))


def launch_browser(p):
  # Prefer the browsers already on the machine; fall back to Playwright's Chromium.
  for channel in ('msedge', 'chrome', None):
    try:
      if channel:
        return p.chromium.launch(channel=channel, headless=False)
      return p.chromium.launch(headless=False)
    except PlaywrightError:
      continue
  sys.exit('No usable browser found. Install Edge/Chrome or run: playwright install chromium')


def get_xf_session():
  with sync_playwright() as p:
    browser = launch_browser(p)
    context = browser.new_context()
    page = context.new_page()
    page.goto(LOGBOOK_URL)
    print('Log in to QRZ.com in the browser window that just opened...')

    deadline = time.time() + LOGIN_TIMEOUT
    try:
      while time.time() < deadline:
        for c in context.cookies():
          if c['name'] == 'xf_session' and c['domain'].endswith('qrz.com'):
            if is_logged_in(c['value']):
              return c['value']
        time.sleep(POLL_INTERVAL)
    except PlaywrightError:
      sys.exit('Browser was closed before login completed.')
    finally:
      try:
        browser.close()
      except PlaywrightError:
        pass
  sys.exit('Timed out waiting for login.')


def main():
  out = sys.argv[1] if len(sys.argv) > 1 else 'qrz_log_{}.adif'.format(datetime.now().strftime('%Y%m%d'))
  out = os.path.abspath(out)

  xf_session = get_xf_session()
  print('Login detected, session captured. Exporting logbook to', out)

  env = dict(os.environ, PYTHONUTF8='1')  # qrzdump.py opens the output with the default encoding
  rc = subprocess.call([sys.executable, DUMP_SCRIPT, xf_session, out], env=env)
  if rc == 0:
    print('Done:', out)
  sys.exit(rc)


if __name__ == '__main__':
  main()
