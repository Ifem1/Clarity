#!/usr/bin/env python3
"""Local, no-network release preflight. This does not simulate on-chain deployment."""
import ast,hashlib,json,pathlib,sys
p=pathlib.Path(__file__).resolve().parents[1]
s=(p/'contracts/clarity.py').read_bytes()
mod=ast.parse(s)
classes=[n for n in mod.body if isinstance(n,ast.ClassDef)]
assert sum(x.name=='Clarity' for x in classes)==1
classnode=next(n for n in classes if n.name=='Clarity')
methods={n.name for n in classnode.body if isinstance(n,ast.FunctionDef)}
required={'create_grant','submit_task','evaluate_task','challenge_task','resolve_challenge','finalize_task','activate_task','claim_task','recover_stalled_challenge','refund_task','get_grant','get_task','get_manifest','get_accounting'}
assert required<=methods,'missing methods: '+','.join(sorted(required-methods))
assert b'run_nondet_unsafe' in s and b'emit_transfer' in s
record={'source_sha256':hashlib.sha256(s).hexdigest(),'contract_methods':sorted(methods),'deployment':'NOT_DEPLOYED','checks':'SOURCE_ONLY'}
print(json.dumps(record,indent=2))
