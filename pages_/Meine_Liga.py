import streamlit as st
from kickbase_api.models.user import User


def map_league_user_to_user(league_user):
    # Create a dictionary from the league_user instance, mapping keys as needed
    league_user_data = {
        "id": league_user.id,
        "email": league_user.email,
        "name": league_user.name,
        # The mapping for 'profile_image_path' will be handled by _json_mapping in User class
        "profile": league_user.profile_image_path,
        # Setting a default value for notifications
        "notifications": 0,
    }

    # Create a User instance with the dictionary
    user_instance = User(league_user_data)
    return user_instance


if __name__ == "__main__":
    if "data_ready" not in st.session_state or not st.session_state.logged:
        st.warning("Bitte zuerst anmelden!")
        st.link_button("Zum Login", "https://kickbased.streamlit.app/")

    else:
        kb = st.session_state.kb
        # Fetch league user data
        users = kb.league_users(st.session_state.liga)  # returns LeagueUserData
        # Fetch league user stats and sort them by placement
        user_stats = [
            kb.league_user_stats(st.session_state.liga, user.id) for user in users
        ]
        sorted_user_stats = sorted(user_stats, key=lambda x: x.placement)

        st.title("Meine Liga")

        league_instance = kb.league_info(st.session_state.liga)
        st.write(f"Aktive Nutzer: {league_instance.active_users}")
        st.write(f"Durchschnittliche Punkte: {league_instance.average_points}")
        st.write(f"Maximale Nutzer: {league_instance.max_users}")
        st.write(f"Totale Transfers: {league_instance.total_transfers}")
        st.divider()
        st.divider()
        # Display league stats
        col1, col2 = st.columns(2)

        # Display user stats sorted by placement
        for i, stats in enumerate(sorted_user_stats):
            col = col1 if i % 2 == 0 else col2
            with col:
                st.image(
                    stats.profile_image_path,
                    width=100,
                )
                st.markdown(f"**Name:** {stats.name}")
                st.markdown(f"**Platzierung:** {stats.placement}")
                st.markdown(f"**Punkte:** {stats.points}")
                st.markdown(f"**Teamwert:** €{stats.team_value:,.0f}")

                st.divider()
