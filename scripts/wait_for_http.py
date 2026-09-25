"""Wait briefly for localhost test servers."""
import sys
import time
from urllib.request import urlopen
from urllib.error import URLError

for url in sys.argv[1:]:
    deadline = time.monotonic() + 45
    while True:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    break
        except (URLError, TimeoutError):
            pass
        if time.monotonic() >= deadline:
            raise SystemExit(f"Test server did not become ready: {url}")
        time.sleep(0.5)
