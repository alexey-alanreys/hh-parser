import js from '@eslint/js';
import { defineConfig, globalIgnores } from 'eslint/config';
import prettier from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import unusedImports from 'eslint-plugin-unused-imports';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default defineConfig([
  js.configs.recommended,

  // Type-aware rules (no-floating-promises etc.) need parser type info.
  ...tseslint.configs.recommendedTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  prettier,

  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },

    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'simple-import-sort': simpleImportSort,
      'unused-imports': unusedImports,
    },

    settings: {
      react: { version: 'detect' },
    },

    rules: {
      /* ------------------------------------------------------------------ */
      /* TypeScript                                                          */
      /* ------------------------------------------------------------------ */

      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'separate-type-imports' },
      ],

      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/await-thenable': 'error',
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': [
        'warn',
        { allowExpressions: true },
      ],

      /* ------------------------------------------------------------------ */
      /* React / JSX                                                         */
      /* ------------------------------------------------------------------ */

      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules, // React 17+ JSX transform — no need to import React per file
      ...reactHooks.configs.recommended.rules,

      'react/jsx-sort-props': [
        'warn',
        {
          reservedFirst: true,
          callbacksLast: true,
          shorthandFirst: true,
          ignoreCase: true,
        },
      ],

      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],

      /* ------------------------------------------------------------------ */
      /* Imports                                                             */
      /* ------------------------------------------------------------------ */

      // No path aliases in this project — groups are flat, no @/shared|blocks|elements tiers.
      'simple-import-sort/imports': [
        'error',
        {
          groups: [
            ['^node:'],
            ['^react', '^@?\\w'],
            ['^\\.\\.(?!/?$)', '^\\.\\./?$'],
            ['^\\./(?=.*/)(?!/?$)', '^\\.(?!/?$)', '^\\./?$'],
            ['^.+\\.css$'],
          ],
        },
      ],
      'simple-import-sort/exports': 'error',

      /* ------------------------------------------------------------------ */
      /* Unused                                                              */
      /* ------------------------------------------------------------------ */

      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        { varsIgnorePattern: '^_', argsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-unused-vars': 'off', // delegated to unused-imports
    },
  },

  globalIgnores([
    'dist/**',
    'coverage/**',
    'node_modules/**',
    'vite.config.ts',
    'eslint.config.mjs',
  ]),
]);
