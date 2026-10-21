export const STATUSES=['AWAITING','SUBMITTED','RETRYABLE','PROVISIONAL','CHALLENGED','SATISFIED_BLOCKED','READY','REJECTED','CLAIMED','REFUNDED'];
export const CHAIN_ID=61999;
export const GEN_BASE=1000000000000000000n;
export function taskActions(task,grant,tasks,account,now){
 const status=Number(task.status), me=(account||'').toLowerCase();
 const recipient=me===addressText(task.recipient).toLowerCase();
 const sponsor=me===addressText(grant.sponsor).toLowerCase();
 const deps=JSON.parse(task.dependencies||'[]');
 return {
  submit:!!me&&recipient&&status===0&&now<=Number(grant.deadline),
  evaluate:[1,2].includes(status)&&now<=Number(grant.deadline)+604800&&Number(task.attempts)<3&&(Number(task.attempts)===0||now>=Number(task.last_attempt_at)+60),
  finalize:status===3&&now>=Number(task.challenge_deadline),
  challenge:!!me&&status===3&&now<Number(task.challenge_deadline)&&((sponsor&&task.provisional_label==='SATISFIED')||(recipient&&task.provisional_label==='VIOLATED')),
  resolve:status===4&&Number(task.challenge_attempts)<3&&now<=Number(task.challenged_at)+86400&&(Number(task.challenge_attempts)===0||now>=Number(task.last_challenge_attempt_at)+60),
  recover:status===4&&now>=Number(task.challenged_at)+86400,
  activate:status===5&&deps.every(d=>[6,8].includes(Number(tasks[d]?.status))),
  claim:!!me&&recipient&&status===6,
  refund:!!me&&sponsor&&(status===7||([0,1,2,5].includes(status)&&now>=Number(grant.deadline)+604800))
 };
}
export function parseGen(value){const s=String(value).trim();if(!/^\d+(\.\d{1,18})?$/.test(s))throw Error('Enter a valid GEN amount (up to 18 decimals).');const [a,b='']=s.split('.');return BigInt(a)*GEN_BASE+BigInt((b+'0'.repeat(18)).slice(0,18));}
export function formatGen(value){const n=BigInt(value??0);const neg=n<0n?'-':'';const x=n<0n?-n:n;const decimal=(x%GEN_BASE).toString().padStart(18,'0').replace(/0+$/,'');return neg+(x/GEN_BASE).toString()+(decimal?'.'+decimal:'');}
export function bondWei(value){return BigInt(value)*500n/10000n;}
export function allocations(total,tasks){const sum=tasks.reduce((n,t)=>n+Number(t.allocation_bps),0);if(sum!==10000)throw Error('Task allocations must total exactly 100%.');let used=0n;return tasks.map((t,i)=>{const x=i===tasks.length-1?total-used:total*BigInt(t.allocation_bps)/10000n;used+=x;return x;});}
export function graphError(tasks){if(tasks.length<2||tasks.length>8)return 'Create between two and eight tasks.';let sum=0;for(let i=0;i<tasks.length;i++){const t=tasks[i];if(!/^0x[0-9a-fA-F]{40}$/.test(t.recipient))return `Task ${i+1} needs a recipient wallet.`;if(!t.title.trim()||!t.requirement.trim())return `Task ${i+1} needs its title and requirement.`;if(!Number.isInteger(t.allocation_bps)||t.allocation_bps<1)return `Task ${i+1} requires a positive whole-number bps allocation.`;if(!Array.isArray(t.dependencies)||new Set(t.dependencies).size!==t.dependencies.length||t.dependencies.some(d=>!Number.isInteger(d)||d<0||d>=i))return `Task ${i+1} contains an invalid prerequisite.`;if(t.sources.length<2||t.sources.length>3||!t.sources.some(s=>s.role==='PRIMARY'&&s.required)||!t.sources.some(s=>s.role==='CORROBORATING'&&s.required))return `Task ${i+1} needs required primary and corroborating sources from independent publishers.`;if(t.challenge_sources.length>2)return `Task ${i+1} exceeds two challenge sources.`;sum+=t.allocation_bps;}return sum===10000?'':`Allocations total ${(sum/100).toFixed(2)}%, not 100%.`;}
export function isSuccessfulFinal(receipt){if(!receipt)return false;const name=String(receipt.txExecutionResultName??receipt.tx_execution_result_name??receipt.execution_result??receipt.executionResult??receipt.consensus_data?.leader_receipt?.[0]?.execution_result??'');return ['FINISHED_WITH_RETURN','SUCCESS','return','1'].includes(name);}
const TX_STATUS_NAMES={0:'UNINITIALIZED',1:'PENDING',2:'PROPOSING',3:'COMMITTING',4:'REVEALING',5:'ACCEPTED',6:'UNDETERMINED',7:'FINALIZED',8:'CANCELED',9:'APPEAL_REVEALING',10:'APPEAL_COMMITTING',11:'READY_TO_FINALIZE',12:'VALIDATORS_TIMEOUT',13:'LEADER_TIMEOUT'};
export function transactionStatusName(receipt){if(!receipt)return'';const status=receipt.statusName??receipt.status_name??receipt.status;return typeof status==='number'||/^\d+$/.test(String(status))?TX_STATUS_NAMES[Number(status)]??String(status):String(status??'');}
export function isFinalized(receipt){return transactionStatusName(receipt)==='FINALIZED';}
export function addressText(value){if(typeof value==='string')return value;const v=value&&typeof value==='object'&&'bytes'in value?value.bytes:value;if(v instanceof Uint8Array)return'0x'+Array.from(v,b=>b.toString(16).padStart(2,'0')).join('');return String(value??'');}
