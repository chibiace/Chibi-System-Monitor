#
# -----------------------------------------------------------
#  Displays some system information, which updates. Nvidia GPU required.
#  chibiace 18/05/2023
# -----------------------------------------------------------
#

import psutil
import os
import time
import sys
import json
from pygments import highlight, lexers, formatters
from pynvml import *
from terminaltables import AsciiTable


# How often data gets retrieved and displayed.
UPDATE_INTERVAL = 1

# Initialize py-nvidia-ml
nvmlInit()
# like an ID i think, hard set to 0, who can afford a second gpu these days anyway.
gpu_handle = nvmlDeviceGetHandleByIndex(0)


def get_system_info():
    # Get system information
    cpu_percent = psutil.cpu_percent(interval=1)
    # for i in psutil.sensors_temperatures():
    #     print(i)
    # cpu_temp = psutil.sensors_temperatures()['coretemp'][0].current
    sensor_temps = []
    for i in psutil.sensors_temperatures():
        if i in ["k10temp","coretemp"]:
            name = "CPU Temp"
        else:
            name = i
        sensor_temps.append([name,round(psutil.sensors_temperatures()[i][0].current,1), '°C'])
        # print(i)
    # print(sensor_temps)
    # sys.exit()
    # cpu_temp = round(psutil.sensors_temperatures()['k10temp'][0].current,1)
    mem_info = psutil.virtual_memory()
    swap_info = psutil.swap_memory()
    mem_total = round(mem_info.total / (1024 * 1024 * 1024), 2)
    mem_used = round(mem_info.used / (1024 * 1024 * 1024), 2)
    mem_percent = mem_info.percent



    swap_percent = swap_info.percent
    swap_total = round(swap_info.total / (1024 * 1024 * 1024), 2)
    swap_free = round(swap_info.free / (1024 * 1024 * 1024), 2)
    swap_used = round(swap_info.used / (1024 * 1024 * 1024), 2)

    # get nvidia information
    nvidia_memory = nvmlDeviceGetMemoryInfo(gpu_handle)
    nvidia_info = [
        ['Driver Version', nvmlSystemGetDriverVersion(), ' '],
        ['Clock Speed', nvmlDeviceGetClockInfo(gpu_handle, 0), 'Mhz'],
        ['Max Clock Speed', nvmlDeviceGetMaxClockInfo(gpu_handle, 0), 'Mhz'],
        ['VRAM Total', round(nvidia_memory.total /
                             (1024 * 1024 * 1024), 2), 'GB'],
        ['VRAM Free', round(nvidia_memory.free /
                            (1024 * 1024 * 1024), 2), 'GB'],
        ['VRAM Used', round(nvidia_memory.used /
                            (1024 * 1024 * 1024), 2), 'GB'],
        ['Fan Speed', nvmlDeviceGetFanSpeed(gpu_handle), '%'],
        ['Temperature', nvmlDeviceGetTemperature(gpu_handle, 0), '°C'],]

    # Get disk usage information
    disks_info = []
    for partition in psutil.disk_partitions():
        if partition.fstype:
            usage = psutil.disk_usage(partition.mountpoint)
            total = round(usage.total / (1024 * 1024 * 1024), 2)
            used = round(usage.used / (1024 * 1024 * 1024), 2)
            free_space = round(total-used, 2)
            percent = usage.percent
            disks_info.append([
                partition.device, total, used, free_space, percent])
    disks_info.append(['Swap', swap_total, swap_used, swap_free, swap_percent])

    sensor_temps.append(['CPU Usage', cpu_percent, '%'])
    sensor_temps.append(['Memory Usage', mem_used, 'GB', mem_percent, '%'])
    sensor_temps.sort()
    return (sensor_temps, disks_info, nvidia_info)


def display_system_info():
    single_display = False
    try:
        if sys.argv[1] == "-h":
            print("with h")
            single_display = True
    except:
        pass

    if single_display == False:
        #loop
        while True:
            # System Information table
            system_info, disks_info, nvidia_info = get_system_info()
            system_table = AsciiTable(system_info)
            system_table.title = 'System Information'
            system_table.inner_heading_row_border = False
            system_table.justify_columns = {
                0: 'center', 1: 'right', 2: 'center', 3: 'right', 4: 'center'}

            # NVIDIA GPU table
            nvidia_table = AsciiTable(nvidia_info)
            nvidia_table.title = 'Nvidia GPU'
            nvidia_table.inner_heading_row_border = False
            nvidia_table.justify_columns = {
                0: 'center', 1: 'right', 2: 'right', 3: 'center'}

            # Disk Usage table
            disks_table = AsciiTable(
                [['Device', 'Total', 'Used', 'Free', 'Usage']])
            disks_table.title = 'Disk Usage'
            disks_table.inner_heading_row_border = False
            disks_table.justify_columns = {
                0: 'center', 1: 'right', 2: 'right', 3: 'right', 4: 'center'}
            for disk in disks_info:
                device = disk[0]
                total = disk[1]
                used = disk[2]
                free_space = disk[3]
                percent = disk[4]
                disks_table.table_data.append(
                    [device, total, used, free_space, f'{percent}%'])
                


            term_rows = os.get_terminal_size().lines
            term_cols = os.get_terminal_size().columns
            # clock
            t = time.localtime()
            current_time = (" "*round(((term_cols/2)-11)))+"\033[92m--`-{\033[91m@ \033[96m" + \
                time.strftime("%H:%M:%S", t) + \
                "\033[91m @\033[92m}-'--\033[0m"+(" "*15)

            # joins all the tables into one string to stop screen tearing issues
            data = "\n"+system_table.table+"\n\n" + \
                nvidia_table.table+"\n\n" + disks_table.table + \
                "\n\n"

            data_len = len(data.split("\n"))
            add_vertical_lines = round((term_rows-data_len)/2)

            # prints out the mess
            print("\033c", "\n"*add_vertical_lines, "\n".join(line.center(term_cols)
                for line in data.split("\n")), current_time, '\n'*add_vertical_lines)

            # some information for debugging
            # print(term_cols)
            # print(term_rows)
            # print(data_len)
            # print(add_vertical_lines)

            # sleep for x seconds
            time.sleep(UPDATE_INTERVAL)

    else:
        #need to work on this
        system_info, disks_info, nvidia_info = get_system_info()
            
        for disk in disks_info:
            device = disk[0]
            total = disk[1]
            used = disk[2]
            free_space = disk[3]
            percent = disk[4]
        jsonbuilder = {}
        jsonbuilder = {"Filename": filename, "Positive Prompt": positive,
                       "Negative Prompt": negative, "Settings": {}}

        json_object = json.dumps(jsonbuilder, indent=4)
        colorful_json = highlight(json_object, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)
    


if __name__ == '__main__':
    try:
        display_system_info()
    except KeyboardInterrupt:
        print("\n")
        print("Goodbye!".center(os.get_terminal_size().columns))
        sys.exit()
