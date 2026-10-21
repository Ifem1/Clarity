import {test} from 'node:test';
import {strict as a} from 'node:assert';
import {parseGen,formatGen,bondWei,allocations,graphError,isSuccessfulFinal,isFinalized,transactionStatusName,taskActions} from '../src/lib/protocol.mjs';
test('precision in GEN',()=>{for(const v of ['0','0.000000000000000001','1.234500000000000001','8900000'])a.equal(formatGen(parseGen(v)),v.includes('.')?v.replace(/0+$/,'').replace(/\.$/,''):v);});
test('reject too many decimals',()=>a.throws(()=>parseGen('1.0000000000000000001')));
test('exact bond',()=>a.equal(bondWei(parseGen('0.02')),parseGen('0.001')));
test('rounding goes to last task',()=>a.deepEqual(allocations(1000000000000000007n,[{allocation_bps:4000},{allocation_bps:6000}]).reduce((a,b)=>a+b,0n),1000000000000000007n));
test('reject incompatible allocations',()=>a.throws(()=>allocations(10n,[{allocation_bps:9000}])));
test('only explicit execution success counts',()=>{a.equal(isSuccessfulFinal({txExecutionResultName:'FINISHED_WITH_RETURN'}),true);a.equal(isSuccessfulFinal({resultName:'MAJORITY_AGREE'}),false);});
test('StudioNet numeric and named statuses identify finality correctly',()=>{a.equal(transactionStatusName({status:7}),'FINALIZED');a.equal(transactionStatusName({statusName:'FINALIZED'}),'FINALIZED');a.equal(isFinalized({status:7}),true);a.equal(isFinalized({status:5}),false);a.equal(isFinalized({statusName:'ACCEPTED'}),false);a.equal(isSuccessfulFinal({status:7,consensus_data:{leader_receipt:[{execution_result:'SUCCESS'}]}}),true);});
test('reject missing tasks',()=>a.match(graphError([]),/two and eight/));

const grant={deadline:1000,sponsor:'0xaaa'};
const task={status:1,attempts:0,dependencies:'[]',recipient:'0xbbb'};
test('evaluation respects grace, retry cap and cooldown',()=>{
 a.equal(taskActions(task,grant,[],'',1000).evaluate,true);
 a.equal(taskActions(task,grant,[],'',605801).evaluate,false);
 a.equal(taskActions({...task,attempts:3},grant,[],'',1000).evaluate,false);
 a.equal(taskActions({...task,attempts:1,last_attempt_at:950},grant,[],'',1000).evaluate,false);
 a.equal(taskActions({...task,attempts:1,last_attempt_at:940},grant,[],'',1000).evaluate,true);
});
test('activation requires every prerequisite to be eligible',()=>{
 const blocked={...task,status:5,dependencies:'[0]'};
 a.equal(taskActions(blocked,grant,[{status:3}],'',1000).activate,false);
 a.equal(taskActions(blocked,grant,[{status:6}],'',1000).activate,true);
 a.equal(taskActions(blocked,grant,[{status:8}],'',1000).activate,true);
});
test('submission and challenge depend on frozen party roles',()=>{
 a.equal(taskActions({...task,status:0},grant,[],'0xbbb',1000).submit,true);
 a.equal(taskActions({...task,status:0},grant,[],'0xccc',1000).submit,false);
 const provisional={...task,status:3,provisional_label:'SATISFIED',challenge_deadline:1100};
 a.equal(taskActions(provisional,grant,[],'0xaaa',1000).challenge,true);
 a.equal(taskActions(provisional,grant,[],'0xbbb',1000).challenge,false);
});
test('only direct recipient can claim and sponsor can refund',()=>{
 const ready={...task,status:6}, rejected={...task,status:7};
 a.equal(taskActions(ready,grant,[],'0xbbb',1000).claim,true);
 a.equal(taskActions(ready,grant,[],'0xaaa',1000).claim,false);
 a.equal(taskActions(rejected,grant,[],'0xaaa',1000).refund,true);
 a.equal(taskActions(rejected,grant,[],'0xbbb',1000).refund,false);
});
test('challenge recovery and retry use exact time boundaries',()=>{
 const challenged={...task,status:4,challenged_at:100,challenge_attempts:1,last_challenge_attempt_at:950};
 a.equal(taskActions(challenged,grant,[],'',1000).resolve,false);
 a.equal(taskActions(challenged,grant,[],'',1010).resolve,true);
 a.equal(taskActions(challenged,grant,[],'',86500).recover,true);
 a.equal(taskActions(challenged,grant,[],'',86501).resolve,false);
});
