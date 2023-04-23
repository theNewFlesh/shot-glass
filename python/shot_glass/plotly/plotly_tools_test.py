import unittest

import shot_glass.plotly.plotly_tools as plot
# ------------------------------------------------------------------------------


class HiFiveValidatorsTests(unittest.TestCase):
    def test_get_mesh_plot_layout(self):
        result = plot.get_mesh_plot_layout(-2, 9, 1.3)
        x = result['scene']['camera']['eye']['x']
        y = result['scene']['camera']['eye']['y']
        z = result['scene']['camera']['eye']['z']

        zoom = 1.0 / 1.3
        expected = [1 * zoom, 0.75 * zoom, -1 * zoom]
        self.assertEqual([x, y, z], expected)

        x_range = result['scene']['xaxis']['range']
        y_range = result['scene']['yaxis']['range']
        z_range = result['scene']['zaxis']['range']

        expected = [-2, 9]
        self.assertEqual(x_range, expected)
        self.assertEqual(y_range, expected)
        self.assertEqual(z_range, expected)

    def test_get_mesh3d_trace(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 2, 3, 4, 5]
        z = [0, 1, 2, 3, 4, 5]
        i = [0, 3]
        j = [1, 4]
        k = [2, 5]
        result = plot.get_mesh3d_trace(x, y, z, i, j, k)
        self.assertEqual(result['x'], x)
        self.assertEqual(result['y'], y)
        self.assertEqual(result['z'], z)
        self.assertEqual(result['i'], i)
        self.assertEqual(result['j'], j)
        self.assertEqual(result['k'], k)

    def test_get_mesh_plot_figure(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 2, 3, 4, 5]
        z = [0, 1, 2, 3, 4, 5]
        i = [0, 3]
        j = [1, 4]
        k = [2, 5]
        min_ = -2
        max_ = 9
        zoom = 1.3
        result = plot.get_mesh_plot_figure(x, y, z, i, j, k, min_, max_, zoom)

        self.assertEqual(result['data'][0]['x'], x)
        self.assertEqual(result['data'][0]['y'], y)
        self.assertEqual(result['data'][0]['z'], z)
        self.assertEqual(result['data'][0]['i'], i)
        self.assertEqual(result['data'][0]['j'], j)
        self.assertEqual(result['data'][0]['k'], k)

        x = result['layout']['scene']['camera']['eye']['x']
        y = result['layout']['scene']['camera']['eye']['y']
        z = result['layout']['scene']['camera']['eye']['z']

        temp = 1.0 / zoom
        expected = [1 * temp, 0.75 * temp, -1 * temp]
        self.assertEqual([x, y, z], expected)
