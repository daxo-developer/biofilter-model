import pandas as pd
from unittest.mock import patch
from bio_model.data_loader import load_usgs_data

@patch("requests.get")
def test_load_usgs_data_mock(mock_get):
    mock_rdb = (
        "# This is a comment line\n"
        "agency_cd\tsite_no\tdatetime\ttz_cd\t00631_00000\t00631_00000_cd\n"
        "USGS\t01646500\t2023-01-01 00:00\tEST\t1.2\tA\n"
        "USGS\t01646500\t2023-01-01 01:00\tEST\t1.1\tA\n"
    )
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = mock_rdb

    df = load_usgs_data(site="01646500", parameter="00631",
                        start="2023-01-01", end="2023-01-02")
    assert isinstance(df, pd.DataFrame)
    assert "time_days" in df.columns
    assert "inlet" in df.columns
    assert "outlet" in df.columns
    assert len(df) == 2

def test_load_local_data(tmp_path):
    from bio_model.data_loader import load_local_data
    df_test = pd.DataFrame({
        'time_days': [0.0, 1.0, 2.0],
        'inlet': [1.0, 1.1, 1.2],
        'outlet': [0.9, 0.95, 1.0]
    })
    csv_path = tmp_path / "test_data.csv"
    df_test.to_csv(csv_path, index=False)
    df_loaded = load_local_data(str(csv_path))
    pd.testing.assert_frame_equal(df_test, df_loaded)
