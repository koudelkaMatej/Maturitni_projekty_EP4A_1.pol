const fs = require('fs');
const path = require('path');
const iconv = require('iconv-lite');

function processDir(dir) {
  for (const file of fs.readdirSync(dir)) {
    if (file === 'node_modules' || file === '.git') continue;
    
    const fp = path.join(dir, file);
    if (fs.statSync(fp).isDirectory()) {
      processDir(fp);
    } else if (fp.endsWith('.html') || fp.endsWith('.js') || fp.endsWith('.css') || fp.endsWith('.json')) {
      let originalContent = fs.readFileSync(fp);
      let c = originalContent.toString('utf8');
      
      let changed = false;
      const fixed = c.replace(/[���][\s\S]/g, match => {
        try {
          const encoded = iconv.encode(match, 'win1250');
          // If the match was genuinely 2 characters that translate to UTF-8 leading bytes for Central Europe:
          if (encoded.length === 2 && (encoded[0] === 0xC3 || encoded[0] === 0xC4 || encoded[0] === 0xC5)) {
            const decodedUtf8 = encoded.toString('utf8');
            // Make sure we didn't just produce a broken character again
            if (decodedUtf8 !== '') {
              changed = true;
              return decodedUtf8;
            }
          }
        } catch(e) {}
        return match;
      });

      if (changed && fixed !== c) {
        console.log('Fixed encoding in ' + fp);
        fs.writeFileSync(fp, fixed, 'utf8');
      }
    }
  }
}

processDir(__dirname);
console.log("Done!");
