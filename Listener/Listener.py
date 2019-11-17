import socketserver
import threading
import time
import sqlite3
import datetime

global conn
event = threading.Event()


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        if event.is_set():
            self.delete_sql()
            event.clear()
        self.insert_sql(self.client_address[0], self.client_address[1])
        self.request.sendall(bytes(self.select_sql(), "utf-8"))

    def insert_sql(self, host, port):
        global conn

        sql = """INSERT INTO cons VALUES (?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(sql, [(host), (port), (datetime.datetime.now())])
        conn.commit()

    def select_sql(self):
        global conn

        sql = "SELECT * FROM cons"

        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        requests = ""
        for str in data:
            requests += "{0}:{1}   {2}\n".format(str[0], str[1], str[2])
        return requests

    def delete_sql(self):
        global conn

        cur = conn.cursor()
        cur.execute("DELETE FROM cons")


class Listener:

    def __init__(self, host, port):

        global conn

        self.server = socketserver.TCPServer((host, port), MyTCPHandler)

        self.server.start_time = time.time()

        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.clear_memory, daemon=True).start()

    def start_server(self):
        global conn

        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE cons (host text, port text, date text)""")
        self.server.serve_forever()

    def clear_memory(self):

        timeout = 10

        while True:
            if time.time() - self.server.start_time >= timeout:
                self.server.start_time += timeout
                event.set()


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 3000

    server = Listener(HOST, PORT)
    input()