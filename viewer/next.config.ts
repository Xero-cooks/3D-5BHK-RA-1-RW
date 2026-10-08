import type {NextConfig} from 'next';
const config:NextConfig={reactStrictMode:true,async headers(){return [
 {source:'/:path*',headers:[{key:'X-Content-Type-Options',value:'nosniff'},{key:'Referrer-Policy',value:'strict-origin-when-cross-origin'},{key:'X-Frame-Options',value:'SAMEORIGIN'},{key:'Permissions-Policy',value:'camera=(), microphone=(), geolocation=()'}]},
 {source:'/assets/:path*',has:[{type:'query',key:'v',value:'[a-f0-9]{16}'}],headers:[{key:'Cache-Control',value:'public, max-age=31536000, immutable'}]},
];}};export default config;
