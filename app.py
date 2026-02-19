import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="VoiceOfDine AI", layout="wide")

st.title("🍽️ VoiceOfDine AI")
st.subheader("Restaurant Review Intelligence System")
st.caption("Login and analyze your customer reviews using AI")

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
    st.warning("No reviews found for this restaurant. Please upload your review file.")
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

# ---------------- DASHBOARD ----------------
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
st.subheader("🗣️ Word Cloud")

text = " ".join(restaurant_df[review_col].astype(str))
wc = WordCloud(width=800, height=400, background_color="white").generate(text)

plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

# ---------------- SIMPLE AI SUGGESTION ----------------
st.subheader("🤖 AI Suggestion")

negative_count = len(restaurant_df[restaurant_df["Sentiment"] == "Negative"])

if negative_count > len(restaurant_df) * 0.4:
    st.error("High negative feedback detected. Immediate improvement required.")
elif negative_count > len(restaurant_df) * 0.2:
    st.warning("Moderate negative feedback. Focus on service improvements.")
else:
    st.success("Customer sentiment is mostly positive. Maintain quality.")

# ---------------- SHOW REVIEWS ----------------
st.subheader("📄 Recent Reviews")
st.dataframe(restaurant_df[[review_col]].head(10))
