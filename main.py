import json
import click
import requests
import os, re

APPDATA = os.getenv("APPDATA")

__version__ = "0.0.3"

def check_for_updates():
    print("Frissítések keresése...")
    try:
        resp = requests.get(
            "https://raw.githubusercontent.com/pintermor9/sm-backup/main/main.py"
        )
    except requests.exceptions.SSLError:
        print("Hiba történt a frissítés keresése közben!")
        return
    else:
        if resp.status_code == 200:
            new_version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', resp.text, re.MULTILINE).group(1)
            if new_version != __version__:
                print("Frissítés érzékelve!")
                print("Frissítés letöltése...")
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print("Frissítés sikeres!")
            else:
                print("Nincs frissítés!")
        else:
            print("Hiba történt a frissítés keresése közben!")
                


# ANCHOR Manual config
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

#ANCHOR autoconfig
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

#ANCHOR save config
def save_config(conf):
    print("Konfiguráció mentése...")
    if not os.path.exists(f"{APPDATA}\\pintermor9"):
        os.mkdir(f"{APPDATA}\\pintermor9")
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "w") as f:
        json.dump(conf, f)

#ANCHOR load config
def load_config():
    print("Konfiguráció betöltése...")
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "r") as f:
        return json.load(f)


def main():
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
            last_text = f"[{last}]"
        fn = input(
            f"Melyik világot szeretnéd feltölteni (.db fájl neve; pl. Kozos_4) [default]\n{last_text} > "
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



if __name__ == "__main__":
    check_for_updates()
    click.pause()
    main()
