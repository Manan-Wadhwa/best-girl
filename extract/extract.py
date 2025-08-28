# requires: pip install fandom-py tqdm
import os, json, sys, csv, urllib.parse
import fandom
from tqdm import tqdm

# ensure UTF-8 stdout (Windows)
sys.stdout.reconfigure(encoding="utf-8")

waifus = [
    # ("Hinata Hyūga", "naruto"),
    # ("Tsunade", "naruto"),
    # ("Nezuko Kamado", "kimetsu-no-yaiba"),
    # ("Mitsuri Kanroji", "kimetsu-no-yaiba"),
    # ("Marin Kitagawa", "my-dress-up-darling"),
    # ("Zero Two", "darling-in-the-franxx"),
    # ("Maki Zenin", "jujutsu-kaisen"),
    # ("Yor Forger", "spy-x-family"),
    ("Rem", "saimoe"),
    ("Asuna Yuuki", "hero"),
    ("Nico Robin", "onepiece"),
    # ("Erza Scarlet", "fairy-tail"),
    ("Rias Gremory", "highschooldxd"),
    ("Mai Sakurajima", "aobuta"),
    ("C.C.", "codegeass"),
    ("Emilia", "saimoe"),
    # ("Kurisu Makise", "steins-gate"),
    ("Shinobu Oshino", "bakemonogatari"),
    # ("Tohru", "miss-kobayashis-dragon-maid"),
    # ("Holo", "spice-and-wolf"),
    # ("Power", "chainsaw-man"),
    ("Shinobu Kocho", "kimetsu-no-yaiba"),
#     ("Nobara Kugisaki", "jujutsu-kaisen"),
#     ("Yoruichi Shihōin", "bleach"),
#     ("Yukino Yukinoshita", "oregairu")
]

OUT_DIR = "waifu_fandom_pages"
os.makedirs(OUT_DIR, exist_ok=True)
status_rows = []

for name, wiki in tqdm(waifus, desc="Fetching wiki pages"):
    fandom.set_wiki(wiki)
    record = {"name": name, "wiki": wiki, "status": None, "url": None, "error": None}
    try:
        # try direct fetch (follows redirects)
        page = fandom.page(title=name, redirect=True)
        record.update({"status": "fetched", "url": page.url})
        data = {
            "requested_name": name,
            "resolved_title": page.title,
            "url": page.url,
            "summary": page.summary,
            "full_text": page.plain_text
        }
        fname = os.path.join(OUT_DIR, f"{name.replace(' ', '_')}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        # fallback: try search on the wiki and fetch first hit
        try:
            results = fandom.search(name)
            if results:
                best = results[0]  # dict with 'title' and 'url' typically
                # attempt to fetch using resolved title
                page = fandom.page(title=best.get("title") or name, redirect=True)
                record.update({"status": "fetched_via_search", "url": page.url})
                data = {
                    "requested_name": name,
                    "resolved_title": page.title,
                    "url": page.url,
                    "summary": page.summary,
                    "full_text": page.plain_text
                }
                fname = os.path.join(OUT_DIR, f"{name.replace(' ', '_')}.json")
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                raise RuntimeError("No search results")
        except Exception as e2:
            # final fallback: construct encoded URL and log error
            encoded = urllib.parse.quote(name.replace(" ", "_"))
            fallback = f"https://{wiki}.fandom.com/wiki/{encoded}"
            record.update({"status": "fallback", "url": fallback, "error": str(e2 or e)})
    status_rows.append(record)
    # safe console line (avoid printing raw unicode errors)
    print(f"{name} -> {record['status']}: {record['url']}")

# save summary CSV/JSON
with open(os.path.join(OUT_DIR, "fetch_status.json"), "w", encoding="utf-8") as f:
    json.dump(status_rows, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, "fetch_status.csv"), "w", encoding="utf-8", newline='') as f:
    w = csv.DictWriter(f, fieldnames=["name", "wiki", "status", "url", "error"])
    w.writeheader()
    w.writerows(status_rows)

print("Done. Check fetch_status.json / fetch_status.csv for which pages need manual attention.")
