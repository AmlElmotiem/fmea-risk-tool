from fmea_tool import FailureMode, FMEAAnalysis, to_dataframe, write_csv


def test_to_dataframe_has_expected_columns_and_is_ranked():
    analysis = FMEAAnalysis(title="t")
    analysis.add(FailureMode("A", "f", "low-risk", "e", 2, 2, 2))
    analysis.add(FailureMode("B", "f", "high-risk", "e", 9, 8, 7))

    df = to_dataframe(analysis)
    assert list(df.columns) == [
        "Komponente", "Funktion", "Fehlerart", "Auswirkung",
        "S", "A", "E", "RPN", "Risiko", "Empfohlene Maßnahme",
    ]
    assert df.iloc[0]["Fehlerart"] == "high-risk"  # highest RPN first


def test_write_csv_creates_a_readable_file(tmp_path):
    analysis = FMEAAnalysis(title="t")
    analysis.add(FailureMode("A", "f", "fm", "e", 5, 5, 5))
    csv_path = tmp_path / "report.csv"

    write_csv(analysis, csv_path)

    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "RPN" in content
    assert "125" in content
