import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from kickbase_api.models.user import User
from streamlit import session_state as ss


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


# Adjust the function to correct the legend values


def create_network_graph(player_transfers, kb_league_users, kb_leagues):
    # Create a new graph
    G = nx.Graph()

    # Process the transfer data
    for player, data in player_transfers.items():
        transactions = data["Transaction"]
        for buyer, seller, value in zip(
            transactions["Buyer"], transactions["Seller"], transactions["Value"]
        ):
            # Add nodes for buyers and sellers
            G.add_node(buyer, type="buyer")
            G.add_node(seller, type="seller")

            # Add an edge representing the transfer
            G.add_edge(buyer, seller, weight=value, player=player)

    # Use the Kamada-Kawai layout algorithm
    pos = nx.kamada_kawai_layout(G)

    # Create a dictionary to map user IDs to user names
    user_id_to_name = {user.id: user.name for user in kb_league_users(kb_leagues()[0])}

    # Calculate edge widths based on the sum of weights between two nodes
    edge_weights = nx.get_edge_attributes(G, "weight")
    max_edge_weight = max(edge_weights.values())
    scaled_edge_widths = [
        edge_weights[edge] / max_edge_weight * 10 for edge in G.edges()
    ]  # Adjust scaling factor as needed

    # Create edges
    edge_traces = []
    for edge, width in zip(G.edges(), scaled_edge_widths):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_traces.append(
            go.Scatter(
                x=[
                    x0,
                    x1,
                    None,
                ],  # None will create a break between lines, simulating separate edges
                y=[y0, y1, None],
                line=dict(width=width, color="Grey"),
                hoverinfo="none",
                mode="lines",
            )
        )

    # Create nodes with sizes reflecting the number of connections
    node_x = []
    node_y = []
    node_sizes = []
    node_text = []
    degrees = []
    for node in G.nodes():
        x, y = pos[node]
        degree = nx.degree(G, node)
        node_x.append(x)
        node_y.append(y)
        node_sizes.append(10 * degree)  # Visual scaling factor for node size
        degrees.append(degree)  # Actual degree for the legend
        node_text.append(f"{user_id_to_name.get(node, 'Unknown')} ({degree} transfers)")

    # Normalize the degrees to create a continuous range for the color scale
    max_degree = max(degrees)
    node_color = [degree / max_degree for degree in degrees]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            size=node_sizes,
            color=node_color,  # Use normalized degrees for coloring
            colorscale="Blues",
            showscale=True,
            colorbar=dict(
                title="Number of Transfers", xanchor="left", titleside="right"
            ),
            line=dict(width=2, color="DarkSlateGrey"),
        ),
    )

    # Create the layout for the graph
    layout = go.Layout(
        title="<br>Network graph of player transfers",
        titlefont_size=16,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False,
    )

    # Create the figure adding all edge traces and the node trace
    fig = go.Figure(layout=layout)
    for edge_trace in edge_traces:
        fig.add_trace(edge_trace)
    fig.add_trace(node_trace)

    # Return the figure
    return fig


# The function would be called and the graph displayed in an interactive environment.
# fig = create_network_graph(player_transfers, kb_league_users, kb_leagues)
# fig.show()


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
        tab1, tab2 = st.tabs(["Ligaranking", "Transfers"])
        st.divider()

        with tab1:
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
        with tab2:
            if "player_transfers" not in ss:
                ss.player_transfers = {}
                for player in ss.players:
                    ss.player_transfers[f"{player.firstName} {player.lastName}"] = (
                        kb.player_market_history(kb.leagues()[0].id, player.id)
                    )
            st.plotly_chart(
                create_network_graph(ss.player_transfers, kb.league_users, kb.leagues)
            )
