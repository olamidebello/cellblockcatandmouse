import json, os, time, sqlite3, secrets, hashlib, threading, math, random
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from policy import POLICY, near, record, nearest, FACILITIES, facility
ROOT=Path(__file__).parent
DB=os.environ.get('GAME_DB',str(ROOT/'data/game.db'))
Path(DB).parent.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock(); rooms={}; rates={}
MAP=['#####################','#...#.....#.....#...#','#...#.....#.....#...#','#...................#','###.###.#####.###.###','#.....#.......#.....#','#.....#.......#.....#','#...................#','#.###.###.###.###.#.#','#...................#','#.....#.......#.....#','#.....#.......#.....#','#####################']
SPOTS=[(2,1),(7,1),(13,1),(18,1),(3,5),(10,5),(17,5),(3,10),(10,10),(17,10)]
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with db() as c:c.executescript('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT UNIQUE,password TEXT,salt TEXT,wins INTEGER DEFAULT 0,points INTEGER DEFAULT 0); CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user TEXT,expires REAL);')
def walk(x,y):return 0<=y<len(MAP) and 0<=x<len(MAP[0]) and MAP[y][x]!='#'
def log(r,s):r['events']=(r['events']+[s])[-12:]
def player(uid,name,role,bot=False):return dict(id=uid,name=name,role=role,x=1 if role=='inmate' else 19,y=3,bag=0,score=0,caught=False,ready=bot,bot=bot,last=0,cool=0,stamina=100,concealment="pockets",review=None,signals={},scan_cool=0,report_cool=0)
def finish(r,winner):
 if r['phase']!='playing':return
 r['phase']='finished';r['winner']=winner;log(r,winner.title()+' team wins the round!')
 with db() as c:
  for p in r['players'].values():
   if not p['bot']:c.execute('UPDATE users SET points=points+?,wins=wins+? WHERE id=?',(p['score'],int(p['role']==winner),p['id']))
def check(r):
 for q in r['players'].values():
  review=q.get('review')
  if review and time.time()>=review['until']:
   officer=r['players'].get(review['officer'])
   if officer and r['phase']=='playing':
    if q['bag']:seize(r,officer,q,'private review')
    else:log(r,q['name']+' completed a private review; no tokens found.')
    record(r,officer,q,'private_review','completed','Approved NPC team; private off-screen review; evidence recorded')
   q['review']=None
 ins=[p for p in r['players'].values() if p['role']=='inmate']
 if r['delivered']>=r['target']:finish(r,'inmate')
 elif ins and all(p['caught'] for p in ins):finish(r,'officer')
 elif time.time()>=r['ends']:finish(r,'officer')
 elif sum(x['items'] for x in r['spots'])+sum(x['bag'] for x in r['players'].values())+r['delivered']<r['target']:finish(r,'officer')
def seize(r,p,q,method):
 amount=q['bag'];q['caught']=True;p['score']+=amount*75+50;r['seized']+=amount;q['bag']=0
 record(r,p,q,'evidence','sealed',str(amount)+' fictional tokens; '+method)
 log(r,p['name']+' secured tokens from '+q['name']+' after '+method+'.')
def action(r,p,a):
 now=time.time()
 if a=='report':
  if now>=p['report_cool']:
   p['report_cool']=now+10;record(r,p,None,'dignity_concern','recorded','No retaliation; no gameplay penalty');log(r,'A policy concern was recorded for this round. No player penalty.')
  return
 if r['phase']!='playing' or p['caught'] or p.get('review'):return
 if a not in ['up','down','left','right','interact','conceal','scan','private','surrender','report']:
  record(r,p,None,'blocked_action','denied','Unsupported or invasive action');raise ValueError('That action is not allowed by facility policy.')
 if a in ['up','down','left','right']:
  if now-p['last']<.14:return
  dx,dy={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}[a];x,y=p['x']+dx,p['y']+dy
  if walk(x,y):p['x'],p['y']=x,y
  p['last']=now
 elif a=='conceal' and p['role']=='inmate' and now>=p['cool']:
  p['concealment']='underwear' if p['concealment']=='pockets' else 'pockets';p['cool']=now+2
 elif a=='surrender' and p['role']=='inmate' and p['bag']:
  r['seized']+=p['bag'];p['bag']=0;p['score']+=10;record(r,p,p,'voluntary_surrender','completed');log(r,p['name']+' voluntarily surrendered tokens; no detention.')
 elif a in ['scan','private'] and p['role']=='officer':
  q=nearest(r,p)
  if not q:raise ValueError('Stand next to an active inmate.')
  if a=='scan':
   if now<p['scan_cool']:raise ValueError('Scanner is recharging.')
   p['scan_cool']=now+8
   # Fictional detector reads game tokens, not anatomy or personal characteristics.
   if q['bag']:p['signals'][q['id']]=now+20
   record(r,p,q,'fictional_token_scan','signal' if q['bag'] else 'clear');log(r,p['name']+(' received a token scanner signal.' if q['bag'] else ' completed a clear scan.'))
  else:
   if now<p['cool']:raise ValueError('Wait for your search cooldown.')
   if p['signals'].get(q['id'],0)<now:
    record(r,p,q,'private_review','denied','No current recorded grounds');raise ValueError('Supervisor denied: obtain a current scanner signal first.')
   p['signals'].pop(q['id'],None);q['review']=dict(until=now+4,officer=p['id']);p['cool']=now+4
   record(r,p,q,'private_review','approved','Current token signal; NPC supervisor approved; qualified NPC staff and private room assigned')
   log(r,'Supervisor approved an off-screen private review. Qualified staff handle the search.')
 elif a=='interact' and now>=p['cool']:
  p['cool']=now+1
  if p['role']=='inmate':
   if (p['x'],p['y'])==(19,11) and p['bag']:
    r['delivered']+=p['bag'];p['score']+=p['bag']*100;log(r,p['name']+' delivered '+str(p['bag'])+' tokens.');p['bag']=0
   else:
    for s in r['spots']:
     if abs(s['x']-p['x'])+abs(s['y']-p['y'])<=1 and s['items'] and p['bag']<3:
      s['items']-=1;p['bag']+=1;log(r,p['name']+' found a mystery token.');break
  else:
   found=False
   q=nearest(r,p)
   if q:
    record(r,p,q,'routine_search','completed','Qualified NPC staff; respectful fully clothed abstraction')
    if q['bag'] and q['concealment']=='pockets':
     seize(r,p,q,'routine search');found=True
    else:log(r,q['name']+' completed a routine search; no accessible tokens found.');p['score']=max(0,p['score']-10)
   for s in r['spots']:
    if abs(s['x']-p['x'])+abs(s['y']-p['y'])<=1 and s['items']:
     r['seized']+=s['items'];p['score']+=s['items']*25;s['items']=0;found=True;log(r,p['name']+' confiscated a stash.')
   p['cool']=now+3
   if not found:log(r,p['name']+' completed a search.')
   remaining=sum(s['items'] for s in r['spots'])+sum(q['bag'] for q in r['players'].values())
   if remaining+r['delivered']<r['target']:finish(r,'officer')
 check(r)
def start(r):
 if not any(p['role']=='inmate' for p in r['players'].values()) or not any(p['role']=='officer' for p in r['players'].values()):raise ValueError('Both teams need at least one player. Add bots or invite a friend.')
 for p in r['players'].values():p.update(x=1 if p['role']=='inmate' else 19,y=3,bag=0,caught=False,score=0,last=0,cool=0,concealment="pockets",review=None,signals={},scan_cool=0,report_cool=0)
 r.update(phase='playing',ends=time.time()+180,spots=[dict(x=x,y=y,items=2) for x,y in SPOTS],delivered=0,seized=0,target=6,winner=None,events=[],audit=[],policy=POLICY);log(r,'Round started. Inmates: deliver 6 tokens to the yard. Officers: search and seize.')
def step_toward(r,p,tx,ty):
 # Breadth-first pathfinding respects every wall.
 queue=[(p['x'],p['y'],None)];seen={(p['x'],p['y'])}
 for x,y,first in queue:
  if (x,y)==(tx,ty):
   if first:action(r,p,first)
   return
  for a,dx,dy in [('up',0,-1),('down',0,1),('left',-1,0),('right',1,0)]:
   n=x+dx,y+dy
   if walk(*n) and n not in seen:seen.add(n);queue.append((*n,first or a))
def ticker():
 while True:
  time.sleep(.45)
  with LOCK:
   for code,r in list(rooms.items()):
    if time.time()-r['updated']>7200:del rooms[code];continue
    if r['phase']!='playing':continue
    for p in list(r['players'].values()):
     if not p['bot'] or p['caught']:continue
     if p['role']=='inmate':
      if p['bag']>=2:target=(19,11)
      else:
       spots=[s for s in r['spots'] if s['items']]
       target=(min(spots,key=lambda s:abs(s['x']-p['x'])+abs(s['y']-p['y'])) if spots else {'x':19,'y':11});target=(target['x'],target['y'])
      if (p['x'],p['y'])==target:action(r,p,'interact')
      else:step_toward(r,p,*target)
     else:
      targets=[q for q in r['players'].values() if q['role']=='inmate' and not q['caught']]
      if targets:
       q=min(targets,key=lambda q:abs(q['x']-p['x'])+abs(q['y']-p['y']))
       if abs(q['x']-p['x'])+abs(q['y']-p['y'])<=1:
        if p['signals'].get(q['id'],0)>time.time():action(r,p,'private')
        elif time.time()>=p['scan_cool']:action(r,p,'scan')
        else:action(r,p,'interact')
       else:step_toward(r,p,q['x'],q['y'])
    check(r)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,status,data,ctype='application/json'):
  b=json.dumps(data).encode() if ctype=='application/json' else data
  self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(b)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','same-origin');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def user(self):
  token=self.headers.get('Authorization','').removeprefix('Bearer ')
  with db() as c:u=c.execute('SELECT u.* FROM users u JOIN sessions s ON s.user=u.id WHERE s.token=? AND s.expires>?',(token,time.time())).fetchone()
  if not u:raise PermissionError('Please sign in.')
  return dict(u)
 def do_GET(self):
  try:
   with LOCK:
    path=self.path.split('?')[0]
    if path=='/api/facilities':return self.send(200,FACILITIES)
    if path=='/health':return self.send(200,{'ok':True})
    if path=='/api/leaderboard':
     with db() as c:rows=[dict(x) for x in c.execute('SELECT name,wins,points FROM users ORDER BY points DESC LIMIT 20')]
     return self.send(200,rows)
    if path=='/api/state':
     u=self.user();r=next((r for r in rooms.values() if u['id'] in r['players']),None)
     if not r:return self.send(200,{'room':None,'user':{'id':u['id'],'name':u['name']}})
     state=json.loads(json.dumps(r));me=r['players'][u['id']]
     for q in state['players'].values():
      if q['id']!=u['id']:
       for private_key in ['bag','concealment','signals']:q.pop(private_key,None)
     state['audit']=[e for e in state.get('audit',[]) if e['actor']==u['id'] or e['target']==u['id']][-30:]
     for s in state.get('spots',[]):
      if me['role']=='officer':s.pop('items',None)
     return self.send(200,{'room':state,'user':{'id':u['id'],'name':u['name']},'map':MAP,'now':time.time()})
    if path=='/assets/cover.webp':return self.send(200,(ROOT/'public/assets/cover.webp').read_bytes(),'image/webp')
    if path=='/assets/logo.webp':return self.send(200,(ROOT/'public/assets/logo.webp').read_bytes(),'image/webp')
    files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}
    if path in files:
     f,t=files[path];return self.send(200,(ROOT/'public'/f).read_bytes(),t)
    self.send(404,{'error':'Not found'})
  except PermissionError as e:self.send(401,{'error':str(e)})
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size>4096:raise ValueError('Request too large')
   data=json.loads(self.rfile.read(size));path=self.path
   with LOCK:
    if path in ['/api/register','/api/login']:
     key=(self.client_address[0],int(time.time()/60));rates[key]=rates.get(key,0)+1
     if rates[key]>30:return self.send(429,{'error':'Too many attempts. Try again in a minute.'})
     if len(rates)>2000:rates.clear()
     name=str(data.get('name','')).strip();pw=str(data.get('password',''))
     if not 3<=len(name)<=24 or not 10<=len(pw)<=128:raise ValueError('Use a 3–24 character name and a 10–128 character password.')
     with db() as c:
      u=c.execute('SELECT * FROM users WHERE name=?',(name,)).fetchone()
      if path=='/api/register':
       if u:raise ValueError('That name is already registered.')
       salt=secrets.token_hex(16);uid=secrets.token_hex(16);digest=hashlib.scrypt(pw.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex();c.execute('INSERT INTO users(id,name,password,salt) VALUES(?,?,?,?)',(uid,name,digest,salt))
      else:
       if not u or not secrets.compare_digest(u['password'],hashlib.scrypt(pw.encode(),salt=u['salt'].encode(),n=16384,r=8,p=1).hex()):raise ValueError('Invalid name or password.')
       uid=u['id']
      token=secrets.token_urlsafe(32);c.execute('DELETE FROM sessions WHERE expires<?',(time.time(),));c.execute('INSERT INTO sessions VALUES(?,?,?)',(token,uid,time.time()+86400*7))
     return self.send(200,{'token':token})
    u=self.user();uid=u['id'];r=next((r for r in rooms.values() if uid in r['players']),None)
    if path=='/api/logout':
     with db() as c:c.execute('DELETE FROM sessions WHERE token=?',(self.headers.get('Authorization','').removeprefix('Bearer '),))
    elif path=='/api/leave':
     if r:
      del r['players'][uid]
      humans=[q for q in r['players'].values() if not q['bot']]
      if not humans:del rooms[r['code']]
      else:
       if r['host']==uid:r['host']=humans[0]['id']
       if r['phase']=='playing':finish(r,'officer' if not any(q['role']=='inmate' and not q['caught'] for q in r['players'].values()) else 'inmate')
    elif path in ['/api/create','/api/join']:
     if r:raise ValueError('Leave your current room first.')
     role=data.get('role','inmate')
     if role not in ['inmate','officer']:raise ValueError('Invalid role')
     if path=='/api/create':
      if len(rooms)>=200:raise ValueError('Server full')
      selected_facility=facility(data.get('facility'));code=secrets.token_hex(3).upper();r=dict(facility=selected_facility,code=code,host=uid,phase='lobby',players={},events=[],updated=time.time());rooms[code]=r
     else:
      r=rooms.get(str(data.get('code','')).upper())
      if not r or r['phase']!='lobby':raise ValueError('Room unavailable or already playing.')
     if len(r['players'])>=12:raise ValueError('Room full (12 players).')
     r['players'][uid]=player(uid,u['name'],role)
    elif not r:raise ValueError('Join a room first.')
    elif path=='/api/facility':
     if r['host']!=uid or r['phase']=='playing':raise ValueError('Only the host can change the facility between rounds.')
     r['facility']=facility(data.get('facility'))
    elif path=='/api/role':
     if r['phase']=='playing':raise ValueError('Wait until the round finishes.')
     if data.get('role') not in ['inmate','officer']:raise ValueError('Invalid role')
     r['players'][uid]['role']=data['role']
    elif path=='/api/bots':
     if r['host']!=uid or r['phase']=='playing':raise ValueError('Only the host can add bots between rounds.')
     for role in ['inmate','officer']:
      if not any(p['role']==role for p in r['players'].values()) and len(r['players'])<12:
       bid=secrets.token_hex(8);r['players'][bid]=player(bid,'Bot '+role.title(),role,True)
    elif path=='/api/start':
     if r['host']!=uid or r['phase']=='playing':raise ValueError('Only the host can start a new round.')
     start(r)
    elif path=='/api/action':action(r,r['players'][uid],data.get('action'))
    else:raise ValueError('Unknown action')
    if r:r['updated']=time.time()
    self.send(200,{'ok':True})
  except PermissionError as e:self.send(401,{'error':str(e)})
  except (ValueError,KeyError,TypeError) as e:self.send(400,{'error':str(e)})
  except Exception:self.send(500,{'error':'Server error'})
if __name__=='__main__':
 init();threading.Thread(target=ticker,daemon=True).start();ThreadingHTTPServer((os.environ.get('HOST','127.0.0.1'),int(os.environ.get('PORT','18842'))),Handler).serve_forever()
