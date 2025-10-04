import json
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 

def plot_drone_paths(json_file, output_file):


    with open(json_file, 'r') as f:
        flights = json.load(f)


        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        for drone in flights:
            x_coords, y_coords = [], []
            for wp in drone["path"]:
                x_coords.append(wp["x"])
                y_coords.append(wp["y"])
              #  z_coords.append(wp["z"])

            ax.plot(x_coords, y_coords, marker='o',label=drone["drone_id"])          

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("2D Drone Flight Paths")
        ax.legend()



    plt.savefig(output_file, dpi=300)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_drones.py <path_to_json> <output_png>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    output_png_path = sys.argv[2]
  
    plot_drone_paths(json_file_path, output_png_path)
