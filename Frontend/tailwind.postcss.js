const fs = require('fs');
const path = require('path');
const tailwind = require('tailwindcss');
const postcss = require('postcss');
const ts = require('typescript');

const SIMPLE_CLASS_ALLOWLIST = new Set([
  'flex',
  'grid',
  'block',
  'inline',
  'inline-block',
  'inline-flex',
  'hidden',
  'contents',
  'table',
  'table-row',
  'table-cell',
  'static',
  'relative',
  'absolute',
  'fixed',
  'sticky',
  'container'
]);

function loadTailwindConfig() {
  const configPath = path.resolve('tailwind.config.js');
  delete require.cache[configPath];
  const loaded = require(configPath);
  return loaded?.default ?? loaded;
}

function normalizeContentArray(content) {
  if (!content) return [];
  if (Array.isArray(content)) return content;
  if (Array.isArray(content.files)) return content.files;
  return [];
}

function resolveFilePatterns(patterns) {
  const files = new Set();
  for (const pattern of patterns) {
    const resolved = resolvePattern(pattern);
    for (const file of resolved) {
      files.add(file);
    }
  }
  return Array.from(files);
}

function resolvePattern(pattern) {
  if (!pattern) return [];
  const normalized = pattern.replace(/\\/g, '/');
  const absolutePattern = path.resolve(pattern);
  if (!pattern.includes('*')) {
    const filePath = path.resolve(pattern);
    return fs.existsSync(filePath) ? [filePath] : [];
  }

  const braceMatch = normalized.match(/^(.*)\*\*\/\*\.\{([^}]+)\}$/);
  if (braceMatch) {
    const baseDir = path.resolve(braceMatch[1] || '.');
    const extensions = braceMatch[2].split(',').map((ext) => ext.trim().replace(/^[.]/, ''));
    return walkDir(baseDir, new Set(extensions));
  }

  const extMatch = normalized.match(/^(.*)\*\*\/\*\.([a-zA-Z0-9]+)/);
  if (extMatch) {
    const baseDir = path.resolve(extMatch[1] || '.');
    const ext = extMatch[2];
    return walkDir(baseDir, new Set([ext]));
  }

  const dirMatch = normalized.match(/^(.*)\*\*\/*\*?$/);
  if (dirMatch) {
    const baseDir = path.resolve(dirMatch[1] || '.');
    return walkDir(baseDir);
  }

  if (fs.existsSync(absolutePattern)) {
    return [absolutePattern];
  }

  return [];
}

function walkDir(dir, extensions) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walkDir(fullPath, extensions));
    } else if (!extensions || extensions.has(path.extname(entry.name).slice(1))) {
      results.push(fullPath);
    }
  }
  return results;
}

function extractCandidatesFromFiles(filePaths, candidates) {
  for (const filePath of filePaths) {
    const ext = path.extname(filePath).toLowerCase();
    if (!fs.existsSync(filePath)) continue;
    const content = fs.readFileSync(filePath, 'utf8');
    if (ext === '.html' || ext === '.htm') {
      extractFromHtml(content, candidates);
    } else if (ext === '.css') {
      extractFromCss(content, candidates);
    } else if (['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'].includes(ext)) {
      extractFromTs(content, filePath, candidates);
    }
  }
}

function extractFromHtml(content, candidates) {
  const regex = /class(?:Name)?=["']([^"']+)["']/g;
  let match;
  while ((match = regex.exec(content))) {
    addClassCandidates(match[1], candidates);
  }
}

function extractFromCss(content, candidates) {
  const applyRegex = /@apply\s+([^;\n]+)[;\n]/g;
  let match;
  while ((match = applyRegex.exec(content))) {
    addClassCandidates(match[1], candidates);
  }
}

function extractFromTs(source, filePath, candidates) {
  const scriptKind = filePath.endsWith('.tsx') || filePath.endsWith('.jsx')
    ? ts.ScriptKind.TSX
    : filePath.endsWith('.ts')
    ? ts.ScriptKind.TS
    : ts.ScriptKind.JS;
  const sourceFile = ts.createSourceFile(filePath, source, ts.ScriptTarget.Latest, true, scriptKind);

  function visit(node) {
    if (ts.isJsxAttribute(node) && (node.name.text === 'className' || node.name.text === 'class')) {
      if (!node.initializer) return;
      if (ts.isStringLiteral(node.initializer) || ts.isNoSubstitutionTemplateLiteral(node.initializer)) {
        addClassCandidates(node.initializer.text, candidates);
      } else if (ts.isJsxExpression(node.initializer) && node.initializer.expression) {
        extractFromExpression(node.initializer.expression, candidates);
      }
    }

    if (ts.isCallExpression(node)) {
      const fnName = getCallExpressionName(node.expression);
      if (fnName && ['cn', 'clsx', 'classnames', 'cva', 'twMerge'].includes(fnName)) {
        node.arguments.forEach((arg) => extractFromExpression(arg, candidates));
      }
    }

    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
}

function getCallExpressionName(expression) {
  if (ts.isIdentifier(expression)) return expression.text;
  if (ts.isPropertyAccessExpression(expression)) return expression.name.text;
  return null;
}

function extractFromExpression(expression, candidates) {
  if (!expression) return;
  if (ts.isStringLiteral(expression) || ts.isNoSubstitutionTemplateLiteral(expression)) {
    addClassCandidates(expression.text, candidates);
  } else if (ts.isTemplateExpression(expression)) {
    addClassCandidates(expression.head.text, candidates);
    expression.templateSpans.forEach((span) => {
      addClassCandidates(span.literal.text, candidates);
      extractFromExpression(span.expression, candidates);
    });
  } else if (ts.isBinaryExpression(expression) && expression.operatorToken.kind === ts.SyntaxKind.PlusToken) {
    extractFromExpression(expression.left, candidates);
    extractFromExpression(expression.right, candidates);
  } else if (ts.isArrayLiteralExpression(expression)) {
    expression.elements.forEach((el) => extractFromExpression(el, candidates));
  } else if (ts.isObjectLiteralExpression(expression)) {
    expression.properties.forEach((prop) => {
      if (ts.isPropertyAssignment(prop) || ts.isShorthandPropertyAssignment(prop)) {
        if (prop.name) {
          if (ts.isStringLiteral(prop.name) || ts.isNoSubstitutionTemplateLiteral(prop.name)) {
            addClassCandidates(prop.name.text, candidates);
          } else if (ts.isComputedPropertyName(prop.name)) {
            extractFromExpression(prop.name.expression, candidates);
          }
        }
        if (ts.isPropertyAssignment(prop)) {
          extractFromExpression(prop.initializer, candidates);
        }
      } else if (ts.isMethodDeclaration(prop) && prop.name) {
        if (ts.isIdentifier(prop.name)) {
          addClassCandidates(prop.name.text, candidates);
        }
      }
    });
  } else if (ts.isConditionalExpression(expression)) {
    extractFromExpression(expression.whenTrue, candidates);
    extractFromExpression(expression.whenFalse, candidates);
  } else if (ts.isParenthesizedExpression(expression)) {
    extractFromExpression(expression.expression, candidates);
  } else if (ts.isCallExpression(expression)) {
    const fnName = getCallExpressionName(expression.expression);
    if (fnName && ['cn', 'clsx', 'classnames', 'cva', 'twMerge'].includes(fnName)) {
      expression.arguments.forEach((arg) => extractFromExpression(arg, candidates));
    }
  }
}

function addClassCandidates(value, candidates) {
  if (!value) return;
  const cleaned = value.replace(/[`\r\n\t]/g, ' ');
  for (const raw of cleaned.split(/\s+/)) {
    const trimmed = raw.trim();
    if (!trimmed) continue;
    const withoutImportant = trimmed.replace(/!important$/, '').replace(/!$/, '');
    if (!withoutImportant) continue;
    if (withoutImportant !== withoutImportant.toLowerCase()) continue;
    if (!/[0-9:\-\[\]\/\.]/.test(withoutImportant) && !SIMPLE_CLASS_ALLOWLIST.has(withoutImportant)) continue;
    if (!/^[a-z0-9@:_\-\[\]\/\.#!%\(\)]+$/i.test(withoutImportant)) continue;
    candidates.add(withoutImportant);
  }
}

function extractConfigSafelist(config, candidates) {
  const safelist = config?.safelist;
  if (!safelist) return;
  const values = Array.isArray(safelist) ? safelist : [safelist];
  for (const value of values) {
    if (typeof value === 'string') {
      candidates.add(value);
    } else if (value?.pattern instanceof RegExp) {
      // patterns are not supported without runtime context
    } else if (value?.variants) {
      // ignore complex safelist objects for now
    }
  }
}

function extractCandidates(config, cssInput, fromPath) {
  const candidates = new Set();
  const contentPatterns = normalizeContentArray(config?.content);
  const files = resolveFilePatterns(contentPatterns);
  extractCandidatesFromFiles(files, candidates);
  extractFromCss(cssInput, candidates);
  extractConfigSafelist(config, candidates);
  return candidates;
}

async function loadStylesheet(specifier, context = {}) {
  const fromDir = context.from ? path.dirname(context.from) : process.cwd();
  let resolved;
  const attempts = [];
  const tryResolve = (request) => {
    try {
      return require.resolve(request);
    } catch (error) {
      attempts.push(request);
      return null;
    }
  };

  if (specifier === 'tailwindcss') {
    resolved = tryResolve('tailwindcss/index.css');
  } else if (specifier.startsWith('tailwindcss/')) {
    resolved = tryResolve(`${specifier}.css`) ?? tryResolve(specifier);
  } else if (specifier.startsWith('.') || specifier.startsWith('/')) {
    const candidate = path.resolve(fromDir, specifier);
    resolved = fs.existsSync(candidate) ? candidate : null;
    if (!resolved && path.extname(candidate) === '') {
      const withCss = `${candidate}.css`;
      resolved = fs.existsSync(withCss) ? withCss : null;
    }
  } else {
    resolved = tryResolve(specifier) ?? tryResolve(`${specifier}.css`);
  }

  if (!resolved) {
    throw new Error(`Unable to resolve stylesheet import: ${specifier} (attempted ${attempts.join(', ')})`);
  }

  return fs.promises.readFile(resolved, 'utf8');
}

function createTailwindPlugin() {
  return {
    postcssPlugin: 'custom-tailwind',
    async Once(root, { result }) {
      const fromPath = result.opts.from ? path.resolve(result.opts.from) : undefined;
      const cssInput = root.toString();
      const config = loadTailwindConfig();
      const compiled = await tailwind.compile(cssInput, {
        config,
        from: fromPath,
        loadStylesheet,
      });
      const candidates = extractCandidates(config, cssInput, fromPath);
      const outputCss = compiled.build(candidates);
      const newRoot = postcss.parse(outputCss, { from: result.opts.from });
      root.removeAll();
      newRoot.each((node) => {
        root.append(node);
      });
    },
  };
}

createTailwindPlugin.postcss = true;

module.exports = { createTailwindPlugin };
