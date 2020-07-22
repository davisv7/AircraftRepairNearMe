import googlemaps

from config import API_KEY

from openpyxl import load_workbook, Workbook
from time import sleep
import json


def get_ICAO_codes():
    wb = load_workbook("Airport_Codes.xlsx")
    last_row = 2922
    sheet = wb["Vendors"]
    codes = []
    for i in range(2, last_row + 1):
        # if sheet["A{}".format(i)].value != None:
        #     state = " ".join([x.capitalize() for x in sheet["A{}".format(i)].value.split()])
        icao_codes = sheet["G{}".format(i)].value
        iata_codes = sheet["H{}".format(i)].value
        if icao_codes and not iata_codes and icao_codes != "N/A":
            codes.append(icao_codes)
    return codes


def get_ICAO_codes_mapped(codes):
    code_to_coord = {}
    wb = load_workbook("Airport Master.xlsx")
    last_row = 2728
    sheet = wb["US Airports Master"]
    for i in range(2, last_row + 1):
        # if sheet["A{}".format(i)].value != None:
        #     state = " ".join([x.capitalize() for x in sheet["A{}".format(i)].value.split()])
        airport_code = sheet["M{}".format(i)].value
        lat, long = sheet["E{}".format(i)].value, sheet["F{}".format(i)].value
        # print(airport_code,lat,long)
        if airport_code in codes:
            code_to_coord[airport_code] = (lat, long)
    print(len(code_to_coord), len(codes))
    # print(set(codes) - set(list(code_to_coord.keys())))
    return code_to_coord


def get_IATA_codes():
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


def get_IATA_codes_mapped(codes):
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


def get_IATA_businesses():
    iata_codes = get_IATA_codes()
    iata_code_to_coord = get_IATA_codes_mapped(iata_codes)

    results_dict = {}
    client = googlemaps.Client(key=API_KEY)

    for code in iata_codes:
        query = "aircraft maintenance"
        try:
            lat, lon = list(map(str, iata_code_to_coord[code]))
            print(query, code)
        except:
            print("NO DATA FOR AIRPORT CODE: {}".format(code))
            results_dict[code] = []
            continue

        results = client.places_nearby(keyword=query, location=(lat, lon), radius=48000)["results"]
        print(results)

        results_dict[code] = results
    with open('IATA_results.json', 'w') as outfile:
        json.dump(results_dict, outfile)


def get_ICAO_businesses():
    icao_codes = get_ICAO_codes()
    icao_code_to_coord = get_ICAO_codes_mapped(icao_codes)

    results_dict = {}
    client = googlemaps.Client(key=API_KEY)

    for code in icao_codes:
        query = "aircraft maintenance"
        try:
            lat, lon = list(map(str, icao_code_to_coord[code]))
            print(query, code)
        except:
            print("NO DATA FOR AIRPORT CODE: {}".format(code))
            results_dict[code] = []
            continue

        results = client.places_nearby(keyword=query, location=(lat, lon), radius=48000)["results"]
        print(results)

        results_dict[code] = results

    with open('ICAO_results.json', 'w') as outfile:
        json.dump(results_dict, outfile)


def check_IATA_dupes():
    with open("IATA_results.json", "r") as f:
        results = json.load(f)
    all_values = []
    for code in results:
        all_values.extend(results[code])
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
        all_new_values.extend(new_results[code])
    print(len(all_new_values))
    with open('filtered_IATA_results.json', 'w') as outfile:
        json.dump(new_results, outfile)


def check_ICAO_dupes():
    with open("ICAO_results.json", "r") as f:
        results = json.load(f)
    all_values = []
    for code in results:
        all_values.extend(results[code])
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
        all_new_values.extend(new_results[code])
    print(len(all_new_values))
    with open('filtered_ICAO_results.json', 'w') as outfile:
        json.dump(new_results, outfile)


def get_contact_info():
    client = googlemaps.Client(key=API_KEY)

    # open results
    # with open("filtered_results.json", "r") as f:
    #     result = json.load(f)
    with open("filtered_ICAO_results.json", "r") as f:
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
            address = result.get('formatted_address', "")
            phone = result.get('formatted_phone_number', "")

            place_details = [code, business_name, address, phone]
            details.append(place_details)
            print(place_details)
    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "ICAO"
    sheet["B1"] = "Name"
    sheet["C1"] = "Address"
    sheet["D1"] = "Phone"

    for i in range(2, len(details) + 2):
        for letter, detail in zip(["A", "B", "C", "D"], details[i - 2]):
            sheet["{}{}".format(letter, i)] = detail

    workbook.save(filename="Place_Details_ICAO.xlsx")

    # save list as excel

    pass


def final_steps():
    _dict = codes_to_states()
    wb = load_workbook("Place_Details_Final.xlsx")
    last_row = 7502
    sheet = wb.active
    for i in range(2, last_row + 1):
        iata_code = sheet["{}{}".format("A", i)].value
        icao_code = sheet["{}{}".format("B", i)].value
        if iata_code:
            sheet["F{}".format(i)] = _dict[iata_code]
        else:
            sheet["F{}".format(i)] = _dict[icao_code]

    wb.save(filename="Place_Details_Final.xlsx")


def codes_to_states():
    icao_col = "M"
    iata_col = "N"
    state_col = "J"
    state_to_initials = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    initials_to_state = {
        y: x for x, y in state_to_initials.items()
    }
    code_to_state = {}
    wb = load_workbook("Airport Master.xlsx")
    last_row = 2728
    sheet = wb["US Airports Master"]
    for i in range(2, last_row + 1):
        # if sheet["A{}".format(i)].value != None:
        #     state = " ".join([x.capitalize() for x in sheet["A{}".format(i)].value.split()])
        iata_code = sheet["{}{}".format(iata_col, i)].value
        icao_code = sheet["{}{}".format(icao_col, i)].value
        state = initials_to_state[sheet["{}{}".format(state_col, i)].value.split("-")[1]]
        code_to_state[iata_code] = state
        code_to_state[icao_code] = state
        # print(airport_code,lat,long)
    return code_to_state


if __name__ == '__main__':
    # get_ICAO_businesses()
    # get_IATA_businesses()
    # check_IATA_dupes()
    # check_ICAO_dupes()
    # get_contact_info()
    # codes = get_ICAO_codes()
    # print(get_IATA_codes_mapped(codes))
    final_steps()
