// groups rule lists per file type with files + extends, from the eslint package itself
import {defineConfig} from 'eslint/config'
// core js rules, provides js.configs.recommended: undefined vars, unused vars, unreachable code
import js from '@eslint/js'
// css language and rules, provides css.configs.recommended: invalid properties, empty blocks
import css from '@eslint/css'
// vue parser and style guide rules, provides pluginVue.configs['flat/recommended']
import pluginVue from 'eslint-plugin-vue'
// one config object that turns off every layout rule, so eslint and prettier never disagree
import prettierOff from 'eslint-config-prettier'
// lists of predefined names per environment, globals.browser stops "window is not defined" reports
import globals from 'globals'

// each entry applies to the files it lists, an entry without files applies to every file
// language: how eslint parses a file into a tree before rules walk it
// eslint's default language is '@/js' for every file (node_modules/eslint/lib/config/default-config.js)
export default defineConfig([
    {ignores: ['dist/']},
    // js and vue keep the default js language
    // vue's setup entry swaps in vue-eslint-parser for .vue, it reads <template> and <script setup>
    // flat/: the current eslint.config.js format, keys without it are for the old .eslintrc format
    // recommended: strictest of 3 vue levels, essential < strongly-recommended < recommended
    {
        files: ['**/*.{js,vue}'],
        extends: [js.configs.recommended, pluginVue.configs['flat/recommended']],
        languageOptions: {globals: globals.browser},
    },
    // css is not js, without language the js parser fails on the first {
    // 'css/css': <plugin name>/<language name>, plugin registered as css by css.configs.recommended
    {
        files: ['**/*.css'],
        language: 'css/css',
        extends: [css.configs.recommended],
        // --x variables live in variables.css, the rule reads one file at a time and can't see them
        // true: skip checks on values using var(--x), every other property is still checked
        rules: {'css/no-invalid-properties': ['error', {allowUnknownVariables: true}]},
    },
    // last: turns off the layout rules switched on by the lists above
    prettierOff,
])
