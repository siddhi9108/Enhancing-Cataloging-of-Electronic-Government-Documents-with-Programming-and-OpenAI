# Define the folder where the PDFs are located
pdf_folder = "/Users/pdfs"

# Function to extract metadata from a PDF file
def extract_pdf_metadata(pdf_path):
    metadata = {}  # Create an empty dictionary to store the extracted metadata
    
    with open(pdf_path, "rb") as file:  # Open the PDF file in binary mode ('rb')
        pdf_reader = PdfReader(file)  # Create a PdfReader object to read the PDF
        info = pdf_reader.metadata  # Get the metadata from the PDF
        
        # Extract the specific metadata fields and add them to the dictionary, with fallback values if missing
        metadata['title'] = info.title if info.title else "Unknown Title"
        metadata['subject'] = info.subject if info.subject else "Unknown Subject"
        metadata['producer'] = info.producer if info.producer else "Unknown Producer"
        
        # Try to extract the date_last_issue_online field
        metadata['publication_date'] = info.get('date_last_issue_online', None)  # Get the date_last_issue_online field
        
    return metadata

# Function to extract publication year and other info using Apache Tika (from your provided code)
def get_baseinfo(d, date):
    logname = "log_" + date + ".txt"
    f = open(logname, "a")
    int = 0
    for key in d:
        line1 = "Now processing " + str(key) + "\n"
        f.write("************************************************************\n")
        
        file_path = os.path.join(pdf_folder, key)  # Full absolute file path
        raw = parser.from_file(file_path)  # Use the absolute file path
        rawcontent = raw['content'].replace("\n", " ")
        raw_lan = raw["metadata"]['dc:language']
        
        if type(raw_lan) is list:
            raw_lan = [i.lower() for i in raw_lan]
            if "en" in raw_lan:
                d[key]["lan"] = "eng"
            elif "da-dk" in raw_lan:
                d[key]["lan"] = "dan"
            else:
                f.write("       language needs to be manually filled in")
                raw_lan_str = ";".join(raw_lan)
                line2 = "       language value is: " + raw_lan_str
                f.write(line2)
        else:
            if raw_lan.lower() == "en-us" or raw_lan.lower() == "en":
                d[key]["lan"] = "eng"
            elif raw_lan.lower() == "da-dk":
                d[key]["lan"] = "dan"
            else:
                f.write("       language needs to be manually filled in")
                line2 = "       language value is: " + raw_lan
                f.write(line2)
        
        # Extract title and publication year
        titlea = d[key]["fulltitle"]
        titleb = ""
        if ":" in titlea:
            titlea = d[key]["fulltitle"].split(":")[0]
            titleb = d[key]["fulltitle"].replace(titlea, "")
        d[key]["titleb"] = titleb
        ind2245 = ""
        if titlea[:2].lower() == "a ":
            ind2245 = 2
        if titlea[:3].lower() == "an ":
            ind2245 = 3
        if titlea[:4].lower() == "the ":
            ind2245 = 4
        print("The main title of the file is:", titlea)
        print("******************************************")
        d[key]["titlea"] = titlea
        d[key]["titleind2"] = ind2245

        # Extract publication year from the metadata
        try:
            pubYear = raw["metadata"]['xmp:CreateDate'].split("T")[0].split("-")[0]
        except KeyError:
            pubYear = "Unknown Year"
        
        d[key]["url"] = d[key]["url"]
        d[key]["pubYear"] = "[" + pubYear + "]"
        int += 1
    return d

# Function to generate a KBART CSV file based on the PDFs in the specified folder
def generate_kbart_csv(pdf_folder):
    # Ask the user to input the author
    first_author = input("Please enter the author (e.g., agency name): ").strip()

    data = []  # Create an empty list to store each PDF's metadata in the correct format
    
    # Loop through each file in the specified folder
    for filename in os.listdir(pdf_folder):  # List all files in the folder
        if filename.endswith(".pdf"):  # Only process files that end with '.pdf'
            pdf_path = os.path.join(pdf_folder, filename)  # Create the full path for the PDF file
            
            # Extract metadata from the current PDF file
            metadata = extract_pdf_metadata(pdf_path)
            
            # Use Apache Tika's get_baseinfo to extract other relevant metadata (like publication year)
            tika_metadata = get_baseinfo({filename: {"fulltitle": metadata['title'], "url": pdf_path}}, "2025")
            publication_year = tika_metadata[filename]["pubYear"]  # Get the publication year extracted by Tika
            
            # Append the extracted metadata in the KBART format to the data list
            data.append({
                'publication_title': metadata['title'],
                'print_identifier': "Unknown Identifier",  # Placeholder
                'online_identifier': "Unknown Identifier",  # Placeholder
                'date_first_issue_online': metadata['publication_date'] if metadata['publication_date'] else "Unknown Date",
                'num_first_vol_online': "Unknown Volume",  # Placeholder
                'num_first_issue_online': "Unknown Issue",  # Placeholder
                'date_last_issue_online': metadata['publication_date'] if metadata['publication_date'] else "Unknown Date",
                'num_last_vol_online': "Unknown Volume",  # Placeholder
                'num_last_issue_online': "Unknown Issue",  # Placeholder
                'title_url': f"http://example.com/{filename}",
                'coverage_depth': "Full",
                'publication_type': "Government Publication",
                'date_monograph_published_print': "Unknown Date",  # Placeholder
                'date_monograph_published_online': "Unknown Date",  # Placeholder
                'embargo_info': "None",  # Placeholder
                'first_author': first_author,
                'publication_date': publication_year
            })
    
    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(data)
    
    # Save the DataFrame as a CSV file, without including row numbers
    output_csv = "kbart_metadata8.csv"
    df.to_csv(output_csv, index=False)
    print(f"KBART CSV generated: {output_csv}")

# Call the function to generate the CSV
generate_kbart_csv(pdf_folder)
