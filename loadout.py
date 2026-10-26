"""Abstract fictional inventory choices, not real concealment guidance."""
ITEMS=[{'id':i,'name':n} for i,n in [('phone','Unauthorized phone token'),('radio','Unauthorized radio token'),('cards','Unapproved card-deck token'),('snack','Restricted snack token'),('currency','Fictional currency token'),('data_chip','Restricted data-chip token')]]
LOCATIONS=[{'id':i,'name':n,'search':s} for i,n,s in [('pockets','Pockets (abstract)','routine'),('carry_bag','Carried bag (abstract)','routine'),('uniform','Uniform slot (abstract)','private'),('underwear','Underwear slot (off-screen only)','private')]]
RESOURCES=[
 {'id':'collect','name':'Collect / deliver','roles':['inmate'],'action':'interact','description':'Collect nearby tokens or deliver at the yard.'},
 {'id':'conceal','name':'Change concealment','roles':['inmate'],'action':'conceal','description':'Cycle abstract inventory slots; no concealment instructions.'},
 {'id':'surrender','name':'Voluntary surrender','roles':['inmate'],'action':'surrender','description':'Surrender carried tokens without detention.'},
 {'id':'search','name':'Routine search kit','roles':['officer'],'action':'interact','description':'Search adjacent players and stashes using NPC staff.'},
 {'id':'scanner','name':'Fictional token scanner','roles':['officer'],'action':'scan','description':'Scan an adjacent player; 8-second recharge. Signals last 20 seconds.'},
 {'id':'review','name':'Supervisor review request','roles':['officer'],'action':'private','description':'Request an off-screen private review using a current scanner signal.'},
 {'id':'map','name':'Mission map','roles':['inmate','officer'],'action':'map','description':'Show the cellblock route, position, and yard marker.'},
 {'id':'sprint','name':'Sprint control','roles':['inmate','officer'],'action':'sprint','description':'Toggle sprint on your controls. Fast movement consumes stamina.'},
 {'id':'report','name':'Policy concern recorder','roles':['inmate','officer'],'action':'report','description':'Record a concern without a score penalty; not a real-world complaint.'}
]
def catalog():return dict(items=ITEMS,locations=LOCATIONS,resources=RESOURCES)
def apply(p,data,phase):
 if not isinstance(data,dict):raise ValueError('Invalid selection.')
 if p.get('caught') or p.get('review'):raise ValueError('Selection unavailable while detained or under review.')
 item=data.get('item_type',p.get('item_type','phone'));target=data.get('target_type',p.get('target_type','any'));location=data.get('location',p.get('concealment','pockets'));resource=data.get('resource',p.get('resource','collect' if p['role']=='inmate' else 'search'))
 if item not in {x['id'] for x in ITEMS} or target not in {'any'}|{x['id'] for x in ITEMS} or location not in {x['id'] for x in LOCATIONS}:raise ValueError('Unknown item, location, or search target.')
 selected=next((x for x in RESOURCES if x['id']==resource and p['role'] in x['roles']),None)
 if not selected:raise ValueError('Resource unavailable for your role.')
 if p['role']=='inmate' and p.get('bag',0) and item!=p.get('item_type','phone'):raise ValueError('Deliver or surrender your current inventory before changing its type.')
 if p['role']=='inmate' and phase=='playing' and location!=p['concealment']:
  import time
  if time.time()<p['cool']:raise ValueError('Wait for your concealment cooldown.')
  p['cool']=time.time()+2
 if p['role']=='inmate':p['item_type']=item;p['concealment']=location
 else:p['target_type']=target
 p['resource']=resource
 return selected
def selected_resource(p):
 resource=next((x for x in RESOURCES if x['id']==p.get('resource') and p['role'] in x['roles']),None)
 if not resource:raise ValueError('Select an available resource first.')
 return resource
