import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ENEM Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data():
    """Load preprocessed ENEM data"""
    try:
        df = pd.read_csv("data/processed/preprocessed_data.csv")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


st.title("📊 ENEM Analysis Dashboard")
st.markdown(
    """
        This dashboard provides insights into the Brazilian National High School Exam (ENEM) results.
        Explore student performance across different demographic groups, socioeconomic factors, and knowledge areas.
    """
)

with st.spinner("Loading data... This may take a moment."):
    df = load_data()

if df is not None:
    st.sidebar.header("Data Overview")
    st.sidebar.text(f"Total Students: {df['ID'].nunique():,}")

    st.sidebar.header("Filters")

    area_cols = ['Natural Sciences', 'Human Sciences', 'Language', 'Mathematics']
    if all(col in df.columns for col in area_cols):
        knowledge_options = ["All"] + area_cols
        selected_knowledge = st.sidebar.selectbox("Filter by Knowledge Area", knowledge_options)
        
        if selected_knowledge != "All":
            min_score = float(df[selected_knowledge].min())
            threshold = st.sidebar.slider(
                f"Minimum {selected_knowledge} Score",
                min_value=min_score,
                max_value=float(df[selected_knowledge].max()),
                value=min_score,
                step=10.0
            )
            df = df[df[selected_knowledge] >= threshold]

    if "Sex" in df.columns:
        genders = ["All"] + sorted(df["Sex"].unique().tolist())
        selected_gender = st.sidebar.selectbox("Gender", genders)
        if selected_gender != "All":
            df = df[df["Sex"] == selected_gender]

    if "Family Income" in df.columns:
        income_values = sorted(df["Family Income"].unique().tolist())
        min_income = min(income_values)
        max_income = max(income_values)

        st.sidebar.subheader("Family Income (R$)")
        income_range = st.sidebar.slider(
            "Select income range",
            min_value=min_income,
            max_value=max_income,
            value=(min_income, max_income),
            step=1000
        )

        df = df[(df["Family Income"] >= income_range[0]) & (df["Family Income"] <= income_range[1])]

    if "Internet Access" in df.columns:
        internet_options = ["All", "Yes", "No"]
        selected_internet = st.sidebar.selectbox("Internet Access", internet_options)

        if selected_internet != "All":
            internet_value = 1 if selected_internet == "Yes" else 0
            df = df[df["Internet Access"] == internet_value]

    if "Number of Computers" in df.columns:
        computer_values = sorted(df["Number of Computers"].unique().tolist())
        computer_options = ["All"] + [str(val) for val in computer_values]
        selected_computers = st.sidebar.selectbox("Number of Computers", computer_options)

        if selected_computers != "All":
            df = df[df["Number of Computers"] == int(selected_computers)]

    st.sidebar.text(f"Filtered Students: {len(df):,}")

    # Main dashboard
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Average Overall Score",
            value=f"{df['Average'].mean():,.2f}",
            delta=None
        )

    with col2:
        if "Natural Sciences" in df.columns:
            st.metric(
                label="Avg Natural Sciences",
                value=f"{df['Natural Sciences'].mean():.2f}",
                delta=None
            )

    with col3:
        if "Mathematics" in df.columns:
            st.metric(
                label="Avg Mathematics",
                value=f"{df['Mathematics'].mean():.2f}",
                delta=None
            )

    with col4:
        if "Human Sciences" in df.columns:
            st.metric(
                label="Avg Human Sciences",
                value=f"{df['Human Sciences'].mean():.2f}",
                delta=None
            )

    with col5:
        if "Language" in df.columns:
            st.metric(
                label="Avg Language",
                value=f"{df['Language'].mean():.2f}",
                delta=None
            )

    st.markdown("---")

    st.header("📚 Performance by Knowledge Area")

    area_cols = ['Natural Sciences', 'Human Sciences', 'Language', 'Mathematics']

    # Create a sample for plotting to improve performance
    sample_size = min(50000, len(df))
    df_sample = df.sample(sample_size, random_state=42) if len(df) > sample_size else df

    area_means = df[area_cols].mean().sort_values()
    fig = px.bar(
        x=area_means.values,
        y=area_means.index,
        orientation='h',
        title='Average scores by knowledge area',
        labels={'x': 'Average Score', 'y': ''},
        text=[f'{val:.2f}' for val in area_means.values]
    )
    fig.update_layout(height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Score Distribution by Knowledge Area")

    tab1, tab2 = st.tabs(["Histograms", "Boxplots"])

    with tab1:
        hist_data = []
        for col in area_cols:
            hist_data.append(df_sample[col].dropna())

        fig = go.Figure()
        for i, col in enumerate(area_cols):
            fig.add_trace(go.Histogram(
                x=hist_data[i],
                name=col,
                opacity=0.7,
                nbinsx=30
            ))

        fig.update_layout(
            title="Score Distribution by Knowledge Area",
            xaxis_title="Score",
            yaxis_title="Count",
            barmode='overlay',
            legend_title="Subject",
            height=500,
            xaxis=dict(
                tickmode='linear',
                tick0=200,
                dtick=50,
                tickformat='.0f'
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = go.Figure()
        for col in area_cols:
            fig.add_trace(go.Box(
                y=df_sample[col].dropna(),
                name=col,
                boxmean=True
            ))

        fig.update_layout(
            title="Score Distribution by Knowledge Area",
            yaxis_title="Score",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.header("💰 Socioeconomic Analysis")

    if "Family Income" in df.columns:
        st.subheader("Family Income vs Performance")

        income_stats = df.groupby(['Family Income'])['Average'].mean().reset_index()

        fig = px.line(
            income_stats,
            x='Family Income',
            y='Average',
            markers=True,
            title="Average Score by Family Income",
            labels={"Family Income": "Family Income (R$)", "Average": "Average Score"}
        )

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Income vs Score Distribution")

        if "Score Bin" not in df.columns:
            df["Score Bin"] = pd.cut(df["Average"], bins=8)
            # Convert interval objects to strings to avoid serialization issues
            df["Score Bin"] = df["Score Bin"].astype(str)

        heatmap_data = pd.crosstab(df['Family Income'], df['Score Bin'], normalize='index')

        formatted_income = [f'Up to R${x:,.2f}' for x in heatmap_data.index]
        heatmap_data.index = formatted_income

        fig = px.imshow(
            heatmap_data,
            color_continuous_scale='RdBu_r',
            labels=dict(x="Score Range", y="Income Level", color="Percentage"),
            title="Distribution of Score Ranges Within Each Income Level"
        )

        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.header("👨‍👩‍👧‍👦 Demographic Analysis")

    if "Age Group" in df.columns:
        st.subheader("Age vs Performance")

        age_performance = df.groupby(['Age Group'])['Average'].mean().reset_index()

        fig = px.line(
            age_performance,
            x='Age Group',
            y='Average',
            markers=True,
            title="Average Score by Age Group",
            labels={"Age Group": "Age Group", "Average": "Average Score"}
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    if "Sex" in df.columns:
        st.subheader("Gender Analysis")

        col1, col2 = st.columns(2)

        with col1:
            gender_counts = df["Sex"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]

            fig = px.pie(
                gender_counts,
                values="Count",
                names="Gender",
                title="Gender Distribution",
                hole=0.4
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            gender_perf = df.groupby("Sex")["Average"].mean().reset_index()
            gender_perf.columns = ["Gender", "Average Score"]

            fig = px.bar(
                gender_perf,
                x="Gender",
                y="Average Score",
                title="Average Score by Gender",
                color="Gender"
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Score Distribution by Gender")
        fig = px.box(
            df_sample,
            x="Sex",
            y="Average",
            title="Distribution of Overall Scores by Gender",
            color="Sex",
            notched=True
        )

        fig.update_layout(
            height=500,
            xaxis_title="Gender",
            yaxis_title="Score"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.header("💻 Technology Access Analysis")

    if "Internet Access" in df.columns and "Number of Computers" in df.columns:
        st.subheader("Internet Access vs Performance")

        internet_sample = df.sample(min(100000, len(df)), random_state=42) if len(df) > 100000 else df

        fig = px.histogram(
            internet_sample,
            x="Average",
            color="Internet Access",
            color_discrete_map={0: "red", 1: "green"},
            barmode="overlay",
            opacity=0.7,
            nbins=50,
            title="Score Distribution by Internet Access",
            hover_data=["Average"]
        )

        fig.update_layout(
            height=500,
            legend_title="Internet Access",
        )

        newnames = {0: "No Internet", 1: "Has Internet"}
        fig.for_each_trace(lambda t: t.update(name=newnames[int(t.name)])
        if t.name in ["0", "1"] else t)

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Number of Computers vs Performance")

        fig = px.box(
            df,
            x='Number of Computers',
            y='Average',
            title="Score Distribution by Number of Computers",
            labels={
                'Number of Computers': 'Number of Computers',
                'Average': 'Score'
            }
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Combined Technology Access Effect")

        df_sample_tech = df.sample(min(50000, len(df)), random_state=42) if len(df) > 50000 else df

        fig = px.scatter(
            df_sample_tech,
            x='Number of Computers',
            y='Average',
            color='Internet Access',
            color_discrete_map={0: 'red', 1: 'green'},
            labels={
                'Number of Computers': 'Number of Computers at Home',
                'Average': 'Average Score',
                'Internet Access': 'Internet Access'
            },
            title="Score vs Number of Computers by Internet Access",
            hover_data=['Average']
        )

        for internet_value, color in [(0, 'red'), (1, 'green')]:
            subset = df_sample_tech[df_sample_tech['Internet Access'] == internet_value]
            if not subset.empty:
                avg_by_computer = subset.groupby('Number of Computers')['Average'].mean().reset_index()
                fig.add_trace(
                    go.Scatter(
                        x=avg_by_computer['Number of Computers'],
                        y=avg_by_computer['Average'],
                        mode='lines+markers',
                        line=dict(color=color, width=3),
                        name=f"{'With' if internet_value == 1 else 'Without'} Internet (avg)",
                        showlegend=True
                    )
                )

        fig.update_layout(
            height=500,
            legend_title="Internet Access",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Distribution of Students by Technology Access")

        col1, col2 = st.columns(2)

        with col1:
            internet_counts = df['Internet Access'].map({0: 'No Internet', 1: 'Has Internet'}).value_counts()

            fig = px.pie(
                values=internet_counts.values,
                names=internet_counts.index,
                title="Internet Access Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            computer_counts = df['Number of Computers'].value_counts().sort_index().reset_index()
            computer_counts.columns = ['Number of Computers', 'Count']

            fig = px.bar(
                computer_counts,
                x='Number of Computers',
                y='Count',
                title="Distribution by Number of Computers",
                color='Number of Computers'
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Internet Access or Number of Computers data not available.")

    st.markdown("---")
    st.markdown("""
    **Note:** This dashboard presents insights from ENEM data. The visualizations can help educators,
    policymakers, and researchers understand patterns and factors influencing student performance.
    
    Data source: INEP (National Institute for Educational Studies and Research "Anísio Teixeira").
    """)

else:
    st.error("Failed to load data. Please check the data path and file availability.")
    st.info("Make sure the preprocessed data is available at 'data/processed/preprocessed_data.csv'")
