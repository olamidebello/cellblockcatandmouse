import unittest,tempfile,sys,time,threading,json,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server as s
class GameTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();s.DB=self.tmp.name+'/db';s.init();s.rooms.clear();self.r=dict(code='ABC123',host='i',players={'i':s.player('i','I','inmate',True),'o':s.player('o','O','officer',True)},phase='lobby',events=[],updated=time.time());s.start(self.r)
 def tearDown(self):self.tmp.cleanup()
 def test_walls_and_pacing(self):
  p=self.r['players']['i'];p.update(x=1,y=1);s.action(self.r,p,'up');self.assertEqual(p['y'],1);p['last']=0;s.action(self.r,p,'right');s.action(self.r,p,'right');self.assertEqual(p['x'],2)
 def test_delivery_and_capacity(self):
  p=self.r['players']['i'];p.update(x=2,y=1,bag=3);s.action(self.r,p,'interact');self.assertEqual(p['bag'],3);p.update(x=19,y=11,cool=0);s.action(self.r,p,'interact');self.assertEqual(self.r['delivered'],3)
 def test_search(self):
  p=self.r['players']['o'];q=self.r['players']['i'];q['bag']=2;s.action(self.r,p,'interact');self.assertFalse(q['caught']);p.update(x=2,y=3,cool=0);s.action(self.r,p,'interact');self.assertTrue(q['caught']);self.assertEqual(self.r['winner'],'officer')
 def test_empty_search(self):
  p=self.r['players']['o'];p.update(x=2,y=3,score=30);s.action(self.r,p,'interact');self.assertFalse(self.r['players']['i']['caught']);self.assertEqual(p['score'],20)
 def test_outcomes(self):
  self.r['delivered']=6;s.check(self.r);self.assertEqual(self.r['winner'],'inmate');s.start(self.r);self.r['ends']=0;s.check(self.r);self.assertEqual(self.r['winner'],'officer')
 def test_accounts_and_privacy(self):
  h=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler);threading.Thread(target=h.serve_forever,daemon=True).start()
  def req(path,data=None,t=''):
   q=urllib.request.Request('http://127.0.0.1:'+str(h.server_port)+'/api/'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+t});return json.load(urllib.request.urlopen(q))
  try:
   t=req('register',dict(name='Tester',password='long-test-password'))['token'];self.assertIn('token',req('login',dict(name='Tester',password='long-test-password')));req('create',dict(role='officer'),t);req('bots',{},t);req('start',{},t);st=req('state',t=t);self.assertNotIn('items',st['room']['spots'][0]);self.assertNotIn('bag',next(p for p in st['room']['players'].values() if p['bot']));req('logout',{},t)
   with self.assertRaises(urllib.error.HTTPError):req('state',t=t)
  finally:h.shutdown();h.server_close()
