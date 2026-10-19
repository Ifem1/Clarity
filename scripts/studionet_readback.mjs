/**
 * Read-only canonical contract/state export. Never calls a write or signs anything.
 * Execute after npm install with:
 *   CLARITY_CONTRACT=0x... node scripts/studionet_readback.mjs
 * It cannot replace transaction receipts, GenVM live proofs or ABI/schema checks.
 */
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
const address=process.env.CLARITY_CONTRACT||'';
if(!/^0x[0-9a-fA-F]{40}$/.test(address)){console.error('Set exact CLARITY_CONTRACT after verified Studionet deployment');process.exit(2)}
const client=createClient({chain:studionet});
const read=async(functionName,args=[])=>client.readContract({address,functionName,args});
const count=Number(await read('get_grant_count'));
const accounting=await read('get_accounting');
const items=[];
for(let id=1;id<=Math.min(count,12);id++){
 const grant=await read('get_grant',[BigInt(id)]);
 const tasks=[];
 for(let n=0;n<Number(grant.task_count);n++)tasks.push(await read('get_task',[BigInt(id),n]));
 items.push({id,grant,tasks});
}
console.log(JSON.stringify({network:'studionet',chainId:61999,contract:address,grantCount:count,accounting,grants:items},(_,v)=>typeof v==='bigint'?v.toString():v,2));
