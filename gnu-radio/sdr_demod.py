#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SDR audio search
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import osmosdr
import time

from gnuradio import qtgui

class sdr_demod(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SDR audio search")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SDR audio search")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "sdr_demod")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.squelch_on = squelch_on = 0
        self.squelch = squelch = -50
        self.samp_rate = samp_rate = 2.048e6
        self.fine_grained_centre_freq = fine_grained_centre_freq = 0
        self.centre_freq = centre_freq = 500e6
        self.audio_rate = audio_rate = 32000
        self.squelch_value = squelch_value = squelch_on+squelch
        self.mute = mute = 1
        self.freq = freq = centre_freq+fine_grained_centre_freq
        self.filter_gain = filter_gain = 1.0
        self.demod_mode = demod_mode = 0
        self.decimation = decimation = int(samp_rate/audio_rate)
        self.bw_factor = bw_factor = 1
        self.audio_gain = audio_gain = 1
        self.audio_bw = audio_bw = audio_rate/2

        ##################################################
        # Blocks
        ##################################################
        _mute_check_box = Qt.QCheckBox('Mute')
        self._mute_choices = {True: 1, False: 0}
        self._mute_choices_inv = dict((v,k) for k,v in self._mute_choices.items())
        self._mute_callback = lambda i: Qt.QMetaObject.invokeMethod(_mute_check_box, "setChecked", Qt.Q_ARG("bool", self._mute_choices_inv[i]))
        self._mute_callback(self.mute)
        _mute_check_box.stateChanged.connect(lambda i: self.set_mute(self._mute_choices[bool(i)]))
        self.top_grid_layout.addWidget(_mute_check_box, 1, 4, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._filter_gain_range = Range(0.8, 8, 0.1, 1.0, 200)
        self._filter_gain_win = RangeWidget(self._filter_gain_range, self.set_filter_gain, 'Input Gain', "dial", float)
        self.top_grid_layout.addWidget(self._filter_gain_win, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._demod_mode_options = (0, 1, 2, )
        # Create the labels list
        self._demod_mode_labels = ('AM', 'FM', 'Raw', )
        # Create the combo box
        self._demod_mode_tool_bar = Qt.QToolBar(self)
        self._demod_mode_tool_bar.addWidget(Qt.QLabel('Demodulation mode' + ": "))
        self._demod_mode_combo_box = Qt.QComboBox()
        self._demod_mode_tool_bar.addWidget(self._demod_mode_combo_box)
        for _label in self._demod_mode_labels: self._demod_mode_combo_box.addItem(_label)
        self._demod_mode_callback = lambda i: Qt.QMetaObject.invokeMethod(self._demod_mode_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._demod_mode_options.index(i)))
        self._demod_mode_callback(self.demod_mode)
        self._demod_mode_combo_box.currentIndexChanged.connect(
            lambda i: self.set_demod_mode(self._demod_mode_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._demod_mode_tool_bar, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._bw_factor_range = Range(0, 1, .01, 1, 200)
        self._bw_factor_win = RangeWidget(self._bw_factor_range, self.set_bw_factor, 'BW adjust', "dial", float)
        self.top_grid_layout.addWidget(self._bw_factor_win, 0, 4, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._audio_gain_range = Range(0, 10, .01, 1, 200)
        self._audio_gain_win = RangeWidget(self._audio_gain_range, self.set_audio_gain, 'Audio Gain', "dial", float)
        self.top_grid_layout.addWidget(self._audio_gain_win, 1, 3, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        _squelch_on_check_box = Qt.QCheckBox('Squelch On')
        self._squelch_on_choices = {True: 0, False: -500}
        self._squelch_on_choices_inv = dict((v,k) for k,v in self._squelch_on_choices.items())
        self._squelch_on_callback = lambda i: Qt.QMetaObject.invokeMethod(_squelch_on_check_box, "setChecked", Qt.Q_ARG("bool", self._squelch_on_choices_inv[i]))
        self._squelch_on_callback(self.squelch_on)
        _squelch_on_check_box.stateChanged.connect(lambda i: self.set_squelch_on(self._squelch_on_choices[bool(i)]))
        self.top_grid_layout.addWidget(_squelch_on_check_box, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._squelch_range = Range(-100, 0, 1, -50, 200)
        self._squelch_win = RangeWidget(self._squelch_range, self.set_squelch, 'Squelch', "counter", float)
        self.top_grid_layout.addWidget(self._squelch_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(freq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(10*filter_gain, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.qtgui_waterfall_sink_x_1 = qtgui.waterfall_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            audio_rate, #bw
            "Downsampled", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_1.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_1.enable_grid(False)
        self.qtgui_waterfall_sink_x_1.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_1.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_1.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_1.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_1_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_1_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            2048, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "IF", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 2, 0, 1, 5)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_sink_x_3 = qtgui.sink_f(
            1024, #fftsize
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            audio_bw, #bw
            "Demodulated", #name
            True, #plotfreq
            True, #plotwaterfall
            False, #plottime
            False #plotconst
        )
        self.qtgui_sink_x_3.set_update_time(1.0/10)
        self._qtgui_sink_x_3_win = sip.wrapinstance(self.qtgui_sink_x_3.pyqwidget(), Qt.QWidget)

        self.qtgui_sink_x_3.enable_rf_freq(False)

        self.top_grid_layout.addWidget(self._qtgui_sink_x_3_win, 3, 2, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.low_pass_filter_1 = filter.fir_filter_ccf(
            decimation,
            firdes.low_pass(
                filter_gain,
                samp_rate,
                bw_factor*(audio_bw-1e3),
                1e3,
                firdes.WIN_HAMMING,
                6.76))
        self.high_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.high_pass(
                1,
                audio_rate,
                25,
                25,
                firdes.WIN_HAMMING,
                6.76))
        self._fine_grained_centre_freq_range = Range(-1e6, 1e6, 1e3, 0, 200)
        self._fine_grained_centre_freq_win = RangeWidget(self._fine_grained_centre_freq_range, self.set_fine_grained_centre_freq, 'Fine grained centre freq', "counter_slider", float)
        self.top_grid_layout.addWidget(self._fine_grained_centre_freq_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._centre_freq_range = Range(20e6, 1.7e9, 1.0e6, 500e6, 200)
        self._centre_freq_win = RangeWidget(self._centre_freq_range, self.set_centre_freq, 'Centre Frequency', "counter_slider", float)
        self.top_grid_layout.addWidget(self._centre_freq_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('./signals.wav', 1, audio_rate, 16)
        self.blocks_selector_1 = blocks.selector(gr.sizeof_float*1,demod_mode,0)
        self.blocks_selector_1.set_enabled(True)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(audio_gain * (1-mute), 1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.audio_sink_0 = audio.sink(audio_rate, 'hw:CARD=AudioPCI,DEV=0', False)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc(squelch_value, 1)
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=audio_rate,
        	audio_decim=1,
        	deviation=1000,
        	audio_pass=0.8*audio_bw,
        	audio_stop=0.95*audio_bw,
        	gain=1.0,
        	tau=75e-6,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_selector_1, 1))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.high_pass_filter_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_selector_1, 2))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.qtgui_sink_x_3, 0))
        self.connect((self.high_pass_filter_0, 0), (self.blocks_selector_1, 0))
        self.connect((self.low_pass_filter_1, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.qtgui_waterfall_sink_x_1, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.qtgui_waterfall_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "sdr_demod")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_squelch_on(self):
        return self.squelch_on

    def set_squelch_on(self, squelch_on):
        self.squelch_on = squelch_on
        self._squelch_on_callback(self.squelch_on)
        self.set_squelch_value(self.squelch_on+self.squelch)

    def get_squelch(self):
        return self.squelch

    def set_squelch(self, squelch):
        self.squelch = squelch
        self.set_squelch_value(self.squelch_on+self.squelch)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decimation(int(self.samp_rate/self.audio_rate))
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.filter_gain, self.samp_rate, self.bw_factor*(self.audio_bw-1e3), 1e3, firdes.WIN_HAMMING, 6.76))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_fine_grained_centre_freq(self):
        return self.fine_grained_centre_freq

    def set_fine_grained_centre_freq(self, fine_grained_centre_freq):
        self.fine_grained_centre_freq = fine_grained_centre_freq
        self.set_freq(self.centre_freq+self.fine_grained_centre_freq)

    def get_centre_freq(self):
        return self.centre_freq

    def set_centre_freq(self, centre_freq):
        self.centre_freq = centre_freq
        self.set_freq(self.centre_freq+self.fine_grained_centre_freq)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_audio_bw(self.audio_rate/2)
        self.set_decimation(int(self.samp_rate/self.audio_rate))
        self.high_pass_filter_0.set_taps(firdes.high_pass(1, self.audio_rate, 25, 25, firdes.WIN_HAMMING, 6.76))
        self.qtgui_waterfall_sink_x_1.set_frequency_range(0, self.audio_rate)

    def get_squelch_value(self):
        return self.squelch_value

    def set_squelch_value(self, squelch_value):
        self.squelch_value = squelch_value
        self.analog_simple_squelch_cc_0.set_threshold(self.squelch_value)

    def get_mute(self):
        return self.mute

    def set_mute(self, mute):
        self.mute = mute
        self._mute_callback(self.mute)
        self.blocks_multiply_const_xx_0.set_k(self.audio_gain * (1-self.mute))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.qtgui_sink_x_3.set_frequency_range(self.freq, self.audio_bw)
        self.rtlsdr_source_0.set_center_freq(self.freq, 0)

    def get_filter_gain(self):
        return self.filter_gain

    def set_filter_gain(self, filter_gain):
        self.filter_gain = filter_gain
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.filter_gain, self.samp_rate, self.bw_factor*(self.audio_bw-1e3), 1e3, firdes.WIN_HAMMING, 6.76))
        self.rtlsdr_source_0.set_gain(10*self.filter_gain, 0)

    def get_demod_mode(self):
        return self.demod_mode

    def set_demod_mode(self, demod_mode):
        self.demod_mode = demod_mode
        self._demod_mode_callback(self.demod_mode)
        self.blocks_selector_1.set_input_index(self.demod_mode)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_bw_factor(self):
        return self.bw_factor

    def set_bw_factor(self, bw_factor):
        self.bw_factor = bw_factor
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.filter_gain, self.samp_rate, self.bw_factor*(self.audio_bw-1e3), 1e3, firdes.WIN_HAMMING, 6.76))

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_xx_0.set_k(self.audio_gain * (1-self.mute))

    def get_audio_bw(self):
        return self.audio_bw

    def set_audio_bw(self, audio_bw):
        self.audio_bw = audio_bw
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.filter_gain, self.samp_rate, self.bw_factor*(self.audio_bw-1e3), 1e3, firdes.WIN_HAMMING, 6.76))
        self.qtgui_sink_x_3.set_frequency_range(self.freq, self.audio_bw)





def main(top_block_cls=sdr_demod, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
