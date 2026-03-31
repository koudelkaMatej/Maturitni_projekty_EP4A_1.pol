const fs = require('fs');
const path = require('path');

function processDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        if (file === 'node_modules' || file === '.git') continue;
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            processDir(fullPath);
        } else if (file.endsWith('.html') || file.endsWith('.js') || file.endsWith('.css')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            if (content.includes('<<<<<<< HEAD')) {
                console.log('Fixing ' + fullPath);
                // Regex to match conflict blocks, keeping the BOTTOM part
                const regex = /<<<<<<< HEAD[\s\S]*?=======\r?\n([\s\S]*?)>>>>>>> [a-f0-9]+\r?\n/g;
                const newContent = content.replace(regex, '\');
                fs.writeFileSync(fullPath, newContent, 'utf8');
            }
        }
    }
}

processDir(__dirname);
