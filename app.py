import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="VoiceOfDine AI", layout="wide")

st.title("🍽️ VoiceOfDine AI")
st.subheader("Restaurant Review Intelligence & AI Decision System")
st.caption("Dynamic NLP-Powered Business Intelligence Dashboard")

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
    if restaurant_col is None and ("name" in cl or "restaurant" in cl or "cafe" in cl):
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
    st.warning("No reviews found. Please upload your dataset.")
    st.stop()

# ---------------- CLEAN RATING ----------------
if rating_col:
    restaurant_df[rating_col] = restaurant_df[rating_col].astype(str).str.extract(r'(\d+\.?\d*)')
    restaurant_df[rating_col] = pd.to_numeric(restaurant_df[rating_col], errors='coerce')

# ---------------- SENTIMENT FUNCTION ----------------
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

# ---------------- DASHBOARD HEADER ----------------
st.subheader(f"📊 Dashboard for: {restaurant_name}")

col1, col2 = st.columns(2)
col1.metric("Total Reviews", len(restaurant_df))

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

# ---------------- AI DECISION ENGINE ----------------
st.subheader("🧠 AI Risk & Decision Engine")

total_reviews = len(restaurant_df)
negative_count = len(restaurant_df[restaurant_df["Sentiment"] == "Negative"])
positive_count = len(restaurant_df[restaurant_df["Sentiment"] == "Positive"])

negative_ratio = negative_count / total_reviews
positive_ratio = positive_count / total_reviews

# --- Keyword Groups ---
service_words = ["slow", "delay", "waiting", "late"]
food_words = ["bad", "tasteless", "cold", "worst"]
price_words = ["expensive", "overpriced"]
staff_words = ["rude", "unfriendly"]
clean_words = ["dirty", "hygiene"]

def count_words(word_list):
    return sum(text_data.count(w) for w in word_list)

issue_scores = {
    "Service": count_words(service_words),
    "Food Quality": count_words(food_words),
    "Pricing": count_words(price_words),
    "Staff Behavior": count_words(staff_words),
    "Cleanliness": count_words(clean_words)
}

# Normalize scores
for key in issue_scores:
    issue_scores[key] = issue_scores[key] / total_reviews

main_issue = max(issue_scores, key=issue_scores.get)
severity = issue_scores[main_issue]

# ---------------- RISK LEVEL ----------------
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

st.write(f"### 📌 Main Issue Detected: {main_issue}")

# ---------------- DYNAMIC STRATEGY ----------------
if risk == "Critical":
    st.write("### 🚨 Immediate Strategic Intervention Required")

    if main_issue == "Service":
        st.write("- Hire additional staff")
        st.write("- Redesign workflow process")
        st.write("- Implement service KPIs")

    elif main_issue == "Food Quality":
        st.write("- Replace suppliers")
        st.write("- Conduct kitchen audit")
        st.write("- Introduce strict quality control")

    elif main_issue == "Pricing":
        st.write("- Reposition pricing strategy")
        st.write("- Launch aggressive promotions")
        st.write("- Conduct competitor analysis")

    elif main_issue == "Staff Behavior":
        st.write("- Mandatory staff retraining")
        st.write("- Performance monitoring system")
        st.write("- Improve service protocols")

    elif main_issue == "Cleanliness":
        st.write("- Immediate hygiene inspection")
        st.write("- Increase cleaning frequency")
        st.write("- Assign sanitation supervisor")

elif risk == "High":
    st.write("### ⚠ Strategic Improvement Plan")
    st.write(f"- Focus operational improvements on {main_issue}")
    st.write("- Monitor feedback weekly")
    st.write("- Set measurable improvement targets")

elif risk == "Moderate":
    st.write("### 📈 Controlled Optimization Strategy")
    st.write(f"- Minor improvements required in {main_issue}")
    st.write("- Track monthly performance")
    st.write("- Improve operational efficiency")

else:
    st.write("### ✅ Maintain Operational Excellence")

    if positive_ratio > 0.6:
        st.write("- Expand marketing campaigns")
        st.write("- Introduce loyalty programs")
        st.write("- Consider business expansion")

    else:
        st.write("- Maintain monitoring system")
        st.write("- Improve minor customer touchpoints")

# ---------------- RECENT REVIEWS ----------------
st.subheader("📄 Recent Reviews")
st.dataframe(restaurant_df[[review_col]].head(10))
