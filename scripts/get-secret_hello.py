import requests

vault="https://54.172.229.173:8200/v1/secret/hello"

headers = {"X-Vault-Token": "cbbfb448-60ab-22f8-c585-afa4e6aed339"}
r = requests.get(vault, verify=False, headers=headers)
json_response = r.json()


if r.status_code == 200:
    api_key = json_response.get('data',{}).get('value', "")
    print ("Value: %s" %(api_key))