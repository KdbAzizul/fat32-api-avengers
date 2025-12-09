# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# ========================================================
# FIX: Force the API URL at Build Time
# This overrides any config files and hardcodes localhost
# ========================================================
ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

RUN npm run build

# Stage 2: Production Runner
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create system user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the standalone build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# CRITICAL FIX: You MUST copy the static folder or images/CSS will break
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]