x = open("x.txt","r").read().splitlines()

finall = ""
for i in x:
    try:
        bot_id, token, username,email, email_code = i.split("|")
        finall = finall + token + "\n"
    except:
        pass
open("x.txt","w").write(finall)