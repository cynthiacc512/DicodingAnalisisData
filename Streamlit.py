import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    order_items = pd.read_csv("order_items_dataset.csv")
    order_reviews = pd.read_csv("order_reviews_dataset.csv")
    products = pd.read_csv("products_dataset.csv")
    sellers = pd.read_csv("sellers_dataset.csv")
    return order_items, order_reviews, products, sellers

order_items, order_reviews, products, sellers = load_data()

# merge data
order_items_clean = order_items[['order_id', 'product_id', 'seller_id', 'price']]
order_reviews_clean = order_reviews[['order_id', 'review_score']]
products_clean = products[['product_id', 'product_category_name']]
sellers_clean = sellers[['seller_id', 'seller_state']]

merged = order_items_clean.merge(order_reviews_clean, on='order_id', how='left')
merged = merged.merge(products_clean, on='product_id', how='left')
merged = merged.merge(sellers_clean, on='seller_id', how='left')

# Buat filter
st.sidebar.header("Filter Data")

selected_state = st.sidebar.multiselect(
    "Pilih lokasi seller:", 
    options=merged['seller_state'].unique(), 
    default=merged['seller_state'].unique()
)

selected_category = st.sidebar.multiselect(
    "Pilih kategori produk:", 
    options=merged['product_category_name'].dropna().unique(), 
    default=merged['product_category_name'].dropna().unique()
)

min_price = float(merged['price'].min())
max_price = float(merged['price'].max())
price_range = st.sidebar.slider("Rentang harga:", min_price, max_price, (min_price, max_price))

filtered = merged[
    (merged['seller_state'].isin(selected_state)) &
    (merged['product_category_name'].isin(selected_category)) &
    (merged['price'].between(price_range[0], price_range[1]))
]

# Title and angka kesimpulan
st.title("Brazil E-Commerce Dashboard")

st.markdown("## Data")
col1, col2, col3 = st.columns(3)
col1.metric("Total Produk", filtered['product_id'].nunique())
col2.metric("Rata-rata Rating", f"{filtered['review_score'].mean():.2f}")
col3.metric("Total Seller", filtered['seller_id'].nunique())

# Pertanyaan 1
st.header("1. Jumlah Pembelian vs Rating Produk")
st.markdown("Apakah produk yang banyak dibeli cenderung memiliki rating lebih tinggi?")

purchase_rating = filtered.groupby('product_id').agg({
    'order_id': 'count',
    'review_score': 'mean'
}).reset_index().rename(columns={'order_id': 'jumlah_pembelian', 'review_score': 'rata2_rating'})

fig1 = px.scatter(
    purchase_rating,
    x='jumlah_pembelian',
    y='rata2_rating',
    title='Jumlah Pembelian vs Rating',
    labels={'jumlah_pembelian': 'Jumlah Pembelian', 'rata2_rating': 'Rata-rata Rating'},
    hover_data=['jumlah_pembelian', 'rata2_rating']
)
st.plotly_chart(fig1, use_container_width=True)

# Pertanyaan 2
st.header("2. Harga vs Jumlah Pembelian")
st.markdown("Apakah harga produk yang lebih murah cenderung dibeli lebih banyak?")

price_purchase = filtered.groupby('product_id').agg({
    'price': 'mean',
    'order_id': 'count'
}).reset_index().rename(columns={'order_id': 'jumlah_pembelian'})

fig2 = px.scatter(
    price_purchase,
    x='price',
    y='jumlah_pembelian',
    title='Harga Produk vs Jumlah Pembelian',
    labels={'price': 'Harga Rata-rata Produk', 'jumlah_pembelian': 'Jumlah Pembelian'},
    hover_data=['price', 'jumlah_pembelian']
)
st.plotly_chart(fig2, use_container_width=True)

# Pertanyaan 3
st.header("3. Distribusi Penjualan Berdasarkan Lokasi Seller")
st.markdown("Apakah lokasi seller mempengaruhi volume penjualan?")

sales_location = filtered.groupby('seller_state').agg({
    'order_id': 'count'
}).reset_index().rename(columns={'order_id': 'jumlah_penjualan'}).sort_values(by='jumlah_penjualan', ascending=False)

fig3 = px.bar(
    sales_location,
    x='seller_state',
    y='jumlah_penjualan',
    title='Penjualan per Lokasi Seller',
    labels={'seller_state': 'State Seller', 'jumlah_penjualan': 'Jumlah Penjualan'}
)
st.plotly_chart(fig3, use_container_width=True)
