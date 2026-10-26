#!/usr/bin/env python3
"""Owner-only local review; no public administrative endpoint."""
import argparse,json,sqlite3
p=argparse.ArgumentParser();p.add_argument('--database',default='/var/lib/cellblock/game.db');p.add_argument('--resolve',metavar='REQUEST_ID');a=p.parse_args()
c=sqlite3.connect('file:'+a.database+'?mode=rw',uri=True);c.row_factory=sqlite3.Row
if a.resolve:
 c.execute('UPDATE legal_requests SET status=? WHERE id=?',('resolved',a.resolve));c.commit()
else:
 for row in c.execute('SELECT * FROM legal_requests WHERE status=? ORDER BY created',('open',)):print(json.dumps(dict(row)))
c.close()
