import googlemaps

from config import API_KEY

from openpyxl import load_workbook, Workbook
from time import sleep
import json


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


def get_businesses():
    codes = get_codes()
    # codes = ["LGA"]
    code_to_coord = get_codes_mapped(codes)
    print(code_to_coord)
    results_dict = {}
    place_ids = []
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
                    if result['place_id'] not in place_ids:  # awful way to do it
                        filtered_results.append(result)
                        place_ids.append(result['place_id'])
                    else:
                        pass
            except:
                pass
        results_dict[code] = filtered_results
        sleep(1)

    print(len(place_ids))

    with open('results.json', 'w') as outfile:
        json.dump(results_dict, outfile)


def check_dupes():
    with open("results.json", "r") as f:
        results = json.load(f)
    all_values = []
    for code in results:
        # print(results[code])
        # all_values.extend(list(map(lambda x: x.values(), results[code])))
        all_values.extend(results[code])
    # print(len(all_values))
    # print(len(set(all_values)))
    place_ids = []
    for val in all_values:
        place_ids.append(val["place_id"])

    print(len(place_ids))
    print(len(set(place_ids)))
    unique_ids = list(set(place_ids))

    new_results = {}
    for code in results:
        values = results[code]
        new_values = []
        for value in values:
            if value['place_id'] in unique_ids:
                unique_ids.remove(value['place_id'])
                new_values.append(value)
            else:
                pass
        new_results[code] = new_values
    all_new_values = []
    for code in new_results:
        # print(results[code])
        # all_values.extend(list(map(lambda x: x.values(), results[code])))
        all_new_values.extend(new_results[code])
    print(len(all_new_values))
    with open('filtered_results.json', 'w') as outfile:
        json.dump(new_results, outfile)


def get_contact_info():
    client = googlemaps.Client(key=API_KEY)

    # open results
    with open("filtered_results.json", "r") as f:
        result = json.load(f)
    # map airport codes to list of place_ids
    code_to_place_ids = {}
    for code in result:
        place_ids = []
        for place in result[code]:
            place_ids.append(place["place_id"])
        code_to_place_ids[code] = place_ids

    # make places detail request with place_id
    details = []
    for code in code_to_place_ids:
        place_ids = code_to_place_ids[code]

        # create list of tuples of Airport ID, Name, Address, Phone
        for place_id in place_ids:
            result = client.place(place_id=place_id)["result"]
            # print(result)
            business_name = result.get("name")
            address = result.get('formatted_address',"")
            phone = result.get('formatted_phone_number',"")

            place_details = [code, business_name, address, phone]
            details.append(place_details)
            print(place_details)
    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "IATA"
    sheet["B1"] = "Name"
    sheet["C1"] = "Address"
    sheet["D1"] = "Phone"

    for i in range(2, len(details) + 2):
        for letter, detail in zip(["A", "B", "C", "D"], details[i-2]):
            sheet["{}{}".format(letter, i)] = detail

    workbook.save(filename="Place_Details_udf.xlsx")

    # save list as excel

    pass


if __name__ == '__main__':
    # get_businesses()
    # check_dupes()
    get_contact_info()
