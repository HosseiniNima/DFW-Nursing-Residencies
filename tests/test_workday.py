from residency_watch import workday
from residency_watch.fetch import FetchResult

NOW = 2026 * 12 + 9


def test_api_url():
    assert workday.api_url("https://wd12.myworkdaysite.com/en-US/recruiting/parklandhospital/Parkland_Careers") == (
        "https://wd12.myworkdaysite.com/wday/cxs/parklandhospital/Parkland_Careers/jobs",
        "https://wd12.myworkdaysite.com/en-US/recruiting/parklandhospital/Parkland_Careers",
    )
    assert workday.api_url("https://adventhealth.wd12.myworkdayjobs.com/en-US/AH_External_Career_Site") == (
        "https://adventhealth.wd12.myworkdayjobs.com/wday/cxs/adventhealth/AH_External_Career_Site/jobs",
        "https://adventhealth.wd12.myworkdayjobs.com/en-US/AH_External_Career_Site",
    )


class FakeFetcher:
    def __init__(self):
        self.payloads = []

    def post_json(self, url, payload):
        self.payloads.append(payload)
        data = {"total": 3, "jobPostings": [
            {"title": "Nurse Resident - ICU - October 2027", "externalPath": "/job/Dallas/Nurse-Resident_R1", "locationsText": "Dallas, TX"},
            {"title": "Registered Nurse - ED", "externalPath": "/job/Dallas/RN_R2", "locationsText": "Dallas, TX"},
            {"title": "PGY1 Pharmacy Residency", "externalPath": "/job/Dallas/Pharm_R3", "locationsText": "Dallas, TX"},
        ]}
        return FetchResult(url, url, 200, "{}", "api", None, data)


def test_search():
    f = FakeFetcher()
    res, items = workday.search(f, "https://wd12.myworkdaysite.com/en-US/recruiting/parklandhospital/Parkland_Careers", ["nurse resident"], NOW)
    assert res.ok and [i.title for i in items] == ["Nurse Resident - ICU - October 2027"]
    assert items[0].url == "https://wd12.myworkdaysite.com/en-US/recruiting/parklandhospital/Parkland_Careers/job/Dallas/Nurse-Resident_R1"
    assert items[0].cohorts[0].label == "October 2027"
    assert f.payloads[0]["searchText"] == "nurse resident"
