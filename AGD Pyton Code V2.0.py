import streamlit as st
import math

st.set_page_config(page_title="Minimum Trips Calculator", layout="centered")

# Display logos and title
st.markdown("""
<div style='text-align:center;'>
    <img src='https://raw.githubusercontent.com/FlipZlogit/AGD/main/A.jpeg' width='120' style='vertical-align:middle;'/>
    <img src='https://raw.githubusercontent.com/FlipZlogit/AGD/main/NAB.png' width='120' style='vertical-align:middle;'/>
    <h1 style='font-family:Arial, sans-serif; color:black;'>Minimum Trips Calculator</h1>
</div><hr>
""", unsafe_allow_html=True)

# Inputs without pre-filled values
max_ebd_per_trip = st.number_input("Max EBD bags per trip:", min_value=1, step=1, value=None, placeholder="Enter number")
bulk_cash_amount = st.number_input("Enter total bulk cash amount:", min_value=0, step=1, value=None, placeholder="Enter amount")

bulk_bag_values = []

if bulk_cash_amount and bulk_cash_amount > 0:
    num_bulk_bags = st.number_input("Enter number of bulk cash bags (at least 1):", min_value=1, step=1, value=None, placeholder="Enter number")

    if num_bulk_bags:
        if num_bulk_bags > 1:
            known_denomination = st.radio("Do you know the value of each bulk bag?", ["Yes", "No"], index=None)
            if known_denomination == "Yes":
                bulk_bag_values = []
                for i in range(int(num_bulk_bags)):
                    val = st.number_input(f"Value of Bulk Bag {i+1}:", min_value=1, step=1, key=f'bulkbag_{i}', value=None, placeholder="Enter amount")
                    bulk_bag_values.append(val)
                if None not in bulk_bag_values and sum(bulk_bag_values) != bulk_cash_amount:
                    st.error("Values entered do not match the total bulk cash amount.")
                    st.stop()
            else:
                bulk_bag_values = [bulk_cash_amount // num_bulk_bags] * num_bulk_bags
                remainder = bulk_cash_amount % num_bulk_bags
                for i in range(remainder):
                    bulk_bag_values[i] += 1
        else:
            bulk_bag_values = [bulk_cash_amount]

num_ebd_bags = st.number_input("Number of EBD bags (not including bulk):", min_value=0, step=1, value=None, placeholder="Enter number")
num_idm_bags = st.number_input("Number of IDM bags:", min_value=0, step=1, value=None, placeholder="Enter number")

idm_values = []
if num_idm_bags:
    for i in range(int(num_idm_bags)):
        val = st.number_input(f"Value of IDM {i+1}:", min_value=1, step=1, key=f'idm_{i}', value=None, placeholder="Enter amount")
        idm_values.append(val)

has_atm = st.radio("ATM value to consider?", ["No", "Yes"], index=0)
atm_value = 0
if has_atm == "Yes":
    atm_value = st.number_input("Enter ATM value:", min_value=1, step=1, value=None, placeholder="Enter amount")

if st.button("Calculate Minimum Trips"):
    MAX_TRIP_VALUE = 350000
    ebd_value = MAX_TRIP_VALUE / max_ebd_per_trip if max_ebd_per_trip else 0
    trips = []

    cash_items = (
        [('Bulk', val) for val in bulk_bag_values]
        + [('EBD', ebd_value)] * (num_ebd_bags or 0)
        + [('IDM', val) for val in idm_values]
        + ([('ATM', atm_value)] if atm_value else [])
    )

    cash_items.sort(key=lambda x: x[1], reverse=True)

    while cash_items:
        trip, trip_value, ebd_count = [], 0, 0
        for item in cash_items[:]:
            bag_type, value = item
            if bag_type == 'EBD' and ebd_count < max_ebd_per_trip and trip_value + value <= MAX_TRIP_VALUE:
                trip.append(item)
                trip_value += value
                ebd_count += 1
                cash_items.remove(item)
            elif bag_type != 'EBD' and trip_value + value <= MAX_TRIP_VALUE:
                trip.append(item)
                trip_value += value
                cash_items.remove(item)

        trips.append((trip, trip_value))

    st.markdown("---")
    st.header("Trip Breakdown")
    for i, (trip, trip_total) in enumerate(trips, 1):
        bulk_total = sum(val for t, val in trip if t == 'Bulk')
        bulk_count = sum(1 for t in trip if t[0] == 'Bulk')
        ebd_count = sum(1 for t in trip if t[0] == 'EBD')
        idm_items = [f"IDM (${val:,})" for t, val in trip if t == 'IDM']
        atm_items = [f"ATM (${val:,})" for t, val in trip if t == 'ATM']

        summary = []
        if bulk_count:
            summary.append(f"{bulk_count} × Bulk (${bulk_total:,})")
        if ebd_count:
            summary.append(f"{ebd_count} × EBDs")
        summary += idm_items + atm_items

        st.write(f"**Trip {i}:** {', '.join(summary)} → **Total Trip:** ${math.ceil(trip_total):,}")

st.markdown("<hr><div style='text-align: center; color:grey;'>Created by A. Cohen</div>", unsafe_allow_html=True)
