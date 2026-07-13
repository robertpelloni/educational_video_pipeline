import json

with open("postman_collection.json", "r") as f:
    data = json.load(f)

# Add event tests
for item in data["item"]:
    name = item["name"]
    status = 200
    if "400" in name:
        status = 400
    elif "422" in name:
        status = 422
    elif "401" in name:
        status = 401

    script_content = f"""pm.test("Status code is {status}", function () {{
    pm.response.to.have.status({status});
}});
"""
    item["event"] = [
        {
            "listen": "test",
            "script": {
                "exec": script_content.split("\n"),
                "type": "text/javascript"
            }
        }
    ]

with open("postman_collection.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated postman collection with assertions.")
