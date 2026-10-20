FROM node:22-alpine

WORKDIR /app

# Installation des dépendances JavaScript (mise en cache tant que package*.json ne change pas)
COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
