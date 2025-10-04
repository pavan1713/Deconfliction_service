import json
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle
import itertools

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"



def is_point_on_segment(P, Q, R):
    """
    Check if point Q lies on the line segment P-R (inclusive).
    """
    return min(P[0], R[0]) <= Q[0] <= max(P[0], R[0]) and min(P[1], R[1]) <= Q[1] <= max(P[1], R[1])   # checking weather Q point is on segmet p and r 

def is_point_strictly_inside_segment(P, Q, R, tol=1e-6):
    """
    Check if point Q is strictly inside the line segment from P to R (not endpoints)
    P, Q, R are (x, y) tuples
    """
    inside_x = min(P[0], R[0]) + tol < Q[0] < max(P[0], R[0]) - tol    # Check X coordinate: Q must be strictly between P and R X values
    inside_y = min(P[1], R[1]) + tol < Q[1] < max(P[1], R[1]) - tol   # Check Y coordinate: Q must be strictly between P and R Y values
    return inside_x or inside_y                                      # If Q is inside either X or Y range (works for horizontal/vertical segments)

def get_orientation(P, Q, R):
    """
    Check the orientation of three points P, Q, R.
    Returns:
        0 -> points are in a straight line (collinear)
        1 -> points make a clockwise turn
        2 -> points make a counter-clockwise turn
    """
    
    slope_diff = (Q[1] - P[1]) * (R[0] - Q[0]) - (Q[0] - P[0]) * (R[1] - Q[1])    # Calculate the difference in slopes
    
    if slope_diff == 0:        # If difference is 0, points are in a straight line
        return 0
    elif slope_diff > 0:       # Positive difference means clockwise turn
        return 1
    else:                      # Negative difference means counter-clockwise turn
        return 2

def segments_intersect(P1, Q1, P2, Q2):
    """
    Check if line segments P1-Q1 and P2-Q2 intersect.
    """
    o1 = get_orientation(P1, Q1, P2)
    o2 = get_orientation(P1, Q1, Q2)
    o3 = get_orientation(P2, Q2, P1)
    o4 = get_orientation(P2, Q2, Q1)

    
    if o1 != o2 and o3 != o4:                # General case
        return True

    
    if o1 == 0 and is_point_on_segment(P1, P2, Q1): return True    # checking if colinear and point is on the segment
    if o2 == 0 and is_point_on_segment(P1, Q2, Q1): return True
    if o3 == 0 and is_point_on_segment(P2, P1, Q2): return True
    if o4 == 0 and is_point_on_segment(P2, Q1, Q2): return True

    return False

def get_intersection_point(P1, Q1, P2, Q2):

    A1 = Q1[1] - P1[1]
    B1 = P1[0] - Q1[0]
    C1 = A1 * P1[0] + B1 * P1[1]

    A2 = Q2[1] - P2[1]
    B2 = P2[0] - Q2[0]
    C2 = A2 * P2[0] + B2 * P2[1]

    det = A1 * B2 - A2 * B1
    if det == 0:
        return None                         # if det is zero then lines are parallel

    x = (B2*C1 - B1*C2)/det
    y = (A1*C2 - A2*C1)/det

    if is_point_on_segment(P1, (x, y), Q1) and is_point_on_segment(P2, (x, y), Q2):
        return (x, y)                       # if we founf any intersection point retuning it 
    return None

def interpolate_time(P, Q, intersection):

    x1, y1, t1 = P
    x2, y2, t2 = Q
    xi, yi = intersection

    if x1 == x2 and y1 == y2:
        return t1                                # if the flight position not changed or having same coordinates
    seg_len = ((x2-x1)**2 + (y2-y1)**2)**0.5
    inter_len = ((xi-x1)**2 + (yi-y1)**2)**0.5
    ratio = inter_len / seg_len
    return t1 + ratio*(t2 - t1)                  # retuns the estimsted time to reach by paticular flight 

def check_spatial_collisions(existing_flights, new_flight):
    collisions = []                       # This will store all detected collisions
    new_path = new_flight["path"]         # Get the list of points for the new drone

    for i in range(len(new_path) - 1):                        # Loop through each segment (pair of points) in the new drone's path        
        start_new = (new_path[i]["x"], new_path[i]["y"])      # Start of new segment
        end_new = (new_path[i+1]["x"], new_path[i+1]["y"])    # End of new segment

        for drone in existing_flights:     # Check against all existing drones
            existing_path = drone["path"]  # Path of this existing drone

            for j in range(len(existing_path) - 1):                                # Loop through each segment in the existing drone's path
                start_existing = (existing_path[j]["x"], existing_path[j]["y"])
                end_existing = (existing_path[j+1]["x"], existing_path[j+1]["y"])

                if segments_intersect(start_new, end_new, start_existing, end_existing):    # Check if the two segments intersect

                    intersection_point = get_intersection_point(start_new, end_new, start_existing, end_existing)    # If they intersect, get the intersection point

                    if intersection_point:                 # Only add if intersection point exists
                        collisions.append({
                            "new_segment": (start_new, end_new),                    # Segment of new drone
                            "other_drone": drone["drone_id"],                       # Drone it collided with
                            "other_segment": (start_existing, end_existing),        # Segment of other drone
                            "intersection": intersection_point                      # Where they intersect
                        })

    return collisions  # Return the list of all collisions

def check_temporal_collisions(spatial_collisions, new_flight, existing_flights):
    temporal_collisions = []                  # List to store collisions that happen at the same time
    new_path = new_flight["path"]             # Path of the new drone

    for collision in spatial_collisions:           # Go through each spatial collision
        intersection = collision["intersection"]  # Where the collision happens

        t_new = None
        for i in range(len(new_path) - 1):
            start_new = (new_path[i]["x"], new_path[i]["y"], new_path[i]["t"])          # Current segment of new drone with time
            end_new = (new_path[i+1]["x"], new_path[i+1]["y"], new_path[i+1]["t"])

            if is_point_strictly_inside_segment((start_new[0], start_new[1]), intersection, (end_new[0], end_new[1])):    # Check if intersection is strictly inside this segment
                t_new = interpolate_time(start_new, end_new, intersection)                                                # Estimate collision time
                break

        if t_new is None:
            continue  # Skip if collision is at segment endpoint

        for drone in existing_flights:
            if drone["drone_id"] != collision["other_drone"]:
                continue  # Skip unrelated drones

            path_other = drone["path"]
            t_other = None

            for j in range(len(path_other) - 1):
                start_other = (path_other[j]["x"], path_other[j]["y"], path_other[j]["t"])
                end_other = (path_other[j+1]["x"], path_other[j+1]["y"], path_other[j+1]["t"])

                if is_point_strictly_inside_segment((start_other[0], start_other[1]), intersection, (end_other[0], end_other[1])):
                    t_other = interpolate_time(start_other, end_other, intersection)
                    break

            if t_other is None:
                continue  # Skip if collision is at endpoint

            if abs(t_new - t_other) <= 1.0:      # Collision occurs within 1 time unit (e.g., 1 minute)
                collision["temporal"] = True    # Mark as temporal collision
                collision["t_new"] = t_new
                collision["t_other"] = t_other
                temporal_collisions.append(collision)

    return temporal_collisions  # Return the list of temporal collisions



def plot_flight_paths(existing_flights, new_flight, temporal_collisions=None, save_path="flight_paths.png"):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title("Drone Flight Paths")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    for drone in existing_flights:
        x = [p["x"] for p in drone["path"]]
        y = [p["y"] for p in drone["path"]]
        ax.plot(x, y, marker='o', markersize=10, linestyle='--', label=drone["drone_id"])


    x_new = [p["x"] for p in new_flight["path"]]
    y_new = [p["y"] for p in new_flight["path"]]
    ax.plot(x_new, y_new, marker='^', markersize=12, color='blue', label=new_flight["drone_id"], linewidth=2)

    if temporal_collisions:
        for col in temporal_collisions:
            xi, yi = col["intersection"]
            ax.add_patch(Circle((xi, yi), radius=25, color='red', alpha=0.3))
            ax.scatter(xi, yi, color='red', s=150, label="Collision")

    ax.legend()
    ax.grid(True)
    plt.savefig(save_path)
    print(f"Flight paths saved to {save_path}")
    plt.close()




def create_simulation(existing_flights, new_flight, temporal_collisions=None, save_video="simulation.gif"):
    all_flights = existing_flights + [new_flight]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, max(p["x"] for d in all_flights for p in d["path"]) + 10)
    ax.set_ylim(0, max(p["y"] for d in all_flights for p in d["path"]) + 10)
    ax.set_title("Drone Flight Simulation")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)

    markers = {}
    for drone in all_flights:
        if drone == new_flight:
            markers[drone["drone_id"]], = ax.plot([], [], marker='^', markersize=12, linestyle='', label=drone["drone_id"])
        else:
            markers[drone["drone_id"]], = ax.plot([], [], marker='o', markersize=10, linestyle='', label=drone["drone_id"])

    collision_patches = []
    if temporal_collisions:
        for col in temporal_collisions:
            xi, yi = col["intersection"]
            patch = Circle((xi, yi), radius=25, color='red', alpha=0.3)
            ax.add_patch(patch)
            collision_patches.append(patch)

    ax.legend()
    max_t = max(max(p["t"] for p in d["path"]) for d in all_flights)

    def interpolate_position(drone, t):
        path = drone["path"]
        for i in range(len(path)-1):
            p1 = path[i]
            p2 = path[i+1]
            if p1["t"] <= t <= p2["t"]:
                ratio = (t - p1["t"]) / (p2["t"] - p1["t"])
                x = p1["x"] + ratio * (p2["x"] - p1["x"])
                y = p1["y"] + ratio * (p2["y"] - p1["y"])
                return x, y
        return path[-1]["x"], path[-1]["y"]

    def update(frame):
        t = frame * 0.1
        for drone in all_flights:
            x, y = interpolate_position(drone, t)
            markers[drone["drone_id"]].set_data([x], [y])
        return list(markers.values()) + collision_patches

    frames = int(max_t * 10) + 10
    anim = FuncAnimation(fig, update, frames=frames, interval=100, blit=True)
    anim.save(save_video, writer=PillowWriter(fps=10))
    plt.close()
    print(f"Simulation saved to {save_video}")






if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python deconfliction_service.py <existing_flights.json> <new_flight.json>")
        sys.exit(1)

    existing_file = sys.argv[1]  # first argument
    new_file = sys.argv[2]       # second argument

    
    with open(existing_file, "r") as fdata:
        existing_flights = json.load(fdata)

    with open(new_file, "r") as fdata:
        new_flight = json.load(fdata)[0]  # take first flight in file

    
    spatial_collisions = check_spatial_collisions(existing_flights, new_flight)
    temporal_collisions = check_temporal_collisions(spatial_collisions, new_flight, existing_flights)

    
    print(YELLOW + "Number of spatial collisions: " + str(len(spatial_collisions)) + RESET)

    if temporal_collisions:
        print(RED + "Temporal collision detected!" + RESET)

        for col in temporal_collisions:
            msg = "- Collision with " + col["other_drone"]
            msg += " at point " + str(col["intersection"])
            msg += " at time " + str(round(col["t_new"], 1)) + " min"
            print(msg)

        plot_flight_paths(existing_flights, new_flight,
                          temporal_collisions,
                          save_path="flight_paths_collision.png")
        create_simulation(existing_flights, new_flight,
                          temporal_collisions,
                          save_video="simulation_collision.gif")
    else:
        print(GREEN + "Clear to fly!" + RESET)

        plot_flight_paths(existing_flights, new_flight,
                          save_path="flight_paths_clear.png")
        create_simulation(existing_flights, new_flight,
                          save_video="simulation_clear.gif")


