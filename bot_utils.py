import requests


def send_broadcast_message(message, notificationDisabled=False):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer ncW0RX0za1F7wm1IQG1MQ50wrfqPIkT0BprUCepaZRS"
    }

    params = {
        "message": message,
        "notificationDisabled": notificationDisabled
    }

    res = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
    if res.status_code != 200:
        print("Message post error: " + res.text)


def send_broadcast_image(image_url, notificationDisabled=False):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer ncW0RX0za1F7wm1IQG1MQ50wrfqPIkT0BprUCepaZRS"
    }

    params = {
        "message": "\n",
        "imageThumbnail": image_url,
        "imageFullsize": image_url,
        "notificationDisabled": notificationDisabled
    }

    res = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
    if res.status_code != 200:
        print("Message post error: " + res.text)
