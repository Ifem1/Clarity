import './globals.css';import type {Metadata} from 'next';import {WalletProvider} from '@/components/wallet-provider';import {Shell} from '@/components/shell';
export const metadata:Metadata={title:'Clarity | Capital that follows verified progress',description:'GenLayer-native multi-recipient grant escrow with dependency-aware disbursements and evidence consensus.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><WalletProvider><Shell>{children}</Shell></WalletProvider></body></html>}
