import pandas as pd

def display_message(row):
    name = row["First Name"] + row["Last Name"]
    flight_no = row["Flight No"]
    time = row["Time"]
    ori = row["Origin"]
    des = row["Destination"]
    seat = row["SeatNo"]

    dobval = row["DoBValidation"]
    personval = row["PersonValidation"]
    lggval = row["LuggageValidation"]
    nameval = row["NameValidation"]
    bpval = row["BoardingPassValidation"]
    if all([dobval, personval, lggval, nameval, bpval]):
        MSG_PASS = f"Dear Mr./Mrs {name}, \
You are welcome to flight # {flight_no} leaving at {time} from {ori} to {des}.\n\
Your seat number is {seat}, and it is confirmed.\n\
We did not find a prohibited item (lighter) in your carry-on baggage, \
thanks for following the procedure.\n\
Your identity is verified so please board the plane."
        msg = MSG_PASS
    elif not lggval and all([dobval, personval, nameval, bpval]):
        MSG_LIGHTER = f"Dear Mr./Mrs {name}, \
You are welcome to flight # {flight_no} leaving at {time} from {ori} to {des}.\n\
Your seat number is {seat}, and it is confirmed.\n\
We have found a prohibited item in your carry-on baggage, and it is flagged for removal.\n\
Your identity is verified. However, your baggage verification failed, \
so please see a customer service representative."
        msg = MSG_LIGHTER
    elif not personval and all([dobval, lggval, nameval, bpval]):
        MSG_FACE = f"Dear Mr./Mrs {name}, \
You are welcome to flight # {flight_no} leaving at {time} from {ori} to {des}.\n\
Your seat number is {seat}, and it is confirmed.\n\
We did not find a prohibited item (lighter) in your carry-on baggage.\n\
Thanks for following the procedure.\n\
Your identity could not be verified. Please see a customer service representative."
        msg = MSG_FACE
    else:
        MSG_FAIL = "Dear Sir/Madam, \
Some of the information in your boarding pass \
does not match the flight manifest data, so you cannot board the plane.\n\
Please see a customer service representative."
        msg = MSG_FAIL
    return msg

if __name__ == "__main__":
    file_path = "step_5/final_manifest.csv"
    df = pd.read_csv(file_path)
    for i, idx in enumerate(range(len(df)),start=1):
        print(f"----{i}/{len(df)}----")
        msg = display_message(df.loc[idx])
        print(msg)