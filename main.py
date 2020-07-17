import googlemaps

from config import API_KEY

from openpyxl import Workbook, load_workbook
from time import sleep
import json
from pyairports.airports import Airports  # https://github.com/NICTA/pyairports


def get_codes():
    wb = load_workbook("Airport_Codes.xlsx")
    last_row = 2922
    sheet = wb["Vendors"]
    codes = []
    for i in range(2, last_row + 1):
        # if sheet["A{}".format(i)].value != None:
        #     state = " ".join([x.capitalize() for x in sheet["A{}".format(i)].value.split()])
        airport_code = sheet["H{}".format(i)].value
        if airport_code and airport_code != "N/A":
            codes.append(airport_code)
    return codes


def get_codes_mapped(codes):
    code_to_coord = {}
    wb = load_workbook("Airport Master.xlsx")
    last_row = 2728
    sheet = wb["US Airports Master"]
    for i in range(2, last_row + 1):
        # if sheet["A{}".format(i)].value != None:
        #     state = " ".join([x.capitalize() for x in sheet["A{}".format(i)].value.split()])
        airport_code = sheet["N{}".format(i)].value
        lat, long = sheet["E{}".format(i)].value, sheet["F{}".format(i)].value
        # print(airport_code,lat,long)
        if airport_code in codes:
            code_to_coord[airport_code] = (lat, long)
    print(len(code_to_coord), len(codes))
    return code_to_coord


def main():
    codes = get_codes()
    # codes = ["LGA"]
    code_to_coord = get_codes_mapped(codes)
    print(code_to_coord)
    results_dict = {}
    all_results = []
    client = googlemaps.Client(key=API_KEY)

    for code in codes:
        query = "aircraft maintenance"
        try:
            lat, lon = list(map(str, code_to_coord[code]))
            print(query, code)
        except:
            print("NO DATA FOR AIRPORT CODE: {}".format(code))
            results_dict[code] = []
            continue

        results = client.places_nearby(keyword=query, location=(lat, lon), radius=48000)["results"]
        print(results)
        filtered_results = []
        for result in results:
            try:
                if result["business_status"] == 'OPERATIONAL':
                    if result not in all_results:  # awful way to do it
                        filtered_results.append(result)
                        all_results.append(result)
                    else:
                        pass
            except:
                pass
        results_dict[code] = filtered_results
        sleep(1)

    print(len(all_results))

    with open('result.json', 'w') as outfile:
        json.dump(results_dict, outfile)


if __name__ == '__main__':
    main()
