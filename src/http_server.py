from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        message = "You reached the server !"
        self.wfile.write(bytes(message, "utf8"))


with HTTPServer(("127.0.0.80", 8080), Handler) as server:
    server.serve_forever()
    print("Running http server on port 8080!")
