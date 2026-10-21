"use client";
import {useCallback,useEffect,useState} from 'react';
import Link from 'next/link';
import {ArrowLeft,RefreshCw} from 'lucide-react';
import {configured,read,write} from '@/lib/chain';
import {useWallet} from '@/components/wallet-provider';
import {formatGen} from '@/lib/protocol.mjs';

type Credit={label:string;amount:bigint;method:string;description:string};

export default function RecoverFunding(){
 const {account}=useWallet();
 const [credits,setCredits]=useState<Credit[]>([]);
 const [error,setError]=useState('');
 const [busy,setBusy]=useState('');
 const [tx,setTx]=useState('');
 const refresh=useCallback(async()=>{
  if(!configured()||!account){setCredits([]);return}
  try{
   const [funding,transfer,bond]=await Promise.all([
    read('get_funding_recovery',[account]),
    read('get_failed_transfer_recovery',[account]),
    read('get_bond_credit',[account]),
   ]);
   setCredits([
    {label:'Failed grant funding',amount:BigInt(funding),method:'recover_failed_funding',description:'Expected validation errors and unknown-selector payable fallback calls.'},
    {label:'Failed payout or refund',amount:BigInt(transfer),method:'recover_failed_transfer',description:'GEN returned by GenVM after an emitted transfer failed.'},
    {label:'Challenge bond',amount:BigInt(bond),method:'claim_bond_credit',description:'A bond awarded to this wallet after challenge resolution.'},
   ]);
   setError('');
  }catch(e){setError((e as Error).message)}
 },[account]);
 useEffect(()=>{void refresh()},[refresh]);
 const recover=async(method:string)=>{
  setBusy(method);setError('');setTx('');
  try{const hash=await write(method);setTx(hash);await refresh()}
  catch(e){setError((e as Error).message)}
  finally{setBusy('')}
 };
 return <section className="registry">
  <Link href="/" className="back"><ArrowLeft size={16}/> All grants</Link>
  <div className="eyebrow">ORIGIN-OWNED TRANSFER RECOVERY</div>
  <h1>RECOVER <span className="acid">GEN.</span></h1>
  <p className="detail-summary">Check credits returned to your wallet after failed grant funding, failed outgoing transfers, or challenge-bond settlement. Each credit can only be claimed by its directly connected owner. No administrator can withdraw these funds.</p>
  {!account?<div className="feedback">Connect the wallet that funded the grant, was due the transfer, or owns the bond.</div>:<div className="form-section"><h2>WALLET CREDITS</h2>{credits.map(credit=><article className="editor-node" key={credit.method}><div className="form-title"><h3>{credit.label}</h3><strong>{formatGen(credit.amount)} GEN</strong></div><p>{credit.description}</p><button className="action" disabled={busy!==''||credit.amount===0n||!configured()} onClick={()=>void recover(credit.method)}>{busy===credit.method?'Waiting for finalization…':`Recover ${formatGen(credit.amount)} GEN`}</button></article>)}<button className="outline-btn" onClick={()=>void refresh()}><RefreshCw size={14}/> Refresh credits</button></div>}
  {error&&<div className="feedback error" role="alert">{error}</div>}
  {tx&&<div className="feedback">Recovery transaction {tx}</div>}
  <p className="muted">A fatal VM or ABI-decoding failure before dispatch cannot create an application credit. Empty-calldata transfers are not supported by this contract version.</p>
 </section>
}
