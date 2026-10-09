import {test} from 'node:test';import assert from 'node:assert/strict';import {downloadBinary} from '../lib/download';
test('compressed transfer without Content-Length still reports decoded manifest progress',async()=>{
 const values:number[][]=[];const stream=new ReadableStream<Uint8Array>({start(c){c.enqueue(new Uint8Array([1,2,3]));c.enqueue(new Uint8Array([4,5,6]));c.close();}});
 const fetcher=(async()=>new Response(stream,{headers:{'Content-Encoding':'gzip'}})) as typeof fetch;
 const bytes=await downloadBinary('https://example.test/model.glb',(n,t)=>values.push([n,t]),{expectedBytes:6,fetcher});
 assert.deepEqual(values,[[0,6],[3,6],[6,6]]);assert.equal(bytes.length,6);
});
test('an incomplete property download rejects instead of decoding a corrupt buffer',async()=>{
 await assert.rejects(downloadBinary('https://example.test/model.glb',()=>{},{expectedBytes:6,fetcher:(async()=>new Response(new Uint8Array([1,2]))) as typeof fetch}),/incomplete/);
});
test('stalled transfer exits with a timeout rather than an endless loading screen',async()=>{
 const fetcher=(async(_:unknown,init?:RequestInit)=>{const stream=new ReadableStream<Uint8Array>({start(c){init?.signal?.addEventListener('abort',()=>c.error(init.signal?.reason),{once:true});}});return new Response(stream);}) as typeof fetch;
 await assert.rejects(downloadBinary('https://example.test/model.glb',()=>{},{expectedBytes:6,idleTimeoutMs:30,fetcher}),/stopped receiving data/);
});
test('component cancellation aborts an in-flight property request',async()=>{
 const abort=new AbortController();abort.abort(new Error('Navigation cancelled'));
 const fetcher=(async(_:unknown,init?:RequestInit)=>{if(init?.signal?.aborted)throw init.signal.reason;return new Response(new Uint8Array([1]));}) as typeof fetch;
 await assert.rejects(downloadBinary('https://example.test/model.glb',()=>{},{signal:abort.signal,fetcher}),/Navigation cancelled/);
});
