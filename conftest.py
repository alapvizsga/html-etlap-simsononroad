import json
import pytest  # A Pytest framework importálása

# Eredmények tárolására használt lista
results = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """ 
    Ez a hook minden teszt után lefut. 
    Az aktuális teszt eredményét egy listában tárolja, majd ezt a listát
    a pytest_sessionfinish menti el egy JSON fájlba.
    """

    outcome = yield  # Az aktuális teszt eredményének begyűjtése
    report = outcome.get_result()  # A pytest által generált riport megszerzése

    if report.when == "call":  # Csak a tényleges tesztfutás fázisában érdekes
        points = item.get_closest_marker("points")  # Megnézzük, van-e @pytest.mark.points annotáció
        score = points.args[0] if points else 0  # Ha van, kiszedjük a pontértéket

        results.append({
            "name": item.name,  # A teszt neve
            "status": "passed" if report.passed else "failed",  # Sikeres vagy sikertelen
            "points": score  # A teszt által adott pontok
        })

def pytest_sessionfinish(session, exitstatus):
    """
    Ez a hook a teljes tesztfuttatás végén lefut. 
    Az összegyűjtött eredményeket JSON formátumban menti el egy fájlba.
    """

    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)  # Eredmények mentése JSON formátumban, olvasható módon


def pytest_collection_modifyitems(config, items):
    for item in items:
        points = item.get_closest_marker("points")
        if points:
            item.user_properties.append(("points", points.args[0]))

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Summarize total points after all tests run."""
    total_points = 0
    earned_points = 0

    for report in terminalreporter.stats.get("passed", []):
        for prop in report.user_properties:
            if prop[0] == "points":
                earned_points += prop[1]
                total_points += prop[1]

    for report in terminalreporter.stats.get("failed", []):
        for prop in report.user_properties:
            if prop[0] == "points":
                total_points += prop[1]

    terminalreporter.write("\n===== Értékelés eredménye =====\n")
    terminalreporter.write(f"Elért pontok: {earned_points}/{total_points}\n")
