import {createReadStream,createWriteStream} from 'node:fs';
import {mkdir,stat,rename,unlink,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {Readable,Transform} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {resolve} from 'node:path';
const manifest=JSON.parse(await readFile(new URL('./asset-manifest.json',import.meta.url),'utf8'));
const output=resolve(process.env.ASSET_OUTPUT_DIRECTORY||'.asset-cache');
await mkdir(output,{recursive:true});
async function verify(path,asset){
 const file=await stat(path).catch(e=>{if(e.code==='ENOENT')return null;throw e;});
 if(!file)return false;
 if(file.size!==asset.bytes)throw Error(`${asset.name}: incorrect size. Remove stale file or explicitly update the asset manifest for an approved replacement.`);
 const hash=createHash('sha256');for await(const chunk of createReadStream(path))hash.update(chunk);
 if(hash.digest('hex')!==asset.sha256)throw Error(`${asset.name}: checksum mismatch. Asset version must be approved and pinned.`);
 return true;
}
for(const asset of manifest.assets){
 const target=resolve(output,asset.name);
 if(await verify(target,asset)){console.log(`Verified ${asset.name}`);continue;}
 console.log(`Fetching approved ${asset.name}`);
 const response=await fetch(asset.url,{signal:AbortSignal.timeout(300000)});
 if(!response.ok||!response.body)throw Error(`Asset download failed for ${asset.name}: HTTP ${response.status}`);
 const pending=target+'.download';let bytes=0;
 try{
  await pipeline(Readable.fromWeb(response.body),new Transform({transform(chunk,encoding,callback){bytes+=chunk.length;if(bytes>asset.bytes)return callback(Error('Download exceeds pinned size'));callback(null,chunk);}}),createWriteStream(pending,{flags:'w'}));
  await verify(pending,asset);await rename(pending,target);
 }catch(error){await unlink(pending).catch(()=>{});throw error;}
 console.log(`Verified ${asset.name}`);
}
console.log(`Assets ready from source commit ${manifest.sourceCommit}`);
