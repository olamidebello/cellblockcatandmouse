import unittest,importlib.util,tempfile,subprocess,pathlib,ssl,threading,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).resolve().parents[1]/'scripts'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
listeners=module('listeners','nginx-listeners.py');cert=module('cert','check-certificate.py');verify=module('verify','verify-domain.py')
class RoutingTests(unittest.TestCase):
 def test_listener_precedence_group_detection(self):
  config='listen 80; listen 443 ssl; listen 154.16.170.86:80; listen 154.16.170.86:443 ssl; # listen 1.2.3.4:443;'
  self.assertEqual(listeners.discover(config,'154.16.170.86'),dict(http_extra=['154.16.170.86:80'],https_extra=['154.16.170.86:443']))
  self.assertEqual(listeners.discover(config,'1.2.3.4')['https_extra'],[])
 def test_certificate_and_sni_identity(self):
  with tempfile.TemporaryDirectory() as t:
   c=pathlib.Path(t)/'cert';k=pathlib.Path(t)/'key'
   subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(k),'-out',str(c),'-days','2','-subj','/CN=cellblock.test','-addext','subjectAltName=DNS:cellblock.test'],capture_output=True,check=True)
   self.assertTrue(cert.check(str(c),'cellblock.test'))
   with self.assertRaises(ValueError):cert.check(str(c),'kakakin.test')
   class Handler(BaseHTTPRequestHandler):
    app='cellblockcatandmouse'
    def log_message(self,*args):pass
    def do_GET(self):
     self.send_response(200);self.end_headers();self.wfile.write(json.dumps(dict(ok=True,app=self.app)).encode())
   h=ThreadingHTTPServer(('127.0.0.1',0),Handler);ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(c,k);h.socket=ctx.wrap_socket(h.socket,server_side=True);threading.Thread(target=h.serve_forever,daemon=True).start()
   from unittest.mock import patch
   trust=ssl.create_default_context(cafile=str(c))
   try:
    with patch.object(verify.ssl,'create_default_context',return_value=trust):
     self.assertTrue(verify.verify('cellblock.test','127.0.0.1',h.server_port)['verified']);Handler.app='kakakin'
     with self.assertRaises(ValueError):verify.verify('cellblock.test','127.0.0.1',h.server_port)
     with self.assertRaises(ssl.SSLCertVerificationError):verify.verify('wrong.test','127.0.0.1',h.server_port)
   finally:h.shutdown();h.server_close()
