"""
This file is part of SyFoS.
SyFoS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SyFoS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SyFoS.  If not, see <http://www.gnu.org/licenses/>.
"""
from typing import Tuple, List, Dict
import os
import functools

import numpy as np

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gui.default_materials as dm
from gui.tkinter_utility import LabeledParameterInput, ParameterLabel
from gui.export_window import ExportWindow

import data_handling.generate_data as gen_data
import data_visualisation.plot_data as plot_data
from data_visualisation.toolbars.toolbar_line_plot import ToolbarLinePlot

def decorator_check_if_force_volume_selected(function):
	"""Check if a force volume is selected."""
	@functools.wraps(function)
	def wrapper_check_if_force_volume_selected(self):
		if self.activeForceVolume.get() not in self.forceVolumes:
			return messagebox.showerror(
				"Error", 
				"Please select a Force Volume."
			)
		else:
			function(self)

	return wrapper_check_if_force_volume_selected

class MainWindow(ttk.Frame):
	"""A GUI to create and compare synthetic force volumes."""
	def __init__(self, root):
		super().__init__(root, padding=10)

		self.pack(fill=BOTH, expand=YES)

		self.forceVolumes = {}

		self._init_style_parameters()
		self._init_parameter_variables()
		self._create_main_window()

	def _init_style_parameters(self) -> None:
		"""Initialise all style related parameters."""
		self.colorPlot = "#e6f7f4"

	def _init_parameter_variables(self) -> None:
		"""Initialise all parameter variables."""
		# Calculated parameters
		self.etot = ttk.StringVar(self, value="")
		self.jtc = ttk.StringVar(self, value="")
		self.hamaker = ttk.StringVar(self, value="")

	def _create_main_window(self) -> None: 
		"""Define all elements within the main window."""
		self._create_frame_parameters()
		self._create_frame_lineplot()
		self._create_frame_control()

	def _create_frame_parameters(self) -> None:
		"""Define all elements within the parameter frame."""
		smallLabelLength = 3
		normalLabelLength = 7
		wideLabelLength = 20

		frameParameters = ttk.Labelframe(
			self, 
			text="Parameters", 
			padding=15
		)
		frameParameters.pack(fill=X, expand=YES, padx=15, pady=(15, 0))

		# Probe Section
		frameProbeSection = ttk.Frame(frameParameters)
		frameProbeSection.pack(fill=Y, expand=YES)

		labelProbeSection = ttk.Label(
			frameProbeSection, 
			text="Probe", 
			font="bold"
		)
		labelProbeSection.pack(side=LEFT, fill=None, expand=YES)

		self.defaultProbe = tk.StringVar(self, value="Default Probe")
		dropdownProbe = ttk.OptionMenu(
			frameProbeSection, 
			self.defaultProbe, 
			"",
			*dm.defaultMaterials.keys(), 
			command=self._set_default_probe_parameters,
			bootstyle=""
		)
		dropdownProbe.pack(side=TOP, fill=None, expand=YES)

		self.inputEProbe = LabeledParameterInput(
			frameProbeSection,
			"",
			"E",
			"tip",
			smallLabelLength,
			"1e6 - 300e9",
			[1e6, 300e9],
			"Pa"
		)
		self.inputEProbe.pack(side=LEFT, fill=X, expand=YES)

	def _create_frame_parameters_(self) -> None:
		"""Define all elements within the parameter frame."""
		smallLabelLength = 3
		normalLabelLength = 7
		wideLabelLength = 20

		frameParameters = ttk.Labelframe(
			self, 
			text="Parameters", 
			padding=15
		)
		frameParameters.pack(fill=X, expand=YES, padx=15, pady=(15, 0))

		# Probe Section
		labelProbeSection = ttk.Label(
			frameParameters, 
			text="Probe", 
			font="bold"
		)
		labelProbeSection.grid(row=0, column=0, sticky=W, pady=(0, 5))

		self.defaultProbe = tk.StringVar(self, value="Default Probe")
		dropdownProbe = ttk.OptionMenu(
			frameParameters, 
			self.defaultProbe, 
			"",
			*dm.defaultMaterials.keys(), 
			command=self._set_default_probe_parameters,
			bootstyle=""
		)
		dropdownProbe.grid(row=0, column=1, sticky=W, padx=(7, 0), pady=(0, 5))

		self.inputEProbe = LabeledParameterInput(
			frameParameters,
			"",
			"E",
			"tip",
			smallLabelLength,
			"1e6 - 300e9",
			[1e6, 300e9],
			"Pa"
		)
		self.inputEProbe.grid(row=1, column=0, columnspan=2, sticky=W, pady=(0, 5))

		self.inputPoissonRatioProbe = LabeledParameterInput(
			frameParameters,
			"",
			"\u03BD",
			"tip",
			smallLabelLength,
			"0 - 0.5",
			[0, 0.5],
			""
		)
		self.inputPoissonRatioProbe.grid(row=2, column=0, columnspan=2, sticky=W, pady=(0, 5))

		self.inputHamakerProbe = LabeledParameterInput(
			frameParameters,
			"",
			"A",
			"tip",
			smallLabelLength,
			"1 - 450",
			[1e-21, 450e-21],
			"zJ"
		)
		self.inputHamakerProbe.grid(row=3, column=0, columnspan=2, sticky=W, pady=(0, 5))

		self.inputSpringConstant = LabeledParameterInput(
			frameParameters,
			"",
			"k",
			"c",
			smallLabelLength,
			"0.001 - 100",
			[0.001, 100],
			"N/m"
		)
		self.inputSpringConstant.grid(row=4, column=0, columnspan=2, sticky=W, pady=(0, 5))

		self.inputRadius = LabeledParameterInput(
			frameParameters,
			"",
			"R",
			"",
			smallLabelLength,
			"1e-9 - 10e-6",
			[1e-9, 10e-6],
			"m"
		)
		self.inputRadius.grid(row=5, column=0, columnspan=2, sticky=W, pady=(0, 5))

		# Sample Section
		labelSampleSection = ttk.Label(
			frameParameters, 
			text="Sample", 
			font="bold"
		)
		labelSampleSection.grid(row=0, column=2, sticky=W, pady=(0, 5))

		self.defaultSample = tk.StringVar(self, value="Default Sample")
		dropdownSample = ttk.OptionMenu(
			frameParameters, 
			self.defaultSample, 
			"",
			*dm.defaultMaterials.keys(), 
			command=self._set_default_sample_parameters,
			bootstyle=""
		)
		dropdownSample.grid(row=0, column=3, sticky=W, padx=(7, 0), pady=(0, 5))

		self.inputESample = LabeledParameterInput(
			frameParameters,
			"",
			"E",
			"sample",
			normalLabelLength,
			"1e6 - 300e9",
			[1e6, 300e9],
			"Pa"
		)
		self.inputESample.grid(row=1, column=2, columnspan=2, sticky=W, pady=(0, 5))

		self.inputPoissonRatioSample = LabeledParameterInput(
			frameParameters,
			"",
			"\u03BD",
			"sample",
			normalLabelLength,
			"0 - 0.5",
			[0, 0.5],
			""
		)
		self.inputPoissonRatioSample.grid(row=2, column=2, columnspan=2, sticky=W, pady=(0, 5))

		self.inputHamakerSample = LabeledParameterInput(
			frameParameters,
			"",
			"A",
			"sample",
			normalLabelLength,
			"1 - 450",
			[1e-21, 450e-21],
			"zJ"
		)
		self.inputHamakerSample.grid(row=3, column=2, columnspan=2, sticky=W, pady=(0, 5))

		# Force Spectroscopy Experiment section
		labelExperiment = ttk.Label(
			frameParameters, 
			text="Force Spectroscopy Experiment", 
			font="bold"
		)
		labelExperiment.grid(row=0, column=4, columnspan=2, sticky=W, pady=(0, 5))

		self.inputStartDistance = LabeledParameterInput(
			frameParameters,
			"Start Distance ",
			"Z",
			"0",
			wideLabelLength,
			"-10e-6 - 0",
			[-10e-6, 0],
			"m"
		)
		self.inputStartDistance.grid(row=1, column=4, columnspan=2, sticky=W, pady=(0, 5))

		self.inputStepSize = LabeledParameterInput(
			frameParameters,
			"Step Size ",
			"dZ",
			"",
			wideLabelLength,
			"0.01e-9 - 1e-9",
			[0.01e-9, 1e-9],
			"m"
		)
		self.inputStepSize.grid(row=2, column=4, columnspan=2, sticky=W, pady=(0, 5))

		self.inputMaximumPiezo = LabeledParameterInput(
			frameParameters,
			"Maximum Piezo ",
			"Z",
			"max",
			wideLabelLength,
			"0 - 1e-6",
			[0, 1e-6],
			"m"
		)
		self.inputMaximumPiezo.grid(row=3, column=4, columnspan=2, sticky=W, pady=(0, 5))

		self.inputNumberOfCurves = LabeledParameterInput(
			frameParameters,
			"Number Of Curves",
			"",
			"",
			wideLabelLength,
			"1 - 1000",
			[1, 1000],
			""
		)
		self.inputNumberOfCurves.grid(row=4, column=4, columnspan=2, sticky=W, pady=(0, 5))

		# Artefact section
		labelArtefact = ttk.Label(
			frameParameters, 
			text="Artefacts", 
			font="bold"
		)
		labelArtefact.grid(row=0, column=6, columnspan=2, sticky=W, pady=(0, 5))

		self.inputVirtualDeflection = LabeledParameterInput(
			frameParameters,
			"Virtual Deflection",
			"",
			"",
			wideLabelLength,
			"0 - 3e-6",
			[0, 3e-6],
			"m"
		)
		self.inputVirtualDeflection.grid(row=1, column=6, columnspan=2, sticky=W, pady=(0, 5))

		self.inputTopographyOffset = LabeledParameterInput(
			frameParameters,
			"Topography Offset",
			"",
			"",
			wideLabelLength,
			"0 - 10e-6",
			[0, 10e-6],
			"m"
		)
		self.inputTopographyOffset.grid(row=2, column=6, columnspan=2, sticky=W, pady=(0, 5))

		self.inputNoise = LabeledParameterInput(
			frameParameters,
			"Noise",
			"",
			"",
			wideLabelLength,
			"0 - 1e-9",
			[0, 1e-9],
			""
		)
		self.inputNoise.grid(row=3, column=6, columnspan=2, sticky=W, pady=(0, 5))

		self.parameterInputs = {
			"e Probe": self.inputEProbe,
			"Poisson Ratio Probe": self.inputPoissonRatioProbe,
			"Hamaker Probe": self.inputHamakerProbe,
			"kc": self.inputSpringConstant,
			"Radius": self.inputRadius,
			"e Sample": self.inputESample,
			"Poisson Ratio Sample": self.inputPoissonRatioSample,
			"Hamaker Sample": self.inputHamakerSample,	
			"Start Distance": self.inputStartDistance,
			"Step Size": self.inputStepSize,
			"Maximum Piezo": self.inputMaximumPiezo,
			"Number Of Curves": self.inputNumberOfCurves,
			"Virtual Deflection": self.inputVirtualDeflection,
			"Topography Offset": self.inputTopographyOffset,
			"Noise": self.inputNoise
		}

		self._set_test_values()

		frameParameters.grid_columnconfigure(0, weight=1, pad=3)
		frameParameters.grid_columnconfigure(1, weight=1, pad=3)
		frameParameters.grid_columnconfigure(2, weight=1, pad=3)
		frameParameters.grid_columnconfigure(3, weight=1, pad=3)
		frameParameters.grid_columnconfigure(4, weight=1, pad=3)
		frameParameters.grid_columnconfigure(5, weight=1, pad=3)
		frameParameters.grid_columnconfigure(6, weight=1, pad=3)
		frameParameters.grid_columnconfigure(7, weight=1, pad=3)
		frameParameters.grid_columnconfigure(8, weight=1, pad=3)

		frameParameters.grid_rowconfigure(0, weight=1, pad=3)
		frameParameters.grid_rowconfigure(1, weight=1, pad=3)
		frameParameters.grid_rowconfigure(2, weight=1, pad=3)
		frameParameters.grid_rowconfigure(3, weight=1, pad=3)
		frameParameters.grid_rowconfigure(4, weight=1, pad=3)
		frameParameters.grid_rowconfigure(5, weight=1, pad=3)

	def _set_test_values(self):
		""""""
		self.inputSpringConstant.set("1")
		self.inputRadius.set("25e-9")

		self.inputNumberOfCurves.set("4")
		self.inputMaximumPiezo.set("30e-9")
		self.inputStartDistance.set("-10e-9")
		self.inputStepSize.set("0.2e-9")
		self.inputNoise.set("1e-10")
		self.inputVirtualDeflection.set("3e-9")		
		self.inputTopographyOffset.set("10e-9")

	def _create_frame_lineplot(self) -> None:
		"""Define all elements within the line plot frame."""
		frameLinePlot = ttk.Labelframe(self, text="Presentation", padding=15)
		frameLinePlot.pack(side=LEFT, fill=X, expand=YES, padx=15, pady=15)

		rowVariables = ttk.Frame(frameLinePlot)
		rowVariables.pack(fill=X, expand=YES, padx=(15, 0), pady=(0, 10))

		labelEtot = ttk.Label(rowVariables, text="etot:")
		labelEtot.pack(side=LEFT, fill=X, expand=YES)
		
		entryEtot = ttk.Entry(
			rowVariables, 
			textvariable=self.etot, 
			state="readonly", 
			bootstyle="light"
		)
		entryEtot.pack(side=LEFT, fill=X, expand=YES, padx=(0, 20))

		labelJtc = ttk.Label(rowVariables, text="jtc:")
		labelJtc.pack(side=LEFT, fill=X, expand=YES)

		entryJtc = ttk.Entry(
			rowVariables, 
			textvariable=self.jtc, 
			state="readonly", 
			bootstyle="light"
		)
		entryJtc.pack(side=LEFT, fill=X, padx=(0, 15), expand=YES)

		labelHamaker = ttk.Label(rowVariables, text="hamaker:")
		labelHamaker.pack(side=LEFT, fill=X, expand=YES)

		entryHamaker = ttk.Entry(
			rowVariables, 
			textvariable=self.hamaker, 
			state="readonly", 
			bootstyle="light"
		)
		entryHamaker.pack(side=LEFT, fill=X, padx=(0, 15), expand=YES)

		rowLinePlot = ttk.Frame(frameLinePlot)
		rowLinePlot.pack(fill=X, expand=YES)

		figureLinePlot = Figure(figsize=(6, 5), facecolor=(self.colorPlot))
		self.holderFigureLinePlot = FigureCanvasTkAgg(figureLinePlot, rowLinePlot)
		toolbarLinePlot = ToolbarLinePlot(
			self.holderFigureLinePlot, 
			rowLinePlot,
		)
		self.holderFigureLinePlot.get_tk_widget().pack(
			side=TOP, fill=BOTH, expand=YES
		)
		toolbarLinePlot.pack(side=BOTTOM, fill=X)

	def _create_frame_control(self) -> None:
		"""Define all elements within the control frame."""
		frameControl = ttk.Labelframe(self, text="Control", padding=15)
		frameControl.pack(side=RIGHT, fill=X, expand=YES, anchor=N, padx=15, pady=15)

		buttonCreateForceVolume = ttk.Button(
			frameControl,
			text="Create Force Volume",
			command=self._create_force_volume
		)
		buttonCreateForceVolume.pack(pady=(0, 10))

		seperator = ttk.Separator(frameControl)
		seperator.pack(fill=X, expand=YES, pady=(0, 50))

		self.activeForceVolume = tk.StringVar(self, value="Force Volumes")
		
		self.dropdownForceVolumes = ttk.OptionMenu(
			frameControl, 
			self.activeForceVolume, 
			"",
			*self.forceVolumes.keys(), 
			command=self._set_active_force_volume,
			bootstyle=""
		)
		self.dropdownForceVolumes.pack()

		buttonSaveForceVolume = ttk.Button(
			frameControl,
			text="Save Force Volume",
			command=self._export_force_volume,
			width=20
		)
		buttonSaveForceVolume.pack(pady=(20, 0))

		buttonDeleteForceVolume = ttk.Button(
			frameControl,
			text="Delete Force Volume",
			command=self._delete_force_volume,
			width=20
		)
		buttonDeleteForceVolume.pack(pady=(10, 0))

	def _set_probe_label(self) -> None:
		"""Change the probe label if the user changes 
		   any of it's parameters."""
		self.defaultProbe.set("Custom Probe")

	def _set_sample_label(self) -> None:
		"""Change the sample label if the user changes 
		   any of it's parameters."""
		self.defaultSample.set("Custom Sample")

	def _set_default_probe_parameters(self, defaultProbe:str) -> None:
		"""Set the parameters of a selected default probe material.

		Parameter:
			defaultProbe(str): Name of the chosen default probe material.
		"""
		self.inputEProbe.set(dm.defaultMaterials[defaultProbe]["e"])
		self.inputPoissonRatioProbe.set(dm.defaultMaterials[defaultProbe]["poissonRatio"])
		self.inputHamakerProbe.set(dm.defaultMaterials[defaultProbe]["hamaker"])

	def _set_default_sample_parameters(self, defaultSample:str) -> None:
		"""Set the parameters of a selected default sample material.

		Parameter:
			defaultSample(str): Name of the chosen default sample material.
		"""
		self.inputESample.set(dm.defaultMaterials[defaultSample]["e"])
		self.inputPoissonRatioSample.set(dm.defaultMaterials[defaultSample]["poissonRatio"])
		self.inputHamakerSample.set(dm.defaultMaterials[defaultSample]["hamaker"])

	def _create_force_volume(self) -> tk.messagebox:
		"""Create a synthetic force volume with the selected parameters and display it.

		Returns:
			userFeedback(tk.messagebox): Informs the user whether the force volume could be created or not.
		"""
		try:
			self._check_parameters()
		except ValueError as e:
			return messagebox.showerror(
				"Error", 
				e
			)
		else:
			parameterMaterial, parameterMeasurement, parameterForceVolume = self._get_parameters()

		try:
			forceVolume = gen_data.create_synthetic_force_volume(
				parameterMaterial, 
				parameterMeasurement, 
				parameterForceVolume
			)
		except ValueError as e:
			self._reset_parameters()
			return messagebox.showerror(
				"Error", 
				e
			)

		self._cache_force_volume(
			forceVolume,
			parameterMaterial.Etot,
			parameterMaterial.jtc,
			parameterMaterial.Hamaker
		)

		plot_data.plot_force_volume(
			self.holderFigureLinePlot,
			self.forceVolumes[self.activeForceVolume.get()]["lineCollection"]
		)

		return messagebox.showinfo(
			"Success", 
			"Added synthetic force volume."
		)

	def _check_parameters(self) -> None:
		"""Check wether all input parameters are valid.

		Raises:
			ValueError: If a parameter is not a number.
		"""
		for parameterName, parameterInput in self.parameterInputs.items():
			if parameterInput.check_value() == False:
				raise ValueError(
					"Invalid value for " + parameterName + "."
				)

	def _get_parameters(self) -> Tuple:
		"""Group all input parameters into namedtuples.
		
		Returns:
			parameterMaterial(namedtuple): Contains every material parameter.
			parameterMeasurement(namedtuple): Contains every measurment parameter.
			parameterForceVolume(namedtuple): Contains every force volume parameter.
		"""
		ParameterMaterial, ParameterMeasurement, ParameterForceVolume = gen_data.get_parameter_tuples()

		hamaker = gen_data.calculate_hamaker(
			float(self.inputHamakerProbe.get()),
			float(self.inputHamakerSample.get())
		)
		jtc = gen_data.calculate_jtc(
			hamaker,
			float(self.inputRadius.get()),
			float(self.inputSpringConstant.get())
		)
		etot = gen_data.calculate_etot(
			float(self.inputPoissonRatioProbe.get()),
			float(self.inputEProbe.get()),
			float(self.inputPoissonRatioSample.get()),
			float(self.inputESample.get())
		)

		parameterMaterial = ParameterMaterial(
			kc=float(self.inputSpringConstant.get()),
			radius=float(self.inputRadius.get()),
			Hamaker=hamaker,
			Etot=etot,
			jtc=jtc,
		)
		parameterMeasurement = ParameterMeasurement(
			initialDistance=float(self.inputStartDistance.get()),
			distanceInterval=float(self.inputStepSize.get()),
			maximumdeflection=float(self.inputMaximumPiezo.get()),	
		)
		parameterForceVolume = ParameterForceVolume(
			numberOfCurves=int(self.inputNumberOfCurves.get()),
			noise=float(self.inputNoise.get()),
			virtualDeflection=float(self.inputVirtualDeflection.get()),
			topography=float(self.inputTopographyOffset.get())
		)

		return parameterMaterial, parameterMeasurement, parameterForceVolume

	def _cache_force_volume(
		self,
		forceVolume: np.ndarray, 
		etot: float, 
		jtc: float,
		hamaker: float
	) -> None:
		"""Cache the data of a force volume.

		Parameters:
			forceVolume(np.ndarray): Data of the force volume.
			etot(float): etot value of the force volume.
			jtc(float): jtc value of the force volume.
			hamaker(float): hamaker value of the force volume.
		"""
		nameForceVolume = "Force Volume " + str(len(self.forceVolumes) + 1)

		self.forceVolumes[nameForceVolume] = {
			"data": forceVolume,
			"lineCollection": plot_data.create_line_collection(forceVolume),
			"etot": etot,
			"jtc": jtc,
			"hamaker": hamaker
		}

		self._update_dropdown_force_volumes()
		self.activeForceVolume.set(nameForceVolume)
		self._set_active_force_volume()

	def _update_dropdown_force_volumes(self) -> None:
		"""Update the list of generated force volumes in the dropdown menu."""
		self.dropdownForceVolumes.set_menu("", *self.forceVolumes.keys())
	
	@decorator_check_if_force_volume_selected
	def _delete_force_volume(self) -> None:
		"""Delete the active force volume with all its data."""	
		plot_data.delete_force_volume_from_plot(
			self.holderFigureLinePlot,
			self.forceVolumes[self.activeForceVolume.get()]["lineCollection"]
		)
		# Remove force volume from cache.
		del self.forceVolumes[self.activeForceVolume.get()]
		self._update_dropdown_force_volumes()
		self.activeForceVolume.set("Force Volumes")

		self._reset_calculated_parameters()
	
	def _set_active_force_volume(
		self, 
		forceVolume: str=""
	) -> None:
		""".

		Parameters:
			forceVolume(str): .
		"""
		self._set_calculated_parameters(
			self.forceVolumes[self.activeForceVolume.get()]["etot"],
			self.forceVolumes[self.activeForceVolume.get()]["jtc"],
			self.forceVolumes[self.activeForceVolume.get()]["hamaker"]
		)

		for forceVolumeName, forceVolumeData in self.forceVolumes.items():
			if forceVolumeName == self.activeForceVolume.get():
				plot_data.set_active_line_collection(
					forceVolumeData["lineCollection"]
				)
			else:
				plot_data.set_inative_line_collection(
					forceVolumeData["lineCollection"]
				)

		self.holderFigureLinePlot.draw()

	@staticmethod
	def _round_parameter_presentation(
		parameterValue: float
	) -> str: 
		"""Define the format for the parameter presentation in the GUI.

		Parameters:
			parameterValue(float): Calculated parameter value.

		Returns:
			roundedParameterRepresentation(str): Rounded parameter value in scientific format.
		"""
		return '{:.3e}'.format(parameterValue)

	def _set_calculated_parameters(
		self, 
		etot: str,
		jtc: str,
		hamaker: str
	) -> None:
		"""Set the calculated parameters of the active force volume.

		Parameters:
			etot(str): Calculated and rounded etot value.
			jtc(str): Calculated and rounded jtc value.
			hamaker(str): Calculated and rounded hamaker value.
		"""
		self.etot.set(
			self._round_parameter_presentation(etot)
		)
		self.jtc.set(
			self._round_parameter_presentation(jtc)
		)
		self.hamaker.set(
			self._round_parameter_presentation(hamaker)
		)

	def _reset_calculated_parameters(self) -> None:
		"""Reset the calculated parameters if no force volume is active."""
		self.etot.set("")
		self.jtc.set("")
		self.hamaker.set("")
	
	@decorator_check_if_force_volume_selected
	def _export_force_volume(self) -> None:
		"""Open a window to export the data of the active force volume."""
		exportWindow = ttk.Toplevel("Export Force Curve")
		ExportWindow(
			exportWindow,
			self.forceVolumes[self.activeForceVolume.get()]
		)