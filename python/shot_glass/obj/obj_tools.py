from uuid import uuid4

from pandas import DataFrame

from shot_glass.obj.obj_parser import ObjParser
# ------------------------------------------------------------------------------


def obj_face_to_edges(vertex_ids):
    '''
    Converts a list of vertex ids into a HiFive compatible DataFrame.
    Columns of DataFrame include:

        * f_id (with uuids)
        * e_id (with uuids)
        * v_id (integer)
        * v_i_draw_order (preserves draw order of vertices)

    Args:
        vertex_ids (list): List of integers.

    Returns:
        DataFrame: DataFrame.
    '''
    edges = vertex_ids[1:] + [vertex_ids[0]]
    edges = list(zip(vertex_ids, edges))
    o_lut = {k: i for i, k in enumerate(vertex_ids)}

    f_id = str(uuid4())
    output = []
    for edge in edges:
        e_id = str(uuid4())
        for v_id in edge:
            row = dict(
                f_id=f_id,
                e_id=e_id,
                v_id=v_id,
                v_i_draw_order=o_lut[v_id]
            )
            output.append(row)
    output = DataFrame(output)
    return output


def row_to_obj_face(row):
    '''
    Converts row, grouped by face id, into a OBJ parsable string defining a
    face.

    If v_i_draw_order column is present, vertex ids within face will be
    ordered accordingly. For example, a face with the v_ids:
    [10, 20, 30, 40] and a vertex order of [3, 2, 1, 0] would return the
    string 'f 40 30 20 10'.

    OBJ implies edges as existing between successive vertex id in a face
    definition. So, edge [40, 30], [30, 20], and [20, 10] are all implied.
    The face completing edge [10, 40], is also implied. The order they are
    defined in (clockwise, our counterclockwise) determines the orientation
    of the face. Thus, reordering the vertex ids may produce an invalid or
    incorrect face. And reversing the order of all of them will flip the
    face normal, causing it to be rendered incorrectly.

    Args:
        row (Series): Row of DataFrame.

    Returns:
        str: OBJ parsable string.
    '''
    data = row.v_id
    if 'v_i_draw_order' in row.columns.tolist():
        # TODO: This portion is highly inefficient, make it better.
        data = DataFrame()
        data['v_id'] = row.v_id
        data['order'] = row.v_i_draw_order
        data = data.sort_values('order')
        data = data.v_id

    data = data.drop_duplicates()
    data += 1
    data = data.astype(str).tolist()
    output = 'f ' + ' '.join(data)
    return output


def parse(fullpath):
    '''
    Parses a given OBJ file.

    Args:
        fullpath (str): Fullpath to OBJ file.

    Returns:
        list: A list of dictionaries.
    '''
    return ObjParser().parse(fullpath)
