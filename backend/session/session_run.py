import asyncio

from backend.deepagent.agent import deep_agent
from backend.session.session_id_create import session_create
from backend.session.session_start import session_start

def session_run(content):
    res = session_start.send_message(session_create.get_or_create("53A9Lnyc"), content)
    return res

if __name__ == "__main__":
    while True:
        qus = input(">")
        res = session_run(qus)
        print(res)

