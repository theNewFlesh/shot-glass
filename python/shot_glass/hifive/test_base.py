import pandas as pd
from pandas import DataFrame
import unittest
from shot_glass.hifive.hifive import HiFive
# ------------------------------------------------------------------------------


class HiFiveTestBase(unittest.TestCase):
    '''
    Class used for testing the HiFive class and operators.
    '''
    def get_quadrilateral_data(self):
        '''
        Returns:
            DataFrame: DataFrame of single quadrilateral face.
        '''
        # create a DataFrame with 1 face with 4 edges

        cols = HiFive._HiFive__DEFAULT_COLUMNS
        data = DataFrame(columns=cols)
        data['v_id'] = [0, 1, 1, 2, 2, 3, 3, 0]
        data['e_id'] = [0, 0, 1, 1, 2, 2, 3, 3]
        data['f_id'] = [0, 0, 0, 0, 0, 0, 0, 0]
        data['i_id'] = [0, 0, 0, 0, 0, 0, 0, 0]
        data['v_x'] = [0, 1, 1, 2, 2, 3, 3, 0]
        data['v_y'] = [0, 1, 1, 2, 2, 3, 3, 0]
        data['v_z'] = [0, 1, 1, 2, 2, 3, 3, 0]

        data.v_x = data.v_x.astype(float)
        data.v_y = data.v_y.astype(float)
        data.v_z = data.v_z.astype(float)

        return data

    def get_triangle_data(self):
        '''
        Returns:
            DataFrame: DataFrame of single triangular face.
        '''
        # create a DataFrame with 1 face with 3 edges

        cols = HiFive._HiFive__DEFAULT_COLUMNS
        data = DataFrame(columns=cols)
        data['v_id'] = [0, 1, 1, 2, 2, 0]
        data['e_id'] = [0, 0, 1, 1, 2, 2]
        data['f_id'] = [0, 0, 0, 0, 0, 0]
        data['i_id'] = [0, 0, 0, 0, 0, 0]
        data['v_x'] = [0, 1, 1, 2, 2, 0]
        data['v_y'] = [0, 1, 1, 2, 2, 0]
        data['v_z'] = [0, 1, 1, 2, 2, 0]

        data.v_x = data.v_x.astype(float)
        data.v_y = data.v_y.astype(float)
        data.v_z = data.v_z.astype(float)

        return data

    def get_ngon_data(self):
        '''
        Returns:
            DataFrame: DataFrame of single ngon face.
        '''
        # create a DataFrame with 1 face with 5 edges

        cols = HiFive._HiFive__DEFAULT_COLUMNS
        data = DataFrame(columns=cols)
        data['v_id'] = [0, 1, 1, 2, 2, 3, 3, 4, 4, 0]
        data['e_id'] = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
        data['f_id'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data['i_id'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data['v_x'] = [0, 1, 1, 2, 2, 3, 3, 4, 4, 0]
        data['v_y'] = [0, 1, 1, 2, 2, 3, 3, 4, 4, 0]
        data['v_z'] = [0, 1, 1, 2, 2, 3, 3, 4, 4, 0]

        data.v_x = data.v_x.astype(float)
        data.v_y = data.v_y.astype(float)
        data.v_z = data.v_z.astype(float)

        return data

    def get_invalid_data(self):
        '''
        Returns:
            DataFrame: DataFrame of single invalid face.
        '''
        # create a DataFrame with 1 face with 2 edges

        cols = HiFive._HiFive__DEFAULT_COLUMNS
        data = DataFrame(columns=cols)
        data['v_id'] = [0, 1, 1, 0]
        data['e_id'] = [0, 0, 1, 1]
        data['f_id'] = [0, 0, 0, 0]
        data['i_id'] = [0, 0, 0, 0]
        data['v_x'] = [0, 1, 1, 0]
        data['v_y'] = [0, 1, 1, 0]
        data['v_z'] = [0, 1, 1, 0]

        data.v_x = data.v_x.astype(float)
        data.v_y = data.v_y.astype(float)
        data.v_z = data.v_z.astype(float)

        return data

    def get_multi_data(self):
        '''
        Returns:
            DataFrame: DataFrame of with a triangle, a ngon and an invalid face.
        '''

        invalid = self.get_invalid_data()

        ngon = self.get_ngon_data()
        ngon.v_id += invalid.v_id.max() + 1
        ngon.e_id += invalid.e_id.max() + 1
        ngon.f_id += invalid.f_id.max() + 1

        triangle = self.get_triangle_data()
        triangle.v_id += ngon.v_id.max() + 1
        triangle.e_id += ngon.e_id.max() + 1
        triangle.f_id += ngon.f_id.max() + 1

        data = pd.concat([invalid, ngon, triangle])
        return data

    def setUp(self):
        self.fake_data = self.get_quadrilateral_data()

    def tearDown(self):
        self.fake_data = None
