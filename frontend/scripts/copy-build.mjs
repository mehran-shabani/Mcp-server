import { mkdirSync, readdirSync, rmSync, statSync, copyFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const projectRoot = resolve(new URL('..', import.meta.url).pathname, '..');
const buildDir = join(projectRoot, 'frontend', 'dist');
const targetDir = join(projectRoot, 'mcp_server', 'static', 'frontend');
const preservedFiles = new Set(['.gitignore']);

function ensureDirectory(path) {
  mkdirSync(path, { recursive: true });
}

function clearDirectory(path) {
  if (!statExists(path)) {
    return;
  }

  for (const entry of readdirSync(path)) {
    if (preservedFiles.has(entry)) {
      continue;
    }
    rmSync(join(path, entry), { recursive: true, force: true });
  }
}

function statExists(path) {
  try {
    statSync(path);
    return true;
  } catch (error) {
    if (error && error.code === 'ENOENT') {
      return false;
    }
    throw error;
  }
}

function copyDirectory(source, destination) {
  ensureDirectory(destination);
  for (const entry of readdirSync(source, { withFileTypes: true })) {
    const sourcePath = join(source, entry.name);
    const destinationPath = join(destination, entry.name);
    if (entry.isDirectory()) {
      copyDirectory(sourcePath, destinationPath);
    } else if (entry.isFile()) {
      copyFileSync(sourcePath, destinationPath);
    }
  }
}

if (!statExists(buildDir)) {
  console.error('No build output found at', buildDir);
  process.exit(1);
}

ensureDirectory(targetDir);
clearDirectory(targetDir);
copyDirectory(buildDir, targetDir);

console.log(`Copied frontend build to ${targetDir}`);
