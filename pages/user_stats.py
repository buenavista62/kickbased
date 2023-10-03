import streamlit as st
from kickbase_singleton import kickbase_singleton


if st.session_state.logged:
    kb = kickbase_singleton.kb
    user = kickbase_singleton.user
    leagues = kickbase_singleton.leagues

    # Display league selection
    league_names = [leagues[i].name for i in range(len(leagues))]
    selected_league = st.selectbox("Select a league", league_names)

    if selected_league:
        with st.spinner("Fetching league data..."):
            # Fetch league info based on the selected league
            league_info = kb.league_info(leagues[league_names.index(selected_league)])

            st.subheader(f"Basic Stats for League: {selected_league}")
            st.write(f"Active Users: {league_info.active_users}")
            st.write(f"total transfers: {league_info.total_transfers}")
