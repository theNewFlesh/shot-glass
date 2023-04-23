import re

import pandas as pd
from pandas import DataFrame

from shot_glass.hifive.type_base import HiFiveTypeBase
from shot_glass.core.tools import ValidationError
import shot_glass.hifive.hifive_tools as hft

import logging
LOGGER = logging.getLogger(__name__)
# ------------------------------------------------------------------------------

HIFIVE_FILE_EXTENSION = 'hi5'


class HiFiveDataType(HiFiveTypeBase):
    '''
    Legal data types for HiFive columns.
    '''
    FLOAT = ('float', 'f', float, hft.is_float, None)
    INTEGER = ('integer', 'i', int, hft.is_integer, None)
    JSON = ('json', 'j', str, hft.is_json, None)
    OPTIONAL = ('optional', 'x', object, lambda x: True, None)
    STRING = ('string', 's', str, hft.is_string, None)


class HiFiveComponentType(HiFiveTypeBase):
    '''
    Legal component types for HiFive columns.
    '''
    ITEMS = ('item', 'i', None, None, 0)
    FACES = ('face', 'f', None, None, 1)
    EDGES = ('edge', 'e', None, None, 2)
    VERTICES = ('vertex', 'v', None, None, 3)


class HiFive():
    '''
    HIFIVE stands for Homomorphically Indexed Faces Items Vertices and Edges

    It is a class for definining 3D polygonal geometry in a manner that is most
    conducive to computer vision, machine learning and procedural modeling
    algorithm development. It does this by defining relationships between
    the components of 3D geometry (items, faces, edges and vertices) within a
    singular table, such that structure preserving maps between the components
    (homomorphisms) are easily observed, maintained and modified.

    The internal table of this class, being just a Pandas DataFrame of
    optionally typed columns, fits seamnlessy into the workflow of a data
    scientist which is often the application of mathematical models and linear
    algebra to large matrices of numbers/consistently typed data.

    Columns consist of 3 parts: a component type, a datatype and a descriptor.

    **Components**

        Polygonal geometry consist of 4 main component types:

            * *Items (i)*    - A set of faces, edges and/or vertices.
            * *Faces (f)*    - A set of edges connected to form a closed 2D \
                shape.
            * *Edges (e)*    - A set of exactly two vertices.
            * *Vertices (v)* - A set of x,y,z floating point coordinates.

        A ctype (component type) indicates one of these. Ctypes are used for
        homomorphically mapping data from a source component to a target
        component. This is to say, in a way that preserves the relationship
        between the two.

    **Data**

        HiFive DataFrames may contain 5 types of elements:

            * *float (f)*    - Floating point number (such as for coordinates).
            * *integer (i)*  - Integer number (such as for ids).
            * *string (s)*   - String of text (such as notes).
            * *json (j)*     - String which can be converted into JSON \
                (for advanced use).
            * *optional (x)* - Any data type, to be used temporarily for \
                algorithm development. Hopefully, this is purged later on in \
                said algorithm.

        A dtype (data type) indicates the type all values with in a column must
        conform to. Null values (np.nan) are ignored within these columns.
        Optional typing, particulary with non scalar elements is strongly
        discouraged.

    **Naming**

        With the exception of the default columns, which are immutable, all
        columns must follow the following naming convention:
        **[ctype]_[dtype]_[descriptor]**. The dtypes of the default columns are
        ommitted for the sake of brevity.

        The default columns are as follows:

            * *i_id* - Item id (integer)
            * *f_id* - Face id (integer)
            * *e_id* - Edge id (integer)
            * *v_id* - Vertex id (integer)
            * *v_x*  - Vertex x coordinate (float)
            * *v_y*  - Vertex y coordinate (float)
            * *v_z*  - Vertex z coordinate (float)

    All these columns may contain nans and likely will contain duplicates. The
    HiFive DataFrame is granular to the level of a single relationship of a
    vertex and another component, not simply just the level of the vertex.
    '''
    __DEFAULT_COLUMNS = ['i_id', 'f_id', 'e_id', 'v_id', 'v_x', 'v_y', 'v_z']

    def __init__(self):
        '''
        Creates an empty HiFive instance with the default columns.
        '''
        self.data = DataFrame(columns=self.__DEFAULT_COLUMNS)
    # --------------------------------------------------------------------------

    def read_hi5(self, fullpath):
        '''
        Reads a given hi5 file from disk.

        Args:
            fuillpath (str): Full path to hi5 file.

        Raises:
            ValidationError: If file does not end in 'hi5' extension.
            TypeError: If column names or values of data are invalid.

        Returns:
            HiFive: self.
        '''
        hft.validate_file_extension(fullpath, HIFIVE_FILE_EXTENSION)
        self.data = pd.read_hdf(fullpath, 'data')
        self.validate()
        return self

    def write_hi5(self, fullpath):
        '''
        Writes data to given hi5 filepath.

        Args:
            fullpath (str): Full path to hi5 file.

        Raises:
            ValidationError: If file does not end in 'hi5' extension.

        Returns:
            HiFive: self.
        '''
        hft.validate_file_extension(fullpath, HIFIVE_FILE_EXTENSION)
        self.data.to_hdf(fullpath, 'data')
        LOGGER.info(f'HiFive data written to {fullpath}')
        return self
    # --------------------------------------------------------------------------

    def validate_column(self, column):
        '''
        Validate a given column's name, and validate its values according to its
        type indicator.

        Args:
            column (str): Column name.

        Raises:
            ValidationError: If column name or values are invalid.

        Returns:
            HiFive: self.
        '''
        if column not in self.data.columns.tolist():
            msg = f'{column} not found in columns.'
            raise ValidationError(msg)

        self._validate_column_name(column)
        self._validate_column_values(column)
        return self

    def validate(self):
        '''
        Validate all column names and values.

        Raises:
            ValidationError: If any column name or set of values are invalid.

        Returns:
            HiFive: self.
        '''
        for column in self.data.columns.tolist():
            self.validate_column(column)
        return self

    def _get_column_attributes(self, column):
        '''
        Generates a dict of attributes describing a given column.

        Attributes include:

            * name - Full name of column
            * descriptor - Descriptor of column (comes after ctype and dtype)
            * ctype_indicator - Component type indicator (one of i, f, e, v)
            * dtype_indicator - Data type indicator (on of f, i, s, j, x)
            * has_nans - Whether column contains nan values

        Args:
            column (str): Column name.

        Returns:
            dict: dict of attributes.
        '''
        ctype_i = None
        dtype_i = None
        desc = None
        if column in self.__DEFAULT_COLUMNS:
            ctype_i, desc = column.split('_')
            if desc == 'id':
                dtype_i = 'i'
            else:
                dtype_i = 'f'
        else:
            ctype_i, dtype_i, desc = re.split('_', column, maxsplit=2)

        hasnans = None
        if column in self.data.columns.tolist():
            hasnans = self.data[column].hasnans

        return dict(
            name=column,
            descriptor=desc,
            ctype_indicator=ctype_i,
            dtype_indicator=dtype_i,
            has_nans=hasnans
        )

    def _validate_column_name(self, column):
        '''
        Validates a given column name. Ensures that indicated component type
        (ctype) and data type (dtype) are legal.

        Args:
            column (str): Column name to be validated.

        Raises:
            ValidationError: If column name does not have 3 parts separated by
                '_'.
            ValidationError: If indicated ctype is illegal.
            ValidationError: If indicated dtype is illegal.

        Returns:
            HiFive: self.
        '''
        if column not in self.__DEFAULT_COLUMNS:
            parts = re.split('_', column, maxsplit=2)
            if len(parts) != 3:
                msg = f'{column} is not a valid column name.'
                raise ValidationError(msg)

        attrs = self._get_column_attributes(column)

        ctype = attrs['ctype_indicator']
        if not HiFiveComponentType.is_valid_indicator(ctype):
            msg = f'{ctype} is not a valid ctype indicator.'
            raise ValidationError(msg)

        dtype = attrs['dtype_indicator']
        if not HiFiveDataType.is_valid_indicator(dtype):
            msg = f'{dtype} is not a valid dtype indicator.'
            raise ValidationError(msg)

    def _validate_column_values(self, column):
        '''
        Validates that values of a given column are of the type indicated by its
        dtype indicator.

        Args:
            column (str): Name of column to be validated.

        Raises:
            TypeError: If element of column values if not if indicated data
                type.

        Returns:
            HiFive: self.
        '''
        if self.data.shape[0] < 1:
            return

        dtype = self._get_column_attributes(column)['dtype_indicator']
        dtype = HiFiveDataType.from_indicator(dtype)
        for item in self.data[column].tolist():
            if not dtype.is_valid_value(item):
                msg = 'Non-{} value found in column {}: {}'
                msg = msg.format(dtype.fullname, column, str(item))
                raise TypeError(msg)
    # --------------------------------------------------------------------------

    def map(self, source, target, aggregator):
        '''
        Maps data within and across component types homomorphically.

        The given aggregator functions is part of how it does this.
        For example:

        ::

            hi = HiFive().read_hi5('foo.hi5')
            hi.map('v_id', 'f_i_bar', lambda x: int(x.mean()))

        The call to map here maps a column of vertex data, indicated by the
        'v' in 'v_id', into a new column of face data, indicated by the 'f' in
        'f_i_bar'. The relationship between a vertex and a face components is
        many to one. So, the aggregator must convert the many items of x
        (a pandas Series object) into one value (their mean). Additionally,
        because the target column is dtyped with an 'i', its values must be
        integers. Thus, said mean value is coerced into an integer inside the
        aggregator.

        Args:
            source (str): Source column from which data should be mapped.
            target (str): Name of new column to be created.
            aggregator (function): Function responsible for mapping/modifying \
                values of the source column into the target column. Expects a \
                pandas Series object as input.

        Raises:
            ValidationError: If target column ctype is illegal.
            ValidationError: If target column dtype is illegal.
            ValidationError: If source column contains null values.
            TypeError: If target column values are illegal.

        Returns:
            HiFive: self with new target column.
        '''
        self._validate_column_name(source)
        self._validate_column_name(target)

        # Mappings must always be 1 to many or 1 to 1, because aggregators take
        # one or many components and return one. So, establishing the
        # relationship between source and target component is necessary here.

        # component hierarchy
        # items contain faces contain edges contain vertices
        source_attrs = self._get_column_attributes(source)
        target_attrs = self._get_column_attributes(target)
        a = HiFiveComponentType.from_indicator(source_attrs['ctype_indicator'])
        b = HiFiveComponentType.from_indicator(target_attrs['ctype_indicator'])

        # assume target component contains source component
        attrs = target_attrs

        # if source component contains target component
        if a.order < b.order:
            attrs = source_attrs

        ctype_i = attrs['ctype_indicator']
        id_col = ctype_i + '_id'

        dtype = HiFiveDataType.from_indicator(target_attrs['dtype_indicator'])

        if self.data[id_col].hasnans:
            ctype = HiFiveComponentType.from_indicator(ctype_i).fullname
            msg = f'Cannot map to column of {ctype} component type because'
            msg += f' {id_col} column contains null values.'
            raise TypeError(msg)

        temp_column = False
        if id_col == source:
            temp_column = True
            source = '__temp'
            self.data[source] = self.data[id_col]

        # Build a lookup table with the id of largest component in the mapping
        # as the keys and the aggregation of the source column values per key as
        # the values.

        # So, if the data looks like this:
        # f_id | v_id | v_s_foo
        # -----|------|--------
        #   0  |   0  |    a
        #   0  |   1  |    b
        #   1  |   2  |    c
        #   1  |   3  |    d

        # hi.map('v_s_foo', 'f_s_bar', lambda x: '-'.join(x.tolist()))
        # will produce this lut:
        # {
        #   0: [a, b]
        #   1: [b, c]
        # }

        # and this new column to the table:
        # f_id | v_id | v_s_foo | f_s_bar
        # -----|------|---------|--------
        #   0  |   0  |    a    |   a-b
        #   0  |   1  |    b    |   a-b
        #   1  |   2  |    c    |   c-d
        #   1  |   3  |    d    |   c-d

        # The homomorphic aspect of HiFive is to do with the homogenous mapping
        # of information across rows per component id.

        # For example, the face with face id of 0 must have the same properties
        # for its f_s_bar columns across all its rows. Thus 'a-b', and only
        # 'a-b', must be mapped to this column of each of them.

        lut = self.data[[id_col, source]] \
            .groupby(id_col, as_index=False)[source] \
            .agg(lambda x: aggregator(x))
        if dtype != 'optional':
            lut[source] = lut[source].astype(dtype.type_)

        ids = lut[id_col].tolist()
        values = lut[source].tolist()
        lut = dict(zip(ids, values))

        if temp_column:
            del self.data[source]

        self.data[target] = self.data[id_col].apply(lambda x: lut[x])
        self.validate_column(target)

        return self
    # --------------------------------------------------------------------------

    def __expand_row(self, row, source, target, expander):
        '''
        Transform the contents of a given row into many rows via a given
        expander.

        Args:
            row (Series): Series to be expanded.
            source (str): Index element of row to be expanded.
            target (str): Name of new row index to be created.
            expander (function): Function that receives an element and \
                produces a list of new elements.

        Returns:
            DataFrame: DataFrame of new rows.
        '''
        output = DataFrame()
        output[target] = expander(row[source])
        cols = row.index.tolist()
        cols = list(filter(lambda x: x != source, cols))
        for col in cols:
            output[col] = row[col]
        return output

    def expand(self, source, target, id_, expander):
        '''
        Expands elements within each row of a source column into multiple rows.

        Args:
            source (str): Source column to be expanded.
            target (str): Name of new column to be created.
            id_ (str): Name of id column to be created, which groups rows based \
                on source. Must be of integer dtype.
            expander (function): Function which converts a row element in to a \
                list of elements.

        Raises:
            TypeError: If id is not of integer dtype.
            ValidationError: If source, target or id names are invalid.
            TypeError: If source, target or id values are invalid.

        Returns:
            HiFive: self with expanded rows.
        '''
        self._validate_column_name(source)
        self._validate_column_name(target)
        self._validate_column_name(id_)

        id_attrs = self._get_column_attributes(id_)
        dtype = HiFiveDataType.from_indicator(id_attrs['dtype_indicator'])
        if dtype != HiFiveDataType.INTEGER:
            msg = 'Id column must be of dtype INTEGER. '
            msg += f'Provided dtype: {dtype.name}.'
            raise TypeError(msg)

        self.data[id_] = self.data.index

        # create a list of expanded DataFrames
        data = self.data.apply(
            lambda x: self.__expand_row(x, source, target, expander),
            axis=1)\
            .tolist()

        # concatenate that list into a single DataFrame
        data = pd.concat(data, ignore_index=True)

        cols = self.data.columns.tolist()
        cols = [target if x == source else x for x in cols]
        data = data[cols]

        self.data = data
        self.validate()
        return self
    # --------------------------------------------------------------------------

    def copy(self):
        '''
        Copy HiFive instance to new HiFive instance.

        Returns:
            HiFive: new HiFive instance.
        '''
        output = HiFive()
        output.data = self.data.copy()
        return output

    @property
    def info(self):
        '''
        Returns:
            DataFrame: A DataFrame describing the universal attributes of all
            the columns of the internal DataFrame.
        '''
        info = []
        for item in self.data.columns.tolist():
            item = self._get_column_attributes(item)
            item['dtype'] = HiFiveDataType\
                .from_indicator(item['dtype_indicator']).fullname
            item['ctype'] = HiFiveComponentType\
                .from_indicator(item['ctype_indicator']).fullname
            info.append(item)

        info = DataFrame(info)

        cols = [
            'name',
            'descriptor',
            'ctype',
            'dtype',
            'ctype_indicator',
            'dtype_indicator',
            'has_nans'
        ]
        info = info[cols].T
        return info

    @property
    def item_info(self):
        '''
        Returns:
            DataFrame: A DataFrame in which all columns are of item component
            type and each row contains a unique item id.
        '''
        info = self.data.filter(axis=1, regex='^i_')
        return info.groupby('i_id', as_index=False).first()

    @property
    def face_info(self):
        '''
        Returns:
            DataFrame: A DataFrame in which all columns are of face component
            type and each row contains a unique face id.
        '''
        info = self.data.filter(axis=1, regex='^f_')
        return info.groupby('f_id', as_index=False).first()

    @property
    def edge_info(self):
        '''
        Returns:
            DataFrame:  DataFrame in which all columns are of edge component
            type and each row contains a unique edge id.
        '''
        info = self.data.filter(axis=1, regex='^e_')
        return info.groupby('e_id', as_index=False).first()

    @property
    def vertex_info(self):
        '''
        Returns:
            DataFrame: A DataFrame in which all columns are of vertex component
            type and each row contains a unique vertex id.
        '''
        info = self.data.filter(axis=1, regex='^v_')
        return info.groupby('v_id', as_index=False).first()

    @property
    def geometry_info(self):
        '''
        Returns:
            DataFrame: A DataFrame that describes basic geometric and
            topological properties of the internal data.
        '''
        cols = ['item', 'face', 'edge', 'vertex']
        index = [x + 's_per' for x in cols]
        index.insert(0, 'count_of')
        index[-1] = 'vertices_per'
        index.append('topology_of')
        output = DataFrame(columns=cols, index=index)

        output.loc['count_of', 'item'] = self.__get_nunique('i_id')
        output.loc['count_of', 'face'] = self.__get_nunique('f_id')
        output.loc['count_of', 'edge'] = self.__get_nunique('e_id')
        output.loc['count_of', 'vertex'] = self.__get_nunique('v_id')

        output.loc['items_per', 'item'] = 1
        output.loc['faces_per', 'face'] = 1
        output.loc['edges_per', 'edge'] = 1
        output.loc['vertices_per', 'vertex'] = 1

        output.loc['faces_per', 'item'] = self\
            .__get_unique_counts('f_id', 'i_id')
        output.loc['edges_per', 'item'] = self\
            .__get_unique_counts('e_id', 'i_id')
        output.loc['vertices_per', 'item'] = self\
            .__get_unique_counts('v_id', 'i_id')

        output.loc['edges_per', 'face'] = self\
            .__get_unique_counts('e_id', 'f_id')
        output.loc['vertices_per', 'face'] = self\
            .__get_unique_counts('v_id', 'f_id')

        output.loc['vertices_per', 'edge'] = self\
            .__get_unique_counts('v_id', 'e_id')

        temp = self.__get_unique_counts('e_id', 'f_id', False)
        if temp == []:
            return output

        polygon_types = []
        if 1 in temp or 2 in temp:
            polygon_types.append('invalid')
        if 3 in temp:
            polygon_types.append('triangle')
        if 4 in temp:
            polygon_types.append('quadrilateral')
        if max(temp) >= 5:
            polygon_types.append('ngon')
        output.loc['topology_of', 'face'] = sorted(polygon_types)

        return output

    @property
    def display_data(self):
        '''
        Drops _x_ columns from internal data which cause Jupyter Notebook to
        chug.

        Returns:
            DataFrame: DataFrame with _x_ columns replaced with '...'.
        '''
        data = DataFrame()
        cols = self.data.columns.tolist()
        x_cols = list(filter(lambda x: re.search('^._x_', x), cols))
        nonx_cols = set(cols).difference(x_cols)

        for col in nonx_cols:
            data[col] = self.data[col]
        for col in x_cols:
            data[col] = '...'

        data = data[cols]
        return data

    def __get_unique_counts(self, count_column, group_column, summarize=True):
        '''
        Convenience method for calculating the unique counts of a count column,
        per a group column.

        Args:
            count_column (str): Column to get unique counts of.
            group_column (str): Column to group x by.
            summarize (bool, optional): Converts results into list of \
                [1,2,3,4,n]. Default: True

        Returns:
            list: list of unique counts.
        '''
        items = hft.get_nunique_a_per_b(
            self.data, count_column, group_column
        )
        items = sorted(list(set(items)))
        if not summarize:
            return items

        # replace everything >= 5 with 'n'
        output = []
        for i in items:
            if i >= 5:
                output.append('n')
                break
            output.append(i)
        return output

    def __get_nunique(self, column):
        '''
        Convenience method for calculating the unique, non-null values for a
        given column.

        Args:
            column (str): Column to be processed.

        Returns:
            list: list of unique values.
        '''
        return self.data[column].dropna().nunique()

    def is_equivalent(self, hifive, ignore_columns=[]):
        '''
        Determines if this HiFive instance equivalent to a given HiFive
        instance.

        Ignore columns is currently needed for "e_id" because Blender screws up
        the edge ordering.

        Args:
            hifive - HiFive instance to be compared.
            ignore_columns (list, optional): columns to exempt from comparison.

        Returns:
            bool: Equivalence of instances.
        '''
        a_data = self.data
        b_data = hifive.data

        a_cols = sorted(a_data.columns.tolist())
        b_cols = sorted(b_data.columns.tolist())

        # TODO: Remove this once Blender edge ordering is figured out.
        a_cols = list(filter(lambda x: x not in ignore_columns, a_cols))
        b_cols = list(filter(lambda x: x not in ignore_columns, b_cols))
        a_data = a_data[a_cols]
        b_data = b_data[b_cols]

        # both have the same shape
        if a_data.shape != b_data.shape:
            return False

        # both have the same columns
        if a_cols != b_cols:
            return False

        a_data = a_data.sort_values(a_cols)
        b_data = b_data.sort_values(a_cols)

        # all element of the same column from a and b are the same and in the
        # same order
        for col in a_cols:
            a = a_data[col].tolist()
            b = b_data[col].tolist()
            if a != b:
                return False

        return True
