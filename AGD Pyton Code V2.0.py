import streamlit as st
import math

# Set page configuration must be the first Streamlit command
st.set_page_config(page_title="Minimum Trips Calculator", layout="centered")

# Display logos and title
st.markdown("""
<div style='text-align:center;'>
    <img src='https://raw.githubusercontent.com/FlipZlogit/AGD/main/A.jpeg' width='120' style='vertical-align:middle;'/>
    <img src='https://raw.githubusercontent.com/FlipZlogit/AGD/main/NAB.png' width='120' style='vertical-align:middle;'/>
    <h1 style='font-family:Arial, sans-serif; color:black;'>Minimum Trips Calculator</h1>
</div><hr>
""", unsafe_allow_html=True)

# Inputs reordered and without pre-filled values
max_ebd_per_trip = st.number_input("Max EBDs bags allowed per trip", min_value=1, step=1, value=None, placeholder="Enter number")
num_ebd_bags = st.number_input("Number of EBD bags in the safe (not including bulk):", min_value=0, step=1, value=None, placeholder="Enter number")
bulk_cash_amount = st.number_input("Enter total bulk cash amount:", min_value=0, step=1000, value=None, placeholder="Enter amount")

bulk_bag_values = []

if bulk_cash_amount and bulk_cash_amount > 0:
    min_bulk_bags = max(1, math.ceil(bulk_cash_amount / 350000))
    num_bulk_bags = st.number_input("Enter number of bulk cash bags (at least 1):", min_value=min_bulk_bags, step=1, value=min_bulk_bags, placeholder="Enter number")

    if num_bulk_bags > 1:
        bulk_bag_values = [bulk_cash_amount // num_bulk_bags] * num_bulk_bags
        remainder = bulk_cash_amount % num_bulk_bags
        for i in range(remainder):
            bulk_bag_values[i] += 1
    else:
        bulk_bag_values = [bulk_cash_amount]

num_idm_bags = st.number_input("Number of IDM bags:", min_value=0, step=1, value=None, placeholder="Enter number")

idm_values = []
if num_idm_bags:
    for i in range(int(num_idm_bags)):
        val = st.number_input(f"Value of IDM {i+1}:", min_value=1, step=1000, key=f'idm_{i}', value=None, placeholder="Enter amount")
        idm_values.append(val)

has_atm = st.radio("ATM value to consider?", ["No", "Yes"], index=0)
atm_value = 0
if has_atm == "Yes":
    atm_value = st.number_input("Enter ATM value:", min_value=1, step=1000, value=None, placeholder="Enter amount")

has_coin = st.radio("Coin bags to consider?", ["No", "Yes"], index=0)
num_coin_bags = 0
if has_coin == "Yes":
    num_coin_bags = st.number_input("Enter number of coin bags:", min_value=1, step=1, value=None, placeholder="Enter number")

if st.button("Calculate Minimum Trips"):
    MAX_TRIP_VALUE = 350000
    ebd_value = math.ceil(MAX_TRIP_VALUE / max_ebd_per_trip) if max_ebd_per_trip else 0  # Ensure proper rounding up

    cash_items = (
        [('Bulk', val) for val in bulk_bag_values]
        + [('EBD', ebd_value)] * (num_ebd_bags or 0)
        + [('IDM', val) for val in idm_values]
        + ([('ATM', atm_value)] if atm_value else [])
        + [('Coin', 2000)] * num_coin_bags
    )

    cash_items.sort(key=lambda x: x[1], reverse=True)

    trips = []
    total_bags = sum(1 for item in cash_items if item[0] in ['EBD', 'Bulk'])
    total_value = sum(item[1] for item in cash_items)
    total_idms = len(idm_values)
    total_coins = num_coin_bags
    total_atms = 1 if atm_value else 0
    while cash_items:
        trip, trip_value, bag_count = [], 0, 0
        ebd_count = 0
        for item in cash_items[:]:
            bag_type, value = item
            if bag_type == 'EBD' and ebd_count < max_ebd_per_trip:
                if trip_value + value <= MAX_TRIP_VALUE:
                    trip.append(item)
                    trip_value += value
                    ebd_count += 1
                    cash_items.remove(item)
            elif bag_type != 'EBD' and trip_value + value <= MAX_TRIP_VALUE:
                trip.append(item)
                trip_value += value
                cash_items.remove(item)
        trips.append((trip, trip_value, bag_count))

    st.markdown("---")
    st.subheader("Trip Breakdown")
    for i, (trip, trip_total, bag_count) in enumerate(trips, 1):
        trip_summary = []
        ebd_count = sum(1 for t in trip if t[0] == 'EBD')
        bulk_count = sum(1 for t in trip if t[0] == 'Bulk')
        idm_list = [f"IDM (${t[1]:,})" for t in trip if t[0] == 'IDM']
        atm_list = ["ATM ($" + f"{t[1]:,})" for t in trip if t[0] == 'ATM']
        coin_count = sum(1 for t in trip if t[0] == 'Coin')

        if ebd_count:
            trip_summary.append(f"{ebd_count} × EBDs")
        if bulk_count:
            trip_summary.append(f"{bulk_count} × Bulk")
        if idm_list:
            trip_summary.extend(idm_list)
        if atm_list:
            trip_summary.extend(atm_list)
        if coin_count:
            trip_summary.append(f"{coin_count} × Coin Bags")

        st.markdown(f"**Trip {i}:** {', '.join(trip_summary)} → **Total Trip:** ${math.ceil(trip_total):,} | {bag_count} Bags", unsafe_allow_html=True)

    st.markdown(f"<hr><strong>Total:</strong> ${math.ceil(total_value):,} | {total_bags} Bags | {total_idms} IDMs | {total_atms} ATM | {total_coins} Coin Bags", unsafe_allow_html=True)
