import json
import random
import os


def generate_square_or_rectangle(drone_id, start_x, start_y, size_x, size_y, start_t=0, step_t=10):
    """
    Generate square or rectangle path
    """
    path = [
        {"x": start_x, "y": start_y, "t": start_t},
        {"x": start_x + size_x, "y": start_y, "t": start_t + step_t},
        {"x": start_x + size_x, "y": start_y + size_y, "t": start_t + 2 * step_t},
        {"x": start_x, "y": start_y + size_y, "t": start_t + 3 * step_t},
        {"x": start_x, "y": start_y, "t": start_t + 4 * step_t}
    ]
    return {"drone_id": f"Drone_{drone_id}", "path": path}


def generate_triangle(drone_id, start_x, start_y, base, height, start_t=0, step_t=10):
    """
    Generate triangle path
    """
    path = [
        {"x": start_x, "y": start_y, "t": start_t},
        {"x": start_x + base, "y": start_y, "t": start_t + step_t},
        {"x": start_x + base // 2, "y": start_y + height, "t": start_t + 2 * step_t},
        {"x": start_x, "y": start_y, "t": start_t + 3 * step_t}
    ]
    return {"drone_id": f"Drone_{drone_id}", "path": path}


def random_shape(drone_id):
    """
    Randomly choose square/rectangle or triangle
    """
    start_x = random.randint(50, 800)
    start_y = random.randint(50, 800)
    size_x = random.randint(100, 300)
    size_y = random.randint(100, 300)

    if random.choice(["square", "rectangle", "triangle"]) == "triangle":
        return generate_triangle(drone_id, start_x, start_y, size_x, size_y)
    else:
        return generate_square_or_rectangle(drone_id, start_x, start_y, size_x, size_y)



def generate_flights():
    
    existing = [random_shape(i) for i in range(1, 6)]    # Existing flights

    
    non_conflict = [                                                        
        generate_square_or_rectangle(
            1, random.randint(700, 900), random.randint(700, 900),              
            random.randint(100, 200), random.randint(100, 200)
        )                                                                  # New non-conflict flight (placed far away to avoid collisions)
    ]

   
    ex0 = existing[0]["path"][0]  # take first point of Drone_1
    conflict = [
        generate_square_or_rectangle(
            1, ex0["x"] + random.randint(-50, 50), ex0["y"] + random.randint(-50, 50), 
            random.randint(100, 200), random.randint(100, 200), start_t=0
        )                                                                    # New conflict flight (placed near existing[0] so it intersects)
    ]

    # Save files
    with open("existing.json", "w") as f:
        json.dump(existing, f, indent=4)

    with open("new_no_spatial_conflict.json", "w") as f:
        json.dump(non_conflict, f, indent=4)

    with open("new_spatial_conflict.json", "w") as f:
        json.dump(conflict, f, indent=4)

    print("✅ Generated existing.json, new_non_conflict.json, new_conflict.json")



generate_flights()
