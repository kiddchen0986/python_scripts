#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import socket
import json
import time
import datetime
from hashlib import sha256

class S(BaseHTTPRequestHandler):

    devices = {}
    nodes = {}


    def getJsonRequest(self):
        content_length = int(self.headers['Content-Length'])
        return json.loads(self.rfile.read(content_length).decode('utf-8'))

    def too_old_time(self):
        return datetime.datetime.now() - datetime.timedelta(minutes = 10)

    def getNodeState(self, node):
        if(not node['enabled']):
            return "disabled"
        return node['state'] if node['time'] > self.too_old_time() else "offline"

    def getNodeMeta(self, node):
        return node['meta'] if 'meta' in node else {}

    def do_GET(self):
        self.send_response(200)
        self.send_header(u'Access-Control-Allow-Origin', u'*')
        if(self.path == '/client/version'):
            self.send_header(u'Content-type', u'text/plain')
            self.end_headers()
            with open(u'RaspberryClient.py', 'rb') as file:
                self.wfile.write(sha256(file.read()).hexdigest().encode('utf-8'))
            return

        elif(self.path == '/client'):
            self.send_header(u'Content-type', u'text/plain')
            self.send_header(u'Content-Disposition', u'attachment; filename="Client.py"')
            self.end_headers()
            with open(u'RaspberryClient.py', 'r') as file:
                self.wfile.write(file.read().encode('utf-8'))
            return

        elif(self.path == '/nodes'):
            self.send_header(u'Content-type', u'application/json')
            self.end_headers()

            response = []
            for node, node_key in self.nodes.items():
                node_config = node_key.split('@')
                device_node = self.devices[node_key][node]
                response.append({
                    'hardware':node_config[0],
                    'sensor':node_config[1],
                    'ip':node,
                    'state': self.getNodeState(device_node),
                    'meta': self.getNodeMeta(device_node)
                })
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        self.send_header(u'Content-type', u'text/html')
        self.end_headers()
        server_url = u'http://' + self.server.server_name + u':' + str(self.server.server_port)
        with open(u'dashboard.html', 'r') as file:
            self.wfile.write(file.read().replace(u'##SERVERURL##', server_url).encode('utf-8'))


    def do_PUT(self):
        put_json = self.getJsonRequest()
        key = put_json['hardware'] + '@' + put_json['sensor']
        if( not key in self.devices ):
            self.devices[key] = {}
        ip = self.client_address[0]
        self.nodes[ip] = key
        if( not ip in self.devices[key]):
            self.devices[key][ip] = {'state':'ready','enabled':True}
        self.devices[key][ip]['time'] = datetime.datetime.now()
        self.send_response(202)
        self.send_header(u'Access-Control-Allow-Origin', u'*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header(u'Allow', u'OPTIONS, GET, HEAD, POST, PUT, DELETE')
        self.send_header(u'Access-Control-Allow-Origin', u'*')
        self.send_header(u'Access-Control-Allow-Methods', u'OPTIONS, GET, HEAD, POST, PUT, DELETE')
        self.send_header(u'Access-Control-Allow-Headers', u'origin, x-requested-with, content-type')
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header(u'Access-Control-Allow-Origin', u'*')
        self.send_header(u'Content-type', u'application/json')
        self.end_headers()

    def do_POST(self):
        post_json = self.getJsonRequest()
        key = post_json['hardware'] + '@' + post_json['sensor']
        if (key in self.devices):
            response = {}
            too_old = self.too_old_time()
            anyfound = False
            for ip, node in self.devices[key].items():
                if (not node['enabled'] or node['time'] < too_old or self.nodes[ip] != key):
                    continue
                anyfound = True
                if (node['state'] == 'ready'):
                    node['state'] = 'working'
                    response['ip'] = ip
                    if( 'meta' in post_json ):
                        node['meta'] = post_json['meta']
                    break

            if( 'ip' in response):
                self.send_response(200)
                self.send_header(u'Access-Control-Allow-Origin', u'*')
                self.send_header(u'Content-type', u'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(409 if anyfound else 404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        key = self.path[1:]
        delete_mode = None
        if('?' in key):
            keys = key.split('?')
            key = keys[0]
            delete_mode = keys[1]
        if(key in self.nodes):
            if (delete_mode == 'remove'):
                self.devices.pop(self.nodes.pop(key, None), None)
            elif (delete_mode == 'disable'):
                self.devices[self.nodes[key]][key]['enabled'] = False
            elif (delete_mode == 'enable'):
                self.devices[self.nodes[key]][key]['enabled'] = True
            else:
                self.devices[self.nodes[key]][key]['state'] = 'ready'
            self.send_response(200)
            self.send_header(u'Access-Control-Allow-Origin', u'*')
        else:
            self.send_response(405)
        self.end_headers()

def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def run(server_class=HTTPServer, handler_class=S, port=8080):
    ip = get_ip_address()
    server_address = (ip, port)
    httpd = server_class(server_address, handler_class)
    print (u'Starting httpd...')
    print (u'http://' + server_address[0] + u':' + str(server_address[1]))
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
