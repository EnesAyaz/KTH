import csv
import json
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    ROOT_DIR
    / "data"
)

FIGURE_PLAN_FILE = (
    DATA_DIR
    / "figure_plan.json"
)

COMPARISON_CSV = (
    DATA_DIR
    / "comparison.csv"
)

MATLAB_DIR = (
    ROOT_DIR
    / "figures"
    / "matlab"
)

GENERATED_DIR = (
    ROOT_DIR
    / "figures"
    / "generated"
)


MATLAB_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# CSV HEADERS
# =========================================================

def get_csv_columns():

    with COMPARISON_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        return set(
            reader.fieldnames
            or []
        )


# =========================================================
# MATLAB STRING ESCAPE
# =========================================================

def matlab_escape(
    text
):

    if text is None:
        return ""

    return (
        str(text)
        .replace(
            "'",
            "''"
        )
    )


# =========================================================
# VALIDATE FIGURE
# =========================================================

def validate_figure(
    figure,
    csv_columns,
):

    errors = []

    plot_type = (
        figure.get(
            "plot_type"
        )
    )

    x_column = (
        figure.get(
            "x_column"
        )
    )

    y_column = (
        figure.get(
            "y_column"
        )
    )

    # -----------------------------------------------------
    # Y COLUMN
    # -----------------------------------------------------

    if not y_column:

        errors.append(
            "y_column is missing"
        )

    elif (
        y_column
        not in csv_columns
    ):

        errors.append(
            f"y_column does not exist: "
            f"{y_column}"
        )

    # -----------------------------------------------------
    # X COLUMN FOR SCATTER
    # -----------------------------------------------------

    if plot_type == "scatter":

        if not x_column:

            errors.append(
                "scatter plot requires x_column"
            )

        elif (
            x_column
            not in csv_columns
        ):

            errors.append(
                f"x_column does not exist: "
                f"{x_column}"
            )

    # -----------------------------------------------------
    # GROUP COLUMN
    # -----------------------------------------------------

    group_column = (
        figure.get(
            "group_column"
        )
    )

    if (
        group_column
        and group_column
        not in csv_columns
    ):

        errors.append(
            f"group_column does not exist: "
            f"{group_column}"
        )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    for column in figure.get(
        "required_columns",
        []
    ):

        if (
            column
            not in csv_columns
        ):

            errors.append(
                f"required column does not exist: "
                f"{column}"
            )

    return errors


# =========================================================
# SCATTER SCRIPT
# =========================================================

def create_scatter_script(
    figure
):

    x_column = figure[
        "x_column"
    ]

    y_column = figure[
        "y_column"
    ]

    x_label = matlab_escape(
        figure.get(
            "x_label"
        )
        or x_column
    )

    y_label = matlab_escape(
        figure.get(
            "y_label"
        )
        or y_column
    )

    title = matlab_escape(
        figure[
            "title"
        ]
    )

    output_filename = (
        figure[
            "latex_filename"
        ]
    )

    minimum_rows = int(
        figure.get(
            "minimum_rows",
            2,
        )
    )

    script = f"""
clear;
clc;
close all;

%% ========================================================
% PATHS
% =========================================================

scriptFolder = fileparts(mfilename('fullpath'));

projectFolder = fullfile( ...
    scriptFolder, ...
    '..', ...
    '..');

dataFile = fullfile( ...
    projectFolder, ...
    'data', ...
    'comparison.csv');

outputFolder = fullfile( ...
    projectFolder, ...
    'figures', ...
    'generated');

if ~exist(outputFolder, 'dir')
    mkdir(outputFolder);
end

%% ========================================================
% READ DATA
% =========================================================

T = readtable( ...
    dataFile, ...
    'VariableNamingRule', ...
    'preserve');

xColumn = '{matlab_escape(x_column)}';
yColumn = '{matlab_escape(y_column)}';

%% ========================================================
% CHECK COLUMNS
% =========================================================

if ~ismember(xColumn, T.Properties.VariableNames)
    error('Missing column: %s', xColumn);
end

if ~ismember(yColumn, T.Properties.VariableNames)
    error('Missing column: %s', yColumn);
end

%% ========================================================
% CONVERT TO NUMERIC
% =========================================================

xRaw = T.(xColumn);
yRaw = T.(yColumn);

if isnumeric(xRaw)
    x = double(xRaw);
else
    x = str2double(string(xRaw));
end

if isnumeric(yRaw)
    y = double(yRaw);
else
    y = str2double(string(yRaw));
end

%% ========================================================
% REMOVE INVALID DATA
% =========================================================

valid = ...
    ~isnan(x) & ...
    ~isnan(y);

x = x(valid);
y = y(valid);

if numel(x) < {minimum_rows}

    error( ...
        'Not enough valid points for this figure. Found %d; required %d.', ...
        numel(x), ...
        {minimum_rows});

end

%% ========================================================
% FIGURE
% =========================================================

figure;

scatter( ...
    x, ...
    y, ...
    70, ...
    'filled');

xlabel( ...
    '{x_label}', ...
    'Interpreter', ...
    'none');

ylabel( ...
    '{y_label}', ...
    'Interpreter', ...
    'none');

title( ...
    '{title}', ...
    'Interpreter', ...
    'none');

grid on;
box on;

%% ========================================================
% LABEL POINTS
% =========================================================

if ismember( ...
        'citation_key', ...
        T.Properties.VariableNames)

    labelsAll = string( ...
        T.citation_key);

    labels = labelsAll(valid);

    for index = 1:numel(x)

        text( ...
            x(index), ...
            y(index), ...
            " " + labels(index), ...
            'FontSize', ...
            8);

    end

end

%% ========================================================
% EXPORT
% =========================================================

outputFile = fullfile( ...
    outputFolder, ...
    '{matlab_escape(output_filename)}');

exportgraphics( ...
    gcf, ...
    outputFile, ...
    'ContentType', ...
    'vector');

fprintf( ...
    'Figure saved to: %s\\n', ...
    outputFile);
"""

    return (
        script.strip()
        + "\n"
    )


# =========================================================
# BAR SCRIPT
# =========================================================

def create_bar_script(
    figure
):

    y_column = figure[
        "y_column"
    ]

    y_label = matlab_escape(
        figure.get(
            "y_label"
        )
        or y_column
    )

    title = matlab_escape(
        figure[
            "title"
        ]
    )

    output_filename = (
        figure[
            "latex_filename"
        ]
    )

    minimum_rows = int(
        figure.get(
            "minimum_rows",
            2,
        )
    )

    script = f"""
clear;
clc;
close all;

%% ========================================================
% PATHS
% =========================================================

scriptFolder = fileparts(mfilename('fullpath'));

projectFolder = fullfile( ...
    scriptFolder, ...
    '..', ...
    '..');

dataFile = fullfile( ...
    projectFolder, ...
    'data', ...
    'comparison.csv');

outputFolder = fullfile( ...
    projectFolder, ...
    'figures', ...
    'generated');

if ~exist(outputFolder, 'dir')
    mkdir(outputFolder);
end

%% ========================================================
% READ DATA
% =========================================================

T = readtable( ...
    dataFile, ...
    'VariableNamingRule', ...
    'preserve');

yColumn = '{matlab_escape(y_column)}';

if ~ismember(yColumn, T.Properties.VariableNames)
    error('Missing column: %s', yColumn);
end

%% ========================================================
% CONVERT TO NUMERIC
% =========================================================

yRaw = T.(yColumn);

if isnumeric(yRaw)
    yAll = double(yRaw);
else
    yAll = str2double(string(yRaw));
end

valid = ~isnan(yAll);

y = yAll(valid);

if numel(y) < {minimum_rows}

    error( ...
        'Not enough valid points for this figure. Found %d; required %d.', ...
        numel(y), ...
        {minimum_rows});

end

%% ========================================================
% LABELS
% =========================================================

if ismember( ...
        'citation_key', ...
        T.Properties.VariableNames)

    labelsAll = string( ...
        T.citation_key);

    labels = labelsAll(valid);

else

    labels = string( ...
        1:numel(y));

end

%% ========================================================
% FIGURE
% =========================================================

figure;

bar(y);

xticks( ...
    1:numel(y));

xticklabels( ...
    labels);

xtickangle(45);

ylabel( ...
    '{y_label}', ...
    'Interpreter', ...
    'none');

title( ...
    '{title}', ...
    'Interpreter', ...
    'none');

grid on;
box on;

%% ========================================================
% EXPORT
% =========================================================

outputFile = fullfile( ...
    outputFolder, ...
    '{matlab_escape(output_filename)}');

exportgraphics( ...
    gcf, ...
    outputFile, ...
    'ContentType', ...
    'vector');

fprintf( ...
    'Figure saved to: %s\\n', ...
    outputFile);
"""

    return (
        script.strip()
        + "\n"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )
    print(
        "GENERATING MATLAB FIGURE SCRIPTS"
    )
    print(
        "========================================"
    )
    print()

    # -----------------------------------------------------
    # CHECK FILES
    # -----------------------------------------------------

    if not FIGURE_PLAN_FILE.exists():

        print(
            "figure_plan.json does not exist."
        )

        print()
        print(
            "Run:"
        )
        print()
        print(
            "python plan_figures.py"
        )

        return

    if not COMPARISON_CSV.exists():

        print(
            "comparison.csv does not exist."
        )

        return

    # -----------------------------------------------------
    # REMOVE OLD GENERATED MATLAB FILES
    # -----------------------------------------------------

    for old_file in MATLAB_DIR.glob(
        "*.m"
    ):

        old_file.unlink()

    print(
        "Old generated MATLAB scripts removed."
    )

    print()

    # -----------------------------------------------------
    # LOAD PLAN
    # -----------------------------------------------------

    plan = json.loads(
        FIGURE_PLAN_FILE.read_text(
            encoding="utf-8"
        )
    )

    figures = plan.get(
        "figures",
        []
    )

    if not figures:

        print(
            "No figures were proposed."
        )

        return

    # -----------------------------------------------------
    # CSV COLUMNS
    # -----------------------------------------------------

    csv_columns = (
        get_csv_columns()
    )

    print(
        "Available CSV columns:"
    )

    for column in sorted(
        csv_columns
    ):

        print(
            f"  {column}"
        )

    print()

    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    created = 0
    rejected = 0

    for figure in figures:

        figure_id = figure.get(
            "figure_id",
            "unknown"
        )

        errors = validate_figure(
            figure,
            csv_columns,
        )

        if errors:

            print(
                f"REJECTED FIGURE: "
                f"{figure_id}"
            )

            for error in errors:

                print(
                    f"  - {error}"
                )

            print()

            rejected += 1

            continue

        plot_type = (
            figure[
                "plot_type"
            ]
        )

        filename = (
            figure[
                "matlab_filename"
            ]
        )

        output_file = (
            MATLAB_DIR
            / filename
        )

        if plot_type == "scatter":

            script = (
                create_scatter_script(
                    figure
                )
            )

        elif plot_type == "bar":

            script = (
                create_bar_script(
                    figure
                )
            )

        else:

            print(
                f"Unsupported plot type: "
                f"{plot_type}"
            )

            rejected += 1

            continue

        output_file.write_text(
            script,
            encoding="utf-8",
        )

        print(
            f"Created: "
            f"{output_file.name}"
        )

        created += 1

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print(
        "========================================"
    )
    print(
        "GENERATION SUMMARY"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Created:  {created}"
    )

    print(
        f"Rejected: {rejected}"
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()