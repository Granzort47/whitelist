import requests
from bs4 import BeautifulSoup

valve_as_number = '32590'
china_ip_list_url = 'https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt'
direct_domain_list_url = 'https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/direct-list.txt'


def get_bgp_prefixes(as_number):
    url = f'https://bgp.he.net/AS{as_number}'

    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the table containing the BGP prefixes
            table = soup.find('table', {'id': 'table_prefixes4'})

            if table:
                # Extract prefixes from the table
                prefixes = [row.find('td', {'class': 'nowrap'}).text.strip(
                ) for row in table.find_all('tr')[1:]]
                return prefixes
            else:
                print(f"Error: Unable to find BGP prefixes table on {url}")
        else:
            print(
                f"Error: Unable to fetch content. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def get_txt(url, output_file):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode and write the content
            with open(output_file, 'wb') as file:
                file.write(response.content)
            print(f"Download successful. Content saved to {output_file}")
        else:
            print(
                f"Error: Unable to download content. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def convert_txt_to_nft(txt):
    # Read the content from the input text file
    with open(txt, 'r') as file:
        text = file.read()

    # Perform necessary text transformations
    # Replace newlines with commas and indentation
    text = text.replace('\n', ',\n    ')
    text = text.strip()  # Remove leading and trailing whitespaces
    text = text.strip('\n')  # Remove trailing newline characters
    text = text.strip(',')  # Remove trailing commas

    # Prepare the nft format content
    text = f'define {txt.split(".")[0]}' + ' = {\n    ' + text
    text = text + '\n}'

    # Write the nft format content to the output file
    with open(f'{txt.split(".")[0]}.nft', 'w', newline='\n') as file:
        file.write(text)


def convert_txt_to_ip_list(txt):
    # Read the content from the input text file
    with open(txt, 'r') as file:
        lines = file.readlines()

    with open(f'{txt.split(".")[0]}.json', 'w', newline='\n') as file:
        file.write('{\n')
        file.write('  "version": 1,\n')
        file.write('  "rules": [\n')
        file.write('    {\n')
        file.write('      "ip_cidr": [\n')

        for idx, line in enumerate(lines):
            if idx < len(lines)-1:
                file.write(f'        "{line[:-1]}",\n')
            else:
                file.write(f'        "{line[:-1]}"\n')
        file.write('      ]\n')
        file.write('    }\n')
        file.write('  ]\n')
        file.write('}')


if __name__ == "__main__":
    prefixes = get_bgp_prefixes(valve_as_number)
    if prefixes:
        print(f"Download successful. Content saved to valve_ip_list.txt")
        with open('valve_ip_list.txt', 'w', newline='\n') as file:
            for prefix in prefixes:
                file.write(prefix + '\n')
        convert_txt_to_nft('valve_ip_list.txt')
        convert_txt_to_ip_list('valve_ip_list.txt')

    get_txt(china_ip_list_url, 'china_ip_list.txt')
    convert_txt_to_nft('china_ip_list.txt')
    convert_txt_to_ip_list('china_ip_list.txt')
