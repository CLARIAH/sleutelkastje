# build step
FROM node:20-alpine as build

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . ./

RUN npm run build


# release step
FROM nginx:1.21.5-alpine as release

COPY --from=build /app/dist /usr/share/nginx/html/
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
EXPOSE 80

CMD ["/entrypoint.sh"]
