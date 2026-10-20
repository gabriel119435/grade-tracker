# bake mode merges stage namespaces across services; all stage names must be unique
FROM node:26.10.0-alpine AS f-base
WORKDIR /app
COPY package.json package-lock.json ./
# clean install
RUN npm ci
COPY . .

FROM f-base AS f-test
# lint, layout and tests must all pass, any failure stops the build
RUN npm run lint && npm run format:check && npm test && touch /app/.test-passed

FROM f-base AS f-build
RUN npm run build

FROM nginx:1.30.5-alpine AS f-runtime
# forces docker to build test stage first; failing checks block runtime
COPY --from=f-test /app/.test-passed /tmp/.test-passed
# base image's default error page, unused: every error_page in nginx.conf points to its own @location
RUN rm /usr/share/nginx/html/50x.html
COPY --from=f-build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
