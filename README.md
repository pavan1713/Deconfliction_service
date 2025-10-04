# Deconfliction_service
Drone flight deconfliction and simulation project

Requirements

Python 3.8 or higher

Libraries:

matplotlib

itertools (built-in)

json (built-in)

sys (built-in)

Installation

Clone the repository or download the Python file deconfliction_service.py.

Install required Python libraries:

pip install matplotlib


Prepare your drone flight JSON files:

For temporal collison need to create if required we already have a demo temporal collision file 

For spatial collision we have generate_flight_data.py which creates spatial collision and non collision example data flights 


Usage

Run the script from the terminal:

python deconfliction_service.py <existing_flights.json> <new_flight.json>

Example:

python deconfliction_service.py dummy_flights.json new_flight_conflict.json

Output

Terminal Output:

Number of spatial collisions (yellow)

Temporal collision detected messages (red)

"Clear to fly!" message if no collision (green)

Files Created:

flight_paths_clear.png → Static plot if no collision

flight_paths_collision.png → Static plot highlighting collisions

simulation_clear.gif → Animated simulation if no collision

simulation_collision.gif → Animated simulation showing collisions

Code Overview

Collision Detection Functions

is_point_on_segment(): Checks if a point lies on a segment.

get_orientation(): Determines clockwise/counter-clockwise orientation.

segments_intersect(): Detects if two line segments intersect.

get_intersection_point(): Calculates intersection coordinates.

interpolate_time(): Estimates collision time on a segment.

Main Functions

check_spatial_collisions(): Detects all spatial intersections.

check_temporal_collisions(): Detects collisions happening at the same time.

plot_flight_paths(): Generates static 2D plots of flight paths and collisions.

create_simulation(): Generates animated GIF of drone movement.

Notes

Temporal collisions are detected if drones reach the intersection within 1 time unit (default is 1 minute).

Collision markers in plots are highlighted with red circles.

Drone markers:

New drone → Blue ^

Existing drones → Orange o
