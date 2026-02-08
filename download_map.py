import os
import time
import requests
import mercantile
from tqdm import tqdm
from dotenv import load_dotenv
# ---------------- CONFIG ---------------- #

API_KEY = os.getenv("SECRET_KEY") # create .env file with your maptiler api key saved to SECRET_KEY variable
BBOX = (-111.98, 33.38, -111.87, 33.46) #(West, South, East, North) or (x_min, y_min, x_max, y_max) box to bound region to download

ZOOM_LEVELS = [9] # the higher the number the closer the zoom ((10 - 15) typical range)

TILE_URL = (
    "https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png"
    "?key=" + API_KEY
)

OUTPUT_DIR = "tiles"
REQUEST_DELAY = 0.05

# ---------------------------------------- #

def download_tile(z, x, y):
    tile_path = os.path.join(OUTPUT_DIR, str(z), str(x), f"{y}.png")
    if os.path.exists(tile_path):
        return

    os.makedirs(os.path.dirname(tile_path), exist_ok=True)
    r = requests.get(TILE_URL.format(z=z, x=x, y=y), timeout=20)
    if r.status_code == 200:
        with open(tile_path, "wb") as f:
            f.write(r.content)

    time.sleep(REQUEST_DELAY)


def main():
    tiles = []
    for z in ZOOM_LEVELS:
        tiles.extend(mercantile.tiles(*BBOX, z))

    for t in tqdm(tiles):
        download_tile(t.z, t.x, t.y)


if __name__ == "__main__":
    main()