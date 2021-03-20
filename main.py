import subprocess
import platform
from getpass import getpass
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Initial setup of variable.
graph = plt.figure()
graph.tight_layout()
ax = graph.add_subplot()
ax2 = ax.twinx()
x_axis_data = []
y_axis_data = []
y2_axis_data = []
temperature_color = "tab:red"
fan_speed_color = "tab:blue"
plt.title("CPU Temperature and Fan Speed over Time")
ax.set_ylabel("Temperature (deg C)", color=temperature_color)
ax2.set_ylabel("Fan speed (RPM)", color=fan_speed_color)


def verify_os():
    os_name = platform.system()
    print("OS name : " + os_name)
    print("OS version : " + platform.release())
    if "Darwin" != os_name:
        raise ValueError("Unsuuported OS. This script only works on MacOS.")


def extract_metric(data_string, metric_name, value_idx):
    metric_value = -1
    for line in data_string.split("\n"):
        if metric_name in line:
            data = line.strip().split()
            metric_value = data[value_idx]
    return metric_value


def get_powermetrics(user_pass):
    cpu_temperature_value = fan_speed = -1
    command = "powermetrics --samplers smc -n1".split()
    cmd_to_pass_password = subprocess.Popen(["echo", user_pass], stdout=subprocess.PIPE)
    cmd_power_metric = subprocess.run(
        ["sudo", "-S"] + command,
        stdin=cmd_to_pass_password.stdout,
        stdout=subprocess.PIPE,
    )

    output_raw = cmd_power_metric.stdout.decode("UTF-8")
    cpu_temperature_value = extract_metric(output_raw, "CPU die temperature", 3)
    fan_speed = extract_metric(output_raw, "Fan:", 1)
    return float(cpu_temperature_value), float(fan_speed)


def update_graph(i, x_axis_data, y_axis_data, y2_axis_data, user_pass):
    temperature, fan_speed = get_powermetrics(user_pass)

    # add data to graph
    x_axis_data.append(dt.datetime.now().strftime("%H:%M:%S"))
    y_axis_data.append(temperature)
    y2_axis_data.append(fan_speed)

    # show last 30 values on graph
    x_axis_data = x_axis_data[-30:]
    y_axis_data = y_axis_data[-30:]
    y2_axis_data = y2_axis_data[-30:]

    # Draw graph
    ax.clear()
    ax2.clear()
    ax.plot(x_axis_data, y_axis_data, color=temperature_color)
    ax2.plot(x_axis_data, y2_axis_data, color=fan_speed_color)

    # Format graph
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", color=temperature_color)
    ax2.tick_params(axis="y", color=temperature_color)
    plt.subplots_adjust(bottom=0.30)
    plt.grid()
    plt.title("CPU Temperature and Fan Speed over Time")
    ax.set_ylabel("Temperature (deg C)", color=temperature_color)
    ax2.set_ylabel("Fan speed (RPM)", color=fan_speed_color)


# Set up plot to cal(l animate() function periodically
def main():
    user_pass = str(getpass())
    ani = animation.FuncAnimation(
        graph,
        update_graph,
        fargs=(x_axis_data, y_axis_data, y2_axis_data, user_pass),
        interval=3000,
    )
    plt.show()


if __name__ == "__main__":
    print("####### Starting Script #######")
    verify_os()
    main()
