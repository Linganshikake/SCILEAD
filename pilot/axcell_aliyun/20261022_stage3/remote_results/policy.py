"""Execution-only safeguards; no prediction transformation."""
import re
G=2**30
def checkpoint_action(state,verified_or_existing):
 if state is None:return 'BLOCK' if verified_or_existing else 'START'
 if state['status'] in ('EXTRACTION_COMPLETE','VALID_EMPTY') and verified_or_existing:return 'SKIP'
 return 'BLOCK'
def owned_unit(name):return bool(re.fullmatch(r'axcell-stage3-worker-[a-zA-Z0-9]+\.service',name))
def recovered_stop(states):
 return next((x['resource_stop'] for x in states if x.get('resource_stop')),None)
def owns_service(info,token):return info.get('Description')=='scilead-stage3-'+token
def resource_stop(available,free,worker,es,oom,baseline_oom,elapsed):
 if oom>baseline_oom:return 'NEW_KERNEL_OOM'
 if available<4*G:return 'HOST_AVAILABLE_LT_4G'
 if free<20*G:return 'DISK_FREE_LT_20G'
 if worker>=14*G:return 'WORKER_EARLY_14G_LIMIT'
 if es>=2.4*G:return 'ES_EARLY_2_4G_LIMIT'
 if elapsed>1800:return 'WALL_TIME_1800S_LIMIT'
 return None
