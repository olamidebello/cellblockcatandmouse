import unittest,tempfile,threading,urllib.request,urllib.error,json
import server as s
class LegalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=s.DB;s.DB=self.tmp.name+'/test.db';s.init();s.rates.clear();self.h=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler);threading.Thread(target=self.h.serve_forever,daemon=True).start();self.base='http://127.0.0.1:'+str(self.h.server_port)
 def tearDown(self):self.h.shutdown();self.h.server_close();s.DB=self.old;self.tmp.cleanup()
 def test_public_pages_and_footer(self):
  for p in ['/terms','/privacy','/copyright','/contact']:
   with urllib.request.urlopen(self.base+p) as r:self.assertIn('Olamide Olatayo Bello',r.read().decode())
  with urllib.request.urlopen(self.base+'/') as r:self.assertIn('href="/privacy"',r.read().decode())
 def test_request_persistence_and_validation(self):
  def send(data):
   q=urllib.request.Request(self.base+'/api/legal-request',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'});return urllib.request.urlopen(q)
  with send(dict(kind='privacy',email='reply@example.com',message='Please review my privacy request.')) as r:request_id=json.load(r)['id'];self.assertEqual(r.status,201)
  with s.db() as c:row=c.execute('SELECT * FROM legal_requests WHERE id=?',(request_id,)).fetchone();self.assertEqual(row['kind'],'privacy');self.assertEqual(row['status'],'open')
  with self.assertRaises(urllib.error.HTTPError):send(dict(kind='invalid',message='not valid'))
  with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(self.base+'/api/legal-requests')
