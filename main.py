import mimetypes
import pathlib
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from jinja2 import Template, Environment, FileSystemLoader


# 1. Отримуємо шлях до поточної папки скрипта
APP_DIR = pathlib.Path(__file__).resolve().parent
PUBLIC_DIR = APP_DIR / "statics"
STORAGE_DIR = PUBLIC_DIR / "storage"


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(STORAGE_DIR / "data.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)

        json_data[timestamp] = data_dict

        with open(STORAGE_DIR / "data.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=2)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")

        elif pr_url.path == "/message":
            self.send_html_file("message.html")

        elif pr_url.path == "/read":
            output = self.__render_template("read.html", STORAGE_DIR / "data.json")
            with open("temp.html", "w", encoding="utf-8") as f:
                f.write(output)
            self.send_html_file("temp.html")
            # Видалення файлу
            try:
                os.remove('temp.html')
                print(f"Файл 'temp.html' успішно видалено.")
            except OSError as e:
                print(f"Помилка при видаленні файлу 'temp.html': {e}")

        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def __render_template(self, filename, context):
        try:
            with open(context, "r", encoding="utf-8") as message_file:
                messages = json.load(message_file)
        except FileNotFoundError:
            messages = {}
            print(f"Помилка: Файл не знайдено: {context}")
            print("Повертаємо порожній словник повідомлень.")
            print(messages)

        env = Environment(loader=FileSystemLoader(PUBLIC_DIR))
        template = env.get_template(filename)
        return template.render(messages=messages)
    
    # def __send_mime_type_header(self):
    #     mt = mimetypes.guess_type(self.path)
    #     if mt:
    #         self.send_header("Content-type", mt[0])
    #         # print(f"MIME type: {mt}")
    #     else:
    #         self.send_header("Content-type", "text/plain")

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        # self.__send_mime_type_header()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            with open(filename, "rb") as fd:
                self.wfile.write(fd.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("error.html", "rb") as error_file:
                self.wfile.write(error_file.read())

    def send_static(self):
        self.send_response(200)
        self.end_headers()
        # self.__send_mime_type_header()
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())
            print(f"Відправлено файл: .{self.path}")
            print(f"MIME type: {mt}")


def run(server_class=HTTPServer, handler_class=HttpHandler):
    # Змінюємо робочу директорію ДО запуску сервера
    try:
        os.chdir(PUBLIC_DIR)
        print(f"Сервер роздає файли з: {PUBLIC_DIR}")
    except FileNotFoundError:
        print(f"Помилка: Директорія не знайдена: {PUBLIC_DIR}")
        return

    server_address = ("", 3000)
    http = server_class(server_address, handler_class)

    print("Сервер запущено на http://localhost:3000")
    print(f"Роздає файли з: {PUBLIC_DIR}")

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        print("Сервер зупинено.")


if __name__ == "__main__":
    run()
