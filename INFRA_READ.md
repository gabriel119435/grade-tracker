# infrastructure reading order

a beginner's guide to the infrastructure codebase, ordered from simple to complex.
each new file builds on what came before; read them in order for the most coherent picture.

- `.gitignore`: excludes auto-generated artifacts, secrets, local data, and tooling from version control
- `backend/.dockerignore`: same concept as .gitignore but for the backend docker build context
- `frontend/.dockerignore`: same as above for the frontend build context
- `frontend/nginx.conf`: serves vue files and proxies flask with per-ip rate and connection limiting
- `backend/Dockerfile`: multi-stage build with base, test and runtime stages
- `frontend/Dockerfile`: multi-stage build with base, test, build and runtime stages
- `docker-compose.yml`: exposes nginx, keeps flask internal, named sqlite volume and sets hardware limits
