import requests

def get_price(coin):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids":coin,
        "vs_currencies":"usd",
        "include_24hr_change":"true"
    }
    response = requests.get(url, params=params).json()
    if coin in response:
        return{
            "price":response[coin]["usd"],
            "change":round(response[coin]["usd_24h_change"], 2)
        }
    return None
