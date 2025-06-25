from agents.email_finder_agent import find_email_for_website

def test_email_extraction():
    # Replace this with a real business website
    test_url = "http://versaillesmassagebar.com/"
    print(f"🔍 Testing email extraction for: {test_url}")
    result = find_email_for_website(test_url)
    print("✅ Extracted email (or result):", result)

if __name__ == "__main__":
    test_email_extraction()
