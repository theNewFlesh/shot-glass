import lunchbox.stopwatch as lbsw
import pyparsing
from pyparsing import Keyword, Group, Regex, Optional, Suppress, OneOrMore
from pyparsing import StringEnd, StringStart, empty

import logging
LOGGER = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


class ObjParser():
    '''
    A simple parser for files in OBJ format.

    Currently supports:

        * vertices
        * vertex normals
        * vertex points
        * vertex textures
        * faces
    '''
    def __init__(self):
        '''
        Defines Backus-Naur form for parsing OBJ files.
        '''
        # numbers
        flt = pyparsing.pyparsing_common.number\
            .setParseAction(lambda s, l, t: float(t[0]))
        int_ = pyparsing.pyparsing_common.integer

        # vertex
        v_key = Keyword('v').setParseAction(lambda s, l, t: 'vertex')
        v = Group(v_key + flt + flt + flt + Optional(flt))\
            .setResultsName('component')\
            .setParseAction(lambda s, l, t: self.__vertex_to_dict(t, list('xyzw')))
        self.__v = v

        # vertex normal
        vn_key = Keyword('vn').setParseAction(lambda s, l, t: 'vertex_normal')
        vn = Group(vn_key + flt + flt + flt)\
            .setResultsName('component')\
            .setParseAction(lambda s, l, t: self.__vertex_to_dict(t, list('ijk')))
        self.__vn = vn

        # vertex parametric point
        vp_key = Keyword('vp').setParseAction(lambda s, l, t: 'vertex_point')
        vp_w = Optional(flt, default=1.0)
        vp = Group(vp_key + flt + flt + vp_w)\
            .setResultsName('component')\
            .setParseAction(lambda s, l, t: self.__vertex_to_dict(t, list('uvw')))
        self.__vp = vp

        # vertex texture
        vt_key = Keyword('vt').setParseAction(lambda s, l, t: 'vertex_texture')
        vt_w = Optional(flt, default=0.0)
        vt = Group(vt_key + flt + flt + vt_w)\
            .setResultsName('component')\
            .setParseAction(lambda s, l, t: self.__vertex_to_dict(t, list('uvw')))
        self.__vt = vt

        # generic vertex
        vertex = v | vn | vp | vt
        self.__vertex = vertex

        # face
        f_key = Keyword('f')\
            .setResultsName('component_type')\
            .setParseAction(lambda s, l, t: 'face')

        f_v = int_.setResultsName('vertex_id')

        f_vt = Optional(int_, default=None).setResultsName('vertex_texture_id')
        f_vt_empty = empty\
            .setResultsName('vertex_texture_id')\
            .setParseAction(lambda s, l, t: [None])

        f_vn = Optional(int_, default=None).setResultsName('vertex_normal_id')
        f_vn_empty = empty\
            .setResultsName('vertex_normal_id')\
            .setParseAction(lambda s, l, t: [None])

        # face item are delimited with '/' but can omit elements which makes
        # parsing them difficult
        slash = Suppress('/')
        a = f_v + slash + f_vt_empty + slash + f_vn
        b = f_v + slash + f_vt + slash + f_vn
        c = f_v + slash + f_vt + f_vn_empty
        d = f_v + f_vt_empty + f_vn_empty
        f_item = Group(a | b | c | d)

        face = f_key + OneOrMore(f_item).setResultsName('parts')
        self.__face = face

        # parser
        component = StringStart() + (vertex | face) + StringEnd()
        self.__component = component
        comment = Suppress(Regex('^#'))
        comment = comment + Regex('.*').setResultsName('comment') + StringEnd()
        parser = component | comment | empty

        self._parser = parser

    @staticmethod
    def __vertex_to_dict(tokens, components):
        '''
        Convenience method for converting parsed vertex data into a dictionary.

        Args:
            tokens (list): list of pyparsing tokens.
            compoents (list): list of components.

        Returns:
            dict: Vertex dictionary.
        '''
        return dict(zip(['component_type'] + components, tokens[0]))

    def _parse_line(self, line):
        '''
        Parses given line of OBJ file.

        Args:
            line (str): Line of OBJ file.

        Returns:
            object: Pyparsing object.
        '''
        return self._parser.parseString(line.strip('\n'))

    def parse(self, fullpath):
        '''
        Parses a given OBJ file.

        Args:
            fullpath (str): Fullpath to OBJ file.

        Returns:
            list: A list of dictionaries.
        '''
        stopwatch = lbsw.StopWatch()
        stopwatch.start()

        def assign_component_id(item, line_number, lut):
            comp = item['component_type']
            first = lut[comp]
            if first is None:
                first = line_number
                lut[comp] = line_number
            item[comp + '_id'] = (line_number - first) + 1
            return item

        lut = dict(
            vertex=None,
            vertex_normal=None,
            vertex_point=None,
            vertex_texture=None,
            face=None
        )
        output = []
        with open(fullpath) as f:
            for i, line in enumerate(f.readlines()):
                item = self._parse_line(line)
                if item.asList() == []:
                    continue
                item = item.asDict()

                if 'comment' in item.keys():
                    item['line_type'] = 'comment'

                elif 'component' in item.keys():
                    item = item['component']
                    item['line_type'] = 'component'
                    item = assign_component_id(item, i, lut)

                output.append(item)

        stopwatch.stop()
        LOGGER.info(f'Parse runtime: {stopwatch.human_readable_delta}.')
        return output
