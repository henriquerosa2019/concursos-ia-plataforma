const fs = require('fs');
const path = require('path');

const rootDir = process.cwd();
const outputStatic = path.join(rootDir, '.vercel', 'output', 'static');
const publicDir = path.join(rootDir, 'public');

try {
  fs.mkdirSync(outputStatic, { recursive: true });
} catch (e) {}
try {
  fs.mkdirSync(publicDir, { recursive: true });
} catch (e) {}

const filesToCopy = [
  { src: 'landing.html', dest: 'index.html' },
  { src: 'landing.html', dest: 'landing.html' },
  { src: 'index.html', dest: 'app.html' },
  { src: 'index.html', dest: 'plataforma.html' },
  { src: 'sucesso.html', dest: 'sucesso.html' },
  { src: 'mockup_projeto_aprovacao.jpg', dest: 'mockup_projeto_aprovacao.jpg' },
  { src: 'preseeded_topics.json', dest: 'preseeded_topics.json' }
];

for (const item of filesToCopy) {
  const srcPath = path.join(rootDir, item.src);
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, path.join(outputStatic, item.dest));
    fs.copyFileSync(srcPath, path.join(publicDir, item.dest));
    console.log(`[build.js] ${item.src} -> ${item.dest}`);
  }
}

// Copy assets folder
const assetsSrc = path.join(rootDir, 'assets');
const assetsDestStatic = path.join(outputStatic, 'assets');
const assetsDestPublic = path.join(publicDir, 'assets');

if (fs.existsSync(assetsSrc)) {
  fs.mkdirSync(assetsDestStatic, { recursive: true });
  fs.mkdirSync(assetsDestPublic, { recursive: true });
  for (const f of fs.readdirSync(assetsSrc)) {
    const s = path.join(assetsSrc, f);
    if (fs.statSync(s).isFile()) {
      fs.copyFileSync(s, path.join(assetsDestStatic, f));
      fs.copyFileSync(s, path.join(assetsDestPublic, f));
      console.log(`[build.js] assets/${f} -> assets/${f}`);
    }
  }
}

console.log('[build.js] Static assets successfully prepared in .vercel/output/static and public/!');
