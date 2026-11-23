# Self-Healing Infrastructure (Kubernetes + Prometheus + Ansible)

Zautomatyzowany system typu **self-healing** dla klastra Kubernetes. Rozwiązanie wykrywa awarie wdrożeń za pomocą stosu Prometheus + Alertmanager i automatycznie przywraca klaster do pożądanego stanu przy użyciu webhooka napisanego w Pythonie (Flask) oraz idempotentnych playbooków Ansible.

## Stack technologiczny

* **Orkiestracja:** Kubernetes (Minikube)
* **Monitoring i alertowanie:** Prometheus, Alertmanager
* **Webhook / API:** Python 3.11, Flask (`logging`, `subprocess`)
* **Automatyzacja:** Ansible, kolekcja `kubernetes.core`
* **Konteneryzacja:** Docker

## Architektura i przepływ działania

1. **Detekcja awarii (Prometheus & Alertmanager):** Reguła `NginxReplicasLow` monitoruje liczbę dostępnych podów w `web-deployment` (namespace `web-prod`). Po wykryciu spadku replik Alertmanager wysyła żądanie `POST` z payloadem JSON na endpoint `/alert`.
2. **Walidacja i routing (Flask Webhook):** Aplikacja `app.py` sprawdza poprawność struktury JSON, filtruje aktywne incydenty (`alertname == "NginxReplicasLow"` oraz `status == "firing"`) i wywołuje proces naprawczy.
3. **Idempotentna remediacja (Ansible):** Playbook `remediate_nginx.yml` komunikuje się bezpośrednio z API Kubernetesa za pomocą modułu `kubernetes.core.k8s_scale`, skalując deployment z powrotem do **3 replik**.
4. **Obsługa błędów i statusy HTTP:** Webhook loguje wynik działania playbooka i zwraca do Alertmanagera odpowiedni kod statusu (`200 OK` po udanej naprawie, `400 Bad Request` przy nieprawidłowym JSON-ie, `500 Internal Server Error` w razie błędu wykonania Ansible).

## Kluczowe pliki w repozytorium

* `app.py` – aplikacja Flask odbierająca webhooki z Alertmanagera i uruchamiająca Ansible.
* `remediate_nginx.yml` – playbook Ansible skalujący `web-deployment` przy użyciu `kubernetes.core.k8s_scale`.
* `deploy_target.yml` – manifest docelowego wdrożenia w namespace `web-prod`.
* `nginx-alert-rule.yaml` – definicja reguły `PrometheusRule` wyzwalającej alert.
* `monitoring-values.yaml` – konfiguracja odbiornika webhooków w Alertmanagerze.
* `Dockerfile` & `requirements.txt` – definicja obrazu kontenera z Pythonem, Ansible oraz biblioteką `kubernetes`.

## Uruchomienie w Dockerze

### 1. Budowanie obrazu
```bash
docker build -t self-healing-webhook .
