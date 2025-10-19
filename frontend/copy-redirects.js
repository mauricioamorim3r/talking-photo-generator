// Copy _redirects and serve.json files to build directory
const fs = require('fs');
const path = require('path');

const files = [
  { source: '_redirects', dest: '_redirects', desc: '_redirects file' },
  { source: 'serve.json', dest: 'serve.json', desc: 'serve.json file' }
];

let successCount = 0;

files.forEach(file => {
  const source = path.join(__dirname, 'public', file.source);
  const dest = path.join(__dirname, 'build', file.dest);
  
  try {
    if (fs.existsSync(source)) {
      fs.copyFileSync(source, dest);
      console.log(`✅ ${file.desc} copied to build directory`);
      successCount++;
    } else {
      console.warn(`⚠️  ${file.desc} not found in public directory`);
    }
  } catch (error) {
    console.error(`❌ Error copying ${file.desc}:`, error.message);
  }
});

if (successCount === 0) {
  console.error('❌ No files were copied');
  process.exit(1);
}

console.log(`\n✅ ${successCount}/${files.length} files copied successfully`);

