# Principaux endpoints de l'API MediSecure

## Authentification

- POST /auth/login
  Authentifie un utilisateur et retourne un token JWT.

## Patients

- GET /patients
  Retourne la liste des patients.

- POST /patients
  Crée un nouveau patient.

- GET /patients/{id}
  Détaille un patient par identifiant.

## Rendez-vous

- GET /appointments
  Liste des rendez-vous pour un patient ou un praticien.

- POST /appointments
  Création d'un rendez-vous.

- PUT /appointments/{id}
  Mise à jour d'un rendez-vous existant.
