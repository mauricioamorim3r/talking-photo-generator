// Copy _redirects file to build directory
const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'public', '_redirects');
const dest = path.join(__dirname, 'build', '_redirects');

try {
  if (fs.existsSync(source)) {
    fs.copyFileSync(source, dest);
    console.log('✅ _redirects file copied to build directory');
  } else {
    console.warn('⚠️  _redirects file not found in public directory');
  }
} catch (error) {
  console.error('❌ Error copying _redirects:', error.message);
  process.exit(1);
}
