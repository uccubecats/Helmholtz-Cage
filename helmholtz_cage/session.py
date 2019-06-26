#!/usr/bin/env python

"""
Session logging functions for the UC Helmholtz Cage

Copyright 2018-2019 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.

Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import csv
import datetime
import os
import threading


def log_session_data():
    """
    Create a session log file.
    """
    main_page = app.frames[MainPage]
    print("instruments.log_data is {}".format(instruments.log_data))

    if instruments.log_data == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.session_log_filename == "":
            data.session_log_filename = "HelmholtzCage_SessionData_{}.csv".\
                format(today)
            logger.info("creating log: {}".format(data.session_log_filename))

            if not os.path.exists("session_files"):
                os.mkdir("session_files")

            with open(os.path.join("session_files", data.session_log_filename),
                      'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])

        with open(os.path.join("session_files", data.session_log_filename),
                  'a') as file:
            threading.Timer(update_plot_time, log_session_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time)
                       .total_seconds())
            print("logging data at {}".format(str(time)))

            # *** can be used for debugging if requested voltages from template
            # file seem wrong on the output side from the power supply
            # x_req, y_req, z_req = instruments.get_requested_voltage()

            x_out, y_out, z_out = instruments.get_output_voltage()
            # TODO: add below line back in
            x_mag, y_mag, z_mag = instruments.get_magnetometer_field()
            #x_mag, y_mag, z_mag = 100, 100, 100

            if not x_mag:
                try:
                    x_mag = data.x_mag_field_actual[-1]
                except IndexError:
                    x_mag = 0.0
            if not y_mag:
                try:
                    y_mag = data.y_mag_field_actual[-1]
                except IndexError:
                    y_mag = 0.0
            if not z_mag:
                try:
                    z_mag = data.z_mag_field_actual[-1]
                except IndexError:
                    z_mag = 0.0

            writer.writerow([time,
                             data.active_x_voltage_requested,
                             data.active_y_voltage_requested,
                             data.active_z_voltage_requested,
                             x_out, y_out, z_out,
                             x_mag, y_mag, z_mag])

            data.time.append(time)
            data.x_req.append(data.active_x_voltage_requested)
            data.y_req.append(data.active_y_voltage_requested)
            data.z_req.append(data.active_z_voltage_requested)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

            data.x_mag_field_actual.append(x_mag)
            data.y_mag_field_actual.append(y_mag)
            data.z_mag_field_actual.append(z_mag)

            data.x_mag_field_requested.append(data.active_x_mag_field_requested)
            data.y_mag_field_requested.append(data.active_y_mag_field_requested)
            data.z_mag_field_requested.append(data.active_z_mag_field_requested)

            main_page.fill_plot_frame()

def log_calibration_data():
    """
    Creates a calibration file from a loaded template file.
    """
    main_page = app.frames[MainPage]

    if instruments.log_data == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.calibration_log_filename == "":
            data.calibration_log_filename = "HelmholtzCage_CalibrationData_{}" \
                                            ".csv".format(today)
            if not os.path.exists("calibration_files"):
                os.mkdir("calibration_files")

            logger.info("creating calibration file: {}"
                        .format(data.calibration_log_filename))

            with open(os.path.join("calibration_files",
                                   data.calibration_log_filename), 'a') as file:

                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])
                data.start_time = datetime.datetime.now()
                data.current_value = 0

        with open(os.path.join("calibration_files",
                               data.calibration_log_filename), 'a') as file:

            threading.Timer(update_plot_time, log_calibration_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time)
                       .total_seconds())

            # Check if it is time to get new values from template yet
            logger.info("time calibrating is: {}".format(time))
            logger.info("data.current_value is {}".format(data.current_value))
            logger.info("update_calibrate_time * data.current_value is: {}".
                        format(data.current_value * update_calibrate_time))
                        
            # Get current calibration voltages for whichever increment
            if time >= (data.current_value*update_calibrate_time):
                try:
                    data.cur_cal_x = float(data.template_voltages_x
                                           [data.current_value])
                    data.cur_cal_y = float(data.template_voltages_y
                                           [data.current_value])
                    data.cur_cal_z = float(data.template_voltages_z
                                           [data.current_value])
                except Exception as err:
                    logger.info("Could not get x,y,z voltages to send, likely "
                                "finished calibrating | {}".format(err))
                    data.cur_cal_x, data.cur_cal_y, data.cur_cal_z = 0, 0, 0
                instruments.send_voltage(data.cur_cal_x, data.cur_cal_y,
                                         data.cur_cal_z)
                data.current_value += 1

            # *** can be used for debugging if requested voltages from template
            # file seem wrong on the output side from the power supply
            # x_req, y_req, z_req = instruments.get_requested_voltage()

            # TODO: verify this gets the correct output voltage
            # get the currently read voltages on the power supply displays
            x_out, y_out, z_out = instruments.get_output_voltage()
            x_mag = 1  # *** this will have to come from magnetometer connection
            y_mag = 2
            z_mag = 3

            # Update values saved to calibration file
            writer.writerow([time, data.cur_cal_x, data.cur_cal_y,
                             data.cur_cal_z, x_out, y_out, z_out,
                             x_mag, y_mag, z_mag])

            # Update lists that will be plotted
            data.time.append(time)
            data.x_req.append(data.cur_cal_x)
            data.y_req.append(data.cur_cal_y)
            data.z_req.append(data.cur_cal_z)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

        # Update plot if calibration is still going on
        if not data.stop_calibration:
            main_page.fill_plot_frame()

        # Stop calibration if all template voltages have been used
        if data.current_value == len(data.template_voltages_x):
            instruments.log_data = "OFF"
            logger.info("calibration file {} created - load it in before "
                        "doing a dynamic test or requesting based on "
                        "magnetic field".format(data.calibration_log_filename))
            # Allows for a new calibration file to be created again? TODO: test
            data.calibration_log_filename = ""
            data.stop_calibration = True
            logger.info("data.calibrating_now: {} | data.stop_calibration: {}"
                        .format(data.calibrating_now, data.stop_calibration))
            logger.info("in log calibration: data.stop_calibration is {}"
                        .format(data.stop_calibration))
            data.current_value = 0
            logger.info("stopping calibration")
            main_page.calibrate_cage_update_buttons()

