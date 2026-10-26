"""Fictional game policy; not an operational prison search procedure."""
import time
POLICY={
 'name':'Dignity-first fictional facility',
 'version':1,
 'summary':'Fully clothed avatars. Routine searches use qualified NPC staff. Enhanced reviews require recorded grounds, supervisor approval, privacy, and a qualified search team. No invasive examinations or identity-based targeting.',
 'sources':['https://www.ecfr.gov/current/title-28/chapter-I/part-115/subpart-A/subject-group-ECFR4b237dabeebeb07/section-115.15'],
 'note':'PREA-informed game rules are deliberately stricter and simplified. Not a PREA certification or a reproduction of any prison policy.'
}
def near(a,b):return abs(a['x']-b['x'])+abs(a['y']-b['y'])<=1
def record(r,actor,target,kind,outcome,reason=''):
 event=dict(time=time.time(),actor=actor['id'],target=target['id'] if target else None,kind=kind,outcome=outcome,reason=reason)
 r.setdefault('audit',[]).append(event);return event
def nearest(r,p):
 candidates=[q for q in r['players'].values() if q['role']=='inmate' and not q['caught'] and not q.get('review') and near(p,q)]
 return min(candidates,key=lambda q:(abs(p['x']-q['x'])+abs(p['y']-q['y']),q['id'])) if candidates else None

FACILITIES=[
 dict(id='stonehaven',name='Stonehaven Correctional',address='100 Lantern Road',city='Stonehaven',region='Fictional District',country='Game World'),
 dict(id='harbor',name='Harbor Point Facility',address='42 Beacon Avenue',city='Harbor Point',region='Coastal District',country='Game World'),
 dict(id='mesa',name='Red Mesa Cellblock',address='7 Horizon Way',city='Red Mesa',region='Desert District',country='Game World')
]
def facility(data):
 if data is None:return dict(FACILITIES[0])
 if not isinstance(data,dict):raise ValueError('Invalid facility details.')
 preset=next((x for x in FACILITIES if x['id']==data.get('id')),None)
 if preset:return dict(preset)
 result={'id':'custom'}
 for key,limit in [('name',80),('address',140),('city',60),('region',60),('country',60)]:
  value=data.get(key,'')
  if not isinstance(value,str) or len(value.strip())>limit or any(ord(c)<32 for c in value):raise ValueError('Invalid facility '+key)
  result[key]=value.strip()
 if not result['name'] or not result['country']:raise ValueError('Facility name and country are required.')
 return result
