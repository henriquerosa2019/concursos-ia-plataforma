const fs = require('fs');
const path = require('path');

const rootDir = process.cwd();
const outputStatic = path.join(rootDir, '.vercel', 'output', 'static');

try {
  fs.mkdirSync(outputStatic, { recursive: true });
} catch (e) {}

const filesToCopy = [
  { src: 'landing.html', dest: 'index.html' },
  { src: 'landing.html', dest: 'landing.html' },
  { src: 'index.html', dest: 'app.html' },
  { src: 'index.html', dest: 'plataforma.html' },
  { src: 'mockup_projeto_aprovacao.jpg', dest: 'mockup_projeto_aprovacao.jpg' }
];

for (const item of filesToCopy) {
  const srcPath = path.join(rootDir, item.src);
  const destPath = path.join(outputStatic, item.dest);
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    console.log(`[build.js] ${item.src} -> ${item.dest}`);
  }
}

// Copy assets folder
const assetsSrc = path.join(rootDir, 'assets');
const assetsDest = path.join(outputStatic, 'assets');
if (fs.existsSync(assetsSrc)) {
  fs.mkdirSync(assetsDest, { recursive: true });
  for (const f of fs.readdirSync(assetsSrc)) {
    const s = path.join(assetsSrc, f);
    const d = path.join(assetsDest, f);
    if (fs.statSync(s).isFile()) {
      fs.copyFileSync(s, d);
      console.log(`[build.js] assets/${f} -> assets/${f}`);
    }
  }
}

console.log('[build.js] Static assets successfully prepared in .vercel/output/static!');
