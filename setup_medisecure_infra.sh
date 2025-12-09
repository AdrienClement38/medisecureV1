#!/usr/bin/env bash
set -e

# Se placer dans le dossier où se trouve le script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Création de l'arborescence et des fichiers de configuration..."

########################
# Monitoring: Prometheus / Grafana
########################
mkdir -p monitoring/prometheus monitoring/grafana/dashboards

cat << 'EOF' > monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq-exporter:9419']
EOF

cat << 'EOF' > monitoring/prometheus/alert.rules.yml
groups:
  - name: backend_alerts
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le)) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          description: "Latency above 500ms for HTTP requests."

      - alert: BackendDown
        expr: up{job="backend"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          description: "Backend API is not responding."
EOF

cat << 'EOF' > monitoring/grafana/dashboards/overview.json
{
  "title": "MediSecure - Overview",
  "timezone": "browser",
  "schemaVersion": 16,
  "version": 1,
  "panels": [],
  "time": {
    "from": "now-6h",
    "to": "now"
  }
}
EOF

cat << 'EOF' > monitoring/grafana/dashboards/performance.json
{
  "title": "MediSecure - Performance",
  "timezone": "browser",
  "schemaVersion": 16,
  "version": 1,
  "panels": [],
  "time": {
    "from": "now-1h",
    "to": "now"
  }
}
EOF

cat << 'EOF' > monitoring/grafana/dashboards/appointments.json
{
  "title": "MediSecure - Appointments KPIs",
  "timezone": "browser",
  "schemaVersion": 16,
  "version": 1,
  "panels": [],
  "time": {
    "from": "now-24h",
    "to": "now"
  }
}
EOF

echo "→ Monitoring (Prometheus / Grafana) OK"


########################
# GitLab CI/CD
########################
cat << 'EOF' > .gitlab-ci.yml
stages:
  - build
  - test
  - docker
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  DOCKER_TLS_CERTDIR: ""

build_backend:
  stage: build
  image: python:${PYTHON_VERSION}
  script:
    - cd medisecure-backend
    - pip install -r requirements.txt
  artifacts:
    paths:
      - medisecure-backend/

test_backend:
  stage: test
  image: python:${PYTHON_VERSION}
  script:
    - cd medisecure-backend
    - pip install -r requirements.txt
    - pytest --junitxml=tests/reports/junit.xml --cov=. --cov-report=xml:tests/reports/coverage.xml
  artifacts:
    when: always
    paths:
      - medisecure-backend/tests/reports/

docker_build:
  stage: docker
  image: docker:stable
  services:
    - docker:dind
  script:
    - docker build -t registry.local/medisecure/backend:latest medisecure-backend
    - docker build -t registry.local/medisecure/frontend:latest medisecure-frontend
    - docker push registry.local/medisecure/backend:latest
    - docker push registry.local/medisecure/frontend:latest

deploy:
  stage: deploy
  image: alpine:3.19
  before_script:
    - apk add --no-cache ansible openssh-client
  script:
    - ansible-playbook ansible/playbooks/deploy.yml -i ansible/inventories/prod/hosts.ini
  when: manual
EOF

echo "→ .gitlab-ci.yml OK"


########################
# Ansible
########################
mkdir -p ansible/inventories/dev ansible/inventories/prod ansible/group_vars \
         ansible/roles/docker/tasks ansible/roles/docker/templates ansible/roles/docker/handlers \
         ansible/roles/backend/tasks ansible/roles/backend/templates ansible/roles/backend/handlers \
         ansible/roles/frontend/tasks ansible/roles/frontend/templates ansible/roles/frontend/handlers \
         ansible/roles/monitoring/tasks ansible/roles/monitoring/templates ansible/playbooks

cat << 'EOF' > ansible/ansible.cfg
[defaults]
inventory = inventories
host_key_checking = False
retry_files_enabled = False
timeout = 30
deprecation_warnings = False
EOF

cat << 'EOF' > ansible/inventories/dev/hosts.ini
[backend]
localhost ansible_connection=local

[frontend]
localhost ansible_connection=local

[database]
localhost ansible_connection=local
EOF

cat << 'EOF' > ansible/inventories/prod/hosts.ini
[backend]
prod-backend ansible_host=192.168.1.10

[frontend]
prod-frontend ansible_host=192.168.1.11

[database]
prod-db ansible_host=192.168.1.12
EOF

cat << 'EOF' > ansible/group_vars/all.yml
app_name: "medisecure"
app_env: "production"

docker_registry: "registry.local"

paths:
  project_root: "/opt/medisecure"
  backend: "/opt/medisecure/backend"
  frontend: "/opt/medisecure/frontend"
EOF

cat << 'EOF' > ansible/playbooks/setup_infra.yml
- hosts: all
  become: yes
  roles:
    - docker
EOF

cat << 'EOF' > ansible/playbooks/setup_monitoring.yml
- hosts: all
  become: yes
  roles:
    - monitoring
EOF

cat << 'EOF' > ansible/playbooks/deploy.yml
- hosts: backend
  become: yes
  tasks:
    - name: Pull backend image
      community.docker.docker_image:
        name: "registry.local/medisecure/backend:latest"
        source: pull

    - name: Apply database migrations
      command: docker compose run backend alembic upgrade head
      args:
        chdir: "{{ paths.project_root }}"

    - name: Restart application stack
      command: docker compose up -d
      args:
        chdir: "{{ paths.project_root }}"

    - name: Check health endpoint
      uri:
        url: "http://localhost:8000/health"
        status_code: 200
EOF

echo "→ Ansible (inventories, group_vars, playbooks) OK"


########################
# Documentation API (OpenAPI)
########################
mkdir -p docs/api

cat << 'EOF' > docs/api/openapi.json
{
  "openapi": "3.0.0",
  "info": {
    "title": "MediSecure API",
    "version": "1.0.0",
    "description": "API de la plateforme MediSecure (patients, rendez-vous, authentification)."
  },
  "paths": {
    "/auth/login": {
      "post": {
        "summary": "Authentifier un utilisateur",
        "responses": {
          "200": { "description": "Authentification réussie, JWT retourné." },
          "401": { "description": "Identifiants invalides." }
        }
      }
    },
    "/patients": {
      "get": {
        "summary": "Lister les patients",
        "responses": {
          "200": { "description": "Liste des patients." }
        }
      },
      "post": {
        "summary": "Créer un patient",
        "responses": {
          "201": { "description": "Patient créé." }
        }
      }
    }
  }
}
EOF

cat << 'EOF' > docs/api/endpoints.md
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
EOF

echo "→ Documentation API (OpenAPI + endpoints) OK"


########################
# Tests / Couverture
########################
mkdir -p medisecure-backend/tests/reports

cat << 'EOF' > medisecure-backend/tests/reports/coverage.xml
<!-- Coverage report generated by pytest-cov in CI -->
EOF

cat << 'EOF' > medisecure-backend/tests/reports/junit.xml
<!-- JUnit report generated by pytest in CI -->
EOF

echo "→ Dossiers de rapports de tests créés (coverage.xml / junit.xml placeholders)"


########################
# Alembic version initiale
########################
mkdir -p medisecure-backend/alembic/versions

cat << 'EOF' > medisecure-backend/alembic/versions/0001_init.py
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "patients",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("firstname", sa.String, nullable=False),
        sa.Column("lastname", sa.String, nullable=False),
        sa.Column("birthdate", sa.Date, nullable=True),
    )

def downgrade():
    op.drop_table("patients")
EOF

echo "→ Alembic version initiale créée"

echo "✅ Setup terminé avec succès."
