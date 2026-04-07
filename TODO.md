# current tasks

- currently none

# future tasks

- missing tests: backend has no coverage for auth, categories, students, and teachers routes
- frontend has no component or composable tests (`useGrades`, `useToast`, `useConfirm`, and all vue components); highest-risk gap is the orchestration logic in `useGrades` (`cellStates`, `submitStudentGrades`)
- per-request user load query: `load_user` runs a full `SELECT` on every authenticated request; add session-local caching if traffic grows
- migrate to postgresql: add alembic for migrations (inline migration functions in `__init__.py` have no applied-state tracking and break on non-idempotent changes), convert `Grade.date` to `Mapped[datetime.date]`
- migrate to typescript: typed props/emits, api response interfaces, and composable return types; vite supports ts out of the box
