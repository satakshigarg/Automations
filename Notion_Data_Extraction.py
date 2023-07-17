import pandas as pd
from notion_client import Client
from collections import OrderedDict

def extract_data(database_url):
    # Enter your Notion access token and database URL
    token = "Notion API token"

    # Create a Notion client
    client = Client(auth=token)

    import re

    # Extract the database ID from the view URL
    url_pattern = r"([0-9a-fA-F]{32})"
    match = re.search(url_pattern, database_url)
    if match:
        database_id = match.group(1)
    else:
        raise ValueError("Invalid database view URL.")

    # Retrieve properties (fields) of the database
    properties_res = client.databases.retrieve(database_id)
    properties = properties_res["properties"]

    # Retrieve the data from the database
    data = []
    next_cursor = None

    while True:
        query_params = {
            "database_id": database_id,
            "page_size": 100,
            "start_cursor": next_cursor
        }

        response = client.databases.query(**query_params)
        database_rows = response["results"]
        next_cursor = response.get("next_cursor")

        for row in database_rows:
            row_data = {}

            for key, prop in properties.items():
                prop_name = prop["name"]
                prop_type = prop["type"]

                if prop_name in row["properties"]:
                    prop_value = row["properties"][prop_name][prop_type]

                    if prop_type == "title":
                        value = prop_value[0]["plain_text"] if prop_value else ""
                    elif prop_type == "rich_text":
                        value = prop_value[0]["plain_text"] if prop_value else ""
                    elif prop_type == "date":
                        value = prop_value["start"] if prop_value else ""
                    elif prop_type == "person":
                        value = prop_value[0]["name"] if prop_value else ""
                    elif prop_type == "checkbox":
                        value = prop_value["checkbox"] if prop_value else False
                    elif prop_type == "select":
                        value = prop_value["name"] if prop_value else ""
                    elif prop_type == "multi_select":
                        if isinstance(prop_value, list) and prop_value:
                            value = ", ".join([option["name"] for option in prop_value])
                        else:
                            value = ""
                    else:
                        value = prop_value
                else:
                    value = ""

                row_data[prop_name] = value

            data.append(row_data)

        if not next_cursor:
            break

    # Create a DataFrame from the retrieved data
    df = pd.DataFrame(data)

    # Generate readable form
    readable_data = []
    for index, row in df.iterrows():
        readable_data.append({})
        for key, value in row.items():
            # if value != "":
                # Exclude metadata fields from the output
                if not isinstance(value, dict) and not isinstance(value, list):
                    readable_data[index] = {**readable_data[index], **{key: value}}


    return readable_data

def list_database_files():
    return extract_data("Database URL")
