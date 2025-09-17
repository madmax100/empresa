// Test script to verify the utils fix
// Run with: node test-utils-fix.js

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Testing Backend Frontend Utils Fix...');

function checkFile(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${description}: ${filePath}`);
    return true;
  } else {
    console.log(`❌ ${description}: ${filePath} - NOT FOUND`);
    return false;
  }
}

function checkPackageJson() {
  console.log('\n📦 Checking dependencies...');
  
  try {
    const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
    const requiredDeps = ['clsx', 'tailwind-merge', 'date-fns', 'lucide-react'];
    
    let allFound = true;
    for (const dep of requiredDeps) {
      const isInstalled = 
        (packageJson.dependencies && packageJson.dependencies[dep]) ||
        (packageJson.devDependencies && packageJson.devDependencies[dep]);
      
      if (isInstalled) {
        console.log(`✅ ${dep}: ${packageJson.dependencies[dep] || packageJson.devDependencies[dep]}`);
      } else {
        console.log(`❌ ${dep}: NOT INSTALLED`);
        allFound = false;
      }
    }
    
    return allFound;
  } catch (error) {
    console.error('❌ Error reading package.json:', error.message);
    return false;
  }
}

function checkUtilsContent() {
  console.log('\n🔍 Checking utils.ts content...');
  
  try {
    const utilsContent = fs.readFileSync('./src/lib/utils.ts', 'utf8');
    const requiredFunctions = ['formatCurrency', 'formatDate', 'formatNumber', 'cn'];
    
    let allFound = true;
    for (const func of requiredFunctions) {
      if (utilsContent.includes(`export function ${func}`)) {
        console.log(`✅ Function found: ${func}`);
      } else {
        console.log(`❌ Function missing: ${func}`);
        allFound = false;
      }
    }
    
    console.log(`📊 Total functions: ${(utilsContent.match(/export function/g) || []).length}`);
    console.log(`📊 File size: ${utilsContent.length} characters`);
    
    return allFound;
  } catch (error) {
    console.error('❌ Error reading utils.ts:', error.message);
    return false;
  }
}

function main() {
  console.log('🎯 Backend Frontend: C:\\Users\\Cirilo\\Documents\\kiro\\empresa\\backend\\empresa\\frontend\n');
  
  // Check critical files
  const filesOk = [
    checkFile('src/lib/utils.ts', 'Utils file'),
    checkFile('src/components/dashboard/CustosFixosDashboard.tsx', 'CustosFixosDashboard component'),
    checkFile('package.json', 'Package.json')
  ].every(Boolean);
  
  // Check dependencies
  const depsOk = checkPackageJson();
  
  // Check utils content
  const utilsOk = checkUtilsContent();
  
  console.log('\n🎉 SUMMARY:');
  console.log(`Files: ${filesOk ? '✅ OK' : '❌ MISSING'}`);
  console.log(`Dependencies: ${depsOk ? '✅ OK' : '❌ MISSING'}`);
  console.log(`Utils Functions: ${utilsOk ? '✅ OK' : '❌ MISSING'}`);
  
  if (filesOk && depsOk && utilsOk) {
    console.log('\n🚀 SUCCESS! Import error should be fixed.');
    console.log('\n📋 Next steps:');
    console.log('1. Run: npm run dev');
    console.log('2. Check if CustosFixosDashboard loads without errors');
    console.log('3. Verify formatCurrency function works');
  } else {
    console.log('\n⚠️  Some issues found. Please check the errors above.');
  }
}

main();