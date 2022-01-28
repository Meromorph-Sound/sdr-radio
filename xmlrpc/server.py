#!/usr/bin/python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

class RequestHandler(SimpleXMLRPCRequestHandler):

    def handle_request(request_text=None):
        if request_text is not None:
            print(str(request_text))
        super().handle_request(request_text)

with SimpleXMLRPCServer(('localhost',8000),requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    class SampleFuncs:
        def string(self,x):
            return f'My String value is {str(x)}'

    server.register_instance(SampleFuncs())

    server.serve_forever()
    
    
