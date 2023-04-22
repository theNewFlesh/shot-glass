from pandas import DataFrame

import shot_glass.obj.obj_tools as obt
from shot_glass.hifive.test_base import HiFiveTestBase
# ------------------------------------------------------------------------------


class ValidatorsTests(HiFiveTestBase):
    def test_obj_face_to_edges(self):
        expected = DataFrame()
        expected['v_id'] = [0, 1, 1, 2, 2, 3, 3, 0]
        expected['e_id'] = [0, 0, 1, 1, 2, 2, 3, 3]
        expected['v_i_draw_order'] = [0, 1, 1, 2, 2, 3, 3, 0]
        expected['f_id'] = 0

        result = obt.obj_face_to_edges([0, 1, 2, 3])

        #  convert uuids to ints
        e_lut = result.e_id.drop_duplicates().tolist()
        e_lut = {k: i for i, k in enumerate(e_lut)}
        result.e_id = result.e_id.apply(lambda x: e_lut[x])

        #  convert uuids to ints
        f_lut = result.f_id.drop_duplicates().tolist()
        f_lut = {k: i for i, k in enumerate(f_lut)}
        result.f_id = result.f_id.apply(lambda x: f_lut[x])

        for col in expected.columns:
            self.assertEqual(result[col].tolist(), expected[col].tolist())

    def test_row_to_obj_face(self):
        data = self.fake_data
        result = data.groupby('f_id') \
            .apply(obt.row_to_obj_face) \
            .tolist()
        expected = ['f 1 2 3 4']
        self.assertEqual(result, expected)
