__author__ = 'Serg Khayrulin'

import re
import math


class SubSegment:
    def __init__(self):
        """

        :type self: object
        """
        self.start_x = 0
        self.start_y = 0
        self.start_z = 0
        self.end_x = 0
        self.end_y = 0
        self.end_z = 0
        self.diam = 0
        self.h = 0
        self.params = {}

    def calc_h(self):
        self.h = math.sqrt(math.pow(self.start_x - self.end_x, 2) + math.pow(self.start_y - self.end_y, 2) + math.pow(self.start_z - self.end_z, 2))

    def get_param(self, p_name):
        return self.params[p_name]


class Segment:
    def __init__(self, index=-1, name=''):
        self.index = index
        self.signal = -1
        self.color = 0
        self.name = name
        self.sub_sec = []

    def init_segment(self, h, params):
        self.nseg = h.cas().nseg
        self.h_seg = h.cas()
        for i in range(self.nseg - 1):
            m_s = SubSegment()
            m_s.start_x = h.x3d(i)
            m_s.start_y = h.y3d(i)
            m_s.start_z = h.z3d(i)
            m_s.end_x = h.x3d(i + 1)
            m_s.end_y = h.y3d(i + 1)
            m_s.end_z = h.z3d(i + 1)
            m_s.diam = h.diam3d(i)
            m_s.calc_h()
            self.__update_data(params, m_s, float(float(i)/float(self.nseg)))
            self.sub_sec.append(m_s)

    def __update_data(self, params, m_s, n):
        """
        Initializing parameters what we want get from NEURON simulation

        :param params: parameters interesting
        :param m_s: current subsegmet
        :param n: number of current subsection in section it defines by nseg
        """
        for p in params:
            m_s.params[p] = self.h_seg(n)._ref_v[0]
            # TODO find mode suitable way how to do it

    def update_data(self, params):
        for s_sec in self.sub_sec:
            i = float(float(self.sub_sec.index(s_sec))/float(self.nseg))
            self.__update_data(params, s_sec, i)


class MyNeuron:
    def __init__(self, name=""):
        self.name = name
        self.section = []

    def init_sections(self, h, params):
        """
        Select from list of sections
        only sections for particular helper
        fill list of section ids

        :param h: hocObject
        """
        pattern = '^' + self.name + '_.*'
        nrn_pattern = re.compile(pattern)
        index = 0
        for h_sec in h.allsec():
            section_name = h_sec.name()
            if not (nrn_pattern.search(section_name) is None):
                s = Segment(index, section_name)
                s.init_segment(h, params)
                self.section.append(s)
            index += 1

    def update_seg_data(self, params):
        """

        :rtype : object
        """
        for s in self.section:
            s.update_data(params)