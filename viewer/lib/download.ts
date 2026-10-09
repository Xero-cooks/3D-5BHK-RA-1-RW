export type DownloadOptions={expectedBytes?:number;signal?:AbortSignal;idleTimeoutMs?:number;fetcher?:typeof fetch};
export async function downloadBinary(url:string,onProgress:(loaded:number,total:number)=>void,options:DownloadOptions={}){
 const controller=new AbortController();const idle=options.idleTimeoutMs??60000;let timer:ReturnType<typeof setTimeout>;let reader:ReadableStreamDefaultReader<Uint8Array>|undefined;
 const reset=()=>{clearTimeout(timer);timer=setTimeout(()=>controller.abort(new Error('Download stopped receiving data')),idle);};
 const cancel=()=>controller.abort(options.signal?.reason);
 options.signal?.addEventListener('abort',cancel,{once:true});if(options.signal?.aborted)cancel();reset();
 try{
  const response=await (options.fetcher||fetch)(url,{signal:controller.signal});
  if(!response.ok)throw Error(`Asset request failed (${response.status})`);
  // Browser fetch returns DECOMPRESSED bytes. A compressed Content-Length is not
  // that length, and Cloudflare often omits it: use the approved asset manifest.
  const total=options.expectedBytes||(!response.headers.get('Content-Encoding')?Number(response.headers.get('Content-Length')):0)||0;
  reader=response.body?.getReader();if(!reader)throw Error('Streaming assets unavailable');
  const chunks:Uint8Array[]=[];let loaded=0;onProgress(0,total);
  while(true){const {done,value}=await reader.read();if(done)break;reset();chunks.push(value);loaded+=value.length;onProgress(loaded,total);}
  if(options.expectedBytes&&loaded!==options.expectedBytes)throw Error('The property download was incomplete');
  const data=new Uint8Array(loaded);let offset=0;for(const chunk of chunks){data.set(chunk,offset);offset+=chunk.length;}chunks.length=0;
  return data;
 }finally{clearTimeout(timer!);options.signal?.removeEventListener('abort',cancel);reader?.releaseLock();}
}
