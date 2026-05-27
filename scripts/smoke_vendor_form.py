"""Smoke-test vendor profile UI against a running dev server."""
import re
import sys
import http.cookiejar
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:8004'
USERNAME = 'admin'
PASSWORD = 'admin123'


class Client:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))

    def get(self, url):
        req = urllib.request.Request(url, method='GET')
        with self.opener.open(req, timeout=15) as resp:
            return resp.status, resp.read().decode('utf-8', errors='replace'), resp.geturl()

    def post(self, url, data, referer):
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(
            url,
            data=body,
            method='POST',
            headers={'Referer': referer, 'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with self.opener.open(req, timeout=15) as resp:
            return resp.status, resp.read().decode('utf-8', errors='replace'), resp.geturl()


def main():
    c = Client()
    status, html, _ = c.get(f'{BASE}/login/')
    if status != 200:
        print(f'FAIL: login page {status}')
        sys.exit(1)
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    if not m:
        print('FAIL: CSRF on login')
        sys.exit(1)
    status2, _, url2 = c.post(
        f'{BASE}/login/',
        {'csrfmiddlewaretoken': m.group(1), 'username': USERNAME, 'password': PASSWORD},
        f'{BASE}/login/',
    )
    if status2 not in (200, 302) or 'login' in url2.lower():
        print('FAIL: login — use: python manage.py seed_erp_data --reset-admin-password')
        sys.exit(1)
    print('OK: Logged in')

    manage = f'{BASE}/parties/1/roles/1/manage/'
    status4, page, _ = c.get(manage)
    if status4 != 200:
        print(f'FAIL: GET manage -> {status4}')
        sys.exit(1)
    for label in (
        'Vendor Type',
        'Vendor Category',
        'Vendor Sub Category',
        'Office Status',
        'vendor-subcategories-data',
        'vendor_form.js',
        'vendor-master-save',
    ):
        if label not in page:
            print(f'FAIL: missing {label}')
            sys.exit(1)
    print('OK: Vendor tab UI')

    m2 = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page)
    if not m2:
        print('FAIL: CSRF on manage page')
        sys.exit(1)

    def first_option(field):
        hit = re.search(rf'name="{field}"[^>]*>.*?<option value="(\d+)"', page, re.S)
        return hit.group(1) if hit else None

    vt, vc, vsc = first_option('vendor_type'), first_option('vendor_category'), first_option('vendor_sub_category')
    if vt and vc and vsc:
        status5, _, _ = c.post(
            manage,
            {
                'csrfmiddlewaretoken': m2.group(1),
                'company_name': 'UI Verified Vendor',
                'vendor_type': vt,
                'vendor_category': vc,
                'vendor_sub_category': vsc,
                'office_status': 'inactive',
                'gst_no': '',
                'dispatch_location': 'Pune',
                'bank-TOTAL_FORMS': '0',
                'bank-INITIAL_FORMS': '0',
                'bank-MIN_NUM_FORMS': '0',
                'bank-MAX_NUM_FORMS': '1000',
                'contact-TOTAL_FORMS': '0',
                'contact-INITIAL_FORMS': '0',
                'contact-MIN_NUM_FORMS': '0',
                'contact-MAX_NUM_FORMS': '1000',
                'document-TOTAL_FORMS': '0',
                'document-INITIAL_FORMS': '0',
                'document-MIN_NUM_FORMS': '0',
                'document-MAX_NUM_FORMS': '1000',
            },
            manage,
        )
        if status5 not in (200, 302):
            print(f'FAIL: POST save -> {status5}')
            sys.exit(1)
        print('OK: Save submitted')

    print(f'Open: {manage}')


if __name__ == '__main__':
    main()
