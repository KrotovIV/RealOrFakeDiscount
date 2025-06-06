from model import Model
from steam_parser import SteamPriceParser


model = Model()
parser = SteamPriceParser()

price_history = parser.parse('1126310')

prediction = model.predict(price_history)
print(prediction)
