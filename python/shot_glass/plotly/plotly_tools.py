import plotly
# ------------------------------------------------------------------------------


def get_mesh_plot_layout(min_, max_, zoom):
    '''
    Generates a dictionary representation of a Plotly Layout object optimized
    for displaying 3D mesh data.

    Args:
        min_ (float): Minimum value for x, y, z of plot bounding box.
        max_ (float): Maximum value for x, y, z of plot bounding box.
        zoom (float): Multiplier for camera zoom toward object center.

    Returns:
        dict: JSON dictionary representation of plotly.Layout instance.
    '''
    zoom_out = 1.0 / zoom
    range_ = [min_, max_]
    return plotly.graph_objs.Layout(
        height=1024,
        width=1024,
        margin=plotly.graph_objs.layout.Margin(t=0, b=0, l=0, r=0),  # noqa: E741
        paper_bgcolor='rgb(8, 8, 8)',
        title=plotly.graph_objs.layout.Title(
            font=dict(
                color="rgb(244, 244, 244)"
            )
        ),
        font=dict(color='rgb(8, 8, 8)'),
        scene=plotly.graph_objs.layout.Scene(
            xaxis=plotly.graph_objs.layout.scene.XAxis(
                range=range_,
                showgrid=False,
                zeroline=False,
                autorange=False,
                showspikes=False,
                showbackground=False,
                showticklabels=False
            ),
            yaxis=plotly.graph_objs.layout.scene.YAxis(
                range=range_,
                showgrid=False,
                zeroline=False,
                autorange=False,
                showspikes=False,
                showbackground=False,
                showticklabels=False
            ),
            zaxis=plotly.graph_objs.layout.scene.ZAxis(
                range=range_,
                showgrid=False,
                zeroline=False,
                autorange=False,
                showspikes=False,
                showbackground=False,
                showticklabels=False
            ),
            camera=plotly.graph_objs.layout.scene.Camera(
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(
                    x=1 * zoom_out,
                    y=0.75 * zoom_out,
                    z=-1 * zoom_out
                )
            )
        )
    ).to_plotly_json()


def get_mesh3d_trace(x, y, z, i, j, k):
    '''
    Generates a dictionary representation of a Plotly Mesh3d trace object
    optimized for 3D mesh display.

    Args:
        x (list): List of vertex x coordinate values.
        y (list): List of vertex y coordinate values.
        z (list): List of vertex z coordinate values.
        i (list): List of 1st vertices of each triangular face.
        j (list): List of 2nd vertices of each triangular face.
        k (list): List of 3rd vertices of each triangular face.

    Returns:
        dict: JSON dictionary representation of plotly.Mesh3d instance.
    '''
    # swap y and z, beacuse plotly is z up and camera.up.y = 1 doesn't work
    return plotly.graph_objs.Mesh3d(
        x=x, y=z, z=y, i=i, j=j, k=k,
        color="rgb(255, 255, 255)",
        opacity=1,
        lighting=dict(
            ambient=0.09,
            diffuse=0.72,
            specular=0.13,
            roughness=0.28,
            fresnel=0.04
        ),
        lightposition=dict(
            x=0.98,
            y=0.87,
            z=0.0
        )
    ).to_plotly_json()


def get_mesh_plot_figure(x, y, z, i, j, k, min_, max_, zoom):
    '''
    Generates a dictionary representation of a Plotly Figure object optimized
    and directly used for plottingg 3D mesh data.

    Args:
        x (list): List of vertex x coordinate values.
        y (list): List of vertex y coordinate values.
        z (list): List of vertex z coordinate values.
        i (list): List of 1st vertices of each triangular face.
        j (list): List of 2nd vertices of each triangular face.
        k (list): List of 3rd vertices of each triangular face.
        min_ (float): Minimum value for x, y, z of plot bounding box.
        max_ (float): Maximum value for x, y, z of plot bounding box.
        zoom (float): Multiplier for camera zoom toward object center.

    Returns:
        dict: JSON dictionary representation of plotly.Figure instance.
    '''
    layout = get_mesh_plot_layout(min_, max_, zoom)
    data = get_mesh3d_trace(x, y, z, i, j, k)
    return plotly.graph_objs.Figure(layout=layout, data=[data]).to_plotly_json()
