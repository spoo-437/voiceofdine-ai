import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="VoiceOfDine AI", layout="wide")

st.title("🍽️ VoiceOfDine AI")
st.subheader("Restaurant Review Intelligence & Decision Support System")
st.caption("AI-powered Customer Feedback Analysis")

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
    st.error("No dataset available.")
    st.stop()

# ---------------- AUTO DETECT COLUMNS ----------------
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
    st.warning("No reviews found. Please upload your review file.")
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
st.subheader("🧠 AI Decision Engine")

total_reviews = len(restaurant_df)
negative_count = len(restaurant_df[restaurant_df["Sentiment"] == "Negative"])

negative_ratio = negative_count / total_reviews

# Complaint keyword groups
service_words = ["slow", "delay", "waiting", "late"]
food_words = ["bad", "tasteless", "cold", "worst"]
price_words = ["expensive", "overpriced"]
staff_words = ["rude", "unfriendly"]
clean_words = ["dirty", "hygiene"]

def count_words(word_list):
    return sum(text_data.count(w) for w in word_list)

service_score = count_words(service_words)
food_score = count_words(food_words)
price_score = count_words(price_words)
staff_score = count_words(staff_words)
clean_score = count_words(clean_words)

issue_dict = {
    "Service": service_score,
    "Food Quality": food_score,
    "Pricing": price_score,
    "Staff Behavior": staff_score,
    "Cleanliness": clean_score
}

main_issue = max(issue_dict, key=issue_dict.get)

# ---------------- RISK LEVEL ----------------
if negative_ratio > 0.4:
    st.error("🔴 CRITICAL RISK LEVEL")
    st.write("### 📌 Strategic Actions Required:")

elif negative_ratio > 0.2:
    st.warning("🟡 MODERATE RISK LEVEL")
    st.write("### 📌 Improvement Recommended:")

else:
    st.success("🟢 STABLE PERFORMANCE")
    st.write("### 📌 Maintain Current Standards")

# ---------------- STRATEGIC ACTION PLAN ----------------
if main_issue == "Service":
    st.write("- Increase staff during peak hours")
    st.write("- Optimize order management system")
    st.write("- Conduct service training")

elif main_issue == "Food Quality":
    st.write("- Review ingredient quality")
    st.write("- Standardize cooking process")
    st.write("- Conduct kitchen audit")

elif main_issue == "Pricing":
    st.write("- Compare competitor pricing")
    st.write("- Introduce combo offers")
    st.write("- Improve value perception")

elif main_issue == "Staff Behavior":
    st.write("- Provide customer service training")
    st.write("- Monitor staff performance")
    st.write("- Improve customer interaction protocols")

elif main_issue == "Cleanliness":
    st.write("- Conduct hygiene inspection")
    st.write("- Increase cleaning frequency")
    st.write("- Assign cleanliness supervisor")

# ---------------- SHOW REVIEWS ----------------
st.subheader("📄 Recent Reviews")
st.dataframe(restaurant_df[[review_col]].head(10))
