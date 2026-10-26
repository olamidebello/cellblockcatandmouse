#!/usr/bin/env python3
"""Verify certificate, TLS SNI, hostname and Cellblock application identity."""
import argparse,json,socket,ssl,http.client

def verify(domain,address,port=443):
 context=ssl.create_default_context()
 with socket.create_connection((address,port),timeout=15) as tcp:
  with context.wrap_socket(tcp,server_hostname=domain) as tls:
   tls.sendall(('GET /health HTTP/1.1\r\nHost: '+domain+'\r\nConnection: close\r\n\r\n').encode())
   response=http.client.HTTPResponse(tls);response.begin();data=json.loads(response.read(8192))
   if response.status!=200 or data.get('app')!='cellblockcatandmouse' or data.get('ok') is not True:raise ValueError('Wrong backend at '+address+': '+str(data))
 return {'address':address,'app':data['app'],'verified':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--domain',required=True);p.add_argument('--address',action='append',default=[]);a=p.parse_args()
 print(json.dumps([verify(a.domain,address) for address in (a.address or [a.domain])]))
