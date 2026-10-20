// prettier reads this file from the folder it runs in, options not listed keep prettier's defaults
export default {
    // longest line prettier aims for, longer code gets wrapped, matches backend ruff line-length
    // comments and strings are never wrapped, a long one stays long
    printWidth: 120,
    // no semicolon at the end of statements: `const a = 1` instead of `const a = 1;`
    semi: false,
    // single quotes for js strings: 'text' instead of "text", html attributes keep double quotes
    singleQuote: true,
    // no spaces inside object braces: {ref} instead of { ref }
    bracketSpacing: false,
    // a tag with 2+ attributes puts each attribute on its own line, a tag with 1 stays on one line
    singleAttributePerLine: true,
    // spaces per indent level in js and css
    tabWidth: 4,
    // per file type exceptions, each overrides the options above for the files it matches
    overrides: [
        // vue files indent with 2 spaces, as they do today
        {files: '*.vue', options: {tabWidth: 2}},
        // json indents with 2 spaces, as npm writes package.json
        {files: '*.json', options: {tabWidth: 2}},
    ],
}
