import json
import click
import requests
import os

APPDATA = os.getenv("APPDATA")


def manual_config():
    print(
        "Hiba történt a konfigurációs fájl automatikus generálása közben. Manuális beállítás szükséges:"
    )
    print("Kérlek add meg a Scrap Mechanic Save mappa útját!")
    print(
        "Ez alapból: '%appdata%\\Axolot Games\\Scrap Mechanic\\User\\User_<számok>\\Save\\Survival'"
    )
    while True:
        inp = input("> ")
        if not os.path.exists(inp.replace("%appdata%", APPDATA)):
            print("Nem létezik ilyen mappa! probáld ujra!")
        else:
            return {"savedir": inp.replace("%appdata%", APPDATA)}


def generate_config():
    print("Konfigurációs fájl generálása...")
    if not os.path.exists(f"{APPDATA}\\Axolot Games\\Scrap Mechanic\\User"):
        return manual_config()
    else:
        userdir = os.listdir(f"{APPDATA}\\Axolot Games\\Scrap Mechanic\\User")
        if len(userdir) != 1:
            return manual_config()
        else:
            user = userdir[0]
            if not os.path.exists(
                f"{APPDATA}\\Axolot Games\\Scrap Mechanic\\User\\{user}\\Save\\Survival"
            ):
                return manual_config()
            else:
                return {
                    "savedir": f"{APPDATA}\\Axolot Games\\Scrap Mechanic\\User\\{user}\\Save\\Survival"
                }


def save_config(conf):
    print("Konfiguráció mentése...")
    if not os.path.exists(f"{APPDATA}\\pintermor9"):
        os.mkdir(f"{APPDATA}\\pintermor9")
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "w") as f:
        json.dump(conf, f)


def load_config():
    print("Konfiguráció betöltése...")
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "r") as f:
        return json.load(f)


if not os.path.exists(f"{APPDATA}\\pintermor9\\sm-upload.json"):
    print("1. indítás érzékelve, konfiguráció generálása")
    conf = generate_config()
    save_config(conf)
else:
    conf = load_config()

while True:
    last = conf.get("last_file")
    last_text = ""
    if last:
        last_text = f"[alapértelmezett = {last}]"
    fn = input(
        f"Melyik világot szeretnéd feltölteni (.db fájl neve; pl. Kozos_4)\n{last_text} > "
    )
    if fn == "" and last:
        fn = last
    if os.path.exists(fpath := f"{conf['savedir']}\\{fn.replace('.db', '')}.db"):
        conf.update({"last_file": fn})
        save_config(conf)
        print("Fájl létezik, feltöltés...")
        break
    else:
        print("Nem létezik ilyen fájl!")

files = {"file": open(fpath, "rb")}

# ANCHOR Send the file to the server

while True:
    password = input("Kérlek add meg a jelszót (amit elküldtem discordra): ")

    try:
        resp = requests.post(
            f"https://sm-upload.pintermor9.repl.co/upload?password={password}",
            files=files,
        )
    except requests.exceptions.SSLError:
        print("Hibás jelszó!")

    else:
        if resp.status_code == 200:
            print(resp.text)
            break

        print("hiba:\n\n" + resp.text + "\n\nha többször megtörtén szólj nekem!")

click.pause()
