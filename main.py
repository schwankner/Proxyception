import os
import socket
import threading

# Konfiguration über Umgebungsvariablen mit Standardwerten
LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", 8888))

SQUID_HOST = os.environ.get("SQUID_HOST", "192.168.1.244")
SQUID_PORT = int(os.environ.get("SQUID_PORT", 8080))

TARGET_HOST = os.environ.get("TARGET_HOST", "10.0.00.100")
TARGET_PORT = int(os.environ.get("TARGET_PORT", 3000))


class ProxyHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        try:
            # Verbindung zum Squid-Proxy aufbauen
            squid_socket = socket.create_connection((SQUID_HOST, SQUID_PORT))
            print(f"Connected to Squid at {SQUID_HOST}:{SQUID_PORT}")

            # CONNECT-Request an Squid senden, um einen Tunnel zum Backend aufzubauen
            connect_request = (
                f"CONNECT {TARGET_HOST}:{TARGET_PORT} HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}:{TARGET_PORT}\r\n"
                "Proxy-Connection: Keep-Alive\r\n"
                #"User-Agent: curl/8.7.1\r\n"
                "\r\n"
            )
            squid_socket.sendall(connect_request.encode())
            print("CONNECT request sent to Squid:")
            print(connect_request)

            # Antwort von Squid lesen
            response = self._recv_response(squid_socket)
            print("Received response from Squid:")
            print(response.decode(errors='replace'))
            if b"200 Connection established" not in response and b"200 Connection Established" not in response:
                print("Error: Squid did not establish the connection")
                self.client_socket.close()
                squid_socket.close()
                return

            # Tunnel ist aufgebaut, Traffic weiterleiten
            threading.Thread(target=self._forward, args=(self.client_socket, squid_socket), daemon=True).start()
            self._forward(squid_socket, self.client_socket)
        except Exception as e:
            print(f"ProxyHandler error: {e}")
        finally:
            self.client_socket.close()

    def _forward(self, source, destination):
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.sendall(data)
        except Exception as e:
            pass
        finally:
            source.close()
            destination.close()

    def _recv_response(self, sock):
        sock.settimeout(5)
        response = b""
        try:
            # Empfange Daten, bis Headerende gefunden wurde
            while b"\r\n\r\n" not in response:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
        except socket.timeout:
            pass
        finally:
            sock.settimeout(None)
        return response

def start_proxy_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_HOST, LISTEN_PORT))
    server_socket.listen(5)
    print(f"Proxy server listening on {LISTEN_HOST}:{LISTEN_PORT}")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            handler = ProxyHandler(client_socket)
            handler.start()
    except KeyboardInterrupt:
        print("Shutting down proxy server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_proxy_server()
