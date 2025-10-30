# Étape de build correcte pour le mode dev Vite
FROM node:18

WORKDIR /app

# Copier tout le code du projet
COPY . .

# Installer les dépendances
RUN npm install

# Exposer le port utilisé par Vite
EXPOSE 3000

# Lancer le serveur
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
