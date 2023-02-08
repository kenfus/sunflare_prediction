from database_functions import *
from database_utils import *
import argparse
from data_creation import download_ecallisto_files, LOCAL_DATA_FOLDER
from datetime import datetime, timedelta

def main(start_date, end_date, instrument="all", dir=LOCAL_DATA_FOLDER):
    download_ecallisto_files(
        instrument=instrument, start_date=start_date, end_date=end_date, dir=dir
    )

if __name__ == "__main__":
    ## Example:
    # python download_ecallisto_files.py --start_date 2020-01-01 --end_date 2020-01-02 --instrument all
    # Get arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_date",
        type=str,
        default=(datetime.today().date() - timedelta(days=14)))
    parser.add_argument(
        "--end_date",
        type=str,
        default=datetime.today().date())
    parser.add_argument(
        "--instrument",
        type=str,
        default="all")
    parser.add_argument(
        "--dir",
        type=str,
        default=LOCAL_DATA_FOLDER)
    args = parser.parse_args()
    # Update to correct types
    args.start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    args.end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    # Main
    main(**vars(args))
    
    