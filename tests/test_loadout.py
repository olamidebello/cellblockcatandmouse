import unittest,time,json
import test_game
import server as s
from loadout import apply,selected_resource,catalog
class LoadoutTests(unittest.TestCase):
 setUp=test_game.GameTests.setUp
 tearDown=test_game.GameTests.tearDown
 def test_inmate_selection_and_slot_search(self):
  p=self.r['players']['i'];apply(p,dict(item_type='radio',location='uniform',resource='collect'),'lobby');self.assertEqual(p['item_type'],'radio');p['bag']=1;o=self.r['players']['o'];o.update(x=2,y=3);s.action(self.r,o,'interact');self.assertFalse(p['caught'])
 def test_inventory_cannot_be_retyped(self):
  p=self.r['players']['i'];p['bag']=1
  with self.assertRaises(ValueError):apply(p,dict(item_type='radio'),'playing')
 def test_resource_role_validation(self):
  with self.assertRaises(ValueError):apply(self.r['players']['i'],dict(resource='scanner'),'lobby')
  with self.assertRaises(ValueError):apply(self.r['players']['o'],dict(target_type='not-real'),'lobby')
  self.assertTrue(catalog()['resources'])
 def test_focus_bonus(self):
  q=self.r['players']['i'];q.update(item_type='radio',bag=2);p=self.r['players']['o'];apply(p,dict(target_type='radio',resource='search'),'playing');p.update(x=2,y=3);s.action(self.r,p,'interact');self.assertEqual(p['score'],250);self.assertTrue(q['caught'])
 def test_round_preserves_selections(self):
  p=self.r['players']['i'];apply(p,dict(item_type='cards',location='carry_bag',resource='map'),'lobby');s.start(self.r);self.assertEqual(p['concealment'],'carry_bag');self.assertEqual(p['item_type'],'cards');self.assertEqual(selected_resource(p)['action'],'map')
