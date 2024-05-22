from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import socket
import contextlib
from http.server import test as http_server

import threading, asyncio

import sys
sys.path.append("..")
from server import main as rwss_main



def run_http_server():
    handler_class = SimpleHTTPRequestHandler
    # ensure dual-stack is not disabled; ref #38907
    class DualStackServer(ThreadingHTTPServer):

        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(request, client_address, self,
                                        directory=".")

    http_server(
        HandlerClass=handler_class,
        ServerClass=DualStackServer,
    )

if __name__ == "__main__":
    http_thr = threading.Thread(target=run_http_server)
    http_thr.start()
    
    asyncio.run(rwss_main())