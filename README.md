# README.md

## Jira Data Visible Dashboard

### Structure
```

jira_visualizer/
├── data/                    # Source data dir
│   ├── input_data.csv      # Default input date file
│   └── README.md           # Data Readme and Structure
├── src/                    # Source code dir
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_processor.py
│   ├── chart_generator.py
│   ├── dashboard_builder.py
│   └── report_generator.py
├── output/                 # Output dir (auto generated)
├── config/                 # Config dir
│   └── sample_data.csv    # Sample data
├── main.py                # Main program
├── requirements.txt       # Python dependance
├── run.sh                # Run shell（Mac/Linux）
└── README.md             # Project readme
```

### How to Use

#### Run Sample data
```
python3 main.py examples/sample_data.csv
```

#### Run Specific data
```
python3 main.py your_data.csv output_folder
```

#### Run Excel file
```
python3 main.py your_data.xlsx
```

#### Run default file
```
./run.sh
```

#### Run with specific data
```
./run.sh -d data/your_jira_data.csv
```

#### Or run with portfolio/project customization as dashboard title
```
./run.sh --portfolio "Your Portfolio Name" -d data/your_data.csv
./run.sh --project "Your Project Name" -d data/your_data.csv
```

#### Build a dashboard with app.py
```
streamlit run app.py
```


