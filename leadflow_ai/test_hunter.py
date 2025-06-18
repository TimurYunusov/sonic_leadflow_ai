from services.hunter import get_contacts

def test_hunter():
    domain = "hyatt.com"  # Replace with a domain you want to test
    contacts = get_contacts(domain)
    print("Contacts:", contacts)

# Run the test
if __name__ == "__main__":
    test_hunter()
