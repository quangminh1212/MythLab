# syntax=docker/dockerfile:1
# MythLab server image: web UI (Astro) embedded into the Go binary, static, non-root.
#   docker build -t mythlab .
#   docker run -p 127.0.0.1:8765:8765 -e MYTHLAB_ACCESS_KEY=... -v mythlab-data:/data mythlab

# ---- 1. web UI -> web/dist
FROM node:22.21-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ---- 2. Go server with the UI embedded (same copy step as tools/embedui, tools/build-web.ps1 -Embed)
# Keep the Go version equal to server/go.mod.
FROM golang:1.26.11-alpine AS build
WORKDIR /src/server
COPY server/go.mod server/go.sum ./
RUN go mod download
COPY server/ ./
COPY --from=web /web/dist /src/web/dist
RUN go run ./tools/embedui
RUN CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/mythlab-server ./cmd/mythlab-server
# /data owned by the distroless "nonroot" user (65532); a new named volume inherits this ownership
RUN mkdir -p /out/data/library /out/data/cache
COPY docker/config.json /out/data/config.json

# ---- 3. runtime
FROM gcr.io/distroless/static-debian12:nonroot
LABEL org.opencontainers.image.title="MythLab server" \
      org.opencontainers.image.description="MythLab story reader: API, Edge TTS and web UI in one static binary" \
      org.opencontainers.image.source="https://github.com/quangminh1212/MythLab" \
      org.opencontainers.image.licenses="MIT"
COPY --from=build /out/mythlab-server /usr/local/bin/mythlab-server
COPY --from=build --chown=65532:65532 /out/data /data
VOLUME /data
EXPOSE 8765
# --lan binds 0.0.0.0, so every /api/* request from another machine needs the access key.
# Key: -e MYTHLAB_ACCESS_KEY=... (else the server generates one into /data/cache/server.json and prints it in the log).
ENTRYPOINT ["/usr/local/bin/mythlab-server", "--lan", "--port", "8765", "--config", "/data/config.json", "--cache", "/data/cache"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["/usr/local/bin/mythlab-server", "--healthcheck", "--port", "8765"]
