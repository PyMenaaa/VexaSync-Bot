for i in open("wl.txt","r",encoding="utf8").read().splitlines():
    name = i.split(":")[0]

    if (len(name) > 7) and (len(name) < 20):
        if not (" " in name) and not ("." in name) and not ("_" in name):
            open("nl.txt","a").write(name + "\n")

