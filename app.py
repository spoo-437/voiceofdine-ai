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
st.caption("Turning real customer feedback into business insights using NLP")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("reviews.csv")

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

# ---------------- CLEAN RATING COLUMN ----------------
if rating_col:
    df[rating_col] = df[rating_col].astype(str).str.extract(r'(\d+\.?\d*)')
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')

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

df["Sentiment"] = df[review_col].apply(get_sentiment)

# ---------------- RESTAURANT LOGIN ----------------
st.sidebar.title("🔐 Restaurant Login")

restaurants = df[restaurant_col].dropna().unique()

selected_restaurant = st.sidebar.selectbox(
    "Select Your Restaurant",
    sorted(restaurants)
)

restaurant_df = df[df[restaurant_col] == selected_restaurant]

# ---------------- HEADER ----------------
st.subheader(f"📊 Dashboard for: {selected_restaurant}")

col1, col2 = st.columns(2)

col1.metric("Total Reviews", len(restaurant_df))

if rating_col and restaurant_df[rating_col].notna().sum() > 0:
    avg_rating = restaurant_df[rating_col].mean()
    col2.metric("Average Rating", round(avg_rating, 2))
else:
    avg_rating = None
    col2.metric("Average Rating", "N/A")

# ---------------- BUSINESS HEALTH ----------------
if avg_rating is not None:
    if avg_rating >= 4:
        health = "🟢 Excellent"
    elif avg_rating >= 3:
        health = "🟡 Needs Improvement"
    else:
        health = "🔴 At Risk"

    st.subheader("🏥 Business Health Status")
    st.write(health)

# ---------------- SENTIMENT PIE ----------------
st.subheader("😊 Customer Sentiment")

sentiment_counts = restaurant_df["Sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]

fig1 = px.pie(sentiment_counts, names="Sentiment", values="Count")
st.plotly_chart(fig1)

# ---------------- WORD CLOUD ----------------
st.subheader("🗣️ Customer Voice Insights")

text = " ".join(restaurant_df[review_col].astype(str))

wc = WordCloud(width=800, height=400, background_color="white").generate(text)

plt.figure(figsize=(10,5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

# ---------------- SMART COMPLAINT DETECTION ----------------
st.subheader("⚠️ Key Customer Complaints")

reviews_text = text.lower()

service_words = ["slow", "late", "delay", "waiting", "wait"]
price_words = ["expensive", "costly", "overpriced"]
food_words = ["bad", "cold", "tasteless", "worst"]
staff_words = ["rude", "unfriendly", "attitude"]
clean_words = ["dirty", "unclean", "smell", "hygiene"]

def count_mentions(words):
    return sum(reviews_text.count(w) for w in words)

service_issues = count_mentions(service_words)
price_issues = count_mentions(price_words)
food_issues = count_mentions(food_words)
staff_issues = count_mentions(staff_words)
clean_issues = count_mentions(clean_words)

issues_found = False

if service_issues >= 1:
    st.warning(f"{service_issues} mentions about service problems")
    issues_found = True

if price_issues >= 1:
    st.warning(f"{price_issues} mentions about pricing issues")
    issues_found = True

if food_issues >= 1:
    st.warning(f"{food_issues} mentions about food quality issues")
    issues_found = True

if staff_issues >= 1:
    st.warning(f"{staff_issues} mentions about staff behavior")
    issues_found = True

if clean_issues >= 1:
    st.warning(f"{clean_issues} mentions about cleanliness")
    issues_found = True

if not issues_found:
    st.success("No major complaints detected")

# ---------------- AI SUGGESTIONS ----------------
st.subheader("🤖 AI Business Suggestions")

if service_issues > food_issues and service_issues > price_issues:
    st.info("Main issue: Improve service speed and order handling.")

if food_issues > service_issues:
    st.info("Main issue: Improve food taste and consistency.")

if price_issues > 0:
    st.info("Customers feel pricing is high. Review pricing strategy.")

if staff_issues > 0:
    st.info("Staff behavior concerns detected. Consider training.")

if clean_issues > 0:
    st.info("Improve cleanliness and hygiene standards.")

if avg_rating is not None:
    if avg_rating < 3:
        st.error("Urgent action needed: Customer satisfaction is low.")
    elif avg_rating < 4:
        st.warning("Moderate performance. Focus on improvement areas.")
    else:
        st.success("Strong performance. Maintain service quality.")

# ---------------- REVIEWS TABLE ----------------
st.subheader("📄 Recent Customer Reviews")
st.dataframe(restaurant_df[[review_col]].head(15))
