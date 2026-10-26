#!/usr/bin/env python3
"""Remove this game's exact hostname from other active Nginx declarations."""
import argparse,datetime,hashlib,pathlib,re,subprocess,json
p=argparse.ArgumentParser();p.add_argument('--domain',required=True);p.add_argument('--managed',default='/etc/nginx/sites-available/cellblock');a=p.parse_args()
if not re.fullmatch(r'[a-zA-Z0-9.-]+',a.domain):raise SystemExit('Invalid hostname')
ng=subprocess.run(['nginx','-T'],capture_output=True,text=True)
if ng.returncode:raise SystemExit('Existing Nginx configuration is invalid. Repair nginx -t errors before deployment.\n'+ng.stderr)
paths=re.findall(r'^# configuration file (.+):$',ng.stdout,re.M)
managed=pathlib.Path(a.managed).resolve();changes=[];seen=set();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S%f')
for raw in paths:
 f=pathlib.Path(raw).resolve()
 if f==managed or f in seen or not f.is_file():continue
 seen.add(f);original=f.read_text()
 # Preserve comments and all unrelated names. Match complete server_name directives.
 def replace(m):
  body=m.group(2);clean=re.sub(r'#[^\n]*','',body);names=clean.split()
  if a.domain not in names:return m.group(0)
  # Only alter exact hostname tokens outside comments, retaining formatting.
  lines=[]
  for line in body.splitlines(keepends=True):
   code,sep,comment=line.partition('#');code=re.sub(r'(?<!\S)'+re.escape(a.domain)+r'(?!\S)','',code);lines.append(code+sep+comment)
  result=''.join(lines)
  if not [n for n in names if n!=a.domain]:
   result=' retired-cellblock-'+hashlib.sha256(str(f).encode()).hexdigest()[:12]+'.invalid'
  return m.group(1)+result+';'
 updated=re.sub(r'(^[ \t]*server_name\s+)([^;]+);',replace,original,flags=re.M)
 if updated!=original:changes.append((f,original,updated))
try:
 for f,old,new in changes:
  backup=f.with_name(f.name+'.cellblock-backup-'+stamp);backup.write_text(old);f.write_text(new)
 check=subprocess.run(['nginx','-t'],capture_output=True,text=True)
 if check.returncode:raise RuntimeError(check.stderr)
except Exception:
 for f,old,new in changes:f.write_text(old)
 raise
print(json.dumps({'changed':bool(changes),'files':[str(f) for f,_,_ in changes],'domain':a.domain}))
