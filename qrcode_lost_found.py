import os.path
import qrcode
import random
import datetime
import json
import mysql.connector

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1yE2MAsaUePD9xh3wUjDnmrZS6kQXNkE6SfeU7Kjwsoo" 

#1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
SAMPLE_RANGE_NAME = 'Form Responses 1!A2:H3'
#'Form Responses 1!A2:L6'

mydb = mysql.connector.connect(host = 'localhost', password = 'sql123', username = 'rahul', database = 'qrcode_id' )
mycursor = mydb.cursor()


def check_if_processed(id,cursor,name,mob):
   sql = "SELECT * FROM id_check_qr WHERE uni_id = %s AND name_id = %s"
   val = (id,name)
   cursor.execute(sql,val)
   result = cursor.fetchone()
   return result is not None

#generating qrcode function
def generate_qr_code(data,id):
    qr = qrcode.QRCode(
                      version=1,
                      error_correction=qrcode.constants.ERROR_CORRECT_L,
                      box_size=10,
                      border=4,
                  )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    uniqux_id = id
    path = r"C:\\Users\\rahul_pal\\Downloads\\Learning\\project\\Lost&found"

    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path,f"{uniqux_id}")
    try:
       
        print(f"Saving Qr code image ")
        img.save(f"{filepath}.png")
        #print(processed_rows)
                        
    except OSError as e:
                      print(f"Error saving image: {e}")
                      print(f"File path: {filepath}")

def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  #486689715282-0pohcusbjnurhn3j5m79seu3hbm14t9a.apps.googleusercontent.com

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials_lostfound.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
    
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values")
    

    if not values:
      print("No data found.")
      return

    for row in values:
        row_id = row[7]
        name_id = row[1]
        mobile_num = row[3]
        print(row_id,name_id,mobile_num)
        #if row_id not in processed_rows:
        #convert raw data into string
          # Generate unique identifier
        mycursorr = mydb.cursor()
        
        if not check_if_processed(row_id,mycursorr,row[1],mobile_num):
            unique_id = row_id
            mob_num= row[3]
            data_to_encode = f"TimeStamp : {row[0]}\nName : {row[1]}\nAge : {row[2]}\nYour Mobile number : {row[3]}\nGuardian name : {row[4]}\nGuardian mobile number : {row[5]}\nState : {row[6]}\nUnique_ID : {row[7]}"
            # Insert the processed ID and name into the database
            generate_qr_code(data_to_encode,unique_id)

            # Insert the processed ID and name into the database

            sql = "INSERT INTO id_check_qr (uni_id, name_id, mobile_num) VALUES (%s, %s, %s)"
            val = row_id,name_id,mob_num
            mycursorr.execute(sql,val)
            mydb.commit()
        

  except HttpError as err:
    print(err)
  mydb.close()
    
 

if __name__ == "__main__":
  main()























# #DELETE FROM `qrcode_id`.`id_check` WHERE (`uni_id` = 'ID_14');
# sql = "DELETE FROM id_check WHERE name_id is NULL"
# mycursor.execute(sql)
# mydb.commit()
