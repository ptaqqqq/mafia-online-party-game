FROM node:24-slim AS builder
WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# Build arguments for environment variables
ARG VITE_WEBSOCKET_URL
ENV VITE_WEBSOCKET_URL=$VITE_WEBSOCKET_URL

RUN npm run build

FROM node:24-slim AS runtime
WORKDIR /app

COPY --from=builder /app/build ./build

COPY package*.json ./
RUN npm ci --omit=dev
# as
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "build"]
