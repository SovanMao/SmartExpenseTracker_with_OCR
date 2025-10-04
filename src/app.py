import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from PIL import Image
import tempfile
import os

# Import our custom modules
from expense_tracker import ExpenseTracker, DEFAULT_CATEGORIES
from reciept_ocr import ReceiptOCR

# Page configuration
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = ExpenseTracker()

if 'ocr' not in st.session_state:
    st.session_state.ocr = ReceiptOCR()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Title
    st.markdown('<h1 class="main-header">💰 Smart Expense Tracker</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation Bar")
    st.sidebar.markdown("---")
    
    # Navigation options with icons
    nav_options = {
        "📊 Dashboard": "Dashboard",
        "➕ Add Expense": "Add Expense", 
        "📷 Upload Receipt": "Upload Receipt",
        "📋 View Expenses": "View Expenses",
        "📈 Analytics": "Analytics"
    }
    
    # Use radio buttons for navigation
    selected_option = st.sidebar.radio(
        "Go to:",
        list(nav_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    # Get the actual page name
    page = nav_options[selected_option]
    
    # Add some space and info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Tips")
    st.sidebar.info("💰 Track expenses manually or upload receipt photos for automatic processing!")
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Add Expense":
        add_expense_page()
    elif page == "Upload Receipt":
        upload_receipt_page()
    elif page == "View Expenses":
        view_expenses_page()
    elif page == "Analytics":
        analytics_page()

def dashboard_page():
    """Display dashboard with overview statistics and charts."""
    
    st.header("📊 Dashboard Overview")
    
    # Load current expenses
    tracker = st.session_state.tracker
    df = tracker.get_expenses_df()
    
    if df.empty:
        st.info("No expenses found. Start by adding an expense or uploading a receipt!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spending = tracker.get_total_spending()
        st.metric("Total Spending", f"${total_spending:.2f}")
    
    with col2:
        num_expenses = len(tracker.expenses)
        st.metric("Total Expenses", num_expenses)
    
    with col3:
        avg_expense = total_spending / num_expenses if num_expenses > 0 else 0
        st.metric("Average Expense", f"${avg_expense:.2f}")
    
    with col4:
        num_categories = len(tracker.get_categories())
        st.metric("Categories Used", num_categories)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spending by Category")
        category_data = tracker.get_total_by_category()
        if category_data:
            fig = px.pie(
                values=list(category_data.values()),
                names=list(category_data.keys()),
                title="Category Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Recent Expenses Trend")
        if len(df) > 1:
            df_sorted = df.sort_values('date')
            fig = px.line(
                df_sorted,
                x='date',
                y='amount',
                title="Spending Over Time",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need more expenses to show trend")
    
    # Recent expenses
    st.subheader("Recent Expenses")
    recent = tracker.get_recent_expenses(5)
    if recent:
        recent_df = pd.DataFrame(recent)
        st.dataframe(
            recent_df[['date', 'vendor', 'category', 'amount']],
            use_container_width=True,
            hide_index=True
        )

def add_expense_page():
    """Manual expense entry page."""
    
    st.header("➕ Add New Expense")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            vendor = st.text_input("Vendor/Merchant", placeholder="e.g., Starbucks, Walmart")
            
        with col2:
            expense_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", DEFAULT_CATEGORIES)
        
        submitted = st.form_submit_button("Add Expense", type="primary")
        
        if submitted:
            if amount > 0 and vendor.strip():
                success = st.session_state.tracker.add_expense(
                    amount=amount,
                    date_str=expense_date.strftime('%Y-%m-%d'),
                    vendor=vendor.strip(),
                    category=category
                )
                
                if success:
                    st.session_state.tracker.save_expenses_csv()
                    st.success(f"✅ Expense of ${amount:.2f} at {vendor} added successfully!")
                    # Show a balloons animation for successful addition
                    st.balloons()
                    # Wait a moment to show the success message
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to add expense. Please check your input.")
            else:
                st.error("❌ Please enter a valid amount and vendor name.")

def upload_receipt_page():
    """Receipt upload and OCR processing page."""
    
    st.header("📷 Upload Receipt")
    
    # Initialize session state for OCR processing
    if 'ocr_processed' not in st.session_state:
        st.session_state.ocr_processed = False
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    if 'current_file_name' not in st.session_state:
        st.session_state.current_file_name = None
    if 'show_form' not in st.session_state:
        st.session_state.show_form = False
    if 'expense_saved' not in st.session_state:
        st.session_state.expense_saved = False
    
    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Upload a clear image of your receipt for automatic processing"
    )
    
    if uploaded_file is not None:
        # Check if this is a new file
        if st.session_state.current_file_name != uploaded_file.name:
            st.session_state.ocr_processed = False
            st.session_state.ocr_result = None
            st.session_state.current_file_name = uploaded_file.name
            st.session_state.show_form = False
            st.session_state.expense_saved = False
        # Display uploaded image
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Uploaded Receipt")
            image = Image.open(uploaded_file)
            st.image(image, caption="Receipt Image", use_container_width=True)
            
            # Add button to reprocess if needed
            if st.session_state.ocr_processed:
                if st.button("🔄 Process New Receipt", help="Click to reprocess this receipt"):
                    st.session_state.ocr_processed = False
                    st.session_state.ocr_result = None
                    st.session_state.show_form = False
                    st.session_state.expense_saved = False
                    st.rerun()
        
        with col2:
            st.subheader("Processing Results")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Only process OCR if not already processed and expense wasn't just saved
                if not st.session_state.ocr_processed and not st.session_state.expense_saved:
                    with st.spinner("Processing receipt with OCR..."):
                        result_df = st.session_state.ocr.process_receipt(tmp_file_path)
                        st.session_state.ocr_result = result_df
                        st.session_state.ocr_processed = True
                        st.session_state.show_form = True
                        st.rerun()  # Force rerun to show form
                
                # Show success message and reset button if expense was saved
                if st.session_state.expense_saved:
                    st.success("✅ Expense saved successfully!")
                    if st.button("📷 Upload Another Receipt", type="primary"):
                        # Reset all states for next receipt
                        st.session_state.ocr_processed = False
                        st.session_state.ocr_result = None
                        st.session_state.current_file_name = None
                        st.session_state.show_form = False
                        st.session_state.expense_saved = False
                        st.rerun()
                
                # Only show the form if we should show it and have results and expense wasn't saved
                elif st.session_state.show_form and st.session_state.ocr_result is not None and not st.session_state.ocr_result.empty:
                    result_df = st.session_state.ocr_result
                    st.success("✅ Receipt processed successfully!")
                    
                    # Get the first (and only) row of results
                    row = result_df.iloc[0]
                    
                    # Display extracted data in an editable form
                    with st.form("confirm_receipt_data"):
                        st.subheader("Confirm Extracted Data")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Handle amount parsing
                            try:
                                amount_value = float(row['Total']) if row['Total'] != 'Unknown' else 0.01
                                # Ensure amount is at least the minimum value
                                if amount_value < 0.01:
                                    amount_value = 0.01
                            except:
                                amount_value = 0.01
                            
                            amount = st.number_input(
                                "Amount ($)",
                                value=amount_value,
                                min_value=0.01,
                                step=0.01,
                                format="%.2f"
                            )
                            
                            # Show info if amount wasn't detected
                            if row['Total'] == 'Unknown':
                                st.info("💡 Amount not detected - please enter manually")
                            
                            vendor = st.text_input("Vendor", value=row['Place'] if row['Place'] != 'Unknown' else "")
                        
                        with col2:
                            # Handle date parsing
                            try:
                                if row['Date'] != 'Unknown':
                                    default_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                                else:
                                    default_date = date.today()
                            except:
                                default_date = date.today()
                            
                            expense_date = st.date_input("Date", value=default_date)
                            
                            # Handle category
                            category_value = row['Category'] if row['Category'] in DEFAULT_CATEGORIES else DEFAULT_CATEGORIES[0]
                            category = st.selectbox(
                                "Category",
                                DEFAULT_CATEGORIES,
                                index=DEFAULT_CATEGORIES.index(category_value)
                            )
                        
                        # Show extracted data for reference
                        with st.expander("View Extracted Data"):
                            st.write("**Extracted information:**")
                            st.write(f"Date: {row['Date']}")
                            st.write(f"Place: {row['Place']}")
                            st.write(f"Total: {row['Total']}")
                            st.write(f"Category: {row['Category']}")
                        
                        submitted = st.form_submit_button("Save Expense", type="primary")
                        
                        if submitted:
                            if amount > 0 and vendor.strip():
                                success = st.session_state.tracker.add_expense(
                                    amount=amount,
                                    date_str=expense_date.strftime('%Y-%m-%d'),
                                    vendor=vendor.strip(),
                                    category=category
                                )
                                
                                if success:
                                    st.session_state.tracker.save_expenses_csv()
                                    st.success(f"✅ Expense saved successfully!")
                                    st.balloons()
                                    # Set flag to indicate expense was saved
                                    st.session_state.expense_saved = True
                                    st.session_state.show_form = False
                                    # Don't rerun immediately to avoid OCR loop
                                else:
                                    st.error("❌ Failed to save expense.")
                            else:
                                st.error("❌ Please enter valid amount and vendor.")
                
                else:
                    st.error("❌ Failed to process receipt. Please try again with a clearer image.")
                
            except Exception as e:
                st.error(f"❌ Error processing receipt: {str(e)}")
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass

def view_expenses_page():
    """View and manage existing expenses."""
    
    st.header("📋 View Expenses")
    
    tracker = st.session_state.tracker
    df = tracker.get_expenses_df()
    
    if df.empty:
        st.info("No expenses found. Add some expenses to see them here!")
        return
    
    # Filters
    with st.expander("Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = ['All'] + tracker.get_categories()
            selected_category = st.selectbox("Filter by Category", categories)
        
        with col2:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        
        with col3:
            end_date = st.date_input("End Date", value=date.today())
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= start_date) &
        (filtered_df['date'].dt.date <= end_date)
    ]
    
    # Display summary
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Filtered Total", f"${filtered_df['amount'].sum():.2f}")
        
        with col2:
            st.metric("Number of Expenses", len(filtered_df))
        
        with col3:
            st.metric("Average Amount", f"${filtered_df['amount'].mean():.2f}")
        
        # Display expenses table
        st.subheader("Expenses")
        
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(
            display_df[['date', 'vendor', 'category', 'amount']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "expenses.csv",
                    "text/csv"
                )
        
        with col2:
            if st.button("Export to JSON"):
                json_str = filtered_df.to_json(orient='records', date_format='iso')
                st.download_button(
                    "Download JSON",
                    json_str,
                    "expenses.json",
                    "application/json"
                )
    else:
        st.info("No expenses match the selected filters.")

def analytics_page():
    """Advanced analytics and visualizations."""
    
    st.header("📈 Analytics")
    
    tracker = st.session_state.tracker
    df = tracker.get_expenses_df()
    
    if df.empty:
        st.info("No expenses found. Add some expenses to see analytics!")
        return
    
    # Time period selector
    col1, col2 = st.columns(2)
    
    with col1:
        period = st.selectbox(
            "Analysis Period",
            ["Last 30 days", "Last 3 months", "Last 6 months", "All time"]
        )
    
    # Filter by period
    today = date.today()
    if period == "Last 30 days":
        start_date = today - timedelta(days=30)
    elif period == "Last 3 months":
        start_date = today - timedelta(days=90)
    elif period == "Last 6 months":
        start_date = today - timedelta(days=180)
    else:
        start_date = df['date'].min().date()
    
    filtered_df = df[df['date'].dt.date >= start_date]
    
    if filtered_df.empty:
        st.warning("No expenses in the selected period.")
        return
    
    # Key insights
    st.subheader("📊 Key Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spent = filtered_df['amount'].sum()
        st.metric("Total Spent", f"${total_spent:.2f}")
    
    with col2:
        avg_daily = total_spent / max(1, (today - start_date).days)
        st.metric("Avg Daily Spending", f"${avg_daily:.2f}")
    
    with col3:
        top_category = filtered_df.groupby('category')['amount'].sum().idxmax()
        top_category_amount = filtered_df.groupby('category')['amount'].sum().max()
        st.metric("Top Category", top_category)
        st.caption(f"${top_category_amount:.2f}")
    
    with col4:
        most_expensive = filtered_df.loc[filtered_df['amount'].idxmax()]
        st.metric("Largest Expense", f"${most_expensive['amount']:.2f}")
        st.caption(most_expensive['vendor'])
    
    st.divider()
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["Category Analysis", "Spending Trends", "Vendor Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Category pie chart
            category_totals = filtered_df.groupby('category')['amount'].sum()
            fig_pie = px.pie(
                values=category_totals.values,
                names=category_totals.index,
                title="Spending Distribution by Category"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Category bar chart
            fig_bar = px.bar(
                x=category_totals.values,
                y=category_totals.index,
                orientation='h',
                title="Category Spending Amounts",
                labels={'x': 'Amount ($)', 'y': 'Category'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        # Daily spending trend
        daily_spending = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum().reset_index()
        daily_spending.columns = ['date', 'amount']
        
        fig_trend = px.line(
            daily_spending,
            x='date',
            y='amount',
            title="Daily Spending Trend",
            markers=True
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Monthly comparison
        if len(filtered_df) > 0:
            monthly_spending = filtered_df.groupby(filtered_df['date'].dt.to_period('M'))['amount'].sum()
            if len(monthly_spending) > 1:
                fig_monthly = px.bar(
                    x=monthly_spending.index.astype(str),
                    y=monthly_spending.values,
                    title="Monthly Spending Comparison",
                    labels={'x': 'Month', 'y': 'Amount ($)'}
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab3:
        # Top vendors
        vendor_totals = filtered_df.groupby('vendor')['amount'].sum().sort_values(ascending=False).head(10)
        
        if len(vendor_totals) > 0:
            fig_vendors = px.bar(
                x=vendor_totals.values,
                y=vendor_totals.index,
                orientation='h',
                title="Top 10 Vendors by Spending",
                labels={'x': 'Amount ($)', 'y': 'Vendor'}
            )
            st.plotly_chart(fig_vendors, use_container_width=True)
        
        # Vendor frequency
        vendor_frequency = filtered_df['vendor'].value_counts().head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Most Frequent Vendors")
            st.dataframe(vendor_frequency.reset_index())
        
        with col2:
            st.subheader("Spending Summary")
            summary_stats = filtered_df['amount'].describe()
            st.dataframe(summary_stats)

if __name__ == "__main__":
    main()