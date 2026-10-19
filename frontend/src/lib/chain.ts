"use client";
import {createClient} from "genlayer-js";
import {studionet} from "genlayer-js/chains";
import {TransactionStatus} from "genlayer-js/types";
import {addressText,isSuccessfulFinal} from './protocol.mjs';
export const CONTRACT = process.env.NEXT_PUBLIC_CLARITY_CONTRACT || '';
export const EXPLORER = 'https://explorer-studio.genlayer.com';
const readClient:any=createClient({chain:studionet});
export type Provider={request:(request:{method:string;params?:unknown[]})=>Promise<any>;on?:(name:string,fn:(value:any)=>void)=>void;removeListener?:(name:string,fn:(value:any)=>void)=>void};
let walletClient:any=null;
export function configured(){return /^0x[0-9a-fA-F]{40}$/.test(CONTRACT);}
export function contractUrl(){return EXPLORER+'/address/'+CONTRACT;}
export async function read(name:string,args:any[]=[]):Promise<any>{if(!configured())throw Error('Clarity is not deployed. Set NEXT_PUBLIC_CLARITY_CONTRACT after verified Studionet deployment.');return readClient.readContract({address:CONTRACT,functionName:name,args});}
export async function connectProvider(p:Provider):Promise<string>{
 const accounts=await p.request({method:'eth_requestAccounts'});if(!accounts?.[0])throw Error('No account selected.');
 const chain=await p.request({method:'eth_chainId'});
 if(BigInt(chain)!==61999n){try{await p.request({method:'wallet_switchEthereumChain',params:[{chainId:'0xf22f'}]});}
 catch(err:any){if(err?.code===4902){await p.request({method:'wallet_addEthereumChain',params:[{chainId:'0xf22f',chainName:'GenLayer StudioNet',nativeCurrency:{name:'GEN',symbol:'GEN',decimals:18},rpcUrls:['https://studio.genlayer.com/api'],blockExplorerUrls:[EXPLORER]}]});}else throw err;}}
 const confirmed=await p.request({method:'eth_chainId'});if(BigInt(confirmed)!==61999n)throw Error('Wallet is not on StudioNet 61999.');
 const account=String(accounts[0]);walletClient=createClient({chain:studionet,provider:p,account:account as `0x${string}`});
 return account;
}
export function forgetWallet(){walletClient=null;}
export async function write(name:string,args:any[]=[],value:bigint=0n):Promise<string>{
 if(!walletClient)throw Error('Connect a wallet before writing.');if(!configured())throw Error('Contract is not deployed.');
 const hash=await walletClient.writeContract({address:CONTRACT,functionName:name,args,value});
 const receipt=await walletClient.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED});
 if(!isSuccessfulFinal(receipt))throw Error('Transaction finalized without successful contract execution. Inspect '+EXPLORER+'/transactions/'+hash);
 return String(hash);
}
export async function fetchGrants(limit=30){const count=Number(await read('get_grant_count'));if(count>10000)throw Error('Grant index too large for direct browser listing.');const ids=Array.from({length:Math.min(count,limit)},(_,i)=>count-i);return Promise.all(ids.map(async id=>({id,data:await read('get_grant',[BigInt(id)])})));}
export async function fetchGrant(id:number){const grant=await read('get_grant',[BigInt(id)]);const count=Number(grant.task_count);const tasks=await Promise.all(Array.from({length:count},(_,n)=>read('get_task',[BigInt(id),n]).then(t=>({...t,index:n,recipient:addressText(t.recipient)}))));return {id,grant:{...grant,sponsor:addressText(grant.sponsor)},tasks};}
