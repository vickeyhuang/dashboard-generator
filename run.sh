#!/bin/bash

# ============================================================
# Jira data visible tool - by script
# ============================================================

# Color config
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function: print colored information
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function: shows helps
show_help() {
    echo "How to use:"
    echo "  $0 [选项]"
    echo ""
    echo "Options:"
    echo "  -d, --data FILE     Specific data file path"
    echo "  -o, --output DIR    Specific output dir"
    echo "  -c, --config FILE   Specific config file"
    echo "--portfolio NAME   Specific portfolio domain name for Dashboard title"
    echo "--project NAME   Specific project squad name for Dashboard title"
    echo "  -h, --help          Show helps"
    echo ""
    echo "Notes:"
    echo "--portfolio and --project cannot be used at the same time"
    echo "If neither is specified, the default title will be used"
    echo ""
    echo "Sample:"
    echo "  $0                               Using default data file"
    echo "  $0 -d data/my_jira.csv          Using specific data file"
    echo "  $0 --portfolio \"Merchant Experience\""
    echo "  $0 --project \"Squad Self Service\""
    echo "  $0 --portfolio \"Banking, Data & AI\" -d data/banking.csv -o reports/q1"
    echo "  $0 -d data/jira_data.xlsx -o reports/week1  Using Excel file and specific output dir"
    echo ""
}

# Default configuration
DEFAULT_DATA_FILE="data/input_data.csv"
DEFAULT_OUTPUT_DIR="output"
CONFIG_DIR="config"
SAMPLE_DATA_FILE="$CONFIG_DIR/sample_data.csv"

# Parse command paras
DATA_FILE=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--data)
            DATA_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --portfolio)
            PORTFOLIO="$2"
            shift 2
            ;;
        --project)
            PROJECT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_warning "Unknown para: $1"
            show_help
            exit 1
            ;;
    esac
done

# Verify parameter: portfolio and project-name cannot be used at the same time
if [ ! -z "$PORTFOLIO" ] && [ ! -z "$PROJECT" ]; then
    print_error "error: --portfolio and --project cannot be used at the same time"
    echo "请只使用其中一个参数，或者都不使用"
    echo ""
    show_help
    exit 1
fi

# Please use the default if no specific input file
if [ -z "$DATA_FILE" ]; then
    DATA_FILE="$DEFAULT_DATA_FILE"
fi

# Please use the default if no specific output file
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
fi

print_info "🚀 Enable Jira data visible tool"
echo "=================================================="

# Print title info
if [ ! -z "$PORTFOLIO" ]; then
    print_info "🎯 Portfolio Name: $PORTFOLIO Portfolio Dashboard"
elif [ ! -z "$PROJECT" ]; then
    print_info "🎯 Project Name: $PROJECT Project Dashboard"
else
    print_info "🎯 Default name: auto generated title by data provided"
fi

# 1. Check Python env
print_info "1. Checking Python env..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 uninstall, please install Python3 firstly."
    echo "Mac user: brew install python3"
    echo "Linux user: sudo apt-get install python3"
    echo "Windows user: please download and install from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION installed"

# 2. Check data file
print_info "2. Checking data file..."

# When using specific data file
if [ "$DATA_FILE" != "$DEFAULT_DATA_FILE" ]; then
    if [ ! -f "$DATA_FILE" ]; then
        print_error "The specific data file not exist: $DATA_FILE"
        exit 1
    fi
    print_success "Using the specific data file: $DATA_FILE"
else
    # When using default data file
    if [ ! -f "$DATA_FILE" ]; then
        print_warning "The default data file not exist: $DATA_FILE"
        
        # Create data dir
        mkdir -p data
        
        # Check if having sample data
        if [ -f "$SAMPLE_DATA_FILE" ]; then
            print_info "Copy sample data to data/ dir..."
            cp "$SAMPLE_DATA_FILE" "$DATA_FILE"
            print_success "Created sample data file: $DATA_FILE"
            echo ""
            print_warning "⚠️  Please note: This is sample data, please replace your Jira data"
            echo "    Edit file: $DATA_FILE"
            echo ""
        else
            # Create sample data
            print_info "Create sample data..."
            cat > "$DATA_FILE" << 'EOF'
Project,In Progress,To Do,Blocked,Backlog,Prioritised,Done,T:
Merchant Experience Apps,18,12,0,0,0,253,283
Onboarding,11,36,10,0,0,145,202
Nexus Pathway,0,7,0,0,0,163,170
Squad Self Service,5,28,4,0,0,89,126
Squad Onboarding,0,4,4,0,0,117,125
ME AML Uplift,20,60,0,0,0,16,96
Merchant Experience Portal,1,0,2,9,5,5,22
Total Unique Issues:,55,147,20,9,5,788,1024
EOF
            print_success "Created sample data file: $DATA_FILE"
            echo ""
            print_warning "⚠️  Please note: This is sample data, please replace your Jira data"
            echo "    Edit file: $DATA_FILE"
            echo "    Format notes:"
            echo "      - First column name"
            echo "      - Required column name: Project, In Progress, To Do, Done"
            echo "      - Options: Blocked, Backlog, Prioritised, T:"
            echo ""
        fi
    else
        print_success "Use data file: $DATA_FILE"
        
        # Print data file info
        FILE_SIZE=$(du -h "$DATA_FILE" | cut -f1)
        FILE_LINES=$(wc -l < "$DATA_FILE" | tr -d ' ')
        print_info "  file size: $FILE_SIZE, lines: $FILE_LINES"
    fi
fi

# 3. Shows data file format info
print_info "3. Checking data format..."
if [ -f "$DATA_FILE" ]; then
    echo "Supported formats:"
    echo "  - CSV (comma or tab separate)"
    echo "  - Excel (.xlsx, .xls)"
    echo ""
    echo "Required columns:"
    echo "  - Project: Project or Parent or Team name"
    echo "  - In Progress: Inprogress items"
    echo "  - To Do: Todo items"
    echo "  - Done: Completed items"
    echo ""
    echo "Options:"
    echo "  - Blocked: Blocked items"
    echo "  - Backlog: Blocklog items"
    echo "  - Prioritised: Prioritised items"
    echo "  - T:: Total (calculation)"
fi

# 4. Check the dependances
print_info "4. Checking dependances..."

# Create requirements.txt if it's not exist
if [ ! -f "requirements.txt" ]; then
    print_info "Create requirements.txt..."
    cat > requirements.txt << 'EOF'
# Jira data visible tool dependances
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
EOF
    print_success "Created requirements.txt"
fi

# Check and install dependances
print_info "Install Python dependances..."
if pip3 install -r requirements.txt; then
    print_success "Dependances installed completion"
else
    print_warning "Try install via pip..."
    if pip install -r requirements.txt; then
        print_success "Dependance install completion"
    else
        print_error "Dependance install failure, please install manually:"
        echo "  pip install pandas plotly openpyxl"
        exit 1
    fi
fi

# 5. Create output dir
print_info "5. Prepare output dir..."
mkdir -p "$OUTPUT_DIR"
if [ $? -eq 0 ]; then
    print_success "Created output dir: $OUTPUT_DIR"
else
    print_error "Can't create output dir: $OUTPUT_DIR"
    exit 1
fi

# 6. Run main program
print_info "6. Running data visible tool..."
echo "=================================================="

# Build Python command parameters
PYTHON_ARGS="\"$DATA_FILE\" \"$OUTPUT_DIR\""

if [ ! -z "$PORTFOLIO" ]; then
    PYTHON_ARGS="$PYTHON_ARGS --portfolio \"$PORTFOLIO\""
    print_info "  Portfolio name: $PORTFOLIO"
fi

if [ ! -z "$PROJECT" ]; then
    PYTHON_ARGS="$PYTHON_ARGS --project \"$PROJECT\""
    print_info "  Project name: $PROJECT"
fi

CMD="python3 main.py $PYTHON_ARGS"
echo "Implement commands: python3 main.py $DATA_FILE $OUTPUT_DIR"
if [ ! -z "$PORTFOLIO" ]; then
    echo "         --portfolio \"$PORTFOLIO\""
fi
if [ ! -z "$PROJECT" ]; then
    echo "         --project-name \"$PROJECT\""
fi
echo ""

if eval $CMD; then
    print_success "Data process completion!"
else
    print_error "Print error when processing"
    exit 1
fi

# 7. Show results
print_info "7. Generate file..."
echo "=================================================="

# Show the dashboard path if we found it

# Get dashboard file name
DASHBOARD_FILES=$(find "$OUTPUT_DIR" -name "dashboard_*.html" | head -1)

# Show timestamped dashboard files
if [ ! -z "$DASHBOARD_FILES" ]; then
    for file in $DASHBOARD_FILES; do
        print_success "📊 Full Dashboard: $file"
    done
else
    # Look for non-timestamped dashboard (backward compatibility)
    if [ -f "$OUTPUT_DIR/dashboard.html" ]; then
        print_warning "📊 Dashboard (legacy format): $OUTPUT_DIR/dashboard.html"
    fi
fi

if [ -f "$OUTPUT_DIR/pie_chart.html" ]; then
    print_success "🎨 Pie Chart: $OUTPUT_DIR/pie_chart.html"
fi
if [ -f "$OUTPUT_DIR/delivery_progress.html" ]; then
    print_success "📈 Bar Chart: $OUTPUT_DIR/delivery_progress.html"
fi
if [ -f "$OUTPUT_DIR/report.html" ]; then
    print_success "📊 HTML Report: $OUTPUT_DIR/report.html"
fi
if [ -f "$OUTPUT_DIR/detailed_analysis.csv" ]; then
    print_success "💾 Details Report: $OUTPUT_DIR/detailed_analysis.csv"
fi
if [ -f "$OUTPUT_DIR/summary.csv" ]; then
    print_success "📄 Summary Data: $OUTPUT_DIR/summary.csv"
fi

# # 8. Auto open Dashboard
# print_info "8. Openning Dashboard..."
# if [ -f "$OUTPUT_DIR/dashboard.html" ]; then
#     if [[ "$OSTYPE" == "darwin"* ]]; then
#         print_info "Openning Dashboard in the web browser..."
#         open "$OUTPUT_DIR/dashboard.html"
#     elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
#         if command -v xdg-open &> /dev/null; then
#             print_info "Openning Dashboard..."
#             xdg-open "$OUTPUT_DIR/dashboard.html"
#         else
#             print_warning "Please open manually: $OUTPUT_DIR/dashboard.html"
#         fi
#     else
#         print_warning "Please open manually: $OUTPUT_DIR/dashboard.html"
#     fi
# else
#     print_error "Can't fine Dashboard file"
# fi

# 9. Helps
print_info "9. Helps..."
echo "=================================================="
echo ""
echo "📌 How to update data:"
echo "  1. Edit data file: $DATA_FILE"
echo "  2. re-run command: ./run.sh"
echo ""
echo "📌 Support input format:"
echo "  - CSV file (recommand)"
echo "  - Excel file (.xlsx, .xls)"
echo ""
echo "📌 Custom Dashboard Title:"
if [ ! -z "$PORTFOLIO" ]; then
    echo "  Current: $PORTFOLIO Portfolio Dashboard"
elif [ ! -z "$PROJECT" ]; then
    echo "  Current: $PROJECT Project Dashboard"
else
    echo "  use --portfolio or --project parameters self-customized title"
fi
echo ""
echo "📌 Output Dir:"
echo "  - $OUTPUT_DIR/"
echo ""
echo "📌 Quick commands:"
echo "  ./run.sh -d data/your_data.csv    # Using specific data file"
echo "  ./run.sh -o reports/week1         # Specific output dir"
echo "  ./run.sh --help                   # Show helps"
echo ""

print_success "🎉 All tasks completion! "
echo ""