import sys
sys.path.insert(0, r"C:\Users\Ram Singh Bairwa\OneDrive\Desktop\youtube statics\.venv\Lib\site-packages")

import os
import shutil
import kagglehub

raw_dir = r"c:\Users\Ram Singh Bairwa\OneDrive\Desktop\youtube statics\data\raw"

countries = ["INvideos.csv", "GBvideos.csv", "CAvideos.csv"]

for c in countries:
    print(f"[*] Downloading '{c}' via kagglehub...")
    p = kagglehub.dataset_download("datasnaek/youtube-new", c)
    target = os.path.join(raw_dir, c)
    shutil.copy2(p, target)
    size_mb = os.path.getsize(target) / (1024 * 1024)
    print(f"[+] Downloaded and copied {c} ({size_mb:.2f} MB)")

print("\n[+] All requested country datasets downloaded successfully!")

