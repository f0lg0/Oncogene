from mega import Mega

mega = Mega()
m = mega.login("EMAIL", "PASSWORD")

ufile = m.upload("./logs/readable.txt")

