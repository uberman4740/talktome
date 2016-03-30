#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Help will be here :)
"""
from __future__ import division, print_function, absolute_import
from __future__ import unicode_literals
import librosa
import matplotlib.pyplot as plt
import numpy as np
import sys
reload(sys.modules['librosa'])

class Audio:

    def __init__(self,fileName,**kwargs):
        self.fileName = fileName
        self.tempo = None
        self.y = None
        self.sr = None
        self.onsetEnv = None
        self.autocorrelationMean = None
        self.autocorrelationStd = None
        if 'hopLength' in kwargs:
            self.hopLength = kwargs['hopLength']
        else:
            self.hopLength = 512
        if 'autocorrStdThreshold' in kwargs:
            self.autocorrStdThreshold = kwargs['autocorrStdThreshold']
        else:
            self.autocorrStdThreshold = 1.

    def load(self,force=False):
        if force or self.y == None or self.sr == None or self.onsetEnv == None:
            self.y, self.sr = librosa.load(self.fileName,mono=True)
            self.onsetEnv = librosa.onset.onset_strength(self.y,sr=self.sr)

    def setTempo(self,force=False):
        if force or self.tempo == None:
            hop_length = self.hopLength
            self.tempo = librosa.beat.estimate_tempo(self.onsetEnv,sr=self.sr,hop_length=hop_length)
            ac = librosa.util.normalize(librosa.autocorrelate(self.onsetEnv,3*self.sr//hop_length))
            tempo_frames = (60*self.sr/hop_length)/self.tempo
            self.autocorrelationStd = np.std(ac[int(tempo_frames):])
            self.autocorrelationMean = np.mean(ac[int(tempo_frames):])
            fig=plt.figure(figsize=(20,10))
            ax=fig.add_subplot(111)
            ax.plot(ac,label='Onset autocorrelation')
            ax.vlines([tempo_frames],0,1,color='r',alpha=0.75,linestyle='--',
            label='Tempo: {:.2f} BPM'.format(self.tempo))
            ax.axhline(y=self.autocorrelationMean,color='k',linestyle=':',
            label='Mean+-Std {:.3f}'.format(self.autocorrelationStd))
            ax.axhline(y=self.autocorrelationMean+self.autocorrelationStd,color='k',linestyle=':')
            ax.axhline(y=self.autocorrelationMean-self.autocorrelationStd,color='k',linestyle=':')
            librosa.display.time_ticks(librosa.frames_to_time(np.arange(len(ac)),sr=self.sr))
            plt.title(self.fileName)
            plt.xlabel('Lag')
            plt.legend()
            plt.axis('tight') 
            plt.savefig(self.fileName+'.png',format='png',dpi=300)
            plt.close(fig)
            if self.autocorrelationStd < self.autocorrStdThreshold:
                self.tempo = 0.
