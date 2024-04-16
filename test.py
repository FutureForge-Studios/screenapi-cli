# data = {
#     "S.No.": "sl",
#     "Image": "image",
#     "Heading": "description",
#     "URL": "url",
# }

data = {
  "sl": 48,
  "image": "48.0.png",
  "Platform": "www.twitter.com",
  "description": "0",
  "url": "https://twitter.com/goibibo_tpt",
  "Date Added": 0,
  "Priority": "Low",
  "Status": 33,
  "key": "twitter",
  "endpoint": "/twitter",
  "type": None
}
response = {
  "id": "66ef19b4-5bad-5926-8ba8-0b6c4e23f99c",
  "url": "https://twitter.com/goibibo_tpt",
  "image": "/images/66ef19b4-5bad-5926-8ba8-0b6c4e23f99c.png",
  "title": "goibibo_tpt",
  "username": "",
  "description": "",
  "isPost": 1
}

for key, value in response.items():
    if key == "username":
        data["description"] = response[key]

    if key in data:
        if key == "description" and data.get("description") in ["", "0", None]:
            data[key] = [
                response.get("title")
                if response.get("description") == "0"
                or response.get("description") == ""
                else response.get("description")
            ][0]
        else:
            data[key] = value

print(data)
