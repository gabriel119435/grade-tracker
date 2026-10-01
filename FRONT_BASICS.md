# frontend basics

a cheat sheet for backend devs.
it assumes basic html, css and javascript (js), and nothing else.
concepts go from simple to complex.
examples are generic first. grade-tracker appears only when it helps.

---

# part a: what runs where

## browser and server

- the browser runs html (structure), css (looks) and js (behavior).
- the server does not run any of that.
- the server only sends files and answers api calls.
- in production, this frontend is only static files: one `index.html`, some `.js`, some `.css`.
- nginx sends those files. flask answers `/api/...` calls.

## single page app

- classic website: every click asks the server for a new html page.
- single page app (spa): the server sends one html page, once.
- after that, js builds every screen.
- clicking a link only changes what js shows. no new page is downloaded.
- data comes from the api as json. js turns it into html.

## the language

- js is the only language browsers run. this project uses js.
- typescript (ts) is js plus types.
- a build step turns ts into js before the browser gets it.
- backend analogy: like python type hints, but checked at build time.

## runtime

### what it is

- an engine executes js. every browser has one. chrome's is called v8.
- an engine inside a browser can only touch the page. no files, no processes.
- a runtime is an engine plus access to files, network and processes, outside the browser.
- backend analogy: the python interpreter.
- a runtime is not a language, not a library, not a server.
- it can run a server if you write one, like python can run flask.

### why you need one

- your app code runs in the browser.
- the surrounding tools do not: installing packages, the dev server, tests, the build.
- those tools are js programs that run on your machine.
- so you need a runtime on your machine and in the build. never in the browser.

### options

alternatives exist mainly for speed and for built-in tools.

- node: supported by every tool and library; but slower than bun.
- deno: ts, formatter, linter and tests built in; but smaller ecosystem.
- bun: very fast, runtime, package manager and test runner in one tool; but younger, some node packages differ.
- node is the safe default. here, it runs only on your machine and in the docker build, never in production.

## package manager

### what it is

- it installs the libraries (packages) your project declares, plus what they depend on, like uv for python.
- it reads a manifest, writes a lock file and fills a local folder.
- packages come from a registry. npmjs.com is the shared public registry for js.

### why you need one

- the app needs packages: `vue` (framework), `vue-router` (pages), `vue-i18n` (languages), `chart.js` (charts).
- each of those needs other packages, at compatible versions.
- installing and pinning all of that by hand is not practical.

### options

alternatives exist mainly for install speed and disk space.

- npm: comes with node, zero setup; but slower, big `node_modules`. this project uses npm.
- pnpm: fast, one shared store on disk, blocks undeclared deps; but a few old tools expect the npm layout.
- yarn: good support for many packages in one repo; but its major versions differ a lot.
- bun install: the fastest; but best used with bun itself.
- all of them read `package.json` and use the same npm registry.
- each writes its own lock file. a project should pick one.

### npm: files, commands and package.json

files:

- `package.json` = `pyproject.toml`: name, dependencies, scripts.
- `package-lock.json` = `uv.lock`: exact versions, pinned.
- `node_modules/` = `.venv/`: installed packages.

commands:

- `npm install` = `uv sync`: install from the manifest.
- `npm ci` = `uv sync --locked`: install exactly the lock, fail if it is out of date.
- `npm run dev` = `uv run python run.py`: run a named script.

sections inside `package.json`:

```json
{
  "scripts": {
    "dev": "vite"
  },
  "dependencies": {
    "vue": "^3.5.30"
  },
  "devDependencies": {
    "vite": "^8.0.0"
  }
}
```

- `scripts`: named commands. `npm run dev` runs `vite`.
- `dependencies`: used by the app. ends up in the built files.
- `devDependencies`: only to build and test. never reaches the browser.
- `^3.5.30` means 3.5.30 or any newer 3.x.
- the exact installed version is pinned in `package-lock.json`.

## mixing runtimes and package managers

- mostly works.
- the package manager fills `node_modules/`. the runtime reads it.
- node works with npm, pnpm, yarn and bun install.
- bun works with all of them too.
- deno reads `package.json` and `node_modules/`, with some edge cases.
- common pairs: node + npm (default), node + pnpm, bun + bun.

## build tool

### what it is

- it turns your source files into the files the browser gets.
- it also runs a local dev server while you code.

### why you need one

- browsers do not understand `.vue` files or ts. the build tool compiles them into plain js.
- browsers do not understand imports by package name, like `import 'vue'`.
- a real app has hundreds of small files. sending each one is slow.
- production files should be small: no comments, short names, no unused code.
- maven does dependency management and building. in js those are split.
- the package manager manages dependencies, the build tool builds and packages.

### options

alternatives exist for flexibility or for speed.

- vite: fast dev server, simple config, default for vue; but less flexible for unusual setups.
- webpack: most configurable, many plugins; but slower, complex config.
- rspack: webpack compatible, faster; but newer, smaller community.
- parcel: almost zero config; but less control.

this project uses vite, the default for vue:

- `npm run dev` serves the app and forwards `/api` to flask.
- `npm run build` writes `dist/` for nginx.

## ui framework

### what it is

- a library that keeps the screen in sync with your data.
- you describe the screen from data once.
- when the data changes, the framework updates the page for you.

### why you need one

without a framework, every data change needs matching page code:

```js
count++
document.querySelector('#count').textContent = count
```

- every place that changes `count` must also update the page.
- forget one, and the screen shows stale data.
- with many values and screens, this gets hard fast.

with a framework, you describe it once:

```vue
<p>{{ count }}</p>
```

- change `count` anywhere, and the page follows.

### options

- vue: html-like templates plus reactive state. easy to start, official router and i18n; but smaller job market.
- react: ui written as js functions (jsx). biggest ecosystem and job market; but you pick every library.
- svelte: a compiler, tiny code in the browser. very little code to write; but smaller ecosystem.
- angular: full framework with dependency injection, router, forms, http. all included; but heavier, harder to learn.
- solid: react-like syntax, fine-grained updates. very fast; but small ecosystem.
- vanilla: plain js, no framework. no dependencies; but you update the html by hand, hard to scale.
- the framework is a library your code imports. the build tool only processes it. vite works with any of them.
- this project uses vue: html-like templates, easy to start, official router and i18n. part b explains it.

## rendering: where the html is built

### client side rendering (csr)

this project works this way.

1. nginx sends `index.html` with one empty `<div id="app">`, plus the js files.
2. those js files hold two things: the vue library, and your components compiled from `.vue` files.
3. the browser runs them, the vue library calls your components to get the html for the current page.
4. vue puts that html inside the empty div. now the page has content.
5. later clicks change the screen without asking the server for pages.
6. the server never builds html. it only sends files and json.

### server side rendering (ssr)

1. the browser asks for a page, a server runs the same vue components for that request.
2. the server sends a complete html page, with the content already in it, the browser shows it right away.
3. hydration: then the browser runs the same components again and attaches clicks and typing to the html already there.
4. from then on, the app works as a spa. later clicks do not ask the server for pages.

backend analogy: jsp:

- same as jsp: the server fills templates and sends finished html.
- different from jsp: with jsp, every click asks the server for a new page.
- with ssr, only the first page comes from the server. after hydration, the browser takes over.

why ssr exists:

- the first screen appears faster; search engines see real content, not an empty div.
- it matters for public sites: shops, blogs, news.

the cost:

- a server must run your components in production, usually node.
- more moving parts to deploy and debug.

### routes: handwritten or file based

- handwritten: you list every url and its component.
- this project does it in `router/index.js`: `'/teacher/grades'` maps to `TeacherGradesView`.
- file based: the folder layout is the route list.
- a file at `pages/teacher/grades.vue` becomes the url `/teacher/grades` by itself.
- vue-router alone is handwritten.

### meta frameworks

- a meta framework sits on top of a ui framework.
- it adds ssr, file based routes and more.
- nuxt for vue. next.js for react. sveltekit for svelte.
- this project uses none. it is a logged in app: no need for search engines, and flask is the backend.
- so csr and a handwritten route list are enough.

## summary: what is what

format: layer: what this project uses, its role; others.

- language: js, the code you write; others: ts (compiles to js).
- runtime: node, runs tools on your machine and in the build; others: deno, bun.
- package manager: npm, installs dependencies; others: pnpm, yarn, bun.
- build tool: vite, dev server and production build; others: webpack, rspack, parcel.
- ui framework: vue, components and reactive state; others: react, svelte, angular, solid.
- test runner: vitest, runs unit tests; others: jest.
- production server: nginx, serves `dist/` and proxies `/api`; others: caddy, apache, any static host.

## startup sequence

1. the browser asks nginx for `/`. nginx sends `index.html`.
2. `index.html` has one empty `<div id="app"></div>`.
3. `index.html` loads `main.js`, which creates the vue app and plugs in the router and translations.
4. `main.js` mounts the app into that div; the router looks at the url and picks a component.
5. vue renders that component into the div; from now on, js owns the screen.

---

# part b: vue core

## views, components and layouts

every piece of screen is a `.vue` file. a file plays one of three roles:

- component: a small reusable piece, like a title or a button. lives in `components/`.
- view: a full page for one url, like a home page. lives in `views/`.
- layout: the frame around many views, like header and footer. lives in `views/`.

technically all three are the same thing. only the job differs.

files used in this section and the router section:

```
src
|__ components
|   |__ PageTitle.vue
|__ views
|   |__ HomePage.vue
|   |__ MainLayout.vue
|   |__ AboutPage.vue
|__ router
|   |__ index.js
|__ main.js
```

### a component

a `.vue` file has up to three parts: script, template, style.

```vue
<!-- file: components/PageTitle.vue -->
<script setup>
// logic: runs once when the component is created
const content = 'page title content'
</script>

<template>
  <!-- html: what the component shows -->
  <h1>{{ content }}</h1>
</template>

<style>
/* optional css */
h1 {
    color: gray;
}
</style>
```

- everything declared in `<script setup>` can be used in the template.

### a view using it

```vue
<!-- file: views/HomePage.vue -->
<script setup>
import PageTitle from '../components/PageTitle.vue'
</script>

<template>
  <PageTitle/>
  <p>home page content</p>
</template>
```

- `<PageTitle/>` is replaced by what `PageTitle.vue` shows. any view can use it; it is written once.
- each tag is its own copy (an instance), with its own state.

### a layout

```vue
<!-- file: views/MainLayout.vue -->
<template>
  <header>
    <RouterLink to="/home">home link</RouterLink>
    <RouterLink to="/about">about link</RouterLink>
  </header>
  <RouterView/>
  <footer>main layout content</footer>
</template>
```

- the layout looks almost empty on purpose. its only job is the frame.
- `<RouterLink>` is a menu link. `<RouterView/>` is the hole where the current view goes.
- both come from the router, next section.

### what the browser shows

at `/home`:

```html
<header>
    <a href="/home">home link</a>
    <a href="/about">about link</a>
</header>
<h1>page title content</h1>
<p>home page content</p>
<footer>main layout content</footer>
```

- at `/about`, header and footer stay. the router swaps the view in `<RouterView/>`
- `<p>home page content</p>` becomes `<p>about page content</p>`.
- header and footer are written once, in the layout. the title once, in the component.

## router

- an object from the `vue-router` package that maps urls to views.
- a spa has one html page, so the router picks the view for each url, without reloading.
- it is wired in two files. the router file lists the routes and exports the router:

```js
// file: src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import MainLayout from '../views/MainLayout.vue'
import HomePage from '../views/HomePage.vue'
import AboutPage from '../views/AboutPage.vue'

const routes = [
    {
        path: '/',
        component: MainLayout,
        children: [
            {path: 'home', component: HomePage},
            {path: 'about', component: AboutPage},
        ]
    },
]

export default createRouter({history: createWebHistory(), routes})
```

`main.js` imports it by path and plugs it into the app:

```js
// file: src/main.js
import {createApp} from 'vue'
import App from './App.vue'
import router from './router/index.js'

createApp(App).use(router).mount('#app')
```

- the browser loads `index.html`, whose `<script>` runs `main.js`, which imports the router, which imports the views.
- vite follows the same chain: it starts from `index.html` to serve (dev) or bundle into `dist/` (build).
- `RouterView` and `RouterLink` are fixed names registered by `vue-router`.

## template syntax

- the template is html with a few extras.
- the extras always contain js expressions.
- names like `user`, `items` or `save` come from the component's `<script setup>`.

showing values, conditions and lists:

- `<p>{{ user.name }}</p>` -> shows a js value as text.
- `<input :placeholder="user.name"/>` -> makes the attribute value a js expression.
- `<div :class="{active: isActive}">` -> adds the class `active` only while `isActive` is true.
- `<p v-if="error">` -> exists only while true. false removes it. `<p v-else>` right after is the opposite.
- `<p v-show="error">` -> always exists, hidden with css while false. cheaper to toggle often.
- `<li v-for="item in items" :key="item.id">` -> one `<li>` per item. `:key` lets vue update only changed rows.

events sent by the browser:

- an event is a message the browser sends when something happens: a click, typing, a submit.
- `input.addEventListener('input', handler)` -> on typing, the browser calls `handler`, passing the event object.
- in `handler(e)`, `e.type` is `'input'`, `e.target` is the input text box, `e.target.value` is its text.
- plain js, copy typed text into `text`: `input.addEventListener('input', ($event) => { text = $event.target.value })`.
- vue's short form is `<input @input="text = $event.target.value"/>`. vue writes the js above for you.

events sent by your components:

- components send their own events with `emit`. the value sent becomes `$event`.
- the child calls `emit('typed', 'john doe')`, the parent has `<TextBox @typed="typedUsername = $event"/>`.

reacting to events in a template:

- `<button @click="count++">` -> runs js when the event fires.
- `<form @submit.prevent="save">` -> `.prevent` stops the browser's page reload and calls `save` instead.
- `<input v-model="text"/>` -> two-way: shows `text`, typing writes back.

## reactivity

### ref

- declare a js variable, reference it in the template, when its value changes vue updates the screen.
- ref stores number, string, object, array. replacing the whole value, even with null or [], stays reactive.
- in js just declare `const count = ref(0)` and any `count.value++` will update the screen.
- in the template, no `.value`: `<p>{{ count }}</p>`.

### reactive

- wraps one object or array in a proxy. vue tracks only reads and writes that go through the proxy.
- passing a primitive field (number, string, boolean) copies it, so it stops updating.
- replacing the whole object also breaks it: the variable no longer holds the proxy.
- usage `const state = reactive({user: null, loaded: false})`.
- common advice: use `ref` by default. use `reactive` for a fixed shared object.

### computed

- a value recalculated when the refs it reads change.
- `const total = computed(() => price.value * quantity.value)`, given `price` and `quantity` are refs.
- only updated when someone reads `total`, so you cannot predict when it runs.
- so a computed must only return a value, never change other refs.

### watch

- runs an action (a side effect: api call, writing other refs) when a ref changes.
- `watch(userId, async (newId, oldId) => {profile.value = await loadProfile(newId)})`.
- need a value: use `computed`. need to do something (api call, write other refs): use `watch`.

### watchEffect

- a trigger without a named source. it watches whatever refs it reads.
- `watchEffect(() => {document.title = pageTitle.value})`.
- runs once, and again whenever a ref it read changes.

## how updates reach the screen

- at build time, each template becomes a js function: the render function.
- rendering: vue calls it, gets a description of the html, and creates the real elements.
- while a render or a computed runs, vue records every ref it reads.
- when a ref changes, everything that read it is marked outdated.
- outdated renders wait in a queue. when the current code finishes, each component renders once.
- vue compares the new description with the old one and changes only what differs. then the browser draws.
- nobody writes this by hand. it is vue code running in the browser.

example: `<input v-model="quantity"/>`, `<p>{{ total }}</p>`, and `total` computed from `price * quantity`.

- typing `5` fires an input event. `v-model` sets `quantity.value` to 5.
- `total` and the render are marked outdated. the render goes in the queue.
- the render runs and reads `total`, which recalculates to a new number.
- vue changes only the text inside `<p>`. the browser draws it.

## parent and child

- components nest: a page contains a form, a form contains inputs.
- the parent keeps the single copy of shared data. it needs it all together to validate, save or reset.
- data goes down to the child as props. news goes up to the parent as events.
- example: `LoginForm.vue` (parent) uses `TextBox.vue` (child) twice, for username and for password.

props, data down:

- the child declares them in its script: `defineProps({label: String})`.
- `label` is the caption above the text input box.
- the parent passes them: `<TextBox label="username"/>` and `<TextBox label="password"/>`.
- props belong to the parent. the child must not change them.

events, news up:

- component events are named freely, like `typed`. browser events, like `input`, have a fixed list.
- the child declares them: `const emit = defineEmits(['typed'])`.
- the child sends the typed text on each keystroke: `<input @input="emit('typed', $event.target.value)"/>`.
- the parent stores it: `<TextBox label="username" @typed="typedUsername = $event"/>`. `$event` is the text sent.
- the label stays "username", js variable `typedUsername` is updated.

`v-model` on a component:

- `<TextBox v-model="typedUsername"/>` is short for two parts, one per direction:
- `<TextBox :modelValue="typedUsername"/>` -> down: a prop. the box shows the parent's value.
- `<TextBox @update:modelValue="typedUsername = $event"/>` -> up: an event. the parent stores the typed text.
- the child must use these exact names: the prop `modelValue` and the event `update:modelValue`.

slots, the parent puts its own html inside the child:

- a slot is a spot in the child's template where the parent can put its own html.
- the child marks the spot: `<label>{{ label }}</label><input/><slot/>`.
- the parent writes the content between the child's tags: `<TextBox label="password">at least 8 characters</TextBox>`.
- the password box shows the hint under its input. the username box has nothing between its tags, so no hint.
- unlike a prop, a slot can hold any html: bold text, a link, another component.

grade-tracker examples, one of each:

- prop: `<GradeForm :categories="categories"/>` -> the grades page passes its category list down to the form.
- event: `<GradeForm @submit="handleSubmit"/>` -> on "save grades", the form sends `submit`. the page saves.
- v-model: `<AppDropdown v-model="selectedStudentId"/>`
    - down: the dropdown shows the currently selected student.
    - up: picking a student sends its id to the page, which loads that student's grades.
- slot: `<AppTopBar>` has a `<slot/>`. `TabLayout.vue` fills it with the teacher's tab links.

## async and await

- the same idea as python's `async` and `await`.
- the browser runs js on one thread. a slow call, like a network request, returns a promise: a value that exists later.
- `await` pauses the function until the promise is done. the page keeps responding meanwhile.
- an `async` function always returns a promise. `Promise.all([a(), b()])` waits for both, like `asyncio.gather`.
- never block with a busy loop: the whole page freezes.
- example: `const response = await fetch('/api/items')`, then `items.value = await response.json()`.

## lifecycle

a component is created, shown, updated and removed:

- created: `<script setup>` runs once, top to bottom. refs, computed and watches are set up here.
- mounted: the html is in the page. `onMounted(load)` runs your `load` function now, usually to fetch data.
- updated: re-rendered after reactive changes, as often as needed.
- unmounted: removed from the page, because `v-if` became false or the route changed.
- `onUnmounted(() => clearInterval(timer))` -> cleanup: stop timers or listeners, for example.
- `onMounted` and `onUnmounted` are imported from vue, like `ref`.

---

# part c: app structure

## composables

- a composable is a plain js function named `useSomething`. it bundles reactive state and logic, like a small service.
- a component calls it in `<script setup>` and uses what it returns: `const {own, shared} = useCounter()`.
- where a ref is declared decides who shares it:

```js
// file: composables/useCounter.js
import {ref} from 'vue'

// outside the function: one copy, shared by every caller (a singleton)
const shared = ref(0)

export function useCounter() {
    // inside the function: a new copy for each caller
    const own = ref(0)
    return {own, shared}
}
```

- grade-tracker: `useLoading` is per caller. `useToast` and `useConfirm` are singletons.

## global state

- data many screens need, like the logged in user.
- simplest: one `reactive` object in its own file, imported where needed. grade-tracker's `store.js` does this.
- singleton composables also work. pinia, vue's official store library, adds tools and structure for big apps.

## directives

- a directive is reusable behavior for an html element, used as a `v-` attribute.
- built in: `v-if`, `v-for`, `v-model`, `v-show`.
- custom: an object with hooks vue calls for the element: `mounted`, `updated`, `unmounted`.
- `export const autofocus = {mounted(el) { el.focus() }}` -> focuses the element when it appears.
- `mounted(el) { el.focus() }` is shorthand for `mounted: function (el) { el.focus() }`.
- `function` is js's keyword for defining a function, like python's `def`.
- register it in `main.js` with `.directive('autofocus', autofocus)`, then use `<input v-autofocus/>`.
- grade-tracker's `v-click-outside` closes a dropdown when you click anywhere else.

## translations

- each language is a file of keys and texts: `pt-br.js` has `{login: {submit: 'entrar'}}`.
- `t('login.submit')` -> `'entrar'`. `t('students.grade_count', {n: 3})` with `'{n} notas'` -> `'3 notas'`.
- the current language is reactive: switching it re-renders every text.

## talking to the backend

- `fetch(url, options)` is the browser's http client. it returns a promise.
- `credentials: 'include'` sends the session cookie, so the backend knows who is logged in.
- dev: vite forwards `/api` to flask. production: nginx does. one origin, so no cross origin setup.
- grade-tracker's `request.js` wraps every call, so each one returns either data or `{error: code}`.

---

# part d: css

## cascade and specificity

- many rules can match one element. the winner is picked by specificity, then by order.
- `<button id="save" class="btn-primary" style="background: red">` can be styled 4 ways, weakest to strongest:
  tag `button {...}`, class `.btn-primary {...}`, id `#save {...}`, inline `style`. inline wins: it is red.
- same specificity: the later rule wins.

## global vs scoped styles

- global: every rule applies to the whole page.
- scoped: `<style scoped>` in a `.vue` file only hits that component.
- grade-tracker uses global css only, organized with itcss.

## itcss: inverted triangle css

- orders css files from broad and weak to narrow and strong, like a triangle upside down.
- the layers, in import order:
    - settings: variables only, like colors, spacing, sizes.
    - generic: removes the browser's default styles from every element (`*`), like `* {margin: 0}`.
    - elements: bare tags, for every page, like `button` and `input`.
    - layout: page structure, like stacks, rows and cards.
    - components: one ui piece each, like dropdown or toast.
    - views: one specific page, like login or grades.
    - overrides: exceptions that must win, like mobile adjustments.
- later layers come later and are more specific, so they win without `!important`.
- grade-tracker's `style.css` imports the layers in this order.

## css variables

- `:root {--color-action: #e8845a}` defines a design token. `.btn-primary {background: var(--color-action)}` uses it.
- `@media (max-width: 800px) {...}` holds rules for narrow screens. variables work in those rules, not in the condition.
- css cannot color a `<canvas>`: chart.js paints pixels there with js.
- so the chart reads the color in js: `getComputedStyle(document.documentElement).getPropertyValue('--color-action')`.
- `getComputedStyle` is a browser function, no import. `document.documentElement` is `<html>`, what `:root` targets.

---

# part e: tests

## vitest

- the test runner that pairs with vite. its api matches jest. `npm test` runs every `*.test.js` file.
- `describe('add', () => { it('returns the sum', () => { expect(add(2, 3)).toBe(5) }) })`
- `'add'` names the group, `'returns the sum'` names the test. both are only labels in the test report.
- `toBe` compares plain values. `toEqual` compares objects field by field. `it.each([...])` runs one test per input.

## mocks

- a mock replaces a real module with a fake during a test, like mocking a repository.
- `vi.mock('./api.js', () => ({getUser: vi.fn()}))` -> every import of `./api.js` in the test gets the fake.
- the fake module starts empty. `{getUser: vi.fn()}` says it exports `getUser`, a fake function.
- `vi.fn()` records its calls. `getUser.mockResolvedValue({id: 1})` makes it return a promise with that value.
- grade-tracker's router test mocks the api and the router, so the navigation guard runs with no browser or network.
