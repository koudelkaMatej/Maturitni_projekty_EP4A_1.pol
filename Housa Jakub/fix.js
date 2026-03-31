const fs = require('fs');
const path = require('path');

function processDir(dir) {
  for (const file of fs.readdirSync(dir)) {
    if (file === 'node_modules' || file === '.git' || file === 'fix.js') continue;
    
    const fp = path.join(dir, file);
    if (fs.statSync(fp).isDirectory()) {
      processDir(fp);
    } else if (fp.endsWith('.html') || fp.endsWith('.js') || fp.endsWith('.css') || fp.endsWith('.json')) {
      let c = fs.readFileSync(fp, 'utf8');
      if (c.includes('<<<<<<< HEAD')) {
        console.log('Fixing ' + fp);
        const regex = /<<<<<<< HEAD[\s\S]*?=======\r?\n([\s\S]*?)>>>>>>> [a-f0-9A-Z]+\r?\n?/g;
        fs.writeFileSync(fp, c.replace(regex, '$1'), 'utf8');
      }
    }
  }
}

processDir(__dirname);
