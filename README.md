# Phonepe

# 📱 PhonePe Pulse | India's Digital Payment Dashboard

A comprehensive data visualization and analytics dashboard built with Streamlit to analyze PhonePe's transaction, insurance, and user engagement data across India.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)

## 🌟 Features

### 🏠 Interactive Home Page
- **3D India Map Visualization**: Interactive choropleth map showing state-wise payment ecosystem data
- **Real-time Metrics**: Live aggregated statistics for transactions, insurance, and user engagement
- **Dark Theme Design**: Premium dark mode interface with glassmorphism effects
- **Top States Dashboard**: Dynamic ranking of top-performing states by total transaction value

### 📊 Advanced Analytics Cases
The dashboard includes five comprehensive business case studies:

1. **Transaction Analysis for Market Expansion**
   - Market penetration analysis
   - Transaction volume and value trends
   - State-wise transaction distribution

2. **Insurance Transactions Analysis**
   - Insurance policy distribution
   - Premium amount analysis
   - Geographic insurance penetration

3. **Decoding Transaction Dynamics on PhonePe**
   - Transaction type breakdown
   - Temporal trend analysis
   - Correlation between count and amount

4. **User Registration Analysis**
   - User growth patterns
   - App engagement metrics
   - District-wise user distribution

5. **Insurance Engagement Analysis**
   - Policy adoption rates
   - Insurance product performance
   - Regional insurance trends

### 📈 Visualization Suite
Each case study includes **6 comprehensive chart sections**:

1. **Data Overview**: Interactive data tables with 100+ rows
2. **Distribution Analysis**: Dual pie charts for amount and count distribution
3. **Relationship Analysis**: Scatter plots, bar charts, and histograms
4. **Insights Dashboard**: Correlation heatmaps and key metrics
5. **Trend Analysis**: Time-series line charts and stacked bar charts
6. **Advanced Analytics**: Box plots and area charts

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly Express, Plotly Graph Objects
- **Database**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **Data Processing**: Pandas
- **Python**: 3.8+

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0+
- pip package manager

### Setup Instructions

1. **Clone the repository**
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. **Install required packages**
```bash
pip install streamlit pandas plotly sqlalchemy pymysql
```

3. **Database Configuration**
   - Ensure MySQL is running on `localhost:3306`
   - Create a database named `phonepe`
   - Update database credentials in `apply.py` (line 17):
   ```python
   engine = create_engine("mysql+pymysql://root:Password%40123@localhost:3306/phonepe")
   ```

4. **Database Schema**
   
   The application expects the following tables:
   
   **Transaction Tables:**
   - `agg_trans` (state, year, quarter, transaction_type, transaction_count, transaction_amount)
   - `map_trans` (state, year, quarter, district, transaction_count, transaction_amount)
   - `top_trans` (state, year, quarter, pincode, transaction_count, transaction_amount)
   
   **Insurance Tables:**
   - `agg_insur` (state, year, quarter, insurance_type, insurance_count, insurance_amount)
   - `map_insur` (state, year, quarter, district, insurance_count, insurance_amount)
   - `top_insur` (state, year, quarter, pincode, insurance_count, insurance_amount)
   
   **User Tables:**
   - `map_user` (state, year, quarter, district, registered_users, app_opens)
   - `top_users` (state, year, quarter, pincode, registered_users)
   - `agg_users` (state, year, quarter, user_count)

## 🚀 Usage

1. **Start the application**
```bash
streamlit run apply.py
```

2. **Access the dashboard**
   - Open your browser and navigate to `http://localhost:8501`

3. **Navigate the dashboard**
   - **Home Page**: View overall statistics and interactive India map
   - **Analysis Page**: Select from 5 case studies and apply filters

4. **Apply Filters**
   - Use the sidebar to filter by Year, Quarter, and State
   - Click "Apply Filters" to update visualizations

## 📊 Database Utilities

The project includes several utility scripts for database inspection:

- `check_db.py` - Basic database connection test
- `check_schema.py` - Schema validation
- `inspect_db.py` - Detailed table inspection
- `check_columns.py` - Column name verification

## 🎨 Design Features

### Color Palette
- **Primary Background**: `#0d0221` (Deep Purple)
- **Secondary Background**: `#1a0b3e` (Dark Purple)
- **Accent Colors**: 
  - Cyan: `#00d2ff` (Transactions)
  - Pink: `#ff006e` (Insurance)
  - Green: `#06ffa5` (Users)
  - Purple Gradient: `#5a189a` → `#9d4edd` → `#e0aaff`

### Interactive Elements
- Hover effects on metric cards
- Animated transitions
- Responsive layouts
- Custom tooltips with formatted data

## 📁 Project Structure

```
.
├── apply.py                    # Main Streamlit application
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── check_db.py                # Database connection checker
├── check_schema.py            # Schema validator
├── inspect_db.py              # Database inspector
└── README.md                  # This file
```

## 🔧 Configuration

### Streamlit Config
Located in `.streamlit/config.toml`:
- Theme settings
- Server configuration
- Browser settings

### Database Connection
Modify the connection string in `apply.py`:
```python
@st.cache_resource
def get_engine():
    engine = create_engine("mysql+pymysql://username:password@host:port/database")
    return engine
```

## 📈 Data Flow

1. **Data Extraction**: SQLAlchemy connects to MySQL database
2. **Data Processing**: Pandas normalizes and filters data
3. **Visualization**: Plotly generates interactive charts
4. **Rendering**: Streamlit displays the dashboard

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Verify MySQL is running
- Check credentials in connection string
- Ensure database `phonepe` exists

**Missing Data**
- Verify all required tables exist
- Check column names match expected schema
- Ensure data is populated in tables

**Visualization Not Loading**
- Clear Streamlit cache: `streamlit cache clear`
- Check browser console for errors
- Verify Plotly is installed correctly

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- PhonePe for the data inspiration
- Streamlit for the amazing framework
- Plotly for powerful visualizations
- The open-source community



For questions or support, please open an issue in the GitHub repository.

---

**Made with ❤️ using Streamlit and Python**
