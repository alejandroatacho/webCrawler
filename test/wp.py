import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import dotenv


def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as error:
        print(f"Error fetching URL: {error}")
        return None


def check_wordpress_paths(url):
    common_paths = [
        'wp-admin'
    ]
    issues = []
    for path in common_paths:
        full_url = f"{url}/{path}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                issues.append({
                    'path': path,
                    'url': full_url,
                    'status_code': response.status_code
                })
        except requests.exceptions.RequestException as error:
            issues.append({
                'path': path,
                'url': full_url,
                'error': str(error)
            })
    return issues


def parse_homepage(html):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []

    # Check for WordPress generator meta tag
    generator_meta = soup.find('meta', attrs={'name': 'generator'})
    if generator_meta and 'WordPress' in generator_meta.get('content', ''):
        issues.append({
            'issue': 'WordPress generator meta tag found',
            'content': generator_meta.get('content', '')
        })

    # Check for default themes
    default_themes = ['twentytwenty', 'twentynineteen', 'twentysixteen']
    for theme in default_themes:
        if soup.find('link', href=lambda href: href and f"wp-content/themes/{theme}" in href):
            issues.append({
                'issue': f"Default theme detected: {theme}",
                'theme': theme
            })
    return issues


def save_issues(issues, filename):
    df = pd.DataFrame(issues)
    df.to_csv(filename, index=False)


def main():
    dotenv.load_dotenv()
    url = os.getenv('URL_TARGET')
    path_issues = check_wordpress_paths(url)
    homepage_html = fetch_url(url)
    homepage_issues = []
    if homepage_html:
        homepage_issues = parse_homepage(homepage_html)

    all_issues = path_issues + homepage_issues
    print(f"Found {len(all_issues)} issues on {url}:")
    for issue in all_issues:
        print(issue)

    save_issues(all_issues, 'wordpress_issues.csv')
    save_issues(all_issues, 'wordpress_issues.json')


if __name__ == "__main__":
    main()
