#!/usr/bin/env python3
"""Find exact IPv4 listener groups already declared by active Nginx config."""
import argparse,ipaddress,json,re,subprocess

def discover(config,expected):
 ip=ipaddress.IPv4Address(expected);clean=re.sub(r'#[^\n]*','',config);found={80:False,443:False}
 for value in re.findall(r'\blisten\s+([^;]+);',clean):
  endpoint=value.split()[0]
  for port in found:
   if endpoint==str(ip)+':'+str(port) or (port==80 and endpoint==str(ip)):found[port]=True
 return {'http_extra':[str(ip)+':80'] if found[80] else [],'https_extra':[str(ip)+':443'] if found[443] else []}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipv4',required=True);a=p.parse_args();r=subprocess.run(['nginx','-T'],capture_output=True,text=True)
 if r.returncode:raise SystemExit(r.stderr)
 print(json.dumps(discover(r.stdout,a.ipv4)))
