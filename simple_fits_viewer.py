#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 13:55:54 2022

@author: rszakats
https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Image_Elem_Image_Viewer_PIL_Based.py
"""


import os.path

import matplotlib
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from astropy.io import fits
from astropy.visualization import (LinearStretch, LogStretch, MinMaxInterval,
                                   ZScaleInterval)

matplotlib.use('TkAgg')
from pathlib import Path

from astropy.visualization import ImageNormalize
from astropy.wcs import WCS
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def convert_fits(file, scale=None, stretch=None, with_grid=None):
    try:
        hdu = fits.open(file)
        headers = hdu.info(output=False)
        try:
            if len(headers) == 1:
                data = hdu[0].data
            else:
                result = [tup[1] for tup in headers].index('image'.casefold())
                data = hdu[result].data
        except Exception as e:
            print(f"Cannot find image data!\nException: {e}")
    except Exception as e:
        print(f"Not a fits file!\nException: {e}")
    if scale == None or scale == "zscale":
        interval = ZScaleInterval()    
    elif scale == "minmax":
        interval = MinMaxInterval()
    if stretch == None or  stretch == 'linear':
        stre = LinearStretch()
    elif stretch == 'log':
        stre = LogStretch()
    vmin, vmax = interval.get_limits(data)
    norm = ImageNormalize(stretch=stre, vmin=vmin, vmax=vmax)
    plt.figure(figsize=(13.3, 10))
    if with_grid:
        try:
            wcs = WCS(hdu[0].header)
            ax = plt.subplot(projection=wcs)
            ax.imshow(data, origin='lower', norm=norm, cmap='gray')
            overlay = ax.get_coords_overlay('fk5')
            overlay.grid(color='white', ls='dotted')
        except Exception as e:
            print(f"No WCS data in header! {e}")
            plt.imshow(data, origin='lower', norm=norm, cmap='gray')
    else:
        plt.imshow(data, origin='lower', norm=norm, cmap='gray')
    fig = plt.gcf()
    return fig


def get_header_data(file):
    hdu = fits.open(file)
    header = hdu[0].header
    try:
        obj = header['object']
    except Exception as e:
        print(f"Exception occured! {e}")
        obj = "None"
    try:
        dateobs = header['DATE-OBS']
    except Exception as e:
        print(f"Exception occured! {e}")
        dateobs = "None"
    return obj, dateobs


def draw_figure(canvas, figure):
    if not hasattr(draw_figure, 'canvas_packed'):
        draw_figure.canvas_packed = {}
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    if widget not in draw_figure.canvas_packed:
        draw_figure.canvas_packed[widget] = figure
        widget.pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f'Error removing {figure_agg} from list', e)
    plt.close('all')


def plot_fits(figure_agg, scale, stretch, grid):
    l = ""
    try:
        filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
        l = f"Plotting {filename}"
        window['-TOUT-'].update(filename)
        obj, dateobs = get_header_data(filename)
        window['-OBJECT-'].update(obj)
        window['-DATEOBS-'].update(dateobs)
        if figure_agg:
        # ** IMPORTANT ** Clean up previous drawing before drawing again
            delete_figure_agg(figure_agg)
        figure_agg = draw_figure(window['-CANVAS-'].TKCanvas, convert_fits(filename, scale=scale, stretch=stretch, with_grid=grid))
    except Exception as E:
        print(f'** Error {E} **')
        pass
    return figure_agg, obj, dateobs, l


def get_header(hnum):
    try:
        file = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
        hdu = fits.open(file)
        eq = "="
        l = (list(hdu[hnum[0]].header.keys()))
        h = f'KEY\t\t   \tVALUE\n----------------------------------------------------------\n'
        for ll in l:
            h += f"{ll}\t\t {eq:^8} \t {hdu[0].header[ll]}\n"
    except Exception as e:
        print(f"Not a fits file!\nException: {e}")
    return h


def make_win2(head):
    layout2 = [[sg.Menu(hmenu)], [sg.Multiline(no_scrollbar=False, size=(170, 200), key="-HEAD-")]]
    window2 = sg.Window('FITS Header Viewer', layout2,resizable=True, size=(600, 900), finalize=True)
    window2.find_element('-HEAD-').Update(head)
    while True:
        event, values = window2.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            window2.close()
            break     
        elif event == sg.WIN_CLOSED or event == 'Exit':
            window2.close()
            break
        if event == 'Save':
            file_path = sg.popup_get_file('Save as', no_window=True, save_as=True) + '.txt'
            file = Path(file_path)
            with open(f"{file}", "w", encoding = 'utf-8') as f:
                f.write(head)
            log = f"Saving {file}."
            window['-LOG-'].update(log+"\n", append=True)

def make_popup(headers):
    layout3 = [[sg.Menu(hmenu), [sg.Listbox(headers, size=(60,10), key='SELECTED')],
        [sg.Button('OK')],]]
    window3 = sg.Window('FITS Header Select', layout3, resizable=True, size=(400, 200), finalize=True)
    # window3.find_element('-SELECTED-').Update(headers)
    while True:
        event, values = window3.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            window3.close()
            break     
        elif event == sg.WIN_CLOSED or event == 'Exit':
            window3.close()
            break
        elif event == 'OK':
            window3.close()
            break
    
    # print(f"Value selected: {values['SELECTED'][0]}")
    if values and values['SELECTED']:
        return values['SELECTED'][0]
    else:
        return [0]

# --------------------------------- Define Layout ---------------------------------
sg.theme('NeutralBlue')
# First the window layout...2 columns
figure_w, figure_h = 950, 950
hmenu = [['File', ['Save', '---', 'Exit']]]
# ----- Menu layout -----
menu_layout = [
        ['File', ['Save', '---', 'Exit']],
        ['View',['WSC Grid on', 'WCS Grid off', 'Header']],
        ['Scale', ['Zscale', 'Minmax', 'Linear', 'Log']] 
        ]

left_col = [[sg.Menu(menu_layout)], [sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Button("Toggle WCS", key='-WCS-')],
            [sg.Button("Zscale", size=(11, 1)), sg.Button("Minmax", size=(11, 1))],
            [sg.Button("Linear", size=(11, 1)), sg.Button("Logarithmic", key='Log', size=(11, 1))],
            [sg.HorizontalSeparator()],
            [sg.Text("Log:")],
            [sg.Output(size=(40, 5), key="-LOG-")]
           ]

images_col = [[sg.Text('File Name:', font="Helvitica 9 bold"),sg.Text(size=(80,1), key='-TOUT-', font="Helvitica 9")],
              [sg.Text('Object:', font="Helvitica 9 bold"),sg.Text(size=(40,1), key='-OBJECT-', font="Helvitica 9")],
              [sg.Text('Date:', font="Helvitica 9 bold"),sg.Text(size=(40,1), key='-DATEOBS-', font="Helvitica 9")],
              [sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-')]]

layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),sg.Column(images_col, element_justification='l')]]

window = sg.Window('FITS Image Viewer', layout,resizable=True, size=(1700,980))

new_size = (1000,1000)
figure_agg = None
scale = None
filename = None
grid = None
stretch = None
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-FOLDER-':
        folder = values['-FOLDER-']
        log = f"Folder {folder} selected."
        window['-LOG-'].update(log+"\n", append=True)
        try:
            file_list = sorted(os.listdir(folder))
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".fit", ".fits"))]
        window['-FILE LIST-'].update(fnames)
    if event == '-FILE LIST-':
        figure_agg, obj, dateobs, ll= plot_fits(figure_agg, scale, stretch, grid)
        log = f"File {values['-FILE LIST-'][0]} was selected."
        window['-LOG-'].update(log+"\n", append=True)
    if event == 'Zscale':
        if figure_agg:
            log = f"Selecting Zscale"
            scale = 'zscale'
            figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
            log += f"\n{ll}"
            window['-LOG-'].update(log+"\n", append=True)
    elif event == 'Minmax':
        if figure_agg:
            log = f"Selecting Minmax"
            scale = 'minmax'
            figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
            log += f"\n{ll}"
            window['-LOG-'].update(log+"\n", append=True)
    if event == 'Linear':
        if figure_agg:
            log = f"Selecting Linear stretch"
            stretch = 'linear'
            figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
            log += f"\n{ll}"
            window['-LOG-'].update(log+"\n", append=True)
    elif event == 'Log':
        if figure_agg:
            log = f"Selecting logarithmic stretch"
            stretch = 'log'
            figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
            log += f"\n{ll}"
            window['-LOG-'].update(log+"\n", append=True)
    if event == 'WSC Grid on':
        if figure_agg:
            if grid:
                log = f"WCS grid is already set!"
                window['-LOG-'].update(log+"\n", append=True)
            else:
                log = f"Setting WCS grid"
                grid = True
                figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
                log += f"\n{ll}"
                window['-LOG-'].update(log+"\n", append=True)
    elif event == 'WCS Grid off':
        if figure_agg:
            if grid:
                log = f"Turning off WCS grid"
                grid = None
                figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
                log += f"\n{ll}"
                window['-LOG-'].update(log+"\n", append=True)
            else:
                log = f"WCS grid is already turned off!"
                window['-LOG-'].update(log+"\n", append=True)
    if event == '-WCS-':
        if figure_agg:
            if grid:
                grid = None
                figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
                log = f"Turning off WCS grid"
                window['-LOG-'].update(log+"\n", append=True)
            else:
                grid = True
                figure_agg, obj, dateobs, ll = plot_fits(figure_agg, scale, stretch, grid)
                log = f"Setting WCS grid"
                window['-LOG-'].update(log+"\n", append=True)
    if event == 'Header':
        try:
            if figure_agg:
                log = f"Viewing header of {values['-FILE LIST-'][0]}"
                window['-LOG-'].update(log+"\n", append=True)
                file = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
                hdu = fits.open(file)
                headers = hdu.info(output=False)
                hnum = make_popup(headers)
                head = get_header(hnum)
                make_win2(head)
        except Exception as e:
            print(e)

    if event == 'Save':
        if figure_agg:
            file_path = sg.popup_get_file('Save as', no_window=True, save_as=True) + '.png'
            file = Path(file_path)
            log = f"Saving {file}."
            window['-LOG-'].update(log+"\n", append=True)
            if grid:
                plt.title(f"Object: {obj}    Date: {dateobs}", loc='center', pad=40)
            else:
                plt.title(f"Object: {obj}    Date: {dateobs}", loc='center', pad=10)
            plt.tight_layout()
            plt.savefig(file, dpi=150)
            plt.close()

if figure_agg:
    delete_figure_agg(figure_agg)
window.close()