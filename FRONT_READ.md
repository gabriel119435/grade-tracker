# frontend reading order

a beginner's guide to the frontend codebase, ordered from simple to complex.
each new file builds on what came before; read them in order for the most coherent picture.

- **entry point**
    - `package.json`: project name, dependencies, and dev scripts
    - `vite.config.js`: build tool and dev server config; includes the proxy that forwards `/api` calls to the flask
    - `index.html`: the html shell the browser loads; the single `<div id="app">` the vue instance mounts into
- **base**: the foundational files that wire the whole app together
    - **scaffold**
        - `main.js`: creates and mounts the vue app; registers the router, i18n, and global directives
        - `App.vue`: root component; a single `<RouterView/>` with no logic
        - `store.js`: global session state: current user, role, and available locales
        - `i18n.js`: vue-i18n setup; the `t()` function all components use for english and portuguese translations
        - `locales/en.js`: all english translation strings
        - `locales/pt-br.js`: portuguese translation strings; same keys as en.js
        - `router/index.js`: all app routes and the auth guard that enforces role-based access on every navigation
    - **api**: one thin file per backend resource, all built on top of `request.js`
        - `api/request.js`: the single http function all api calls go through; normalizes failure responses
        - `api/routes/auth.js`: login, logout, locale change, admin password, and session check
        - `api/routes/students.js`: get, create, and delete students
        - `api/routes/teachers.js`: get, create, and delete teachers
        - `api/routes/categories.js`: get, create, and delete categories and subcategories
        - `api/routes/grades.js`: save grades (upsert + delete in one call) and get a student's grade history
    - **composables**: reusable reactive logic; each file owns one self-contained concern
        - `composables/generic/useLoading.js`: tracks in-flight async state; prevents double-submission
        - `composables/generic/useToast.js`: app-wide notification: one shared message, auto-dismissed after 4 seconds
        - `composables/generic/useConfirm.js`: two-click confirmation state for delete actions
    - **directives**
        - `directives/clickOutside.js`: calls handler when clicked outside registered element; used by AppDropdown
- **css**: global stylesheet following ITCSS; each layer can override the one above
    - `style.css`: the single import file that loads every css layer in ITCSS order
    - **settings**
        - `styles/settings/variables.css`: every design token in one place: colors, spacing, font sizes, borders etc
    - **generic**
        - `styles/generic/reset.css`: clears browser defaults and sets the base body font, color, background, and
          centering
    - **elements**
        - `styles/elements/buttons.css`: all button variants: primary, danger, danger-confirm, group and ghost
        - `styles/elements/inputs.css`: base input styles and the `.field-error` validation message class
    - **layout**
        - `styles/layout/structure.css`: the structural containers used across all views: stacks, rows, cards, and forms
    - **components**
        - `styles/components/user-list.css`: username and grade count display inside list rows
        - `styles/components/top-bar.css`: three-column nav grid, tab link styles, and active tab highlight
        - `styles/components/toast.css`: fixed bottom-center notification pill with fade transition
        - `styles/components/dropdown.css`: custom select trigger, floating option list, and open/hover states
        - `styles/components/grade-input.css`: grade input cell with state-color backgrounds and focus ring
        - `styles/components/grade-charts.css`: history card, category cards, chart cards, and subcategory badges
    - **views**
        - `styles/views/login.css`: viewport-centered login card
        - `styles/views/teacher-grades.css`: student selector row, grade input form card, date field, and category
          blocks
        - `styles/views/categories.css`: category header and subcategory form alignment
    - **overrides**
        - `styles/overrides/mobile.css`: responsive adjustments for narrow screens
- **vue**: components split by kind; shared components are read before the views that depend on them
    - **utils**
        - `utils/dateUtils.js`: date parsing, validation, and conversion between ISO and locale display format
        - `utils/gradeUtils.js`: grade normalization, localization, truncating, validation, and classification helpers
        - `utils/translateError.js`: maps a backend error code to the current locale string
        - `utils/credentialValidation.js`: username and password input validation helpers
    - **components**
        - `components/AppToast.vue`: renders the useToast message with a fade transition
        - `components/AppTopBar.vue`: the nav bar shown on every page; accepts a slot for tab links
        - `components/AppDropdown.vue`: custom styled select; manages open state and outside-click detection
        - `components/GradeInput.vue`: a single grade input cell; reflects the change state as a css class
        - `components/DateInput.vue`: date input with locale-aware display and real-time validation
        - `components/GradeLimitControls.vue`: the grade history limit button group; highlights the active limit
        - `components/GradeForm.vue`: the full grade input form; used only in the teacher grades view
    - **composables**
        - `composables/grades/useLimit.js`: the selected grade history count and the predefined limit options
        - `composables/grades/useGradesLoader.js`: shared grade fetch with built-in error handling; used by both grade
          views
        - `composables/grades/useGrades.js`: all grade state: loads grades, prefills input, compute cell states, and
          builds the save payload
    - **charts**
        - `components/GradeChart.vue`: a single chart.js line chart for one subcategory
        - `components/GradeCharts.vue`: all category and subcategory charts with collapsible categories; accepts a
          `#controls` slot for the limit controls
    - **views**
        - **login**
            - `views/LoginView.vue`: login form; the simplest full page in the app
        - **layouts**
            - `views/BaseLayout.vue`: shared layout for admin and student; wraps the top bar, page content, and toast
            - `views/TabLayout.vue`: same as BaseLayout but passes tab links into the top bar slot
        - **admin**
            - `views/admin/TeachersView.vue`: create and delete teachers and change the admin password
        - **student**
            - `views/student/GradesView.vue`: student's read-only grade history as charts
        - **teacher**
            - `views/teacher/CategoriesView.vue`: create and delete categories and their subcategories
            - `views/teacher/StudentsView.vue`: create and delete students
            - `views/teacher/GradesView.vue`: the most complex view; student selector, grade form, charts, and limit
              controls
- **tests**: colocated next to the source file as `<filename>.test.js`
    - `utils/gradeUtils.test.js`: grade normalization, truncating, validation, index building, and edit classification
    - `utils/dateUtils.test.js`: date localization and validation across formats
    - `utils/credentialValidation.test.js`: username and password validation helpers
    - `router/index.test.js`: auth guard: session loading, role redirects, and access control