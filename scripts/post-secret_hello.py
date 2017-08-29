import requests

vault="https://54.172.229.173:8200/v1/secret/hello"
headers = {"X-Vault-Token": "cbbfb448-60ab-22f8-c585-afa4e6aed339"}
payload = {'value': "meetup-churrops"}

r = requests.post(vault, verify=False, headers=headers, json=payload)

if r.status_code == 204:
    print ("OK - Status: %s" %r.status_code)


