FROM node:22-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
# clean install
RUN npm ci
COPY . .

FROM base AS test
RUN npm test && touch /app/.test-passed

FROM base AS build
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=test /app/.test-passed /tmp/.test-passed  # forces docker to build test stage first; failing tests block runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
