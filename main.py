import mysql.connector as mysql
from configparser import ConfigParser
import get_uex_data as uex
import upload_to_mysql as upload
from datetime import datetime

def load_configs():
    config = ConfigParser()
    mysql_config = ConfigParser()
    routeconfig = ConfigParser()

    config.read('Config/config.ini')
    mysql_config.read('Config/mySql.ini')
    routeconfig.read('Config/tradeRoutes.ini')
    return config, mysql_config, routeconfig

def main():
    timestamp_begin = datetime.now()
    config, mySqlConfig, routeconfig = load_configs()
    print(config['api']['services'])
    print(mySqlConfig['MYSQL_SERVER']['HOST'])

    for service in config['api']['services'].split(','):
        print(service)
        uex_service_data = uex.get_uex_data(service, config)
        upload.upload_to_mysql(uex_service_data, mySqlConfig, service)

    # Hole top Routen für alle Commodities
    uex_commodities = uex.get_uex_data(routeconfig['API']['SERVICE_TRIGGER'], config)
    firstRun = True

    for commodity in uex_commodities['data']:
        route_endpoint = routeconfig['API']['ENDPOINT']
        commodity_id = commodity['id']
        investment = routeconfig['PARAMETERS']['INVESTMENT']

        route_service = f"{route_endpoint}?id_commodity={commodity_id}&investment={investment}"
        uex_route_data = uex.get_uex_data(route_service, config)
        upload.upload_route_data(uex_route_data, mySqlConfig, route_endpoint, firstRun)
        firstRun = False

    timestamp_end = datetime.now()
    print(f"Ich habe {timestamp_end - timestamp_begin} gebraucht")
    print(f"Begonnen: {timestamp_begin}")
    print(f"Ende: {timestamp_end}")

if __name__ == "__main__":
    main()