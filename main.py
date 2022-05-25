import json
import click
import requests
import os
import re

APPDATA = os.getenv("APPDATA")

__version__ = "0.1.0"


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
            new_version = re.search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', resp.text, re.MULTILINE).group(1)

            def need_update(new_version):
                if new_version.split(".")[0] > __version__.split(".")[0]:
                    return True
                if new_version.split(".")[1] > __version__.split(".")[1]:
                    return True
                if new_version.split(".")[2] > __version__.split(".")[2]:
                    return True
                return False
            if need_update(new_version):
                print("Frissítés érzékelve!")
                print("Frissítés letöltése...")
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print("Frissítés sikeres!")
                click.pause()
                exit(0)
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

# ANCHOR autoconfig


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

# ANCHOR save config


def save_config(conf):
    if not os.path.exists(f"{APPDATA}\\pintermor9"):
        os.mkdir(f"{APPDATA}\\pintermor9")
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "w") as f:
        json.dump(conf, f)

# ANCHOR load config


def load_config():
    with open(f"{APPDATA}\\pintermor9\\sm-upload.json", "r") as f:
        return json.load(f)


def main_upload(conf):
    while True:
        last = conf.get("last_file")
        last_text = ""
        if last:
            last_text = f"[{last}]"
        fn = input(
            f"Melyik világot szeretnéd feltölteni (.db fájl neve; pl. 'Közös 4') [default]\n{last_text} > "
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
        password = conf.get("password")
        if not password:
            password = input(
                "Kérlek add meg a jelszót (amit elküldtem discordra): ")
            conf.update({"password": password})
            save_config(conf)

        try:
            resp = requests.post(
                f"https://sm-upload.pintermor9.repl.co/upload?password={password}",
                files=files,
            )
        except requests.exceptions.SSLError:
            print("requests.exceptions.SSLError: Hibás jelszó! probáld ujra")
            del conf["password"]
            save_config(conf)

        else:
            if resp.status_code == 200:
                print(resp.text)
                break

            if resp.status_code == 401:
                print("Hibás jelszó!")
                del conf["password"]
                save_config(conf)

            else:
                print("hiba:\n\n" + resp.text +
                      "\n\nha többször megtörtén szólj nekem!")


def main_download(conf):
    while True:
        last = conf.get("last_downloaded")
        last_text = ""
        if last:
            last_text = f"[{last}]"
        fn = input(
            f"Melyik világot szeretnéd letölteni/frissíteni (.db fájl neve; pl. 'Közös 4') [default]\n{last_text} > "
        )
        if fn == "" and last:
            fn = last

        password = conf.get("password")
        if not password:
            password = input(
                "Kérlek add meg a jelszót (amit elküldtem discordra): ")
            conf.update({"password": password})
            save_config(conf)

        try:
            resp = requests.get(
                f"https://sm-upload.pintermor9.repl.co/download?world={fn.replace('.db', '')}&password={password}"
            )
        except requests.exceptions.SSLError:
            print("requests.exceptions.SSLError: Hibás jelszó! probáld ujra")
            del conf["password"]
            save_config(conf)
        else:
            if resp.status_code == 200:
                print("Letöltés sikeres!")
                with open(f"{conf['savedir']}\\{fn.replace('.db', '')}.db", "wb") as f:
                    f.write(resp.content)
                conf.update({"last_downloaded": fn})
                save_config(conf)
                break
            else:
                print("Hiba történt a letöltés közben!")
                if resp.status_code == 401:
                    print("Hibás jelszó!")
                    del conf["password"]
                    save_config(conf)

                else:
                    print("hiba:\n\n" + resp.text +
                          "\n\nha többször megtörtén szólj nekem!")


def main():
    if not os.path.exists(f"{APPDATA}\\pintermor9\\sm-upload.json"):
        print("1. indítás érzékelve, konfiguráció generálása")
        conf = generate_config()
        save_config(conf)
    else:
        conf = load_config()

    while True:
        inp = input("""
Nyomd meg az 1-es gombot egy világ feltöltéséhez, 
             2-es gombot egy világ frissítéséhez, 
             q-t a kilépéshez.""".strip())
        if inp == "1":
            main_upload(conf)
        elif inp == "2":
            main_download(conf)
        elif inp == "q":
            break


if __name__ == "__main__":
    check_for_updates()
    main()
