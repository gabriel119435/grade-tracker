# frontend basics

a cheat sheet for backend devs.
concepts go from simple to complex. examples are generic first. grade-tracker appears only when it helps.

---

# 1. what runs where

## browser and server

- the browser runs html (structure), css (looks) and js (behavior).
- the server does not run any of that: it only sends files and answers api calls.
- in production, this frontend is only static files: one `index.html`, some `.js`, some `.css`.
- nginx sends those files. flask answers `/api/...` calls.

## single page app

- classic website: every click asks the server for a new html page.
- single page app (spa): the server sends one html page, once. after that, js builds every screen.
- clicking a link only changes what js shows. no new page is downloaded.
- data comes from the api as json. js turns it into html.

## the language

- js is the only language browsers run. this project uses js. typescript (ts) is js plus types.
- a build step turns ts into js before the browser gets it.

## runtime

### what it is

- an engine executes js. every browser has one. chrome's is called v8.
- a runtime is an engine plus access to files, network and processes outside the browser.
- a runtime is not a language, not a library, not a server.

### why you need one

- your app code runs in the browser. surrounding tools do not: installing packages, dev server, tests, build.
- those tools are js programs that run on your machine.
- so you need a runtime on your machine and in the build. never in the browser.

### options

- node: supported by every tool and library, slower than bun.
- deno: ts, formatter, linter and tests built in, smaller ecosystem.
- bun: fast, runtime, package manager and test runner in one tool, younger, some node packages differ.
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

- npm: comes with node, zero setup, slower, big `node_modules`. this project uses npm.
- pnpm: fast, one shared store on disk, blocks undeclared deps, a few old tools expect the npm layout.
- yarn: good support for many packages in one repo, its major versions differ a lot.
- bun install: the fastest, best used with bun itself.
- all of them read `package.json` and use the same npm registry, each writes its own lock file.

### npm: files, commands and package.json

files:

- `package.json` = `pyproject.toml`: name, dependencies, scripts.
- `package-lock.json` = `uv.lock`: exact versions, pinned.
- `node_modules/` = `.venv/`: installed packages.

commands:

- `npm install` = `uv sync`: install from the manifest.
- `npm ci` = `uv sync --locked`: install exactly the lock, fail if it is out of date.
- `npm run dev` = `uv run python run.py`: run a named script.

`package.json` structure:

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
- `dependencies`: used by the app, they end up in the built files.
- `devDependencies`: only for building and testing, like `vite`; they never reach the browser.
- `^3.5.30` means 3.5.30 or any newer 3.x. the exact installed version is pinned in `package-lock.json`.

## build tool

### what it is

- it turns your source files into the files the browser gets.
- it also runs a local dev server while you code.

### why you need one

- browsers do not understand `.vue` files or ts. the build tool compiles them into plain js.
- real apps have many files, sending them one by one is slow.
- the build bundles them and makes production code smaller: no comments, short names, no unused code.
- maven does dependency management and building. in js those are split.
- the package manager manages dependencies, the build tool builds and packages.

### options

alternatives exist for flexibility or for speed.

- vite: fast dev server, simple config, default for vue, less flexible for unusual setups.
- webpack: most configurable, many plugins, slower, complex config.
- rspack: webpack compatible, faster, newer, smaller community.
- parcel: almost zero config, less control.

this project uses vite, the default for vue:

- `npm run dev` serves the app and forwards `/api` to flask.
- `npm run build` writes `dist/` for nginx.

## ui framework

### what it is

- a library that keeps the screen in sync with your data.
- you describe the screen from data once. when the data changes, the framework updates the page for you.

### why you need one

without a framework, every data change needs matching page code:

```js
count++
document.querySelector('#count').textContent = count
```

- every place that changes `count` must also update the page.
- forget one, and the screen shows stale data. with many values and screens, this gets hard fast.
- with a framework, you describe it once `<p>{{ count }}</p>`: change `count` anywhere, and the page follows.

### options

- vue: html-like templates plus reactive state. easy to start, official router and i18n, smaller job market.
- react: ui written as js functions (jsx), biggest ecosystem and job market, you pick every library.
- svelte: a compiler, tiny code in the browser. very little code to write, smaller ecosystem.
- angular: full framework with dependency injection, router, forms, http. all included, heavier, harder to learn.
- solid: react-like syntax, fine-grained updates. very fast, small ecosystem.
- vanilla: plain js, no framework. no dependencies, you update the html by hand, hard to scale.
- the framework is a library your code imports. the build tool only processes it. vite works with any of them.
- this project uses vue: html-like templates, easy to start, official router and i18n.

## rendering: where the html is built

### client side rendering (csr)

this project works this way.

1. nginx sends `index.html` with one empty `<div id="app">` plus the js files.
2. those js files hold two things: the vue library, and your components compiled from `.vue` files.
3. the browser runs them, the vue library calls your components to get the html for the current page.
4. vue puts that html inside the empty div. now the page has content.
5. later clicks change the screen without asking the server for pages.
6. the server never builds html. it only sends files and json.

### server side rendering (ssr)

1. the browser asks for a page, a server runs the same vue components for that request.
2. the server sends a complete html page, with the content already in it, the browser shows it right away.
3. hydration: the browser reruns the same components and attaches clicks and typing to that html.
4. from then on, the app works as a spa. later clicks do not ask the server for pages.

- ssr exists because the first screen appears faster; search engines see real content, not an empty div.
- it matters for public sites: shops, blogs, news.
- it costs a server running your components in production, usually node. more moving parts to deploy and debug.

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
- csr and a handwritten route list are enough for this project.

## summary: what is what

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

# 2. vue core

## views, components and layouts

every piece of screen is a `.vue` file. a file plays one of three roles:

- component: a small reusable piece, like a title or a button. lives in `components/`.
- view: a full page for one url, like a home page. lives in `views/`.
- layout: the frame around many views, like header and footer. lives in `layouts/`.

files used in this section and the router section:

```
src
|-- components
|   |-- PageTitle.vue
|-- views
|   |-- HomePage.vue
|   |-- AboutPage.vue
|-- layouts
|   |-- MainLayout.vue
|-- router
|   |-- index.js
|-- main.js
```

### component

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

### view using it

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

### layout

```vue
<!-- file: layouts/MainLayout.vue -->
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

- at `/about`, header and footer stay. the router swaps the view in `<RouterView/>`.
- `<p>home page content</p>` becomes `<p>about page content</p>`.
- header and footer are written once, in the layout. the title once, in the component.

## router

- an object from the `vue-router` package that maps urls to views.
- a spa has one html page, so the router picks the view for each url, without reloading.
- it is wired in two files. the router file lists the routes and exports the router:

```js
// file: src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
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

- `index.html` runs `main.js`, which imports the router, which imports the views.
- vite follows the same chain: it starts from `index.html` to serve (dev) or bundle into `dist/` (build).
- `RouterView` and `RouterLink` are fixed names registered by `vue-router`.

## template syntax

- the template is html with a few extras. the extras always contain js expressions.
- every name the template uses is declared or imported in the same file's `<script setup>`.

showing values, conditions and lists:

- `<p>{{ user.name }}</p>` -> shows a js value as text.
- `<input :placeholder="user.name"/>` -> makes the attribute value a js expression.
- `:placeholder` is short for `v-bind:placeholder`: `v-bind` binds an attribute to a js value.
- `<div :class="{active: isActive}">` -> adds the class `active` only while `isActive` is true.
- object syntax: each key is a class name, each value a condition, true adds the class, false removes it.
- hyphenated class names needs quotes: `{'app-select-placeholder': !selected}`
- `<p v-if="error">` -> exists only while true. false removes it. `<p v-else>` right after is the opposite.
- `<p v-show="error">` -> always exists, hidden with css while false. cheaper to toggle often.
- `<li v-for="item in items" :key="item.id">` -> one `<li>` per item. `:key` lets vue update only changed rows.

events sent by the browser:

- an event is a message the browser sends when something happens: a click, typing, a submit.
- the browser sends them by itself, hidden: your code only writes the receiving part.
- `const notesBox = document.querySelector('textarea')`: `notesBox` is a js variable holding the html `<textarea>`.
- `notesBox.addEventListener('input', handler)` -> receives: on typing, the browser calls `handler(e)`.
- `e` is the event object: `e.type` is `'input'`, `e.target` is the textarea, `e.target.value` is its text.
- copy typed text into `notes`: `notesBox.addEventListener('input', ($event) => { notes = $event.target.value })`.
- vue's short form: `@` receives an event, `<textarea @input="notes = $event.target.value"/>`.
- `@input` is short for `v-on:input`: `v-on` receives an event, `on` as in "on input, run this".
- read it as: when this `textarea` sends `input`, run the code after `=`. the tag is `textarea`, the event `input`.
- common ones: `click` (button), `input` (each keystroke), `submit` (form), `keydown` (a key).

reacting to events in a template:

- `<button @click="count++">` -> receives `click` event from the button, then runs `count++`.
- right side may be a function name: vue calls it with the event. `@input="onInput"` -> `onInput(e)`.
- right side may be a statement: vue runs it, `$event` holds the event. `@input="notes = $event.target.value"`.
- `<form @submit.prevent="save">` -> receives `submit` and calls `save`.
- `.prevent` cancels the browser's own reaction to `submit`: the page reload. the event and the receiver still run.

## reactivity

### ref

- declare a js variable, reference it in the template, when its value changes vue updates the screen.
- ref stores number, string, object, array. replacing the whole value, even with `null` or `[]`, stays reactive.
- in js just declare `const count = ref(0)` and any `count.value++` will update the screen.
- in the template: `<p>{{ count }}</p>`.
- in the template vue adds `.value` for you, for reading and writing: `@click="count++"` changes `count.value`.

### reactive

- wraps one object or array in a proxy. vue tracks only reads and writes that go through the proxy.
- usage `const state = reactive({user: null, loaded: false})`.
- taking out a primitive field (number, string, boolean) from proxy creates a copy that no longer updates.
- replacing the whole object also breaks it: the variable no longer holds the proxy.
- common advice: use `ref` by default. use `reactive` for a fixed shared object.

### computed

- a value recalculated when the refs it reads change.
- `const total = computed(() => price.value * quantity.value)`, given `price` and `quantity` are refs.
- only updated when someone reads `total`, so you cannot predict when it runs.
- so a computed must only return a value, never change other refs.

### watch

- runs an action (a side effect: api call, writing other refs) when a ref changes.
- practical example `watch(userId, async (newId, oldId) => {profile.value = await loadProfile(newId)})`.
- short form: `watch(watchedRef, callback)`.
- `callback` receives `(newValue, oldValue, onCleanup)`; it may ignore them.
- if `callback` calls `onCleanup(foo)`, vue runs `foo` right before the next `callback` run or on unmount.
- common advice: need a value: use `computed`. need to do something (api call, write other refs): use `watch`.

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

example: `<input @input="quantity = $event.target.value"/>` and `<p>{{ total }}</p>`.
`total` is computed from `price * quantity`.

- typing `5`: the browser sends `input`, the receiver runs `quantity = '5'`, in the script that's `quantity.value`.
- `total` and the render are marked outdated. the render goes in the queue.
- the render runs and reads `total`, which recalculates to a new number.
- vue changes only the text inside `<p>`. the browser draws it.

## parent and child

- components nest: a page contains a form, a form contains inputs.
- whoever writes a tag in its template is its parent: `GradeForm.vue` writes `<DateInput>`, so it's the parent.
- an html tag like `<input>` is the last level, the browser owns it.
- the parent keeps the single copy of shared data, only the owner writes it.
- example used below: `LoginForm.vue` (parent) uses `TextBox.vue` (child) twice, for username and for password.

two directions, four actions:

|            | child's script                             | parent's template            |
|------------|--------------------------------------------|------------------------------|
| prop, down | accepts it: `defineProps({label: String})` | sends it: `:label="caption"` |
| event, up  | sends it: `emit('typed', text)`            | receives it: `@typed="..."`  |

- `:` (short for `v-bind`) and `@` (short for `v-on`) only appear in the parent's template.
- `:` only sends props, `@` only receives events. it's the child's script that accepts props and sends events.

down: props

- the child accepts them in its script: `defineProps({label: String})`.
- the parent passes them: `<TextBox label="username"/>`, or `<TextBox :label="caption"/>` for a js value.
- props belong to the parent, the child only reads them.
- a child only knows its own prop names, never the parent's variable names.
- exception: `:` on an html tag sends an html attribute to the browser, not a prop.
- ex: `<input :placeholder="format"/>`: the browser already knows `placeholder`, no child accepts it.

up: events

- an event is a message going up, with a name and optional data.
- senders:
    - the browser, for html tags: typing in `<input>` sends `input`, no code needed.
    - a component, from its script: `emit('typed', 'john doe')`, names listed in `defineEmits(['typed'])`.
    - `defineModel`, hidden: `model.value = x` sends `update:modelValue` with `x`.
- receiver: the parent, in its template, with `@` on the child's tag: `<TextBox @typed="...">`.
- `$event` is the data that came with the event, here `'john doe'`.
- the code after `=` decides what to do with it:
    - store: `@typed="typedUsername = $event"`.
    - forward under a new name: `@typed="emit('nameChanged', $event)"`.
    - call a function: `@input="onInput"`, vue passes the data as the argument.
- several values: `emit('edit', 3, '7,5')`, the parent names them: `@edit="(id, text) => ..."`.
- with several values, `$event` holds only the first.
- rule: `@` always receives, `emit` always sends.

v-model: both directions in one attribute

- `v-model` adapts to what it is written on.
- on an html tag, it uses names the browser already has. ex: `<textarea v-model="notes"/>` is short for:
    - `:value="notes"` -> down: the textarea shows `notes`.
    - `@input="notes = $event.target.value"` -> up: on each keystroke the browser sends `input`, `notes` gets the text.
- other tags have other browser names: a checkbox uses `checked` and `change`, a select uses `value` and `change`.
- on a component, it uses vue's names instead: `modelValue` and `update:modelValue`, explained below.
- two ends of one connection: `v-model` goes in the parent's template, `defineModel` in the child's script.
- `<TextBox v-model="typedUsername"/>` is short for two parts:
- `:modelValue="typedUsername"` -> down: the box shows the parent's value.
- `@update:modelValue="typedUsername = $event"` -> up: a hidden receiver, the parent stores the typed text.
- in the child, `const model = defineModel()`: reading `model.value` gives the prop, assigning sends the event.
- the variable name `model` is free, the hidden names are fixed: prop `modelValue`, event `update:modelValue`.
- custom name, the child picks it, the parent uses it:
    - in `Parent.vue`: `<Child v-model:childVar="parentVar"/>`.
    - in `Child.vue`: `const childVar = defineModel('childVar')`.
- before `=`, `childVar` is fixed text: the child's name. in quotes, `parentVar` is js run in the parent: its variable.
- in templates, kebab-case and camelCase are the same name: `v-model:child-var` is `v-model:childVar`.
- grade-tracker writes kebab-case in templates and camelCase in scripts.
- `v-model` always replaces the whole value, so it can't change one key of an object the parent passed down.
- for that, the child emits the key and the value, the parent writes that key in its own variable.
- ex: `GradeForm.vue` emits `edit(sub.id, text)`, `GradesView.vue` writes `cellTexts[id] = text`.

slots, the parent puts its own html inside the child:

- a slot is a spot in the child's template where the parent can put its own html.
- the child marks the spot: `<label>{{ label }}</label><input/><slot/>`.
- the parent fills it between the tags: `<TextBox label="password">at least 8 chars</TextBox>`.
- the password box shows the hint under its input. the username box has nothing between its tags, so no hint.
- unlike a prop, a slot can hold any html: bold text, a link, another component.

down: an action, the parent runs a child function

- a prop is a value and an event goes up, neither can tell a child "run this now".
- the child opens a function: `defineExpose({focus})`, macro like `defineProps`, everything else stays hidden.
- the parent names the child tag: `<TextBox ref="nameBox"/>`.
- in its script: `const nameBox = useTemplateRef('nameBox')`, a ref from `'vue'`, holds the child once shown.
- then it calls `nameBox.value.focus()`, ex: focus the username box after a failed login.

grade-tracker examples:

- prop in `GradesView.vue`: `<GradeForm :categories="categories"/>`.
    - sends the category list down to child `GradeForm.vue`.
- event in `GradesView.vue`: `<GradeForm @submit="handleSubmit"/>`.
    - receives `submit` from child `GradeForm.vue`, no data comes with it, then calls `handleSubmit`.
- v-model in `GradesView.vue`: `<AppDropdown v-model="selectedStudentId"/>`.
    - down: child `AppDropdown.vue` shows the selected student.
    - up: picking a student sends its id up, `GradesView.vue` stores it in `selectedStudentId`.
    - a `watch` on `selectedStudentId` then loads that student's grades.
- slot in `TabLayout.vue`: `<AppTopBar>` with the teacher's tab links between its tags.
    - fills the `<slot/>` of child `AppTopBar.vue` with those links.
- action in `TeachersView.vue`: `<UserList ref="userList"/>`.
    - after a seed, calls `userList.value.load()`, opened by child `UserList.vue` with `defineExpose({load})`.
- full chain: `DateInput.vue` -> `GradeForm.vue` -> `GradesView.vue`:
    - up:
        - `DateInput` sets `model.value`, its `defineModel` sends `update:modelValue`.
        - `GradeForm`'s `v-model` receives it and sets `inputGradeDate`.
        - `inputGradeDate` is created from `defineModel('inputGradeDate')`, which sends `update:inputGradeDate`.
        - `GradesView`'s `v-model:input-grade-date` receives it and stores it in its own `inputGradeDate`.
    - down:
        - `GradesView`'s `v-model:input-grade-date` sends its `inputGradeDate` to `GradeForm`.
        - `GradeForm`'s `defineModel('inputGradeDate')` receives prop `inputGradeDate` into a variable.
        - `GradeForm`'s `<DateInput v-model="inputGradeDate">` sends it down as prop `modelValue`.
        - `DateInput`'s `defineModel` reads `modelValue` into `model`.

## async and await

- the same idea as python's `async` and `await`.
- js runs on one thread. a slow call, like a network request, returns a promise: a value that exists later.
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

# 3. app structure

## composables

- a composable is a `useSomething` js function bundling reactive state and logic, like a small service.
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

- data many screens need, like the logged-in user.
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
- same-origin requests send the session cookie by default, so the backend knows who is logged in.
- dev: vite forwards `/api` to flask. production: nginx does. one origin, so no cross origin setup.
- grade-tracker's `request.js` wraps every call, so each one returns either data or `{error: code}`.

---

# 4. css

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
- later layers come later and are more specific, so they win.
- grade-tracker's `style.css` imports the layers in this order.

## css variables

- `:root {--color-bg-action-0: #e8845a}` defines a token.
- `.btn-primary {background: var(--color-bg-action-0)}` uses it.
- `@media (max-width: 800px) {...}` holds narrow screen rules. variables work inside, not in the condition.
- css cannot color a `<canvas>`: chart.js paints pixels there with js.
- so the chart reads it in js: `getComputedStyle(document.documentElement).getPropertyValue('--color-b-2')`.
- `getComputedStyle` is a browser function, no import. `document.documentElement` is `<html>`, what `:root` targets.

---

# 5. tests

## vitest

- the test runner that pairs with vite. its api matches jest. `npm test` runs every `*.test.js` file.

```js
describe('add', () => {                // group named 'add': this function runs now and collects the tests
    it('returns the sum', () => {      // one test named 'returns the sum'
        expect(add(2, 3)).toBe(5)      // toBe compares plain values, toEqual compares inner fields
    })
})

it.each(['11', '-1', 'abc'])('rejects %j', (text) => {  // one test per input; %j shows it in the name
    expect(parseGrade(text, ',').valid).toBe(false)
})
```

## mocks

- a mock replaces a real module with a fake during a test, like mocking a repository.
- `vi.mock('./api.js', () => ({getUser: vi.fn()}))` -> every import of `./api.js` in the test gets the fake.
- the fake module starts empty. `{getUser: vi.fn()}` says it exports `getUser`, a fake function.
- `vi.fn()` records its calls. `getUser.mockResolvedValue({id: 1})` makes it return a promise with that value.
- grade-tracker's router test mocks the api and the router, so the navigation guard runs with no browser or network.
