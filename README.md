**ACMESTOCK-CO by Patient Readings Incorporated Co and Sons.**
# Acmestock-Co RESTful API Microservices Application
This repository contains a microservices structured application to be hosted on the cloud provider Azure.
The application contains several components containerized through docker. There was also at one point a jenkins pipeline for the application as well.
Each component utilizes the built-in logging module with a custom format as well as yml files for most of the application's configuration/storage of constants.
For testing endpoints, I used the swaggerbundle (Like postman but in-browser with one import) and apache jmeter. 
```
THESE ARE THE TWO MAIN OBJECTS STORED IN THE DATABASE.

Stock object *(to_Dict function)*
stock_dict = {
  'company': self.company,
  'listing_id': self.listing_id,
  'share_price': self.share_price,
  'total_shares_available': self.total_shares_available,
  'listing_date': self.listing_date,
  'trace_id': self.trace_id
}
Sell Order object *(to_Dict function)*
sell_order_dict = {
    'seller_id': self.seller_id,
    'broker_id': self.broker_id,
    'share_price': self.share_price,
    'amount': self.amount,
    'sale_date': self.sale_date,
    'trace_id': self.trace_id
}
```
### Running the application
You can deploy the application yourself by running the start.sh script. 


### **Storage**
Responsible for connecting to and mediating between the database and other microservices. Creates the DB and tables on startup by connecting to a separate db container (MySQL).
Contains POST functions to create new objects in the database. These are sent to the storage microservice through a message broker (Kafka).

Contains Health endpoint to return 200 if the service is running.
*/acmestock/health*
Contains GET endpoint for Sell and Stock objects with a start and end date as parameter. Fetches all sell orders created and stocks listed within those dates.
*/acmestock/get_available_stocks*
*/acmestock/get_sell_order*



### **Receiver**
Responsible for receiving new orders and stocks at endpoints and forwarding requests to the storage service through a message broker.

Contains Health endpoint to return 200 if the service is running.
`/acmestock/health`
Contains POST endpoint for Sell and Stock objects following a schema for parameters. Each POST request is routed to the storage service through the message broker.
`/acmestock/new New stock`
`/acmestock/sell New Sell order`

### **Processing**
Conducts periodic statistical review of all new sell and stock orders. Stats calculated and tracked include 'num_sell_orders_listed', 'num_stocks_listed', 'average_stock_price', 'total_shares_available', 'average_shares_available_per_stock'.
Runs calculations every 5 seconds with a maximum of 30 threaded instances. 

Contains Health endpoint to return 200 if the service is running.
`/acmestock/health`
Contains GET endpoint to fetch current statistics stored.
`/stats`

### **Audit**
Service with GET endpoints that returns specific stats from unique stocks and sell orders taking in the listing index as a parameter (Used by the dashboard when fetching random listings).

Contains Health endpoint to return 200 if the service is running.
`/acmestock/health`
Contains GET endpoints to fetch the price of stocks and quantity of a stock listed from a company.
`/get_stock_quantity`
`/get_stock_price`

### **Health**
Service which tracks the status of all other application services. Has one endpoint to fetch the status of all services.

Contains GET endpoint to fetch current status of all services.
`/status`

### **Dashboard**
React App that displays the current stats for all stocks and companies listed in the database, it will also fetch a random stock and company with an index between 0 and 100 (of a list containing only the most recent added).
Lastly, it displays the status of all services running. It gets all this information by requesting the endpoints from the other services.
Application is deployed on a docker container running alpine linux with node package manager installed.
