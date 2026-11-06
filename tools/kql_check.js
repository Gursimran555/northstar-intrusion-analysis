// Parse and type-check .kql files with Microsoft's Kusto.Language
// (npm: @kusto/language-service-next) against tools/kql_schemas.json.
// Catches syntax errors, unknown columns/tables and type mismatches.
// It does not run the queries.
//
//   node tools/kql_check.js hunting/*.kql hunting/original/*.kql
global.Bridge = require('@kusto/language-service-next/bridge.js');
require('@kusto/language-service-next/Kusto.Language.Bridge.js');
const fs = require('fs');
const path = require('path');
const K = Kusto.Language;
const S = K.Symbols;

const schemas = JSON.parse(fs.readFileSync(path.join(__dirname, 'kql_schemas.json'), 'utf8'));
const tables = Object.entries(schemas)
  .filter(([name]) => !name.startsWith('_'))
  .map(([name, schema]) => S.TableSymbol.From(schema).WithName(name));
const globals = K.GlobalState.Default.WithDatabase(new S.DatabaseSymbol.ctor('sentinel', tables));

let failed = 0;
for (const file of process.argv.slice(2)) {
  const text = fs.readFileSync(file, 'utf8');
  const code = K.KustoCode.ParseAndAnalyze(text, globals);
  const diags = code.GetDiagnostics();
  const errors = [];
  for (let i = 0; i < diags.Count; i++) {
    const d = diags.getItem(i);
    if (d.Severity === 'Error') {
      const line = text.slice(0, d.Start).split('\n').length;
      errors.push(`  line ${line}: ${d.Message}`);
    }
  }
  console.log(`${errors.length ? 'FAIL' : 'ok  '} ${file}`);
  errors.forEach(e => console.log(e));
  failed += errors.length ? 1 : 0;
}
process.exit(failed ? 1 : 0);
