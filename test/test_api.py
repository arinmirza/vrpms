import requests

#curl -H "Content-Type: application/json" -X POST -d '{"data_dict":"yus78"}'


#url = " https://vrpms-m7cxc698k-idp-yusufserdar170-deneme.vercel.app/api"
url = "https://vrpms-cr7ecufka-idp-yusufserdar170-deneme.vercel.app/api"
header = {"Content-Type": "application/json"}

data = {
        "program_mode":"TDVRP",
        "algorithm":"GA",
        "N":20,
        "M":3,
        "q":6,
        "k":4,
        "multithreaded":"Y"
        }

response = requests.get("https://vrpms-cr7ecufka-idp-yusufserdar170-deneme.vercel.app/api?program_mode=TDVRP&algorithm=GA&N=20&M=3&q=6&k=4")

print(response)

pass