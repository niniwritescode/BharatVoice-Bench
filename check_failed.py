
import json

with open(
    "results/noisy_transcriptions.json",
    "r",
    encoding="utf-8"
) as file:
    results = json.load(file)

for item in results:
    if item.get("status") != "success":
        print("\nFile:", item["file"])
        print("Status:", item.get("http_status"))
        print("Error:", item.get("error"))
