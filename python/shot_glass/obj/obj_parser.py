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
            .set_parse_action(lambda s, _, t: float(t[0]))
        int_ = pyparsing.pyparsing_common.integer

        # vertex
        v_key = Keyword('v').set_parse_action(lambda s, _, t: 'vertex')
        v = Group(v_key + flt + flt + flt + Optional(flt))\
            .set_results_name('component')\
            .set_parse_action(lambda s, _, t: self.__vertex_to_dict(t, list('xyzw')))
        self.__v = v

        # vertex normal
        vn_key = Keyword('vn').set_parse_action(lambda s, _, t: 'vertex_normal')
        vn = Group(vn_key + flt + flt + flt)\
            .set_results_name('component')\
            .set_parse_action(lambda s, _, t: self.__vertex_to_dict(t, list('ijk')))
        self.__vn = vn

        # vertex parametric point
        vp_key = Keyword('vp').set_parse_action(lambda s, _, t: 'vertex_point')
        vp_w = Optional(flt, default=1.0)
        vp = Group(vp_key + flt + flt + vp_w)\
            .set_results_name('component')\
            .set_parse_action(lambda s, _, t: self.__vertex_to_dict(t, list('uvw')))
        self.__vp = vp

        # vertex texture
        vt_key = Keyword('vt').set_parse_action(lambda s, _, t: 'vertex_texture')
        vt_w = Optional(flt, default=0.0)
        vt = Group(vt_key + flt + flt + vt_w)\
            .set_results_name('component')\
            .set_parse_action(lambda s, _, t: self.__vertex_to_dict(t, list('uvw')))
        self.__vt = vt

        # generic vertex
        vertex = v | vn | vp | vt
        self.__vertex = vertex

        # face
        f_key = Keyword('f')\
            .set_results_name('component_type')\
            .set_parse_action(lambda s, _, t: 'face')

        f_v = int_.set_results_name('vertex_id')

        f_vt = Optional(int_, default=None).set_results_name('vertex_texture_id')
        f_vt_empty = empty\
            .set_results_name('vertex_texture_id')\
            .set_parse_action(lambda s, _, t: [None])

        f_vn = Optional(int_, default=None).set_results_name('vertex_normal_id')
        f_vn_empty = empty\
            .set_results_name('vertex_normal_id')\
            .set_parse_action(lambda s, _, t: [None])

        # face item are delimited with '/' but can omit elements which makes
        # parsing them difficult
        slash = Suppress('/')
        a = f_v + slash + f_vt_empty + slash + f_vn
        b = f_v + slash + f_vt + slash + f_vn
        c = f_v + slash + f_vt + f_vn_empty
        d = f_v + f_vt_empty + f_vn_empty
        f_item = Group(a | b | c | d)

        face = f_key + OneOrMore(f_item).set_results_name('parts')
        self.__face = face

        # parser
        component = StringStart() + (vertex | face) + StringEnd()
        self.__component = component
        comment = Suppress(Regex('^#'))
        comment = comment + Regex('.*').set_results_name('comment') + StringEnd()
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
        return self._parser.parse_string(line.strip('\n'))

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
