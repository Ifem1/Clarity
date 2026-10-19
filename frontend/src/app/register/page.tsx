"use client";
import {useCallback,useEffect,useState} from 'react';
import Link from 'next/link';
import {ArrowLeft,ArrowUpRight,ShieldCheck} from 'lucide-react';
import {read,write,configured} from '@/lib/chain';
import {useWallet} from '@/components/wallet-provider';

export default function RegisterRecipient(){
 const {account}=useWallet();
 const [registered,setRegistered]=useState(false);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [tx,setTx]=useState('');
 const refresh=useCallback(async()=>{
  if(!account||!configured()){setRegistered(false);return;}
  try{setRegistered(Boolean(await read('is_registered_recipient',[account])));setError('');}
  catch(e){setError(String((e as Error).message||e));}
 },[account]);
 useEffect(()=>{void refresh();},[refresh]);
 const register=async()=>{
  setBusy(true);setError('');setTx('');
  try{const hash=await write('register_recipient');setTx(hash);await refresh();}
  catch(e){setError(String((e as Error).message||e));}
  finally{setBusy(false);}
 };
 return <section className="composer">
  <Link href="/new" className="back"><ArrowLeft size={16}/> Create a grant</Link>
  <div className="eyebrow">RECIPIENT WALLET / DIRECT OWNERSHIP</div>
  <h1>REGISTER <span className="acid">YOUR WALLET.</span></h1>
  <p className="detail-summary">Clarity pays native GEN directly to registered EOA wallets. Register once from the wallet that will receive funds. Contract wallets cannot register, which prevents a recipient contract from rejecting or trapping a payout.</p>
  {!configured()&&<div className="feedback">Recipient registration opens after the verified StudioNet contract is deployed.</div>}
  {!account&&<div className="feedback">Connect the recipient wallet in the navigation to check or register it.</div>}
  {account&&<div className="form-section">
   <ShieldCheck className="acid"/><div><h2>CONNECTED WALLET</h2><p><code>{account}</code></p>
   <p>{registered?'This wallet is registered and can receive Clarity grants.':'This wallet is not registered yet.'}</p></div>
   {!registered&&<button className="primary-cta" disabled={busy||!configured()} onClick={()=>void register()}>{busy?'Waiting for finalization…':'Register wallet'} <ArrowUpRight size={18}/></button>}
  </div>}
  {error&&<p className="feedback error" role="alert">{error}</p>}
  {tx&&<p className="feedback">Registration transaction: {tx}</p>}
  <p className="muted">Each distinct task recipient must register before the sponsor funds a grant. The registration is permanent for this contract.</p>
 </section>;
}
