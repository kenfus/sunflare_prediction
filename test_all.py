from database_utils import (
    extract_instrument_name,
    numbers_list_to_postgresql_columns_meta_data,
    np_array_to_postgresql_array,
)
from data_creation import download_ecallisto_files
from database_utils import (
    glob_files,
    create_dict_of_instrument_paths,
    extract_separate_instruments,
    combine_non_unique_frequency_axis_mean,
)
import pytest
import numpy as np
from datetime import datetime
import os


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            "/var/lib/ecallisto/2023/01/27/ALASKA-COHOE_20230127_001500_612.fit.gz",
            "alaska_cohoe_612",
        ),
        (
            "/random_2313/ecallisto/2023/01/27/ALASKA_COHOE_20230127_001500_61212.fit.gz",
            "alaska_cohoe_61212",
        ),
        (
            "/random_2313/ecallisto/2023/01/27/ALASKA_COHOE_20230127_001500.fit.gz",
            "alaska_cohoe",
        ),
        (
            "/ran3123öü¨ö23üöeaöd¨üö2¨/ecallisto/2023/01/27/FHN_W_20230127_001500_11.fit.gz",
            "fhn_w_11",
        ),
    ],
)
def test_instrument_name_extraction(test_input, expected):
    assert extract_instrument_name(test_input) == expected


@pytest.mark.parametrize(
    "names, types, expected",
    [
        (
            ["test", "test2", "test3"],
            ["int", "float", "varchar"],
            "test int, test2 float, test3 varchar",
        ),
        (
            [3133213, 1, 0.0],
            ["int", "float", "varchar"],
            '"3133213" int, "1" float, "0.0" varchar',
        ),
        (
            [31.3, "testa", 0.013],
            ["int", "varchar", "varchar"],
            '"31.3" int, testa varchar, "0.013" varchar',
        ),
    ],
)
def test_sql_column_creation(names, types, expected):
    assert numbers_list_to_postgresql_columns_meta_data(names, types) == expected


class TestDataCreation:
    def test_file_download(self, instrument="ALASKA-COHOE", dir="test_data"):
        """Test that the file download works."""
        download_ecallisto_files(
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2021, 1, 1),
            instrument=instrument,
            dir=dir,
        )
        assert all(
            instrument in file
            for file in os.listdir(os.path.join(dir, "2021", "01", "01"))
        )

    def test_globbing(self, dir="test_data"):
        file_paths = glob_files(
            dir, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 1)
        )
        assert len(file_paths) == 48

    def test_extraction_of_instrument_names(self, dir="test_data"):
        file_paths = glob_files(
            dir, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 1)
        )
        instruments = extract_separate_instruments(file_paths)
        assert len(instruments) == 2
        assert "alaska_cohoe_00" in instruments
        assert "alaska_cohoe_01" in instruments

    def test_dict_of_instruments_paths(self, dir="test_data"):
        file_paths = glob_files(
            dir, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 1)
        )
        instruments = create_dict_of_instrument_paths(file_paths)
        assert len(instruments) == 2
        assert "alaska_cohoe_00" in instruments
        assert "alaska_cohoe_01" in instruments
        assert len(instruments["alaska_cohoe_00"]) == 24
        assert len(instruments["alaska_cohoe_01"]) == 24

    def test_remove_files(self, dir="test_data"):
        file_paths = glob_files(
            dir, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 1)
        )
        assert len(file_paths) > 0
        for file in file_paths:
            os.remove(file)
        file_paths = glob_files(
            dir, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 1)
        )
        assert len(file_paths) == 0


@pytest.mark.parametrize(
    "input,expected",
    [
        (np.array([[1, 2, 3], [4, 5, 6]]), "(1, 2, 3),(4, 5, 6)"),
        (np.array([[1, 2, 3]]), "(1, 2, 3)"),
    ],
)
def test_np_array_to_postgresql_array(input, expected):
    assert np_array_to_postgresql_array(input) == expected


def test_combine_non_unique_frequency_axis_mean():
    index = np.array([1, 2, 2, 3, 3, 3, 4, 5, 5])
    data = np.array(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
            [13, 14, 15],
            [16, 17, 18],
            [19, 20, 21],
            [22, 23, 24],
            [25, 26, 27],
        ]
    )
    result, unique_idxs = combine_non_unique_frequency_axis_mean(index, data)

    expected_result = np.array(
        [
            [1, 2, 3],
            [(4 + 7) / 2, (5 + 8) / 2, (6 + 9) / 2],
            [(10 + 13 + 16) / 3, (11 + 14 + 17) / 3, (12 + 15 + 18) / 3],
            [19, 20, 21],
            [(22 + 25) / 2, (23 + 26) / 2, (24 + 27) / 2],
        ]
    )
    expected_unique_idxs = np.array([1, 2, 3, 4, 5])

    assert np.array_equal(result, expected_result)
    assert np.array_equal(unique_idxs, expected_unique_idxs)
