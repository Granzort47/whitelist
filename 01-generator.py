import requests
from bs4 import BeautifulSoup


def get_primary_domains(path):

    url = f'https://www.netify.ai/resources/applications/{path}'

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers={
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Modify the code below based on the HTML structure of the website
            primary_domains = []

            # Assuming the primary domains are listed in a specific HTML element
            # For example, if they are in <div class="primary-domains">...</div>
            primary_domains_element = soup.find(
                'ul', {'class': 'default-ul indent-2'})

            if primary_domains_element:
                # Extract primary domains from the element
                primary_domains = [
                    domain.text.strip() for domain in primary_domains_element.find_all('li')]

            return primary_domains

        else:
            print(
                f"Error: Unable to fetch content. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_bgp_prefixes(as_number):
    url = f'https://bgp.he.net/{as_number}'

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers={
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})

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


def get_txt(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers={
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Split the content into a list of lines
            ip_list = response.text.splitlines()

            return ip_list
        else:
            print(
                f"Error: Unable to download content. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def convert_list_to_singbox_ruleset(input: list, output, type):
    with open(output, 'w', newline='\n') as file:
        file.write('{\n')
        file.write('  "version": 1,\n')
        file.write('  "rules": [\n')
        file.write('    {\n')
        file.write(f'      "{type}": [\n')
        for idx, content in enumerate(input):
            if idx < len(input)-1:
                file.write(f'        "{content}",\n')
            else:
                file.write(f'        "{content}"\n')
        file.write('      ]\n')
        file.write('    }\n')
        file.write('  ]\n')
        file.write('}')


def convert_list_to_nft(input: list, output):
    with open(output, 'w', newline='\n') as file:
        name = output.replace('-', '_').split('.')[0]
        file.write(f'define {name} ')
        file.write('= {\n')
        for idx, content in enumerate(input):
            if idx < len(input)-1:
                file.write(f'    {content},\n')
            else:
                file.write(f'    {content}\n')
        file.write('}\n')


def remove_subdomains(domain_list):
    result = []
    for domain in domain_list:
        is_subdomain = False
        for other_domain in domain_list:
            if domain != other_domain and domain.endswith("." + other_domain):
                is_subdomain = True
                break
        if not is_subdomain:
            result.append(domain)
    return result


if __name__ == "__main__":
    # generate microsoft domain whitelist
    domains = []
    applications = ['microsoft-ads', 'microsoft', 'microsoft-authentication', 'office-365', 'sharepoint',
                    'teams', 'microsoft-onedrive', 'microsoft-games', 'outlook', 'windows',  'windows-update']

    for application in applications:
        result = get_primary_domains(application)
        if result:
            print(f"Download successful: {application}")
            domains = domains + result

    domains = remove_subdomains(domains)
    convert_list_to_singbox_ruleset(
        domains, 'domain-list-microsoft.json', 'domain_suffix')

    # generate apple domain whitelist
    domains = []
    applications = ['apple-itunes', 'apple', 'apple-id', 'apple-siri',
                    'apple-icloud', 'apple-mail', 'apple-push', 'apple-updates', 'apple-tv']

    for application in applications:
        result = get_primary_domains(application)
        if result:
            print(f"Download successful: {application}")
            domains = domains + result

    domains = remove_subdomains(domains)
    convert_list_to_singbox_ruleset(
        domains, 'domain-list-apple.json', 'domain_suffix')

    # generate steam domain whitelist
    domains = []
    applications = ['steam']

    for application in applications:
        result = get_primary_domains(application)
        if result:
            print(f"Download successful: {application}")
            domains = domains + result

    domains = remove_subdomains(domains)
    convert_list_to_singbox_ruleset(
        domains, 'domain-list-steam.json', 'domain_suffix')

    # generate ip whitelist
    as_numbers = ['as32590']
    for as_number in as_numbers:
        prefixes = get_bgp_prefixes(as_number)
        if prefixes:
            print(f"Download successful: {as_number}")
            convert_list_to_singbox_ruleset(
                prefixes, f'ip-list-{as_number}.json', 'ip_cidr')
            convert_list_to_nft(prefixes, f'ip-list-{as_number}.nft')

    # generate ip list: cn
    china_ip_list_url = 'https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt'
    ip_list = get_txt(china_ip_list_url)
    if ip_list:
        print(f"Download successful: china_ip_list")
        convert_list_to_singbox_ruleset(
            ip_list, 'ip-list-cn.json', 'ip_cidr')
        convert_list_to_nft(ip_list, 'ip-list-cn.nft')
