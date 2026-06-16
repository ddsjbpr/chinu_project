import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main() -> None:
    """Launch the Streamlit app and open it in Chrome browser."""
    app_path = Path(__file__).resolve().parent / "app.py"
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]

    process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    time.sleep(3)

    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]

    chrome_found = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_found = path
            break

    if chrome_found:
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_found))
        webbrowser.get("chrome").open("http://localhost:8501")
    else:
        webbrowser.open("http://localhost:8501")

    try:
        stdout = process.stdout
        if stdout is not None:
            for line in stdout:
                print(line, end="")
    except KeyboardInterrupt:
        process.terminate()
        print("\nStreamlit stopped.")


if __name__ == "__main__":
    main()
