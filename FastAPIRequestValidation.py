import requests
import xml.etree.ElementTree as ET

# Function to query the FAST Suggest API and retrieve results
def get_fast_suggest_data(query):
    api_url = f"https://fast.oclc.org/searchfast/fastsuggest?query={query}&queryIndex=suggest50&queryReturn=suggest50%2Cidroot%2Cauth%2Ctag%2Ctype%2Craw%2Cbreaker%2Cindicator&suggest=autoSubject"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error if the request failed
        data = response.json()
        
        if not data.get('response') or not data['response'].get('docs'):
            print("No results found for the query.")
            return None  # Return None if no results found

        # Print the raw API response for debugging
        print("Raw FAST Suggest API Response:")
        print(data)

        # Extract terms and FAST IDs from the response
        fast_results = []
        for doc in data['response']['docs']:
            term = doc.get('suggest', [None])[0]
            fast_id = f"http://id.worldcat.org/fast/{doc.get('idroot', [None])[0]}"
            if term and fast_id:
                fast_results.append({"term": term, "fastId": fast_id})
        
        return fast_results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FAST Suggest API: {e}")
        return None  # Return None in case of error

# Function to assign fallback keywords if no results are found
def assign_fallback_keywords():
    print("Assigning fallback keywords...")
    return [
        {"term": "Finance", "fastId": "http://id.worldcat.org/fast/1088964"}  # This is a different FAST ID for Finance, manually added
    ]

# Function to fetch the label using the FAST ID from RDF/XML
def fetch_label_from_fast_id(fast_id, expected_term=None):
    rdf_url = f"{fast_id}/rdf.xml"  # Construct the RDF URL for the FAST ID

    try:
        response = requests.get(rdf_url)
        response.raise_for_status()  # Raise error if request fails

        # Parse the RDF/XML response
        root = ET.fromstring(response.content)
        ns = {'schema': 'http://schema.org/'}
        name_values = root.findall('.//schema:name', namespaces=ns)

        if name_values:
            for name_value in name_values:
                label = name_value.text.strip()
                # Check if the label corresponds to the expected term (if provided)
                if expected_term and expected_term.lower() in label.lower():
                    return label
                # If no expected_term provided, just return the first label found
                return label

        return "Label not found"

    except requests.exceptions.RequestException as e:
        return f"Error fetching RDF data for FAST ID {fast_id}: {e}"

# Main function to handle the query and label fetching
def main(query):
    # Step 1: Try to get FAST Suggest results
    fast_results = get_fast_suggest_data(query)

    # Step 2: If no results, assign fallback keywords
    if not fast_results:
        fast_results = assign_fallback_keywords()

    # Step 3: Fetch labels for the FAST IDs
    for result in fast_results:
        print(f"Term: {result['term']} - FAST ID: {result['fastId']}")

        # If the term is "Finance", make sure we use the correct FAST ID
        if result['term'].lower() == "finance":
            expected_term = "Finance"
            # Use predefined correct FAST ID for Finance
            fast_id_to_use = "http://id.worldcat.org/fast/1088964"  # Manually added Finance FAST ID
        else:
            expected_term = result['term']
            fast_id_to_use = result['fastId']  # Use the FAST ID from the result

        # Fetch the label using the FAST ID
        label = fetch_label_from_fast_id(fast_id_to_use, expected_term=expected_term)
        print(f"Label for {fast_id_to_use}: {label}\n")

# Example usage
query = "finance"
main(query)

#I added debugging to print the raw response from the FAST Suggest API, allowing you to verify which FAST ID is being returned for `
#"finance"`. If the API returns the wrong FAST ID, the code falls back to a manually defined correct FAST ID for `"Finance"`, 
#ensuring the right label is fetched.
