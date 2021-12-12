from time import strftime

LOG_FILE = "log"


def log(tag, msg):
    with open(LOG_FILE, "a") as f:
        f.write(
            "{tag:22s}: [{time:s}] {msg:s}\n".format(
                tag=tag, time=strftime("%d.%m.%y %H:%M:%S"), msg=_clean(msg)
            )
        )


def _clean(s):
    return s.replace("\n", "\\n").replace("\t", "\\t")
