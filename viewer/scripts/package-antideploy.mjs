import {spawnSync} from 'node:child_process';
import {statSync} from 'node:fs';
import {resolve} from 'node:path';
const destination=resolve(process.argv[2]||'/tmp/farmhouse-antideploy.tar.gz');
const result=spawnSync('tar',['czf',destination,'--exclude=./node_modules','--exclude=./.next','--exclude=./.git','--exclude=./public/assets','--exclude=./reports/browser-screenshots','--exclude=./.env*','--exclude=./*.tsbuildinfo','.'],{stdio:'inherit'});
if(result.status!==0)process.exit(result.status||1);
const size=statSync(destination).size;
if(size>29360128)throw Error('Archive exceeds Antideploy 28 MiB upload limit');
console.log(`Deployment archive ready: ${size} bytes. Approved assets will be fetched and verified during build.`);
