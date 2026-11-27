import { execFileSync } from 'node:child_process';
import { readFileSync, mkdirSync, rmSync } from 'node:fs';
const v = JSON.parse(readFileSync('manifest.json', 'utf8')).version;
mkdirSync('dist', { recursive: true });
const out = `dist/MythLab-extension-${v}.zip`;
rmSync(out, { force: true });
execFileSync('python', ['-c', "import zipfile,sys;z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED);[z.write(f) for f in ['manifest.json','background.js','panel.html','panel.js','icons/icon-192.png']]", out], { stdio: 'inherit' });
console.log(out);
