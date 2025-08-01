import os
import osmnx as ox
import networkx as nx
import geopandas as gpd
import requests
from datetime import datetime, timedelta
import shapely.geometry
import math
import pyproj
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from shapely.geometry import LineString
import numpy as np

# Boundary files
ILLINOIS_BOUNDARY_GEOJSON = "illinois_boundary.geojson"
ILLINOIS_BOUNDARY_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/IL.geo.json"

CHICAGO_BOUNDARY_GEOJSON = "chicago_boundary.geojson"
CHICAGO_BOUNDARY_URL = "https://data.cityofchicago.org/api/geospatial/igwz-8jzy?method=export&format=GeoJSON"

CRIME_DATA_FILE = "chicago_crimes.geojson"

def fetch_parks(center_point, dist_buffer):
    tags: dict[str, list[str] | str | bool] = {"leisure": ["park"]}
    parks = ox.features_from_point(center_point, dist=dist_buffer, tags=tags)
    if not parks.empty:
        parks = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
    return parks

def fetch_rivers(center_point, dist_buffer):
    tags: dict[str, list[str] | str | bool] = {"waterway": ["river"]}
    rivers = ox.features_from_point(center_point, dist=dist_buffer, tags=tags)
    if not rivers.empty:
        rivers = rivers[rivers.geometry.type.isin(["Polygon", "MultiPolygon", "LineString", "MultiLineString"])]
    return rivers

def estimate_speed_kph(edge):
    maxspeed = edge.get('maxspeed')
    if maxspeed:
        if isinstance(maxspeed, list):
            maxspeed = maxspeed[0]
        try:
            return float(maxspeed)
        except:
            pass
    highway = edge.get('highway', '')
    if isinstance(highway, list):
        highway = highway[0]
    speed_map = {
        'motorway': 100,
        'trunk': 80,
        'primary': 60,
        'secondary': 50,
        'tertiary': 40,
        'residential': 30,
        'service': 20,
        'footway': 5,
        'path': 5,
        'track': 10,
    }
    return speed_map.get(highway, 30)

def smooth_line(coords, window_size=5):
    x, y = zip(*coords)
    pad_width = window_size // 2
    x_padded = np.pad(x, pad_width, mode='edge')
    y_padded = np.pad(y, pad_width, mode='edge')
    kernel = np.ones(window_size) / window_size
    x_smooth = np.convolve(x_padded, kernel, mode='valid')
    y_smooth = np.convolve(y_padded, kernel, mode='valid')
    return list(zip(x_smooth, y_smooth))

def densify_linestring(linestring, max_distance=5):
    if not isinstance(linestring, LineString):
        return linestring
    x, y = linestring.xy
    coords = list(zip(x, y))
    dists = [0]
    for i in range(1, len(coords)):
        dx = coords[i][0] - coords[i-1][0]
        dy = coords[i][1] - coords[i-1][1]
        dists.append(dists[-1] + (dx**2 + dy**2)**0.5)
    new_dists = np.arange(0, dists[-1], max_distance)
    if new_dists[-1] != dists[-1]:
        new_dists = np.append(new_dists, dists[-1])
    new_x = np.interp(new_dists, dists, x)
    new_y = np.interp(new_dists, dists, y)
    return LineString(zip(new_x, new_y))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = map(math.radians, [lat1, lat2])
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- New Illinois boundary fetch function ---
def fetch_illinois_boundary():
    if not os.path.exists(ILLINOIS_BOUNDARY_GEOJSON):
        r = requests.get(ILLINOIS_BOUNDARY_URL)
        r.raise_for_status()
        with open(ILLINOIS_BOUNDARY_GEOJSON, "w") as f:
            f.write(r.text)
    gdf = gpd.read_file(ILLINOIS_BOUNDARY_GEOJSON)
    return gdf.to_crs("EPSG:4326") if gdf.crs != "EPSG:4326" else gdf

# Keep Chicago boundary for crime weighting area
def fetch_chicago_boundary():
    if not os.path.exists(CHICAGO_BOUNDARY_GEOJSON):
        r = requests.get(CHICAGO_BOUNDARY_URL)
        r.raise_for_status()
        with open(CHICAGO_BOUNDARY_GEOJSON, "w") as f:
            f.write(r.text)
    gdf = gpd.read_file(CHICAGO_BOUNDARY_GEOJSON)
    return gdf.to_crs("EPSG:4326") if gdf.crs != "EPSG:4326" else gdf

def point_in_polygon(lat, lon, gdf):
    point = shapely.geometry.Point(lon, lat)
    return gdf.contains(point).any()

def fetch_crime_data(limit=2000):
    if os.path.exists(CRIME_DATA_FILE):
        return gpd.read_file(CRIME_DATA_FILE)
    cutoff = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S')
    url = "https://data.cityofchicago.org/resource/ijzp-q8t2.geojson"
    params = {
        "$where": f"date > '{cutoff}' AND latitude IS NOT NULL AND longitude IS NOT NULL",
        "$limit": limit,
        "$order": "date DESC"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    with open(CRIME_DATA_FILE, "w") as f:
        f.write(r.text)
    return gpd.read_file(CRIME_DATA_FILE)

def to_latlon(x, y, crs):
    transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lat, lon

def generate_directions(route, G, crs):
    directions = []
    last_street = None
    total_distance = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        edge_data = G.get_edge_data(u, v, 0)
        street = edge_data.get("name", "Unnamed Road")
        length = edge_data.get("length", 0)
        if street != last_street and last_street is not None:
            directions.append(f"Continue for {int(total_distance)} meters on {last_street}")
            total_distance = 0
        total_distance += length
        last_street = street
    if last_street:
        directions.append(f"Continue for {int(total_distance)} meters on {last_street}")
    directions.append("You've arrived at your destination!")
    return directions

def plot_colored_route(G_proj, route, edges_df, parks=None, rivers=None):
    fig, ax = plt.subplots(figsize=(12, 12))

    if parks is not None and not parks.empty:
        parks_gdf = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        parks_gdf.plot(ax=ax, color="#b8f2b0", alpha=0.5, edgecolor=None, zorder=0)

    if rivers is not None and not rivers.empty:
        rivers_gdf = rivers[rivers.geometry.type.isin(["Polygon", "MultiPolygon", "LineString", "MultiLineString"])]
        rivers_gdf.plot(ax=ax, color="lightblue", alpha=0.6, edgecolor=None, zorder=1)

    edges_all = ox.graph_to_gdfs(G_proj, nodes=False)
    for _, row in edges_all.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        lw = 1
        color = "#cccccc"
        if geom.geom_type == 'LineString':
            x, y = geom.xy
            ax.plot(x, y, linewidth=lw, color=color, alpha=0.4, zorder=2)
        else:
            for ls in geom.geoms:
                x, y = ls.xy
                ax.plot(x, y, linewidth=lw, color=color, alpha=0.4, zorder=2)

    crime_max = edges_df["crime_score"].max()
    if crime_max > 0:
        norm = mcolors.Normalize(vmin=0, vmax=crime_max)
        cmap = cm.get_cmap("YlOrRd")
        for _, row in edges_df.iterrows():
            geom = row.geometry
            score = row.crime_score
            if geom is None or score <= 0:
                continue
            color = cmap(norm(score))
            alpha = 0.3 + 0.7 * (score / crime_max)  # More visible with higher crime
            if geom.geom_type == 'LineString':
                x, y = geom.xy
                ax.plot(x, y, linewidth=4, color=color, alpha=alpha, zorder=3)
            else:
                for ls in geom.geoms:
                    x, y = ls.xy
                    ax.plot(x, y, linewidth=2, color=color, alpha=alpha, zorder=3)

    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        edge_data = G_proj.get_edge_data(u, v, 0)
        geom = edge_data.get("geometry", None)
        if geom is not None:
            densified_geom = densify_linestring(geom, max_distance=1)
            coords = list(zip(*densified_geom.xy))
            smooth_coords = smooth_line(coords, window_size=5)
            x, y = zip(*smooth_coords)
        else:
            x = [G_proj.nodes[u]['x'], G_proj.nodes[v]['x']]
            y = [G_proj.nodes[u]['y'], G_proj.nodes[v]['y']]
        ax.plot(x, y, linewidth=6, color='blue', alpha=1.0, zorder=10)

    ax.set_title("Crime-Aware Route in Chicago", fontsize=16)
    ax.axis("off")
    plt.tight_layout()
    plt.show()

def get_graph_with_fallback(center_point, initial_buffer, initial_network, min_buffer=1000):
    buffer_dist = initial_buffer
    network = initial_network
    while buffer_dist >= min_buffer:
        try:
            print(f"Trying buffer {int(buffer_dist)}m with network '{network}'...")
            G = ox.graph_from_point(center_point, dist=buffer_dist, network_type=network, simplify=True)
            if len(G.nodes) == 0:
                raise Exception("Empty graph")
            print(f"Graph successfully loaded with buffer {int(buffer_dist)}m and network '{network}'")
            return G
        except Exception as e:
            print(f"Warning: {e}")
            buffer_dist /= 2
            network = "walk" if network == "drive" else "drive"
    raise RuntimeError("Failed to download graph data for all fallback parameters.")

def main():
    # Fetch boundaries
    illinois_boundary = fetch_illinois_boundary()
    chicago_boundary = fetch_chicago_boundary()

    origin_input = input("Enter origin: ").strip()
    destination_input = input("Enter destination: ").strip()

    print("Geocoding...")
    origin = ox.geocode(origin_input)
    destination = ox.geocode(destination_input)

    origin_in_ill = point_in_polygon(origin[0], origin[1], illinois_boundary)
    dest_in_ill = point_in_polygon(destination[0], destination[1], illinois_boundary)
    midpoint = ((origin[0] + destination[0]) / 2, (origin[1] + destination[1]) / 2)
    mid_in_ill = point_in_polygon(midpoint[0], midpoint[1], illinois_boundary)

    origin_in_chi = point_in_polygon(origin[0], origin[1], chicago_boundary)
    dest_in_chi = point_in_polygon(destination[0], destination[1], chicago_boundary)
    mid_in_chi = point_in_polygon(midpoint[0], midpoint[1], chicago_boundary)

    if not (origin_in_ill and dest_in_ill):
        print("Warning: Origin/destination is outside Illinois. Results may be unreliable.")

    dist_m = haversine(origin[0], origin[1], destination[0], destination[1])
    dist_buffer = max(3000, min(dist_m * 0.5 + 2000, 50000))
    network_type = "walk" if dist_m <= 2500 else "drive"

    G = get_graph_with_fallback(midpoint, dist_buffer, network_type)
    G_proj = ox.project_graph(G)

    parks_gdf = gpd.GeoDataFrame()
    rivers_gdf = gpd.GeoDataFrame()

    try:
        parks_raw = fetch_parks(midpoint, dist_buffer)
        if not parks_raw.empty:
            parks_raw = parks_raw.to_crs(G_proj.graph['crs'])

            network_boundary = ox.graph_to_gdfs(G_proj, nodes=False).geometry.union_all().convex_hull

            # Wrap in GeoSeries to satisfy gpd.clip expected type
            mask = gpd.GeoSeries([network_boundary], crs=parks_raw.crs)

            parks_gdf = gpd.clip(parks_raw, mask)
    except Exception as e:
        print("Warning loading parks:", e)

    try:
        rivers_raw = fetch_rivers(midpoint, dist_buffer)
        if not rivers_raw.empty:
            rivers_raw = rivers_raw.to_crs(G_proj.graph['crs'])

            network_boundary = ox.graph_to_gdfs(G_proj, nodes=False).geometry.union_all().convex_hull

            
            mask = gpd.GeoSeries([network_boundary], crs=rivers_raw.crs)


            rivers_gdf = gpd.clip(rivers_raw, mask)
    except Exception as e:
        print("Warning loading rivers:", e)

    origin_proj = shapely.geometry.Point(origin[1], origin[0])
    destination_proj = shapely.geometry.Point(destination[1], destination[0])
    origin_proj = ox.projection.project_geometry(origin_proj, to_crs=G_proj.graph['crs'])[0]
    destination_proj = ox.projection.project_geometry(destination_proj, to_crs=G_proj.graph['crs'])[0]
    assert isinstance(origin_proj, shapely.geometry.Point)
    assert isinstance(destination_proj, shapely.geometry.Point)

    # Convert to numpy arrays for nearest_nodes
    origin_proj_array = np.array([origin_proj.x, origin_proj.y])
    destination_proj_array = np.array([destination_proj.x, destination_proj.y])

    # Use nearest_nodes with numpy arrays
    orig_node = ox.distance.nearest_nodes(G_proj, X=origin_proj_array[0], Y=origin_proj_array[1])
    dest_node = ox.distance.nearest_nodes(G_proj, X=destination_proj_array[0], Y=destination_proj_array[1])
    orig_node = ox.distance.nearest_nodes(G_proj, X=origin_proj.x, Y=origin_proj.y)
    dest_node = ox.distance.nearest_nodes(G_proj, X=destination_proj.x, Y=destination_proj.y)

    #Only uses crime data if point is in Chicago
    use_crime = origin_in_chi or dest_in_chi or mid_in_chi

    if use_crime:
        crimes = fetch_crime_data()
        crimes = crimes.to_crs(G_proj.graph['crs'])
        edges = ox.graph_to_gdfs(G_proj, nodes=False).reset_index()
        edges["buffer"] = edges.geometry.buffer(50)
        joined = gpd.sjoin(crimes, gpd.GeoDataFrame(edges[["buffer"]], geometry="buffer", crs=edges.crs), how="inner", predicate="intersects")
        counts = joined.groupby(joined.index).size()
        edges["crime_score"] = 0
        edges.loc[counts.index, "crime_score"] = counts

        for u, v, k, data in G_proj.edges(keys=True, data=True):
            length = data.get("length", 1)
            speed_kph = estimate_speed_kph(data)
            speed_mps = speed_kph * 1000 / 3600
            travel_time = length / speed_mps if speed_mps > 0 else length / (30 * 1000 / 3600)
            match = edges[(edges.u == u) & (edges.v == v) & (edges.key == k)]
            crime_score = match.iloc[0]["crime_score"] if not match.empty else 0
            crime_penalty = 10 * crime_score
            data["weight"] = travel_time + crime_penalty
    else:
        edges = ox.graph_to_gdfs(G_proj, nodes=False).reset_index()
        edges["crime_score"] = 0
        for _, _, _, data in G_proj.edges(keys=True, data=True):
            data["weight"] = data.get("length", 1)

    try:
        route = nx.astar_path(G_proj, orig_node, dest_node, weight="weight")
        print("Route found.")
        directions = generate_directions(route, G_proj, G_proj.graph["crs"])
        print("\n--- Turn-by-Turn Directions ---")
        for step in directions:
            print(step)
        coords = [to_latlon(G_proj.nodes[n]['x'], G_proj.nodes[n]['y'], G_proj.graph["crs"]) for n in route]
    
        if len(coords) > 20:
            sampled = [coords[0]]  # start
            step = max(1, len(coords) // 8)
            sampled += coords[step:-step:step]
            sampled.append(coords[-1])  # end
        else:
            sampled = coords

        gmaps_url = "https://www.google.com/maps/dir/" + "/".join(f"{lat},{lon}" for lat, lon in sampled)

        print("\nGoogle Maps route:")
        print(gmaps_url)
        plot_colored_route(G_proj, route, edges, parks=parks_gdf, rivers=rivers_gdf)
    except nx.NetworkXNoPath:
        print("No route found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
