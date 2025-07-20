FROM node:24-slim AS builder
WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .
RUN npm run build

FROM node:24-slim AS runtime
WORKDIR /app

COPY --from=builder /app/build ./build

COPY package*.json ./
RUN npm ci --omit=dev

ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "build"]
