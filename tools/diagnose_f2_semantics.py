from pathlib import Path
import json

p=Path(__file__).resolve().parents[1]/'results/official/attempts/E3A-OFFICIAL-ATTEMPT-001/results.jsonl'
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
controls=[r for r in rows if r['case_role']=='control']
f2=[r for r in controls if r['family']=='F2']

def value(r):
    pre=phase=None
    for o in r['tool_transcript']:
        if o['tool']=='read_preop_snapshot': pre=o['result']['value']
        if o['tool']=='read_operation_phase': phase=o['result']['phase_code']
    return pre if phase=='P3' else None

def ok(r):
    v=value(r)
    claim='TRUE' if v==r['target'] else 'FALSE'
    return v is not None and r['agent_claim_value']==claim and r['agent_evidence_status']=='SUFFICIENT' and r.get('model_behavior_failure') is None

frozen=sum(bool(r.get('control_complete_success')) for r in controls)
frozen_f2=sum(bool(r.get('control_complete_success')) for r in f2)
diag=sum(ok(r) for r in f2)
print('F2 controls',len(f2))
print('frozen F2',f'{frozen_f2}/{len(f2)}')
print('diagnostic F2',f'{diag}/{len(f2)}')
print('frozen all controls',f'{frozen}/{len(controls)}')
print('combined F2+documented-F3 diagnostic',f'{frozen-frozen_f2+diag+4}/{len(controls)}')
