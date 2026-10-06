from pathlib import Path

from residency_watch import extract

FIX = Path(__file__).parent / "fixtures"
NOW = 2026 * 12 + 9  # October 2026
TARGET = 2027 * 12 + 7  # August 2027


def rel(text):
    return extract.classify(extract.find_cohorts(text, NOW), TARGET, None)


def test_classify_dates():
    assert rel("Residency – October 2027") == "target"
    assert rel("Graduate Nurse Residency February 2028 cohort") == "target"
    assert rel("Residency – July 2027") == "early"
    assert rel("RN Residency Program – Fall 2027") == "target"
    assert rel("Summer 2027 cohort") == "maybe"  # could start June, July or August
    assert rel("Winter 2028 cohort") == "target"
    assert rel("Winter 2027 cohort") == "early"
    assert rel("2028 cohort") == "target"
    assert rel("2027 cohort") == "maybe"
    assert rel("Graduate Nurse Residency") == "unknown"
    assert rel("Sept. 14, 2027 start") == "target"


def test_target_until():
    cohorts = extract.find_cohorts("June 2028 cohort", NOW)
    assert extract.classify(cohorts, TARGET, 2028 * 12 + 2) == "late"


def test_residency_titles():
    assert extract.is_residency_title("Graduate Nurse (GN) Residency - MICU")
    assert extract.is_residency_title("New Grad RN Residency - Med Surg")
    assert extract.is_residency_title("RN Residency Program – February 2027 Cohort Med/Surg Units")
    assert extract.is_residency_title("Nurse Resident - Methodist Dallas Medical Center - February 2027")
    assert not extract.is_residency_title("PGY1 Pharmacy Residency")
    assert not extract.is_residency_title("Registered Nurse - Emergency")
    assert not extract.is_residency_title("Nurse Practitioner Fellowship")
    assert not extract.is_residency_title("Student Nurse Extern - Summer 2027")


def test_jobs_board():
    page = extract.analyze((FIX / "jobs_board.html").read_text(), "https://jobs.example.org/search", "jobs", NOW)
    by_title = {i.title: i for i in page.items}
    oct_ = by_title["Graduate Nurse (GN) Residency - MICU - October 2027"]
    assert oct_.url == "https://jobs.example.org/job/222/gn-residency-icu-oct-2027"
    assert "Dallas" in oct_.context
    assert extract.classify(oct_.cohorts, TARGET, None) == "target"
    assert extract.classify(by_title["Graduate Nurse Residency (Medical Surgical) – February 2027"].cohorts, TARGET, None) == "early"
    assert extract.classify(by_title["Graduate Nurse Residency, Mom/Baby, Fall Cohort – Full Time"].cohorts, TARGET, None) == "unknown"
    assert "Nurse Resident - Summer 2027 Cohort" in by_title  # pulled from embedded JSON
    assert "Arlington" in by_title["Nurse Resident - Summer 2027 Cohort"].context
    assert "PGY1 Pharmacy Residency" not in by_title
    assert "Registered Nurse - Emergency" not in by_title


def test_program_page():
    page = extract.analyze((FIX / "program_page.html").read_text(), "https://example.org/residency", "page", NOW)
    snippets = [i for i in page.items if i.kind == "snippet"]
    target = [s for s in snippets if extract.classify(s.cohorts, TARGET, None) == "target"]
    assert len(target) == 1 and "October 2027" in target[0].title
    assert target[0].signal == "open"
    assert page.page_signal == "open"
