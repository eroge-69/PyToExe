"""
This script analyzes temperature and humidity data stored in csv files and stores the resulting plot in a png file plus
the extrema in a json file
"""
import json
import os
import pandas as pd
import shutil
import sys
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Union

# ------------------------------------------------- Configuration -----------------------------------------------------#

MEDIAN_FILTER_SIZE: int = 5
LOGGING_INTERVAL_MIN: int = 30

FILEPATH_DATALOGGER_DATA: Path = Path(os.getcwd() + "\\csv_files")
FILEPATH_DATALOGGER_EXTREMA: Path = \
    Path("M:\\Org\\AIRE\\AIREO\\SHARED\\Betriebsmittel Analyse\\Betriebsmittel Analyse.xlsm")

EXTREMA_COLUMN_CONVERTER: Dict[str, str] = {
    "Reg.Nr.": "q_number",
    "Min Temperatur [°C]": "min temperature [°C]",
    "Max Temperatur [°C]": "max temperature [°C]",
    "Min Feuchte [%]": "min relative humidity [%]",
    "Max Feuchte [%]": "max relative humidity [%]",
}

DATA_COLUMN_CONVERTER: Dict[str, str] = {
    "Datum": "timestamp",
    "Temp": "temperature [°C]",
    "RH": "relative humidity [%]"
}

LABEL_COLOR: Dict[str, str] = {"temperature [°C]": "red", "relative humidity [%]": "blue"}


# ---------------------------------------------------- Helpers ------------------------------------------------------- #
def get_user_input(string: str) -> datetime:
    """
    Let user specify the start and end date to which the time frame shall be clipped
    :param string: name of the time the user needs to input
    :return: time: time to which the dataframe shall be clipped
    """
    while True:
        user_input: Union[datetime, str, None] = input(
            f"Enter {string} in \"DD.MM.YYYY\" format (or enter \"esc\" to exit program): "
        )
        try:
            if user_input == "esc":
                sys.exit(0)
            user_input = datetime.strptime(user_input, "%d.%m.%Y")
            break
        except ValueError:
            print("Wrong input, please try again.")
    return user_input


def read_datalogger_extrema_data(file_path_datalogger_extrema: Path, extrema_column_converter: Dict[str, str]) \
        -> pd.DataFrame:
    """
    Load the allowed temperature and humidity min-max values of all data logger
    :param file_path_datalogger_extrema: file path to the min max values of all data loggers
    :param extrema_column_converter: dictionary to rename the colum names of the min max data logger dataframe
    :return datalogger_dataframe: Pandas dataframe containing temperature & humidity min-max data of all datalogger
    """
    if not file_path_datalogger_extrema.exists():
        raise FileNotFoundError(f"File not found: {file_path_datalogger_extrema}!")
    if os.path.splitext(file_path_datalogger_extrema)[1].lower() not in ['.xlsx', ".xlsm"]:
        raise FileNotFoundError(f"File path does not lead to a .xlsx or .xlsm file: {file_path_datalogger_extrema}!")

    datalogger_dataframe: pd.DataFrame = pd.read_excel(file_path_datalogger_extrema, sheet_name="Datenlogger",
                                                       header=1)[extrema_column_converter.keys()]
    datalogger_dataframe.rename(columns=extrema_column_converter, inplace=True)

    if datalogger_dataframe.empty:
        raise ValueError(f"Dataframe of file {file_path_datalogger_extrema} is empty!")

    return datalogger_dataframe


def get_name_and_columns(filepath: Path) -> [str, int]:
    """
    Get name of data logger and nr of columns from csv file
    :param filepath: filepath of csv file
    :return name of data logger and the number of columns of the dataframe
    """
    with open(filepath, mode="r", encoding="utf-8") as reader:
        logger_name: str = reader.readline().split(":")[1][1:-2].replace(' ', '_')
        reader.readline()
        number_columns: int = len(reader.readline().split(","))
    return logger_name, number_columns


def read_to_dataframe(filepath: Path, number_columns: int, column_converter: Dict[str, str],
                      start_time: datetime, end_time: datetime) -> pd.DataFrame:
    """
    Read csv file excluding first row and column
    :param filepath: filepath of csv file
    :param number_columns: number of columns of csv file
    :param column_converter: dictionary to rename the column headers
    :return dataframe: dataframe containing all logged temperature and humidity data
    :param start_time: user defined start time
    :param end_time: user defined end time
    :return dataframe: dataframe containing logger date in specified time range
    """
    # Read data frame
    dataframe: pd.DataFrame = pd.read_csv(filepath, header=1, usecols=range(1, number_columns))

    # Convert column names
    dataframe.columns = [column_converter[x] for x, y in zip(column_converter.keys(), dataframe.columns) if x in y]

    # Convert data types of columns "timestamp", "temperature" and "humidity"
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
    dataframe["temperature [°C]"] = dataframe["temperature [°C]"].astype(float)
    "relative_humidity [%]" in dataframe.columns and dataframe["relative_humidity [%]"].astype(float)

    # Prune dataframe to selected time range if possible
    if start_time > dataframe["timestamp"].max() or end_time < dataframe["timestamp"].min():
        raise ValueError(f"File {os.path.split(filepath)[-1]} does not contain any data for the selected time range!")

    dataframe = dataframe[(start_time <= dataframe["timestamp"]) & (dataframe["timestamp"] <= end_time)]

    return dataframe


def rolling_median(dataframe: pd.DataFrame, median_filter_size: int) -> pd.DataFrame:
    """
    Apply rolling median with specified window size to all columns of the dataframe except the timestamp column
    :param dataframe: dataframe
    :param median_filter_size: window size of the rolling median
    :return: dataframe_median: median-filtered dataframe
    """
    dataframe.loc[:, dataframe.columns != "timestamp"] = dataframe.loc[:, dataframe.columns != "timestamp"]. \
        rolling(median_filter_size, center=True, min_periods=1).median()
    return dataframe


def get_measured_extrema(dataframe_median: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, Union[float, datetime]]]]:
    """
    Find the min/max values of all data columns and store them in dictionary together with the respective timestamps
    :param dataframe_median: median-filtered dataframe
    :return: measured_extrema_dict: dictionary containing all min/max values with their timestamps
    """
    measured_extrema_dict: Dict[str, Dict[str, Dict[str, Union[float, datetime]]]] = {}

    for col in dataframe_median.loc[:, dataframe_median.columns != "timestamp"].columns:
        min_idx = dataframe_median[col].idxmin()
        max_idx = dataframe_median[col].idxmax()

        measured_extrema_dict[col] = {
            'min': {"value": dataframe_median.at[min_idx, col], "timestamp": dataframe_median.at[min_idx, 'timestamp']},
            'max': {"value": dataframe_median.at[max_idx, col], "timestamp": dataframe_median.at[max_idx, 'timestamp']}
        }
    return measured_extrema_dict


def get_allowed_extrema(extrema_dataframe: pd.DataFrame, dataframe_median: pd.DataFrame, logger_name: str) \
        -> Dict[str, Dict[str, float]]:
    """
    Get allowed min-max values of temperature and humidity from
    :param extrema_dataframe: dictionary containing all allowed min/max values from Consumables Master List
    :param dataframe_median: median-filtered dataframe
    :param logger_name: data logger name
    :return: allowed_extrema_dict: dictionary containing all allowed min-max values for temperature and humidity
    """
    q_number = logger_name.split("_")[0]
    allowed_extrema_dict: Dict[str, Dict[str, float]] = {}

    for col in dataframe_median.loc[:, dataframe_median.columns != "timestamp"].columns:
        if q_number not in extrema_dataframe["q_number"].values:
            raise ValueError(f"Datalogger {q_number} does not exist in Master Excel list!")

        allowed_extrema_dict[col] = {
            'min': float(extrema_dataframe.loc[extrema_dataframe["q_number"] == q_number, f"min {col}"]),
            'max': float(extrema_dataframe.loc[extrema_dataframe["q_number"] == q_number, f"max {col}"]),
        }
    return allowed_extrema_dict


def create_figure(dataframe_median: pd.DataFrame, logger_name: str) -> Axes:
    """
    Create the figure canvas to plot the data.
    :param dataframe_median: median-filtered dataframe
    :param logger_name: Name of the temperature logger
    :return ax1: axis of the figure
    """
    fig: Figure
    ax1: Axes
    fig, ax1 = plt.subplots(num=logger_name)
    fig.set_size_inches(10, 5)
    fig.suptitle(logger_name, fontsize=10)
    ax1.set_title(
        f"time period:   {dataframe_median['timestamp'].iat[0].strftime('%d.%m.%Y')}   to   "
        f"{dataframe_median['timestamp'].iat[-1].strftime('%d.%m.%Y')}",
        fontsize=8
    )
    ax1.set_xlabel("timestamp", fontsize=8)
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.xaxis.grid(zorder=1)
    return ax1


def plot_data(dataframe_median: pd.DataFrame, allowed_extrema_dict: Dict[str, Dict[str, float]],
              label_color_dict: Dict[str, str], label: str, axis: Axes) -> None:
    """
    Plot the data from the dataframe on the figure canvas.
    :param dataframe_median: median-filtered dataframe
    :param allowed_extrema_dict: dictionary containing all allowed min-max values for temperature and humidity
    :param label_color_dict: dictionary containing the colors for the respective data labels
    :param label: name of the data referring to this axis
    :param axis: y-axis for the selected data
    """
    axis.set_ylabel(label, color=label_color_dict[label], fontsize=8)
    axis.plot(dataframe_median["timestamp"], dataframe_median[label], label=label, color=label_color_dict[label],
              linestyle="-", linewidth=0.5, alpha=0.9, zorder=2)

    # Plot horizontal min-max lines
    axis.hlines([allowed_extrema_dict[label]["min"], allowed_extrema_dict[label]["max"]],
                dataframe_median['timestamp'].iat[0], dataframe_median['timestamp'].iat[-1],
                color=label_color_dict[label], linestyle=":", linewidth=0.8, zorder=1)


def adjust_x_axis(dataframe_median: pd.DataFrame, axis: Axes) -> None:
    """
    Adjust min-max range of y-axes and define their tickers
    :param dataframe_median: median-filtered dataframe
    :param axis: first y-axis for the temperature
    """
    axis.set_xlim(xmin=dataframe_median['timestamp'].iat[0], xmax=dataframe_median['timestamp'].iat[-1])
    axis.xaxis.set_major_formatter(dates.DateFormatter('%d.%m.%y'))
    if (dataframe_median['timestamp'].iat[-1] - dataframe_median['timestamp'].iat[0]).days > 90:
        axis.xaxis.set_major_locator(dates.MonthLocator())
        axis.minorticks_on()
    else:
        axis.xaxis.set_major_locator(dates.DayLocator(bymonthday=[1, 7, 14, 21, 28]))
        axis.xaxis.set_minor_locator(dates.DayLocator())


def adjust_y_axis(measured_extrema_dict: Dict[str, Dict[str, Dict[str, Union[float, datetime]]]],
                  allowed_extrema_dict: Dict[str, Dict[str, float]], axis: Axes, label: str) -> None:
    """
    Adjust min-max range of the y-axis and define the ticker spacing
    :param measured_extrema_dict: dictionary containing the min-max temperature and humidity values plus timestamps
    :param allowed_extrema_dict: dictionary containing the allowed temperature and humidity values
    :param axis: y-axis for the respective data
    :param label: name of the data referring to this axis
    """
    y_min: float = 0
    y_max: float = 0
    major_ticker_space: float = 0
    minor_ticker_space: float = 0
    if label == "temperature [°C]":
        y_min = min(measured_extrema_dict[label]["min"]["value"], allowed_extrema_dict[label]["min"])
        y_max = round(max(measured_extrema_dict[label]["max"]["value"], allowed_extrema_dict[label]["max"]) + 1.4)
        ticker_spacing: float = 1 if abs(y_max - y_min) < 15 else 2
        major_ticker_space = ticker_spacing
        minor_ticker_space = ticker_spacing / 2

    elif label == "relative humidity [%]":
        y_min = 0
        y_max = round(
            (max(measured_extrema_dict[label]["max"]["value"], allowed_extrema_dict[label]["max"]) + 9) / 10) * 10
        major_ticker_space = 10
        minor_ticker_space = 5

    axis.set_ylim(ymin=y_min, ymax=y_max)
    axis.tick_params(which="major", labelsize=8)
    axis.yaxis.set_major_locator(ticker.MultipleLocator(major_ticker_space))
    axis.yaxis.set_minor_locator(ticker.MultipleLocator(minor_ticker_space))


def annotate_min_max_borders(dataframe_median: pd.DataFrame, allowed_extrema_dict: Dict[str, Dict[str, float]],
                             label_color_dict: Dict[str, str], label: str, axis: Axes) -> None:
    """
    Annotate the min max borders of the plotted data
    :param dataframe_median: median-filtered dataframe
    :param allowed_extrema_dict: dictionary containing the allowed temperature and humidity values
    :param label_color_dict: dictionary containing the colors for the respective data labels
    :param axis: axis for the respective data
    :param label: name of the data referring to this axis
    """
    x_pos = 10 if "temp" in label else -10
    text_align = "left" if x_pos > 0 else "right"

    for val, name in [(allowed_extrema_dict[label]["min"], "min allowed"),
                      (allowed_extrema_dict[label]["max"], "max allowed")]:
        axis.annotate(f"{name} {label.split('[')[0].strip()}", xy=(dataframe_median['timestamp'].iat[x_pos], val),
                      xytext=(1.0, 3.0), ha=text_align, size=8, color=label_color_dict[label],
                      textcoords='offset points', zorder=100,
                      bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))


def annotate_extrema(dataframe_median: pd.DataFrame, label_color_dict: Dict[str, str], label: str, axis: Axes) -> None:
    """
    Annotate the extrema in the plot
    :param dataframe_median: median-filtered dataframe
    :param label_color_dict: dictionary containing the colors for the respective data labels
    :param label: name of the data referring to this axis
    :param axis: y-axis for the respective data
    """
    for val_type in ['min', 'max']:
        idx = dataframe_median[label].idxmin() if val_type == 'min' else dataframe_median[label].idxmax()
        val = dataframe_median[label].min() if val_type == 'min' else dataframe_median[label].max()
        y = -10 if val_type == 'min' else 5

        # Marker
        axis.plot(dataframe_median['timestamp'][idx], val,
                  marker="o", markersize=5, markeredgewidth=1.0, markeredgecolor="black", markerfacecolor="none",
                  zorder=18)

        # Annotation
        axis.annotate(f"{val_type}", xy=(dataframe_median['timestamp'][idx], val), xytext=(0, y), ha='center', size=8,
                      color=label_color_dict[label], textcoords='offset points', zorder=100,
                      bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))


def save_results(directory: Path, filepath: Path, logger_name: str,
                 measured_extrema_dict: Dict[str, Dict[str, Dict[str, Union[float, datetime]]]]) -> None:
    """
    Save the results in separate directory including moving the provided data file
    :param directory: file path to the current directory
    :param filepath: file path of the current datafile
    :param logger_name: name of the data logger
    :param measured_extrema_dict: dictionary containing the min-max temperature and humidity values plus timestamps
    """
    # Create new directory to save the results
    result_name: str = \
        "".join(c for c
                in f"\\{str(datetime.now().replace(microsecond=0)).translate(str.maketrans({':': '-', ' ': '_'}))}"
                   f"_{logger_name}"
                if c.isalnum() or c in "-_.()")
    new_directory: Path = Path(str(directory) + "\\" + result_name)
    new_directory.mkdir()

    # Save figure
    plt.tight_layout()
    plt.savefig(str(new_directory) + "\\" + f"{result_name}.png", bbox_inches='tight', dpi=600)

    # Save extrema in json file
    with open(str(new_directory) + "\\" + f"{result_name}.json", "w") as file:
        json.dump(measured_extrema_dict, file, indent=4, default=str)

    # Move data file to created directory
    try:
        shutil.move(filepath, new_directory)
    except PermissionError:
        print(
            f"\033[91mThe process cannot move the file {filepath} properly because it is being used by another process"
            f"\n-> Please delete the file manually\033[0m"
        )


# ------------------------------------------------- Main pipeline ---------------------------------------------------- #

def main() -> None:
    """
    Main function where parameters and order of function calls can be adjusted
    """
    # Create directory if it does not exist yet
    FILEPATH_DATALOGGER_DATA.mkdir(parents=True, exist_ok=True)

    # User input
    print(f"\nPlace the datalogger files you want to visualize in the following directory: {os.getcwd()}\\csv_files\n")
    start_time: datetime = datetime.strptime(get_user_input("start time").strftime("%Y-%m-%d"), "%Y-%m-%d") - timedelta(
        hours=2 * LOGGING_INTERVAL_MIN / 60)
    end_time: datetime = datetime.strptime(get_user_input("end time").strftime("%Y-%m-%d"), "%Y-%m-%d") + timedelta(
        hours=2 * LOGGING_INTERVAL_MIN / 60)

    # Fetch allowed logger min-max values
    extrema_dataframe: pd.DataFrame = \
        read_datalogger_extrema_data(FILEPATH_DATALOGGER_EXTREMA, EXTREMA_COLUMN_CONVERTER)

    # Iterate over all detected csv files
    for filepath in tqdm(list(FILEPATH_DATALOGGER_DATA.glob("*.csv"))):

        # Get logger name and number of data columns from csv file
        logger_name, number_columns = get_name_and_columns(filepath)

        # Read data from csv file to pandas dataframe and prune it to specified start and end time
        dataframe: pd.DataFrame = read_to_dataframe(
            filepath, number_columns, DATA_COLUMN_CONVERTER, start_time, end_time
        )

        # Compute rolling median of temperature and humidity
        dataframe_median: pd.DataFrame = rolling_median(dataframe, MEDIAN_FILTER_SIZE)

        # Find extrema of the dataframe
        measured_extrema_dict: Dict[str, Dict[str, Dict[str, Union[float, datetime]]]] = get_measured_extrema(
            dataframe_median)

        # Find allowed extrema of the data logger
        allowed_extrema_dict = get_allowed_extrema(extrema_dataframe, dataframe_median, logger_name)

        # Create figure
        ax1: Axes = create_figure(dataframe_median, logger_name)
        ax2: Union[Axes, None] = None

        # Plot data
        plot_data(dataframe_median, allowed_extrema_dict, LABEL_COLOR, "temperature [°C]", ax1)
        if 'relative humidity [%]' in dataframe_median.columns:
            ax2: Axes = ax1.twinx()
            ax2.spines['right'].set_zorder(1)
            ax2.spines['top'].set_zorder(1)
            ax2.spines['left'].set_zorder(1)
            ax2.spines['bottom'].set_zorder(1)
            ax2.patch.set_visible(False)
            ax1.patch.set_visible(False)
            plot_data(dataframe_median, allowed_extrema_dict, LABEL_COLOR, "relative humidity [%]", ax2)

        # Adjust x- and y-axes
        adjust_x_axis(dataframe, ax1)
        adjust_y_axis(measured_extrema_dict, allowed_extrema_dict, ax1, "temperature [°C]")
        if 'relative humidity [%]' in dataframe.columns:
            adjust_y_axis(measured_extrema_dict, allowed_extrema_dict, ax2, "relative humidity [%]")

        # Annotate min-max borders
        annotate_min_max_borders(dataframe, allowed_extrema_dict, LABEL_COLOR, "temperature [°C]", ax1)
        if 'relative humidity [%]' in dataframe.columns:
            annotate_min_max_borders(dataframe, allowed_extrema_dict, LABEL_COLOR, "relative humidity [%]", ax2)

        # Annotate extrema
        annotate_extrema(dataframe, LABEL_COLOR, "temperature [°C]", ax1)
        if 'relative humidity [%]' in dataframe.columns:
            annotate_extrema(dataframe, LABEL_COLOR, "relative humidity [%]", ax2)

        # Save plots and data in separate folders
        save_results(FILEPATH_DATALOGGER_DATA, filepath, logger_name, measured_extrema_dict)


if __name__ == "__main__":
    main()
