import datetime
import json

import connexion
from connexion import NoContent
import swagger_ui_bundle


object_array = []
MAX_EVENTS = 10
EVENT_FILE_NAME = 'events.json'
def process_events(event):
    if 'total_shares_available' in event:
        obj = {
            "received_timestamp": datetime.datetime.now().strftime("%Y-%m-%dT %H:%M:%SZ"),
            f"add_new_stock": f"New stock listed. {event['total_shares_available']} shares at ${event['share_price']}/share from '{event['company']}' on {event['listing_date']}.",
        }
    elif 'sell_order' in event:
        obj = {
            "received_timestamp": datetime.datetime.now().strftime("%Y-%m-%dT %H:%M:%SZ"),
            f"sell_order": f"New Sale Confirmed. Seller '{event['seller_id']}' sold {event['amount']} at ${event['share_price']} per share to broker '{event['broker_id']}' on {event['sale_date']}.",
        }
    else:
        return {'Error': 'Object event type not found'}
    

    # Check length and pop to keep event list at 10.
    if len(object_array) < MAX_EVENTS:
        object_array.append(obj)
    else:
        object_array.pop()
        object_array.insert(0, obj)
    with open(EVENT_FILE_NAME, 'w', encoding='utf-8') as file:
        file.write(json.dumps(object_array))

    #  BASIC LOG 
    print(len(object_array))
    return obj

def add_new_stock(body):
    process_events(body)
    return NoContent, 201

def sell_order(body):
    process_events(body)
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)