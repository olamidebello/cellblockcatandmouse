import unittest,time
import test_game
import server as s
from policy import facility
class PolicyTests(unittest.TestCase):
 setUp=test_game.GameTests.setUp
 tearDown=test_game.GameTests.tearDown
 def test_private_review_requires_server_grounds(self):
  p=self.r['players']['o'];p.update(x=2,y=3)
  with self.assertRaises(ValueError):s.action(self.r,p,'private')
  self.assertEqual(self.r['audit'][-1]['outcome'],'denied')
 def test_concealed_review_and_freeze(self):
  q=self.r['players']['i'];p=self.r['players']['o'];q.update(bag=2,concealment='underwear');p.update(x=2,y=3)
  s.action(self.r,p,'interact');self.assertFalse(q['caught']);p['cool']=0
  s.action(self.r,p,'scan');s.action(self.r,p,'private');self.assertTrue(q['review']);pos=q['x'],q['y'];s.action(self.r,q,'right');self.assertEqual((q['x'],q['y']),pos)
  q['review']['until']=0;s.check(self.r);self.assertTrue(q['caught']);self.assertEqual(self.r['seized'],2);self.assertTrue(any(x['kind']=='evidence' for x in self.r['audit']))
 def test_expired_signal_denied(self):
  p=self.r['players']['o'];p.update(x=2,y=3,signals={'i':time.time()-1})
  with self.assertRaises(ValueError):s.action(self.r,p,'private')
 def test_reports_available_while_detained(self):
  q=self.r['players']['i'];q['caught']=True;s.action(self.r,q,'report');self.assertEqual(q['score'],0);self.assertEqual(self.r['audit'][-1]['kind'],'dignity_concern')
 def test_surrender_not_detention(self):
  q=self.r['players']['i'];q['bag']=2;s.action(self.r,q,'surrender');self.assertFalse(q['caught']);self.assertEqual(self.r['seized'],2)
 def test_invasive_action_blocked(self):
  with self.assertRaises(ValueError):s.action(self.r,self.r['players']['o'],'invasive_search')
 def test_facility_validation(self):
  self.assertEqual(facility({'id':'harbor'})['city'],'Harbor Point');self.assertEqual(facility(dict(name='Custom Prison',country='Nigeria'))['name'],'Custom Prison')
  with self.assertRaises(ValueError):facility(dict(name='x'*81,country='NG'))
 def test_sprint_uses_stamina_and_respects_walls(self):
  p=self.r['players']['i'];p.update(x=1,y=3,last=time.time()-.10,stamina=100,stamina_at=time.time());s.action(self.r,p,'sprint-right');self.assertEqual(p['x'],2);self.assertLess(p['stamina'],83)
  s.action(self.r,p,'sprint-right');self.assertEqual(p['x'],2)
  p.update(x=1,y=1,last=0);before=p['stamina'];s.action(self.r,p,'sprint-up');self.assertEqual(p['y'],1);self.assertGreaterEqual(p['stamina'],before)
 def test_invalid_sprint_action_rejected(self):
  with self.assertRaises(ValueError):s.action(self.r,self.r['players']['i'],'sprint-private')
