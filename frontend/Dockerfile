# bake mode merges stage namespaces across services; all stage names must be unique
FROM node:22-alpine AS f-base
WORKDIR /app
COPY package.json package-lock.json ./
# clean install
RUN npm ci
COPY . .

FROM f-base AS f-test
RUN npm test && touch /app/.test-passed

FROM f-base AS f-build
RUN npm run build

FROM nginx:alpine AS f-runtime
# forces docker to build test stage first; failing tests block runtime
COPY --from=f-test /app/.test-passed /tmp/.test-passed
COPY --from=f-build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
