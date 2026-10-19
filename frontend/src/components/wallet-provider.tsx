"use client";
import {createContext,useContext,useEffect,useState} from 'react';
import {connectProvider,forgetWallet,Provider} from '@/lib/chain';

type ContextType={account:string;busy:boolean;error:string;connect:()=>Promise<void>;disconnect:()=>void};
const WalletContext=createContext<ContextType>({account:'',busy:false,error:'',connect:async()=>{},disconnect:()=>{}});
export function useWallet(){return useContext(WalletContext)};
declare global {interface Window {ethereum?:Provider}}
export function WalletProvider({children}:{children:React.ReactNode}){
 const [account,setAccount]=useState('');const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 useEffect(()=>{const p=window.ethereum;if(!p)return;const change=(accounts:unknown)=>{forgetWallet();setAccount('');if(Array.isArray(accounts)&&accounts.length)setError('Account changed. Reconnect to verify StudioNet.');};const chain=()=>{forgetWallet();setAccount('');setError('Chain changed. Reconnect to verify StudioNet.');};p.on?.('accountsChanged',change);p.on?.('chainChanged',chain);return()=>{p.removeListener?.('accountsChanged',change);p.removeListener?.('chainChanged',chain)}},[]);
 const connect=async()=>{if(!window.ethereum){setError('No injected wallet detected. Install an EIP-1193 browser wallet.');return;}setBusy(true);setError('');try{const connected=await connectProvider(window.ethereum);setAccount(connected);setError('')}catch(e){setAccount('');forgetWallet();setError(String((e as Error).message||e))}finally{setBusy(false)}};
 const disconnect=()=>{forgetWallet();setAccount('');setError('')};
 return <WalletContext.Provider value={{account,busy,error,connect,disconnect}}>{children}</WalletContext.Provider>;
}
