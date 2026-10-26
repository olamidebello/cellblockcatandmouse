#!/usr/bin/env python3
"""OpenSSL x509 -checkhost prints a mismatch but can still exit zero."""
import argparse,subprocess

def check(path,domain,seconds=86400):
 host=subprocess.run(['openssl','x509','-in',path,'-noout','-checkhost',domain],capture_output=True,text=True)
 if host.returncode or 'does NOT match' in host.stdout or 'does match certificate' not in host.stdout:raise ValueError('Certificate hostname mismatch: '+host.stdout+host.stderr)
 valid=subprocess.run(['openssl','x509','-in',path,'-noout','-checkend',str(seconds)],capture_output=True,text=True)
 if valid.returncode:raise ValueError('Certificate is expired or near expiry: '+valid.stdout+valid.stderr)
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--domain',required=True);p.add_argument('--certificate',required=True);a=p.parse_args();check(a.certificate,a.domain);print('Certificate hostname and validity checked')
