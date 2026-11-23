from flask import Flask, request
import subprocess
import logging

app = Flask(__name__)

@app.route('/alert', methods=['POST'])

def przyjmij_dane():
    dane = request.get_json(silent=True)
    if dane is None:
        logging.error("Nieprawidłowe dane JSON w żądaniu.")
        return {"status": "error", "message": "Nieprawidłowe dane JSON"}, 400
    
    logging.info(f'Otrzymano dane: {dane}')

    for alert in dane.get('alerts', []):
        alertname = alert.get('labels', {}).get('alertname')
        status = alert.get('status')
        logging.info(f'Przetwarzanie alertu: {alertname}')


        if alertname == "NginxReplicasLow" and status == "firing":
            logging.warning("Wykryto awarię typu NginxReplicasLow. Inicjuję procedurę naprawczą.")
            try:
                result = subprocess.run(["ansible-playbook", "remediate_nginx.yml",],check=True,  capture_output=True, text=True)
                logging.info(f"Wynik remediacji: {result.stdout}")
            except subprocess.CalledProcessError as e:
                    logging.error(f"Błąd podczas wykonywania playbooka: {e.stderr}")
                    return {"status": "error", "message": f"Błąd podczas wykonywania playbooka: {e.stderr}"}, 500
        else:
            logging.warning(f"Zignorowano nieznany alert: {alertname}")

    return {"status": "ok", "message": "Alert received successfully"}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)