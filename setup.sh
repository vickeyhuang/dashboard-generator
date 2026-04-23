# setup.sh
#!/bin/bash

echo "🔧 Setting up Jira Data Visualization Tool Env..."

# 1. Add execute permission to run script
chmod +x run.sh
echo "✅ Added execute permission to run.sh"

# 2. Create required directories
echo "📁 Creating directory structure..."
mkdir -p data config output

# 3. Create sample data file
echo "📊 Creating sample data file..."
cat > config/sample_data.csv << 'EOF'
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

# 4. Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
EOF

# 5. Create project structure documentation
echo "📝 Creating README file..."
cat > data/README.md << 'EOF'
# Data Directory Instructions

## How to add your data

1. Export your Jira data as CSV or Excel format
2. Save the file to this directory
3. Execute one of the following commands:

```bash
# Use default filename
cp your_data.csv input_data.csv

# Or run with custom filename
./run.sh -d your_data.csv

# Or with portfolio/project customization as dashboard title
./run.sh --portfolio "Your Portfolio Name" -d your_data.csv
./run.sh --project "Your Project Name" -d your_data.csv