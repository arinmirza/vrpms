import requests

#curl -H "Content-Type: application/json" -X POST -d '{"data_dict":"yus78"}'


#url = " https://vrpms-m7cxc698k-idp-yusufserdar170-deneme.vercel.app/api"
url = "https://vrpms-76051jwcm-idp-yusufserdar170-deneme.vercel.app/api/index.py"
header = {"Content-Type": "application/json"}

data = '{"data_dict":"yus78"}'

response = requests.get(url=url, headers=header, json=data)

print(response)

pass