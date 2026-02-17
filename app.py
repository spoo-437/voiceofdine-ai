import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(page_title="VoiceOfDine AI", layout="wide")

st.title("🍽️ VoiceOfDine AI")
st.subheader("Restaurant Review Intelligence & Decision Support System")
st.caption("Turning customer feedback into actionable business insights using NLP")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("reviews.csv")

# -----------------------------
# AUTO DETECT COLUMN NAMES
# -----------------------------
cols = [c.lower() for c in df.columns]

# restaurant name column
restaurant_col = None
for c in df.columns:
    if "name" in c.lower() or "restaurant" in c.lower() or "cafe" in c.lower():
        restaurant_col = c
        break

# review column
review_col = None
for c in df.columns:
    if "review" in c.lower() or "text" in c.lower():
        review_col = c
        break

# rating column (optional)
rating_col = None
for c in df.columns:
    if "rating" in c.lower() or "star" in c.lower():
        rating_col = c
        break

# -----------------------------
# SENTIMENT FUNCTION (NLP)
# -----------------------------
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

# -----------------------------
# LOGIN STYLE SELECTOR
# -----------------------------
st.sidebar.title("🔐 Restaurant Login")

restaurants = df[restaurant_col].dropna().unique()

selected_restaurant = st.sidebar.selectbox(
    "Select Your Restaurant",
    sorted(restaurants)
)

restaurant_df = df[df[restaurant_col] == selected_restaurant]

# -----------------------------
# DASHBOARD HEADER
# -----------------------------
st.subheader(f"📊 Dashboard for: {selected_restaurant}")

col1, col2 = st.columns(2)

col1.metric("Total Reviews", len(restaurant_df))

if rating_col:
    col2.metric("Average Rating", round(restaurant_df[rating_col].mean(), 2))

# -----------------------------
# BUSINESS HEALTH SCORE
# -----------------------------
if rating_col:
    avg_rating = restaurant_df[rating_col].mean()

    if avg_rating >= 4:
        health = "🟢 Excellent"
    elif avg_rating >= 3:
        health = "🟡 Needs Improvement"
    else:
        health = "🔴 At Risk"

    st.subheader("🏥 Business Health")
    st.write(health)

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------
st.subheader("😊 Customer Sentiment Distribution")

sentiment_counts = restaurant_df["Sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]

fig1 = px.pie(sentiment_counts, names="Sentiment", values="Count")
st.plotly_chart(fig1)

# -----------------------------
# WORD CLOUD
# -----------------------------
st.subheader("🗣️ Customer Voice Insights")

text = " ".join(restaurant_df[review_col].astype(str))

wc = WordCloud(width=800, height=400, background_color="white").generate(text)

plt.figure(figsize=(10,5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

# -----------------------------
# COMPLAINT DETECTION
# -----------------------------
st.subheader("⚠️ Detected Customer Complaints")

reviews_text = text.lower()

slow = reviews_text.count("slow")
expensive = reviews_text.count("expensive")
rude = reviews_text.count("rude")
bad = reviews_text.count("bad")

if slow > 2:
    st.warning(f"{slow} mentions of slow service")

if expensive > 2:
    st.warning(f"{expensive} pricing complaints")

if rude > 1:
    st.warning("Staff behavior issues detected")

if bad > 2:
    st.warning("Food quality complaints detected")

if slow == 0 and expensive == 0 and rude == 0 and bad == 0:
    st.success("No major complaints detected")

# -----------------------------
# AI SUGGESTIONS
# -----------------------------
st.subheader("🤖 AI Business Suggestions")

if rating_col:
    if avg_rating < 3:
        st.error("Customers are highly dissatisfied. Immediate improvements needed.")
    elif avg_rating < 4:
        st.info("Focus on improving consistency and service quality.")
    else:
        st.success("Great performance. Maintain current quality!")

if slow > 2:
    st.info("Improve service speed and staff coordination.")

if expensive > 2:
    st.info("Customers feel pricing is high. Review pricing strategy.")

if rude > 1:
    st.info("Provide staff training to improve customer interaction.")

# -----------------------------
# REVIEW TABLE
# -----------------------------
st.subheader("📄 Recent Customer Reviews")
st.dataframe(restaurant_df[[review_col]].head(15))

