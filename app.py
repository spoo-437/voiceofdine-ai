import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="VoiceOfDine AI", layout="wide")

st.title("🍽️ VoiceOfDine AI")
st.subheader("Executive Restaurant Intelligence System")
st.caption("AI-Powered Sentiment, Risk & Business Performance Dashboard")

# ---------------- LOGIN SECTION ----------------
st.sidebar.title("🔐 Restaurant Login")
restaurant_name = st.sidebar.text_input("Enter Your Restaurant Name")
uploaded_file = st.sidebar.file_uploader("Upload Your Reviews CSV (Optional)", type=["csv"])

# ---------------- LOAD DATA ----------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("reviews.csv")
    except:
        df = None

if df is None:
    st.error("No dataset found.")
    st.stop()

# ---------------- DETECT COLUMNS ----------------
restaurant_col = None
review_col = None
rating_col = None

for c in df.columns:
    cl = c.lower()
    if restaurant_col is None and ("name" in cl or "restaurant" in cl):
        restaurant_col = c
    if review_col is None and ("review" in cl or "text" in cl):
        review_col = c
    if rating_col is None and ("rating" in cl or "star" in cl):
        rating_col = c

if review_col is None:
    st.error("Review column not detected.")
    st.stop()

# ---------------- FILTER DATA ----------------
if uploaded_file is not None:
    restaurant_df = df
else:
    if restaurant_col and restaurant_name:
        restaurant_df = df[df[restaurant_col].str.lower() == restaurant_name.lower()]
    else:
        restaurant_df = pd.DataFrame()

if restaurant_df.empty:
    st.warning("No reviews found. Please upload dataset.")
    st.stop()

# ---------------- CLEAN RATING ----------------
if rating_col:
    restaurant_df[rating_col] = restaurant_df[rating_col].astype(str).str.extract(r'(\d+\.?\d*)')
    restaurant_df[rating_col] = pd.to_numeric(restaurant_df[rating_col], errors='coerce')

# ---------------- SENTIMENT ANALYSIS ----------------
def get_sentiment(text):
    try:
        score = TextBlob(str(text)).sentiment.polarity
        if score > 0:
            return "Positive"
        elif score == 0:
            return "Neutral"
        else:
            return "Negative"
    except:
        return "Neutral"

restaurant_df["Sentiment"] = restaurant_df[review_col].apply(get_sentiment)

# ---------------- BASIC METRICS ----------------
st.subheader(f"📊 Dashboard for: {restaurant_name}")

total_reviews = len(restaurant_df)
negative_count = len(restaurant_df[restaurant_df["Sentiment"] == "Negative"])
positive_count = len(restaurant_df[restaurant_df["Sentiment"] == "Positive"])

negative_ratio = negative_count / total_reviews
positive_ratio = positive_count / total_reviews

col1, col2 = st.columns(2)
col1.metric("Total Reviews", total_reviews)

if rating_col and restaurant_df[rating_col].notna().sum() > 0:
    avg_rating = restaurant_df[rating_col].mean()
    col2.metric("Average Rating", round(avg_rating, 2))
else:
    avg_rating = None
    col2.metric("Average Rating", "N/A")

# ---------------- SENTIMENT PIE ----------------
st.subheader("😊 Sentiment Distribution")
sentiment_counts = restaurant_df["Sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]
fig = px.pie(sentiment_counts, names="Sentiment", values="Count")
st.plotly_chart(fig)

# ---------------- WORD CLOUD ----------------
st.subheader("🗣️ Customer Voice Insights")
text_data = " ".join(restaurant_df[review_col].astype(str)).lower()
wc = WordCloud(width=800, height=400, background_color="white").generate(text_data)
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

# ---------------- ISSUE DETECTION ----------------
service_words = ["slow", "delay", "waiting", "late"]
food_words = ["bad", "tasteless", "cold", "worst"]
price_words = ["expensive", "overpriced"]
staff_words = ["rude", "unfriendly"]
clean_words = ["dirty", "hygiene"]

def count_words(word_list):
    return sum(text_data.count(w) for w in word_list)

issue_scores = {
    "Service": count_words(service_words) / total_reviews,
    "Food Quality": count_words(food_words) / total_reviews,
    "Pricing": count_words(price_words) / total_reviews,
    "Staff Behavior": count_words(staff_words) / total_reviews,
    "Cleanliness": count_words(clean_words) / total_reviews
}

main_issue = max(issue_scores, key=issue_scores.get)

# ---------------- PERFORMANCE SCORE ----------------
st.subheader("🏆 Performance Score")

rating_score = (avg_rating / 5) if avg_rating else 0.5
complaint_severity = sum(issue_scores.values())

performance_score = (
    positive_ratio * 40 +
    (1 - negative_ratio) * 30 +
    rating_score * 20 +
    (1 - complaint_severity) * 10
)

performance_score = round(performance_score, 2)
st.metric("Overall Performance Score (0–100)", performance_score)

# ---------------- RISK CLASSIFICATION ----------------
st.subheader("🧠 Risk Classification")

if negative_ratio > 0.5:
    risk = "Critical"
    st.error("🔴 CRITICAL RISK LEVEL")
elif negative_ratio > 0.3:
    risk = "High"
    st.warning("🟠 HIGH RISK LEVEL")
elif negative_ratio > 0.15:
    risk = "Moderate"
    st.warning("🟡 MODERATE RISK LEVEL")
else:
    risk = "Low"
    st.success("🟢 LOW RISK LEVEL")

st.write(f"Main Issue Detected: **{main_issue}**")

# ---------------- STRATEGIC ACTIONS ----------------
st.subheader("📌 Strategic Action Plan")

if risk == "Critical":
    st.write("Immediate operational restructuring required.")
elif risk == "High":
    st.write("Focused improvement strategy recommended.")
elif risk == "Moderate":
    st.write("Minor operational tuning required.")
else:
    st.write("Maintain excellence and expand growth strategy.")

st.write(f"Primary focus area: **{main_issue}**")

# ---------------- COMPETITOR BENCHMARK ----------------
if restaurant_col:
    st.subheader("📊 Competitor Benchmarking")

    competitor_scores = {}

    for rest in df[restaurant_col].unique():
        temp_df = df[df[restaurant_col] == rest]
        if len(temp_df) < 5:
            continue
        temp_df["Sentiment"] = temp_df[review_col].apply(get_sentiment)
        pos_ratio = (temp_df["Sentiment"] == "Positive").mean()
        competitor_scores[rest] = round(pos_ratio * 100, 2)

    benchmark_df = pd.DataFrame(
        competitor_scores.items(),
        columns=["Restaurant", "Positive Sentiment %"]
    ).sort_values(by="Positive Sentiment %", ascending=False)

    st.dataframe(benchmark_df)

# ---------------- PREDICTIVE RISK OUTLOOK ----------------
st.subheader("🔮 Predictive Risk Outlook")

if negative_ratio > 0.4:
    st.write("Projected Risk Next Month: High")
elif negative_ratio > 0.2:
    st.write("Projected Risk Next Month: Moderate")
else:
    st.write("Projected Risk Next Month: Low")

# ---------------- FINANCIAL IMPACT ----------------
st.subheader("💰 Estimated Financial Impact")

average_order_value = 800
lost_customers = negative_count * 2
estimated_loss = lost_customers * average_order_value

st.metric("Estimated Monthly Revenue Loss (₹)", estimated_loss)

# ---------------- RECENT REVIEWS ----------------
st.subheader("📄 Recent Reviews")
st.dataframe(restaurant_df[[review_col]].head(10))
